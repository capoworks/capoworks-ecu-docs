"""Focused stdlib tests for the AI documentation publication gate."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


PUBLISH_SCRIPT = pathlib.Path(__file__).with_name("ai-docs-publish.py")
DEPLOY_WORKFLOW = PUBLISH_SCRIPT.parent.parent / ".github" / "workflows" / "deploy.yml"
SYNC_WORKFLOW = (
    PUBLISH_SCRIPT.parent.parent / ".github" / "workflows" / "ai-docs-sync.yml"
)
spec = importlib.util.spec_from_file_location("ai_docs_publish_test_target", PUBLISH_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load publication script")
publish = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = publish
spec.loader.exec_module(publish)
sync = publish.SYNC

OLD_CURSOR = "2" * 40
NEW_CURSOR = "3" * 40
OLD_HISTORY = "a" * 40


def _base_state() -> dict:
    return {
        "schema_version": 1,
        "source_repository": sync.SOURCE_REPOSITORY,
        "source_branch": sync.SOURCE_BRANCH,
        "target_repository": sync.TARGET_REPOSITORY,
        "target_branch": sync.TARGET_BRANCH,
        "cursor_commit": OLD_CURSOR,
        "initial_backfill": {
            "through_commit": "b" * 40,
            "commit_count": 5,
            "completed": True,
        },
        "last_sync": {
            "range": {
                "base_exclusive": "1" * 40,
                "head_inclusive": OLD_CURSOR,
                "commit_count": 1,
            },
            "model": "deepseek-flash",
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            "summary": "Previous sync.",
            "outcome": "no-impact",
            "decisions": [],
            "files_changed": [],
            "recorded_at": "2026-01-01T00:00:00+00:00",
        },
    }


def _next_state(update: bool, files: list[str]) -> dict:
    state = copy.deepcopy(_base_state())
    state["cursor_commit"] = NEW_CURSOR
    state["last_sync"] = {
        "range": {
            "base_exclusive": OLD_CURSOR,
            "head_inclusive": NEW_CURSOR,
            "commit_count": 1,
        },
        "model": "deepseek-flash",
        "usage": {"prompt_tokens": 2, "completion_tokens": 1},
        "summary": "Candidate sync.",
        "outcome": "update" if update else "no-impact",
        "decisions": [
            {
                "commit": NEW_CURSOR,
                "decision": "update" if update else "no-impact",
                "rationale": "The source change was reviewed.",
                "evidence": ["Fixture evidence"],
            }
        ],
        "files_changed": files,
        "recorded_at": "2026-01-01T01:00:00+00:00",
    }
    return state


class GitCandidate:
    def __init__(
        self, root: pathlib.Path, base: str, head: str, merge: str, branch: str
    ) -> None:
        self.root = root
        self.base = base
        self.head = head
        self.merge = merge
        self.branch = branch


class GitFixture:
    def __init__(self, directory: pathlib.Path) -> None:
        self.root = directory / "repo"
        self.root.mkdir(parents=True)
        (self.root / "docs").mkdir()
        (self.root / ".ai-docs" / "history").mkdir(parents=True)
        self._git("init", "-b", "master")
        self._git("config", "user.name", "Fixture Human")
        self._git("config", "user.email", "human@example.com")
        (self.root / "docs" / "existing.md").write_text(
            "---\ntitle: Existing\n---\n\nOld content.\n", encoding="utf-8"
        )
        (self.root / ".ai-docs" / "state.json").write_text(
            json.dumps(_base_state(), indent=2) + "\n", encoding="utf-8"
        )
        (self.root / ".ai-docs" / "history" / f"{OLD_HISTORY}.json").write_text(
            '{"old": true}\n', encoding="utf-8"
        )
        self._git("add", "-A")
        self._git("commit", "-m", "base")
        self.base = self._git("rev-parse", "HEAD").strip()

    def _git(
        self,
        *args: str,
        env: dict[str, str] | None = None,
    ) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.root,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout

    def candidate(
        self,
        *,
        update: bool = True,
        mutate=None,
        bot_identity: tuple[str, str] = (sync.COMMIT_NAME, sync.COMMIT_EMAIL),
    ) -> GitCandidate:
        branch = f"candidate-{len(list(self.root.glob('docs/*')))}"
        self._git("switch", "-c", branch)
        files = ["docs/existing.md"] if update else []
        if update:
            (self.root / "docs" / "existing.md").write_text(
                "---\ntitle: Existing\n---\n\nNew content.\n", encoding="utf-8"
            )
        next_state = _next_state(update, files)
        (self.root / ".ai-docs" / "state.json").write_text(
            json.dumps(next_state, indent=2) + "\n", encoding="utf-8"
        )
        history = sync._history_text(sync._history_record(_base_state(), next_state))
        (self.root / ".ai-docs" / "history" / f"{NEW_CURSOR}.json").write_text(
            history, encoding="utf-8"
        )
        if mutate is not None:
            mutate(self.root)
        self._git("add", "-A")
        env = dict(
            os.environ,
            GIT_AUTHOR_NAME=bot_identity[0],
            GIT_AUTHOR_EMAIL=bot_identity[1],
            GIT_COMMITTER_NAME=bot_identity[0],
            GIT_COMMITTER_EMAIL=bot_identity[1],
        )
        self._git("commit", "-m", "docs: sync fixture", env=env)
        head = self._git("rev-parse", "HEAD").strip()
        tree = self._git("rev-parse", "HEAD^{tree}").strip()
        merge = self._git("commit-tree", tree, "-p", self.base, "-p", head).strip()
        return GitCandidate(self.root, self.base, head, merge, branch)


def _pull(
    candidate: GitCandidate | None = None,
    *,
    current_master: str = "4" * 40,
    **overrides,
) -> dict:
    base = candidate.base if candidate is not None else current_master
    head = candidate.head if candidate is not None else "5" * 40
    value = {
        "number": 33,
        "state": "open",
        "merged_at": None,
        "draft": False,
        "user": {"login": "github-actions[bot]"},
        "head": {
            "ref": sync.BOT_BRANCH,
            "sha": head,
            "repo": {"full_name": sync.TARGET_REPOSITORY},
        },
        "base": {
            "ref": sync.TARGET_BRANCH,
            "sha": base,
            "repo": {"full_name": sync.TARGET_REPOSITORY},
        },
        "body": f"Summary\n\n{sync.PR_MARKER}\n",
        "merge_commit_sha": candidate.merge if candidate is not None else "6" * 40,
        "mergeable": True,
    }
    value.update(overrides)
    return value


class MetadataTests(unittest.TestCase):
    def assert_refused(self, pull: dict) -> None:
        with self.assertRaises(sync.SyncFailure):
            publish.validate_pull_metadata(pull, "4" * 40)

    def test_accepts_only_exact_bot_membership(self) -> None:
        candidate = publish.validate_pull_metadata(_pull(), "4" * 40)
        self.assertEqual(candidate.pr_number, 33)
        self.assertEqual(candidate.head_sha, "5" * 40)

    def test_wrong_actor_ref_marker_and_repository_are_refused(self) -> None:
        variants = []
        pull = _pull()
        pull["user"]["login"] = "human"
        variants.append(pull)
        pull = _pull()
        pull["head"]["ref"] = "feature/human"
        variants.append(pull)
        pull = _pull()
        pull["base"]["ref"] = "develop"
        variants.append(pull)
        pull = _pull()
        pull["head"]["repo"]["full_name"] = "foreign/repo"
        variants.append(pull)
        pull = _pull()
        pull["base"]["repo"]["full_name"] = "foreign/repo"
        variants.append(pull)
        pull = _pull()
        pull["body"] = "missing marker"
        variants.append(pull)
        pull = _pull()
        pull["draft"] = True
        variants.append(pull)
        pull = _pull()
        pull["head"]["sha"] = "not-a-sha"
        variants.append(pull)
        pull = _pull()
        pull["base"]["sha"] = "g" * 40
        variants.append(pull)
        for variant in variants:
            with self.subTest(variant=variant):
                self.assert_refused(variant)

    def test_stale_reported_creation_base_is_pinned_to_current_master(self) -> None:
        pull = _pull()
        pull["base"]["sha"] = "2" * 40
        candidate = publish.validate_pull_metadata(pull, "4" * 40)
        self.assertEqual(candidate.base_sha, "4" * 40)


class CandidateValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="publish-tests-")
        self.fixture = GitFixture(pathlib.Path(self.temporary.name))
        self.runner = sync.CappedRunner()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def validate(self, candidate: GitCandidate):
        return publish.validate_candidate_diff(
            self.runner,
            candidate.root,
            base_sha=candidate.base,
            head_sha=candidate.head,
            merge_sha=candidate.merge,
        )

    def test_feature_and_no_impact_candidates_are_safe(self) -> None:
        feature = self.fixture.candidate(update=True)
        candidate_doc = feature.root / "docs" / "existing.md"
        unrelated = feature.root / "unrelated.txt"
        unrelated.write_text("leave me alone\n", encoding="utf-8")
        self.assertEqual(
            candidate_doc.read_text(encoding="utf-8"),
            "---\ntitle: Existing\n---\n\nNew content.\n",
        )
        self.assertEqual(self.validate(feature).merge_sha, feature.merge)
        self.assertEqual(
            candidate_doc.read_text(encoding="utf-8"),
            "---\ntitle: Existing\n---\n\nNew content.\n",
        )
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "leave me alone\n")

        no_impact_fixture = GitFixture(
            pathlib.Path(self.temporary.name) / "no-impact"
        )
        no_impact = no_impact_fixture.candidate(update=False)
        publisher = publish.validate_candidate_diff(
            self.runner,
            no_impact.root,
            base_sha=no_impact.base,
            head_sha=no_impact.head,
            merge_sha=no_impact.merge,
        )
        self.assertEqual(publisher.head_sha, no_impact.head)

    def test_older_bot_base_resumes_when_state_is_unchanged(self) -> None:
        fixture = GitFixture(pathlib.Path(self.temporary.name) / "older-base")
        candidate = fixture.candidate(update=False)
        fixture._git("switch", "master")
        (fixture.root / "docs" / "unrelated.md").write_text(
            "---\ntitle: Unrelated\n---\n\nHuman master change.\n", encoding="utf-8"
        )
        fixture._git("add", "-A")
        fixture._git("commit", "-m", "unrelated master change")
        current_base = fixture._git("rev-parse", "HEAD").strip()
        fixture._git("merge", "--no-ff", candidate.branch, "-m", "merge preview")
        merge = fixture._git("rev-parse", "HEAD").strip()
        pull = _pull(
            candidate,
            current_master=current_base,
            merge_commit_sha=merge,
        )
        with mock.patch.object(
            publish, "_fetch_candidate", return_value=merge
        ) as fetch:
            validated = publish.validate_fetched_candidate(
                runner=self.runner,
                root=fixture.root,
                token="test-token",
                number=33,
                current_master=current_base,
                pull=pull,
            )
        fetch.assert_called_once_with(
            self.runner,
            fixture.root,
            "test-token",
            33,
            current_base,
            candidate.head,
        )
        self.assertEqual(pull["base"]["sha"], candidate.base)
        self.assertEqual(validated.base_sha, current_base)
        self.assertEqual(validated.head_sha, candidate.head)

    def test_delete_symlink_config_human_file_are_refused(self) -> None:
        mutations = {
            "delete": lambda root: (root / "docs" / "existing.md").unlink(),
            "symlink": lambda root: (
                root / "docs" / "link.md"
            ).symlink_to("existing.md"),
            "config": lambda root: (root / "package.json").write_text(
                "{}\n", encoding="utf-8"
            ),
            "human-file": lambda root: (root / "scripts").mkdir(),
        }
        for index, (name, mutate) in enumerate(mutations.items()):
            with self.subTest(name=name):
                fixture = GitFixture(
                    pathlib.Path(self.temporary.name) / f"mutation-{index}"
                )
                if name == "human-file":
                    (fixture.root / "scripts").mkdir()

                    def write_human_file(root: pathlib.Path) -> None:
                        (root / "scripts" / "human.py").write_text(
                            "print('human')\n", encoding="utf-8"
                        )

                    mutate = write_human_file
                candidate = fixture.candidate(mutate=mutate)
                with self.assertRaises(sync.SyncFailure):
                    publish.validate_candidate_diff(
                        self.runner,
                        candidate.root,
                        base_sha=candidate.base,
                        head_sha=candidate.head,
                        merge_sha=candidate.merge,
                    )

    def test_exact_history_and_state_transition_are_required(self) -> None:
        def bad_history(root: pathlib.Path) -> None:
            path = root / ".ai-docs" / "history" / f"{NEW_CURSOR}.json"
            path.write_text("{}\n", encoding="utf-8")

        candidate = self.fixture.candidate(mutate=bad_history)
        with self.assertRaises(sync.SyncFailure):
            self.validate(candidate)

        fixture = GitFixture(pathlib.Path(self.temporary.name) / "prior-cursor")

        def bad_state(root: pathlib.Path) -> None:
            path = root / ".ai-docs" / "state.json"
            state = json.loads(path.read_text(encoding="utf-8"))
            state["last_sync"]["range"]["base_exclusive"] = "c" * 40
            path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

        candidate = fixture.candidate(mutate=bad_state)
        with self.assertRaises(sync.SyncFailure):
            publish.validate_candidate_diff(
                self.runner,
                candidate.root,
                base_sha=candidate.base,
                head_sha=candidate.head,
                merge_sha=candidate.merge,
            )

    def test_former_history_is_immutable(self) -> None:
        fixture = GitFixture(pathlib.Path(self.temporary.name) / "history")

        def mutate_old_history(root: pathlib.Path) -> None:
            (root / ".ai-docs" / "history" / f"{OLD_HISTORY}.json").write_text(
                '{"old": false}\n', encoding="utf-8"
            )

        candidate = fixture.candidate(mutate=mutate_old_history)
        with self.assertRaises(sync.SyncFailure):
            publish.validate_candidate_diff(
                self.runner,
                candidate.root,
                base_sha=candidate.base,
                head_sha=candidate.head,
                merge_sha=candidate.merge,
            )

    def test_wrong_bot_identity_and_nonancestor_parent_are_refused(self) -> None:
        fixture = GitFixture(pathlib.Path(self.temporary.name) / "identity")
        candidate = fixture.candidate(
            bot_identity=("Fixture Human", "human@example.com")
        )
        with self.assertRaises(sync.SyncFailure):
            publish.validate_candidate_diff(
                self.runner,
                candidate.root,
                base_sha=candidate.base,
                head_sha=candidate.head,
                merge_sha=candidate.merge,
            )

    def test_extra_bot_commit_is_refused(self) -> None:
        fixture = GitFixture(pathlib.Path(self.temporary.name) / "extra-commit")
        candidate = fixture.candidate()
        fixture._git("switch", "candidate-1")
        (fixture.root / "docs" / "existing.md").write_text(
            "---\ntitle: Existing\n---\n\nSecond bot content.\n", encoding="utf-8"
        )
        fixture._git("add", "-A")
        env = dict(
            os.environ,
            GIT_AUTHOR_NAME=sync.COMMIT_NAME,
            GIT_AUTHOR_EMAIL=sync.COMMIT_EMAIL,
            GIT_COMMITTER_NAME=sync.COMMIT_NAME,
            GIT_COMMITTER_EMAIL=sync.COMMIT_EMAIL,
        )
        fixture._git("commit", "-m", "second bot commit", env=env)
        head = fixture._git("rev-parse", "HEAD").strip()
        tree = fixture._git("rev-parse", "HEAD^{tree}").strip()
        merge = fixture._git(
            "commit-tree", tree, "-p", candidate.base, "-p", head
        ).strip()
        with self.assertRaises(sync.SyncFailure):
            publish.validate_candidate_diff(
                self.runner,
                fixture.root,
                base_sha=candidate.base,
                head_sha=head,
                merge_sha=merge,
            )


class FailureMarkerTests(unittest.TestCase):
    def marker_line(self, *, base: str = "4" * 40, head: str = "5" * 40) -> str:
        return publish._failure_marker_line(
            base_sha=base, head_sha=head, run_id=123456
        )

    def test_strict_marker_round_trip_and_at_most_one(self) -> None:
        line = self.marker_line()
        body = f"Summary\n\n{sync.PR_MARKER}\n\n{line}\n"
        marker = publish.parse_failure_marker(body)
        self.assertIsNotNone(marker)
        assert marker is not None
        self.assertEqual(marker.base_sha, "4" * 40)
        self.assertEqual(marker.head_sha, "5" * 40)
        self.assertEqual(marker.run_id, 123456)
        self.assertEqual(
            marker.run_url,
            "https://github.com/capoworks/capoworks-ecu-docs/actions/runs/123456",
        )
        with self.assertRaises(sync.SyncFailure):
            publish.parse_failure_marker(f"{line}\n{line}\n")

    def test_malformed_markers_fail_closed(self) -> None:
        line = self.marker_line()
        payload = json.loads(line.removeprefix(publish.FAILURE_MARKER_PREFIX).removesuffix(" -->"))
        variants = [
            f" {line}",
            f"{publish.FAILURE_MARKER_PREFIX}{{not-json}} -->",
            f'{publish.FAILURE_MARKER_PREFIX}{{"run_id":1,"run_id":1}} -->',
            f"{publish.FAILURE_MARKER_PREFIX}{json.dumps({**payload, 'extra': 'x'})} -->",
            f"{publish.FAILURE_MARKER_PREFIX}{json.dumps({**payload, 'run_url': 'https://example.com'})} -->",
            f"{publish.FAILURE_MARKER_PREFIX}{json.dumps({**payload, 'run_id': True})} -->",
            f"{publish.FAILURE_MARKER_PREFIX}{'x' * publish.FAILURE_MARKER_MAX_BYTES} -->",
        ]
        for variant in variants:
            with self.subTest(variant=variant[:80]):
                with self.assertRaises(sync.SyncFailure):
                    publish.parse_failure_marker(variant)

    def test_replacement_preserves_body_and_keeps_one_marker(self) -> None:
        original = self.marker_line(base="2" * 40, head="3" * 40)
        current = self.marker_line()
        body = f"Summary\n\n{sync.PR_MARKER}\n\n{original}\n"
        updated = publish._body_with_failure_marker(body, current)
        self.assertEqual(updated.count(publish.FAILURE_MARKER_SENTINEL), 1)
        self.assertIn("Summary", updated)
        self.assertIn(sync.PR_MARKER, updated)
        marker = publish.parse_failure_marker(updated)
        assert marker is not None
        self.assertEqual(marker.base_sha, "4" * 40)


class MarkFailedTests(unittest.TestCase):
    class FakeGitHub:
        token = "test-token"

        def __init__(self, pull: dict, *, current_master: str) -> None:
            self.pull_value = pull
            self.current_master = current_master
            self.updates: list[tuple[int, str]] = []

        def branch_sha(self, repository, branch):
            return self.current_master

        def pull(self, number):
            return copy.deepcopy(self.pull_value)

        def update_pull_body(self, number, body):
            self.updates.append((number, body))

    def test_marks_only_the_matching_candidate(self) -> None:
        github = self.FakeGitHub(_pull(current_master="4" * 40), current_master="4" * 40)
        with mock.patch.object(publish, "_summary") as summary:
            result = publish.mark_failed_phase(
                github=github,
                pr_number=33,
                base_sha="4" * 40,
                head_sha="5" * 40,
                run_id=987654,
            )
        self.assertEqual(result, 0)
        self.assertEqual(len(github.updates), 1)
        number, body = github.updates[0]
        self.assertEqual(number, 33)
        marker = publish.parse_failure_marker(body)
        assert marker is not None
        self.assertEqual(marker.base_sha, "4" * 40)
        self.assertEqual(marker.head_sha, "5" * 40)
        self.assertEqual(marker.run_id, 987654)
        self.assertIn(sync.PR_MARKER, body)
        summary.assert_called_once()

    def test_stale_base_or_head_is_skipped_without_a_write(self) -> None:
        cases = [
            (_pull(current_master="9" * 40), "4" * 40, "5" * 40),
            (_pull(current_master="4" * 40, head={"ref": sync.BOT_BRANCH, "sha": "8" * 40, "repo": {"full_name": sync.TARGET_REPOSITORY}}), "4" * 40, "5" * 40),
        ]
        for pull, selected_base, selected_head in cases:
            with self.subTest(base=pull["base"]["sha"], head=pull["head"]["sha"]):
                github = self.FakeGitHub(
                    pull, current_master=str(pull["base"]["sha"])
                )
                with mock.patch.object(publish, "_summary") as summary:
                    result = publish.mark_failed_phase(
                        github=github,
                        pr_number=33,
                        base_sha=selected_base,
                        head_sha=selected_head,
                        run_id=987654,
                    )
                self.assertEqual(result, 0)
                self.assertEqual(github.updates, [])
                self.assertIn("stale", summary.call_args.args[0][0].lower())

    def test_malformed_existing_marker_never_writes(self) -> None:
        pull = _pull(current_master="4" * 40)
        pull["body"] = (
            f"Summary\n\n{sync.PR_MARKER}\n\n"
            f"{publish.FAILURE_MARKER_PREFIX}not-json -->\n"
        )
        github = self.FakeGitHub(pull, current_master="4" * 40)
        with self.assertRaises(sync.SyncFailure):
            publish.mark_failed_phase(
                github=github,
                pr_number=33,
                base_sha="4" * 40,
                head_sha="5" * 40,
                run_id=987654,
            )
        self.assertEqual(github.updates, [])


class FailureSelectionTests(unittest.TestCase):
    class FakeGitHub:
        token = "test-token"

        def __init__(self, pull: dict, *, current_master: str = "4" * 40) -> None:
            self.pull_value = pull
            self.current_master = current_master

        def branch_sha(self, repository, branch):
            return self.current_master

        def open_automation_pulls(self):
            return [copy.deepcopy(self.pull_value)]

        def pull(self, number):
            return copy.deepcopy(self.pull_value)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="publish-select-")
        self.work_dir = pathlib.Path(self.temporary.name)
        (self.work_dir / "status.json").write_text(
            '{"status":"ready"}\n', encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_matching_failure_marker_stops_before_git_or_build_retry(self) -> None:
        pull = _pull(current_master="4" * 40)
        marker = publish._failure_marker_line(
            base_sha="4" * 40, head_sha="5" * 40, run_id=123456
        )
        pull["body"] += f"\n{marker}\n"
        github = self.FakeGitHub(pull)
        with mock.patch.object(publish, "validate_fetched_candidate") as validate:
            with mock.patch.object(publish, "_summary") as summary:
                with self.assertRaises(sync.ActionRequired) as caught:
                    publish.select_phase(
                        root=self.work_dir,
                        work_dir=self.work_dir,
                        github=github,
                    )
        validate.assert_not_called()
        summary.assert_called_once()
        message = str(caught.exception)
        self.assertIn("Action Required", message)
        self.assertIn("remove the publication failure marker", message)
        self.assertIn("new base or head", message)
        self.assertIn("actions/runs/123456", message)

    def test_old_base_or_head_marker_does_not_block_revalidation(self) -> None:
        markers = [
            publish._failure_marker_line(
                base_sha="2" * 40, head_sha="5" * 40, run_id=123456
            ),
            publish._failure_marker_line(
                base_sha="4" * 40, head_sha="3" * 40, run_id=123456
            ),
        ]
        for marker in markers:
            with self.subTest(marker=marker):
                pull = _pull(current_master="4" * 40)
                pull["body"] += f"\n{marker}\n"
                github = self.FakeGitHub(pull)
                expected = publish.Candidate(33, "4" * 40, "5" * 40, "6" * 40)
                with mock.patch.object(
                    publish, "validate_fetched_candidate", return_value=expected
                ) as validate:
                    with mock.patch.object(publish, "_select_outputs"):
                        with mock.patch.object(publish, "_summary"):
                            selected = publish.select_phase(
                                root=self.work_dir,
                                work_dir=self.work_dir,
                                github=github,
                            )
                validate.assert_called_once()
                self.assertEqual(selected, expected)

    def test_malformed_marker_fails_closed_before_git(self) -> None:
        pull = _pull(current_master="4" * 40)
        pull["body"] += (
            f"\n{publish.FAILURE_MARKER_PREFIX}not-json -->\n"
        )
        github = self.FakeGitHub(pull)
        with mock.patch.object(publish, "validate_fetched_candidate") as validate:
            with self.assertRaises(sync.SyncFailure):
                publish.select_phase(
                    root=self.work_dir,
                    work_dir=self.work_dir,
                    github=github,
                )
        validate.assert_not_called()


class RecoverTests(unittest.TestCase):
    class FakeGitHub:
        def __init__(self, runs: list[dict], *, current_master: str = "7" * 40) -> None:
            self.runs = runs
            self.current_master = current_master
            self.dispatch_calls: list[str] = []

        def branch_sha(self, repository, branch):
            return self.current_master

        def workflow_runs(self, workflow):
            return copy.deepcopy(self.runs)

        def dispatch(self, workflow):
            self.dispatch_calls.append(workflow)

    def _run(self, *, run_id=123456, status="completed", conclusion="failure"):
        return {
            "id": run_id,
            "head_sha": "7" * 40,
            "event": "workflow_dispatch",
            "status": status,
            "conclusion": conclusion,
        }

    def test_first_missing_deploy_dispatches_once(self) -> None:
        github = self.FakeGitHub([])
        with mock.patch.object(publish, "_summary"):
            result = publish.recover_phase(root=pathlib.Path("."), github=github)
        self.assertEqual(result, 0)
        self.assertEqual(github.dispatch_calls, ["deploy.yml"])

    def test_terminal_failure_is_suppressed_with_actionable_summary(self) -> None:
        github = self.FakeGitHub([self._run()])
        with self.assertLogs(publish.LOG, level="WARNING") as logs:
            with mock.patch.object(publish, "_summary") as summary:
                result = publish.recover_phase(root=pathlib.Path("."), github=github)
        self.assertEqual(result, 0)
        self.assertEqual(github.dispatch_calls, [])
        self.assertTrue(any("ACTION REQUIRED" in line for line in logs.output))
        lines = summary.call_args.args[0]
        rendered = "\n".join(lines)
        self.assertIn("actions/runs/123456", rendered)
        self.assertIn("gh workflow run deploy.yml", rendered)
        self.assertIn("generation continues", rendered)

    def test_active_or_successful_deploy_is_left_untouched(self) -> None:
        cases = [
            ("queued", None),
            ("in_progress", None),
            ("requested", None),
            ("waiting", None),
            ("pending", None),
            ("completed", "success"),
        ]
        for status, conclusion in cases:
            with self.subTest(status=status, conclusion=conclusion):
                github = self.FakeGitHub(
                    [self._run(status=status, conclusion=conclusion)]
                )
                with mock.patch.object(publish, "_summary") as summary:
                    result = publish.recover_phase(
                        root=pathlib.Path("."), github=github
                    )
                self.assertEqual(result, 0)
                self.assertEqual(github.dispatch_calls, [])
                summary.assert_not_called()


class MergeGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.expected = publish.Candidate(33, "4" * 40, "5" * 40, "6" * 40)
        self.merged = "7" * 40
        self.pull = _pull()

    def _github(self, *, dispatch_error: str | None = None):
        class FakeGitHub:
            token = "test-token"
            merge_calls = []
            dispatch_calls = []

            def __init__(self) -> None:
                self.branch_values = iter(["4" * 40, self_outer.merged])

            def branch_sha(self, repository, branch):
                return next(self.branch_values)

            def pull(self, number):
                return copy.deepcopy(self_outer.pull)

            def update_pull_body(self, number, body):
                return None

            def merge_pull(self, number, head_sha):
                self.merge_calls.append((number, head_sha))
                return {"merged": True, "sha": self_outer.merged}

            def dispatch(self, workflow):
                self.dispatch_calls.append(workflow)
                if workflow == dispatch_error:
                    raise sync.ApiFailure(f"{workflow} unavailable")

        self_outer = self
        return FakeGitHub()

    def _patch_success(self):
        return mock.patch.multiple(
            publish,
            validate_fetched_candidate=mock.Mock(return_value=self.expected),
            _fetch_master=mock.Mock(return_value=self.merged),
            _parents=mock.Mock(return_value=(self.expected.base_sha, self.expected.head_sha)),
            _tree_sha=mock.Mock(
                side_effect=("a" * 40, "a" * 40)
            ),
        )

    def test_validation_failure_never_invokes_merge(self) -> None:
        github = self._github()
        with mock.patch.object(
            publish, "validate_fetched_candidate", side_effect=sync.ValidationFailure("bad")
        ):
            with self.assertRaises(sync.SyncFailure):
                publish.merge_phase(root=pathlib.Path("."), github=github, expected=self.expected)
        self.assertEqual(github.merge_calls, [])

    def test_changed_head_is_refused_before_merge(self) -> None:
        github = self._github()
        self.pull["head"]["sha"] = "8" * 40
        with self.assertRaises(sync.SyncFailure):
            publish.merge_phase(root=pathlib.Path("."), github=github, expected=self.expected)
        self.assertEqual(github.merge_calls, [])

    def test_changed_base_is_refused_before_merge(self) -> None:
        github = self._github()
        github.branch_values = iter(["9" * 40])
        with self.assertRaises(sync.SyncFailure):
            publish.merge_phase(root=pathlib.Path("."), github=github, expected=self.expected)
        self.assertEqual(github.merge_calls, [])

    def test_active_failure_marker_is_refused_before_merge(self) -> None:
        github = self._github()
        marker = publish._failure_marker_line(
            base_sha=self.expected.base_sha,
            head_sha=self.expected.head_sha,
            run_id=123456,
        )
        self.pull["body"] += f"\n{marker}\n"
        with self.assertRaises(sync.SyncFailure):
            publish.merge_phase(
                root=pathlib.Path("."), github=github, expected=self.expected
            )
        self.assertEqual(github.merge_calls, [])

    def test_rest_merge_failure_is_surfaced(self) -> None:
        github = self._github()
        github.merge_pull = mock.Mock(side_effect=sync.ApiFailure("branch protection"))
        with self._patch_success():
            with self.assertRaises(sync.ApiFailure):
                publish.merge_phase(root=pathlib.Path("."), github=github, expected=self.expected)
        github.merge_pull.assert_called_once()

    def test_dispatch_failures_are_independent_and_recoverable(self) -> None:
        github = self._github(dispatch_error="ai-docs-sync.yml")
        with self._patch_success():
            with self.assertRaises(publish.DispatchFailure) as caught:
                publish.merge_phase(root=pathlib.Path("."), github=github, expected=self.expected)
        self.assertEqual(
            github.dispatch_calls, ["deploy.yml", "ai-docs-sync.yml"]
        )
        self.assertEqual(caught.exception.merged_sha, self.merged)
        self.assertIn("ai-docs-sync.yml", str(caught.exception))

    def test_wrong_merged_tree_prevents_all_dispatch(self) -> None:
        github = self._github()
        with mock.patch.multiple(
            publish,
            validate_fetched_candidate=mock.Mock(return_value=self.expected),
            _fetch_master=mock.Mock(return_value=self.merged),
            _parents=mock.Mock(
                return_value=(self.expected.base_sha, self.expected.head_sha)
            ),
            _tree_sha=mock.Mock(side_effect=("a" * 40, "b" * 40)),
        ):
            with self.assertRaises(sync.ApiFailure):
                publish.merge_phase(
                    root=pathlib.Path("."),
                    github=github,
                    expected=self.expected,
                )
        self.assertEqual(github.dispatch_calls, [])


class PublicationWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        text = SYNC_WORKFLOW.read_text(encoding="utf-8")
        self.failure_job = text.split(
            "\n  mark-publication-failed:", 1
        )[1].split("\n  merge-publication:", 1)[0]

    def test_failure_job_only_marks_failed_selected_candidate(self) -> None:
        job = self.failure_job
        self.assertIn("needs: [sync, validate-publication]", job)
        self.assertIn("always()", job)
        self.assertIn("needs.sync.outputs.publish == 'true'", job)
        self.assertIn(
            "needs.validate-publication.result == 'failure'", job
        )
        self.assertIn("ref: ${{ needs.sync.outputs.base_sha }}", job)
        self.assertIn("PR_NUMBER: ${{ needs.sync.outputs.pr_number }}", job)
        self.assertIn("BASE_SHA: ${{ needs.sync.outputs.base_sha }}", job)
        self.assertIn("HEAD_SHA: ${{ needs.sync.outputs.head_sha }}", job)
        self.assertIn("RUN_ID: ${{ github.run_id }}", job)
        self.assertIn("mark-failed", job)

    def test_failure_job_has_no_model_or_full_build_context(self) -> None:
        job = self.failure_job
        self.assertRegex(job, r"(?m)^\s+contents: read$")
        self.assertRegex(job, r"(?m)^\s+pull-requests: write$")
        self.assertNotIn("DEEPSEEK", job)
        self.assertNotIn("npm ci", job)
        self.assertNotIn("npm run", job)


class DeployWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        text = DEPLOY_WORKFLOW.read_text(encoding="utf-8")
        self.build = text.split("\n  build:", 1)[1].split("\n  deploy:", 1)[0]
        self.deploy = text.split("\n  deploy:", 1)[1]

    def test_read_only_build_runs_lint_and_stdlib_tests_before_build(self) -> None:
        install = self.build.index("run: npm ci")
        lint = self.build.index("run: npm run lint")
        tests = self.build.index("python3 -m unittest discover")
        build = self.build.index("run: npm run build")
        self.assertLess(install, lint)
        self.assertLess(lint, tests)
        self.assertLess(tests, build)
        self.assertIn("--pattern 'test_ai_docs*.py'", self.build)
        self.assertRegex(self.build, r"permissions:\s*\n\s+contents: read")
        self.assertNotIn("DEEPSEEK", self.build)
        self.assertNotIn("GITHUB_TOKEN", self.build)

    def test_write_deploy_job_never_executes_generated_docs(self) -> None:
        self.assertRegex(self.deploy, r"pages: write")
        self.assertRegex(self.deploy, r"id-token: write")
        self.assertIn("actions/deploy-pages@v4", self.deploy)
        self.assertNotRegex(self.deploy, r"(?m)^\s+run:")
        self.assertNotIn("npm ", self.deploy)
        self.assertNotIn("python", self.deploy)


if __name__ == "__main__":
    unittest.main()
