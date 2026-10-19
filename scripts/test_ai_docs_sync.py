#!/usr/bin/env python3
"""Unit tests for scripts/ai-docs-sync.py using only the standard library."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).with_name("ai-docs-sync.py")
SPEC = importlib.util.spec_from_file_location("ai_docs_sync_under_test", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load ai-docs-sync.py")
sync = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = sync
SPEC.loader.exec_module(sync)

SHA_ONE = "1" * 40
SHA_TWO = "2" * 40
SHA_THREE = "3" * 40


def decision(sha: str, value: str = "update") -> dict[str, object]:
    return {
        "commit": sha,
        "decision": value,
        "rationale": "The changed source has a documented user-facing effect.",
        "evidence": ["src/example.c changes the default behavior"],
    }


def payload(
    files: list[dict[str, str]],
    *,
    sha: str = SHA_ONE,
    decision_value: str = "update",
) -> dict[str, object]:
    return {
        "summary": "Synchronize firmware behavior.",
        "decisions": [decision(sha, decision_value)],
        "files": files,
    }


def recent_entry(
    sha: str,
    batch: str,
    *,
    parents: tuple[str, ...] = (),
    subject: str = "Firmware change",
    authored_at: str = "2026-10-18T10:00:00+00:00",
    comment: str = "Describes a firmware change.",
    decision_value: str = "update",
) -> dict[str, object]:
    return {
        "commit": sha,
        "subject": subject,
        "authored_at": authored_at,
        "parents": list(parents),
        "comment": comment,
        "decision": decision_value,
        "model": "deepseek-flash",
        "analyzed_at": "2026-10-20T10:00:00+00:00",
        "integration_batch_commit": batch,
    }


def recent_document(entries: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "source_repository": sync.SOURCE_REPOSITORY,
        "source_branch": sync.SOURCE_BRANCH,
        "latest_analyzed_commit": entries[0]["commit"],
        "latest_analyzed_at": "2026-10-20T10:00:00+00:00",
        "entries": entries,
    }


def prepared_context(commits: list[dict[str, object]]) -> dict[str, object]:
    return {
        "range": {
            "base_exclusive": "a" * 40,
            "head_inclusive": commits[-1]["sha"],
            "commit_count": len(commits),
        },
        "commits": commits,
    }


def prepared_commit(
    sha: str,
    *,
    parents: tuple[str, ...] = ("a" * 40,),
    subject: str = "Firmware change",
    authored_at: str = "2026-10-18T10:00:00+00:00",
) -> dict[str, object]:
    return {
        "sha": sha,
        "parents": list(parents),
        "author": "Sync Test",
        "authored_at": authored_at,
        "subject": subject,
        "changed_paths": ["firmware/example.cpp"],
        "full_diff": "Example diff",
    }


def recent_result(
    decisions: list[tuple[str, str]],
    *,
    comments: dict[str, str] | None = None,
) -> object:
    return sync.SyncResult(
        summary="Reader-facing integration summary.",
        decisions=tuple(
            sync.SyncDecision(
                commit=sha,
                decision=value,
                rationale=(comments or {}).get(
                    sha, "The integration changes documented firmware behavior."
                ),
                evidence=(f"firmware/{sha[:8]}.cpp is the audit evidence",),
            )
            for sha, value in decisions
        ),
        files=(),
    )


class TempDocs(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temporary.name)
        self.docs = self.root / "docs"
        self.docs.mkdir()
        (self.root / ".ai-docs").mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def limits(self) -> object:
        return sync.Limits()


class PathMarkdownAndFrontmatterTests(TempDocs):
    def test_existing_frontmatter_is_preserved_byte_for_byte(self) -> None:
        existing = (
            "---\r\n"
            "title: Existing\r\n"
            "sidebar_position: 7\r\n"
            "---\r\n"
            "# Existing\r\n"
        )
        (self.docs / "Existing.md").write_text(existing, encoding="utf-8", newline="")
        generated = existing + "\nNew safe paragraph.\n"
        result = sync.validate_sync_result(
            payload([{"path": "docs/Existing.md", "content": generated}]),
            [SHA_ONE],
            self.docs,
            self.limits,
        )
        self.assertEqual(result.files[0].content, generated)

    def test_existing_frontmatter_change_is_rejected(self) -> None:
        existing = "---\ntitle: Existing\n---\n# Existing\n"
        (self.docs / "Existing.md").write_text(existing, encoding="utf-8", newline="")
        changed = existing.replace("Existing", "Changed", 1)
        with self.assertRaisesRegex(sync.ValidationFailure, "frontmatter"):
            sync.validate_sync_result(
                payload([{"path": "docs/Existing.md", "content": changed}]),
                [SHA_ONE],
                self.docs,
                self.limits,
            )

    def test_update_that_reproduces_an_existing_file_is_rejected(self) -> None:
        existing = "# Existing\n"
        (self.docs / "Existing.md").write_text(existing, encoding="utf-8", newline="")
        with self.assertRaisesRegex(sync.ValidationFailure, "unchanged document"):
            sync.validate_sync_result(
                payload([{"path": "docs/Existing.md", "content": existing}]),
                [SHA_ONE],
                self.docs,
                self.limits,
            )

    def test_new_frontmatter_is_allowlisted_and_scalar_only(self) -> None:
        safe = (
            "---\n"
            'title: "Safe title"\n'
            "sidebar_position: 4\n"
            "tags: [firmware, tuning]\n"
            "---\n"
            "# Safe\n"
        )
        result = sync.validate_sync_result(
            payload([{"path": "docs/New.md", "content": safe}]),
            [SHA_ONE],
            self.docs,
            self.limits,
        )
        self.assertEqual(result.files[0].path, "docs/New.md")
        unsafe = safe.replace('title: "Safe title"', "owner: hidden")
        with self.assertRaisesRegex(sync.ValidationFailure, "frontmatter key"):
            sync.validate_sync_result(
                payload([{"path": "docs/Unsafe.md", "content": unsafe}]),
                [SHA_ONE],
                self.docs,
                self.limits,
            )

    def test_mdx_executable_syntax_is_rejected(self) -> None:
        unsafe_bodies = [
            "import Widget from './Widget'\n",
            "export const value = 1\n",
            "<Widget value=\"x\" />\n",
            "<>\n",
            "{process.env.SECRET}\n",
            "[click](javascript:alert(1))\n",
            "<img src=x onerror=alert(1)>\n",
        ]
        for body in unsafe_bodies:
            with self.subTest(body=body):
                with self.assertRaises(sync.ValidationFailure):
                    sync.validate_sync_result(
                        payload([{"path": "docs/Unsafe.md", "content": body}]),
                        [SHA_ONE],
                        self.docs,
                        self.limits,
                    )

    def test_safe_markdown_and_fenced_code_are_allowed(self) -> None:
        content = (
            "# Safe title\n\n"
            "[Public link](https://example.com/path)\n\n"
            "```ts\n"
            "import Widget from './Widget'\n"
            "<Widget value={1 + 1} />\n"
            "```\n"
        )
        result = sync.validate_sync_result(
            payload([{"path": "docs/Safe.md", "content": content}]),
            [SHA_ONE],
            self.docs,
            self.limits,
        )
        self.assertEqual(len(result.files), 1)

    def test_invalid_and_noncanonical_paths_are_rejected(self) -> None:
        bad_paths = [
            "../docs/Bad.md",
            "/docs/Bad.md",
            r"docs\Bad.md",
            "docs/../Bad.md",
            "docs/Bad.mdx",
            "other/Bad.md",
            "docs//Bad.md",
        ]
        for path in bad_paths:
            with self.subTest(path=path):
                with self.assertRaises(sync.ValidationFailure):
                    sync.validate_sync_result(
                        payload([{"path": path, "content": "# Bad\n"}]),
                        [SHA_ONE],
                        self.docs,
                        self.limits,
                    )

    def test_case_insensitive_duplicates_and_existing_collisions_are_rejected(self) -> None:
        duplicate_files = [
            {"path": "docs/New.md", "content": "# New\n"},
            {"path": "docs/new.md", "content": "# New\n"},
        ]
        with self.assertRaisesRegex(sync.ValidationFailure, "case-insensitive"):
            sync.validate_sync_result(
                payload(duplicate_files), [SHA_ONE], self.docs, self.limits
            )

        (self.docs / "Existing.md").write_text("# Existing\n", encoding="utf-8")
        with self.assertRaisesRegex(sync.ValidationFailure, "collides by case"):
            sync.validate_sync_result(
                payload([{"path": "docs/existing.md", "content": "# Existing\n"}]),
                [SHA_ONE],
                self.docs,
                self.limits,
            )

        (self.docs / "Protected.mdx").write_text(
            "import Component from './Component';\n\n<Component />\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(sync.ValidationFailure, "Markdown/MDX sibling"):
            sync.validate_sync_result(
                payload([{"path": "docs/Protected.md", "content": "# Protected\n"}]),
                [SHA_ONE],
                self.docs,
                self.limits,
            )

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_symlink_targets_and_parents_are_rejected(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "leak.md").write_text("outside\n", encoding="utf-8")
        os.symlink(outside / "leak.md", self.docs / "Linked.md")
        with self.assertRaisesRegex(sync.ValidationFailure, "symlink"):
            sync.validate_sync_result(
                payload([{"path": "docs/Linked.md", "content": "# Linked\n"}]),
                [SHA_ONE],
                self.docs,
                self.limits,
            )
        os.symlink(outside, self.docs / "linked-dir")
        with self.assertRaisesRegex(sync.ValidationFailure, "symbolic|symlink"):
            sync.validate_sync_result(
                payload([{"path": "docs/linked-dir/New.md", "content": "# New\n"}]),
                [SHA_ONE],
                self.docs,
                self.limits,
            )

    def test_output_file_count_and_bytes_are_bounded(self) -> None:
        limits = sync.Limits(max_output_files=1, max_output_file_bytes=10)
        with self.assertRaisesRegex(sync.ValidationFailure, "too large"):
            sync.validate_sync_result(
                payload([{"path": "docs/Large.md", "content": "# 123456789\n"}]),
                [SHA_ONE],
                self.docs,
                limits,
            )
        limits = sync.Limits(max_output_files=1, max_output_file_bytes=1_000)
        with self.assertRaisesRegex(sync.ValidationFailure, "maximum is 1"):
            sync.validate_sync_result(
                payload(
                    [
                        {"path": "docs/One.md", "content": "# One\n"},
                        {"path": "docs/Two.md", "content": "# Two\n"},
                    ]
                ),
                [SHA_ONE],
                self.docs,
                limits,
            )


class CoverageAndAtomicityTests(TempDocs):
    def test_every_commit_must_be_covered_in_order(self) -> None:
        good = {
            "summary": "Two decisions.",
            "decisions": [decision(SHA_ONE), decision(SHA_TWO)],
            "files": [{"path": "docs/One.md", "content": "# One\n"}],
        }
        result = sync.validate_sync_result(
            good, [SHA_ONE, SHA_TWO], self.docs, self.limits
        )
        self.assertEqual([item.commit for item in result.decisions], [SHA_ONE, SHA_TWO])
        bad = copy.deepcopy(good)
        bad["decisions"].reverse()
        with self.assertRaisesRegex(sync.ValidationFailure, "source order"):
            sync.validate_sync_result(
                bad, [SHA_ONE, SHA_TWO], self.docs, self.limits
            )
        missing = copy.deepcopy(good)
        missing["decisions"].pop()
        with self.assertRaisesRegex(sync.ValidationFailure, "decision count"):
            sync.validate_sync_result(
                missing, [SHA_ONE, SHA_TWO], self.docs, self.limits
            )

    def test_no_impact_requires_empty_files_and_update_requires_files(self) -> None:
        no_impact = payload([], decision_value="no-impact")
        result = sync.validate_sync_result(
            no_impact, [SHA_ONE], self.docs, self.limits
        )
        self.assertFalse(result.files)
        inconsistent = payload(
            [{"path": "docs/New.md", "content": "# New\n"}],
            decision_value="no-impact",
        )
        with self.assertRaisesRegex(sync.ValidationFailure, "exactly when"):
            sync.validate_sync_result(
                inconsistent, [SHA_ONE], self.docs, self.limits
            )

    def test_invalid_output_leaves_all_existing_files_untouched(self) -> None:
        existing = self.docs / "Existing.md"
        existing.write_text("# Original\n", encoding="utf-8", newline="")
        invalid = payload(
            [
                {"path": "docs/Existing.md", "content": "# Changed\n"},
                {"path": "../escape.md", "content": "# Escape\n"},
            ]
        )
        before = existing.read_bytes()
        with self.assertRaises(sync.ValidationFailure):
            sync.validate_sync_result(invalid, [SHA_ONE], self.docs, self.limits)
        self.assertEqual(existing.read_bytes(), before)
        self.assertFalse((self.root / "escape.md").exists())

    def test_atomic_writer_rolls_back_after_replace_failure(self) -> None:
        first = self.docs / "One.md"
        second = self.docs / "Two.md"
        first.write_text("old one\n", encoding="utf-8")
        second.write_text("old two\n", encoding="utf-8")
        original_replace = os.replace
        replace_count = 0

        def failing_replace(source: object, destination: object) -> None:
            nonlocal replace_count
            replace_count += 1
            if replace_count == 2:
                raise OSError("simulated replace failure")
            original_replace(source, destination)

        with mock.patch.object(sync.os, "replace", side_effect=failing_replace):
            with self.assertRaisesRegex(OSError, "simulated"):
                sync.atomic_write_set(
                    self.root,
                    {
                        "docs/One.md": "new one\n",
                        "docs/Two.md": "new two\n",
                    },
                )
        self.assertEqual(first.read_text(encoding="utf-8"), "old one\n")
        self.assertEqual(second.read_text(encoding="utf-8"), "old two\n")


class FakeTransport:
    def __init__(self, responses: list[tuple[int, dict[str, str], bytes]]):
        self.responses = list(responses)
        self.requests: list[dict[str, object]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        body: bytes | None,
        timeout: float,
        max_response_bytes: int,
    ) -> tuple[int, dict[str, str], bytes]:
        self.requests.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),
                "body": body,
                "timeout": timeout,
                "max_response_bytes": max_response_bytes,
            }
        )
        return self.responses.pop(0)


def api_json(value: object, status: int = 200) -> tuple[int, dict[str, str], bytes]:
    return status, {"Content-Type": "application/json"}, json.dumps(value).encode("utf-8")


class LifecycleTests(unittest.TestCase):
    def client(self, responses: list[tuple[int, dict[str, str], bytes]]) -> object:
        return sync.GitHubClient(FakeTransport(responses), "test-token")

    def test_open_bot_pr_is_pending(self) -> None:
        client = self.client(
            [
                api_json({"commit": {"sha": SHA_ONE}}),
                api_json([{"number": 9}]),
            ]
        )
        lifecycle = client.inspect_lifecycle(sync.TARGET_REPOSITORY)
        self.assertEqual(lifecycle.action, "pending")
        self.assertEqual(lifecycle.latest_pr, 9)

    def test_closed_unmerged_bot_pr_stops_actionably(self) -> None:
        client = self.client(
            [
                api_json({"commit": {"sha": SHA_ONE}}),
                api_json([]),
                api_json([{"number": 9, "merged_at": None}]),
            ]
        )
        with self.assertRaisesRegex(sync.ActionRequired, "closed without merging"):
            client.inspect_lifecycle(sync.TARGET_REPOSITORY)

    def test_unknown_branch_without_pr_stops(self) -> None:
        client = self.client(
            [
                api_json({"commit": {"sha": SHA_ONE}}),
                api_json([]),
                api_json([]),
            ]
        )
        with self.assertRaisesRegex(sync.ActionRequired, "without a pull request"):
            client.inspect_lifecycle(sync.TARGET_REPOSITORY)

    def test_missing_branch_rescans_from_master_cursor(self) -> None:
        client = self.client(
            [
                api_json({"message": "Not Found"}, status=404),
                api_json([]),
                api_json([]),
            ]
        )
        lifecycle = client.inspect_lifecycle(sync.TARGET_REPOSITORY)
        self.assertEqual(lifecycle.action, "proceed")
        self.assertIsNone(lifecycle.remote_sha)

    def test_merged_branch_at_pr_head_can_be_reused(self) -> None:
        client = self.client(
            [
                api_json({"commit": {"sha": SHA_TWO}}),
                api_json([]),
                api_json(
                    [
                        {
                            "number": 10,
                            "merged_at": "2026-10-18T00:00:00Z",
                            "head": {"sha": SHA_TWO},
                        }
                    ]
                ),
            ]
        )
        lifecycle = client.inspect_lifecycle(sync.TARGET_REPOSITORY)
        self.assertEqual(lifecycle.action, "proceed")
        self.assertEqual(lifecycle.remote_sha, SHA_TWO)

    def test_merged_pr_with_new_branch_commits_stops(self) -> None:
        client = self.client(
            [
                api_json({"commit": {"sha": SHA_THREE}}),
                api_json([]),
                api_json(
                    [
                        {
                            "number": 10,
                            "merged_at": "2026-10-18T00:00:00Z",
                            "head": {"sha": SHA_TWO},
                        }
                    ]
                ),
            ]
        )
        with self.assertRaisesRegex(sync.ActionRequired, "commits not represented"):
            client.inspect_lifecycle(sync.TARGET_REPOSITORY)


class FakeSource:
    def __init__(self, head: str, *, snapshot: object | None = None):
        self.head = head
        self.snapshot_value = snapshot
        self.snapshot_called = False
        self.integration_event: bool | None = None
        self.runner = sync.CappedRunner()

    def resolve_head(self) -> str:
        return self.head

    def snapshot(
        self, base: str, head: str, *, integration_event: bool = False
    ) -> object:
        self.snapshot_called = True
        self.integration_event = integration_event
        if self.snapshot_value is None:
            raise AssertionError("snapshot should not be called")
        if isinstance(self.snapshot_value, Exception):
            raise self.snapshot_value
        return self.snapshot_value


class FakeGithub:
    def __init__(self, lifecycle: object | None = None):
        self.lifecycle = lifecycle
        self.called = False

    def inspect_lifecycle(self, repository: str) -> object:
        self.called = True
        if isinstance(self.lifecycle, Exception):
            raise self.lifecycle
        return self.lifecycle


class PrepareCursorAndFailureTests(TempDocs):
    def setUp(self) -> None:
        super().setUp()
        state = {
            "schema_version": 1,
            "source_repository": sync.SOURCE_REPOSITORY,
            "source_branch": sync.SOURCE_BRANCH,
            "target_repository": sync.TARGET_REPOSITORY,
            "target_branch": sync.TARGET_BRANCH,
            "cursor_commit": SHA_ONE,
            "initial_backfill": {
                "through_commit": SHA_TWO,
                "commit_count": 5,
                "completed": False,
            },
            "last_sync": None,
        }
        (self.root / sync.STATE_PATH).write_text(
            json.dumps(state, indent=2) + "\n", encoding="utf-8"
        )

    def test_same_cursor_skips_github_api_and_ai(self) -> None:
        source = FakeSource(SHA_ONE)
        github = FakeGithub(Exception("GitHub API must not be called"))
        result = sync.prepare_phase(
            root=self.root,
            work_dir=self.root / "work",
            github=github,
            source=source,
            limits=self.limits,
        )
        self.assertEqual(result, 0)
        self.assertFalse(github.called)
        self.assertFalse(source.snapshot_called)
        status = json.loads((self.root / "work/status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "no-change")

    def test_open_pr_skips_snapshot_without_writing_state(self) -> None:
        source = FakeSource(SHA_TWO)
        lifecycle = sync.Lifecycle(
            action="pending", remote_sha=SHA_THREE, reason="open bot PR"
        )
        github = FakeGithub(lifecycle)
        state_before = (self.root / sync.STATE_PATH).read_bytes()
        result = sync.prepare_phase(
            root=self.root,
            work_dir=self.root / "work",
            github=github,
            source=source,
            limits=self.limits,
        )
        self.assertEqual(result, 0)
        self.assertFalse(source.snapshot_called)
        self.assertEqual((self.root / sync.STATE_PATH).read_bytes(), state_before)

    def test_actionable_failure_does_not_advance_state_or_create_results(self) -> None:
        source = FakeSource(SHA_TWO)
        github = FakeGithub(
            sync.ActionRequired("closed bot PR requires inspection")
        )
        state_before = (self.root / sync.STATE_PATH).read_bytes()
        with self.assertRaises(sync.ActionRequired):
            sync.prepare_phase(
                root=self.root,
                work_dir=self.root / "work",
                github=github,
                source=source,
                limits=self.limits,
            )
        self.assertEqual((self.root / sync.STATE_PATH).read_bytes(), state_before)
        self.assertFalse((self.root / "work/prepared.json").exists())

    def test_no_impact_next_state_advances_cursor_with_audit(self) -> None:
        state = sync.load_state(self.root / sync.STATE_PATH)
        context = {
            "range": {
                "base_exclusive": SHA_ONE,
                "head_inclusive": SHA_TWO,
                "commit_count": 1,
            }
        }
        result = sync.SyncResult(
            summary="No user-facing impact.",
            decisions=(
                sync.SyncDecision(
                    commit=SHA_TWO,
                    decision="no-impact",
                    rationale="Internal-only change.",
                    evidence=("src/internal.c only renames a local variable",),
                ),
            ),
            files=(),
        )
        next_state = sync._next_state(
            state,
            context,
            result,
            model="deepseek-flash",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        )
        self.assertEqual(next_state["cursor_commit"], SHA_TWO)
        self.assertEqual(next_state["last_sync"]["outcome"], "no-impact")
        self.assertTrue(next_state["initial_backfill"]["completed"])
        self.assertEqual(next_state["last_sync"]["decisions"][0]["commit"], SHA_TWO)

    def test_completed_backfill_prepares_one_event_and_records_exact_prompt_size(
        self,
    ) -> None:
        state = json.loads((self.root / sync.STATE_PATH).read_text(encoding="utf-8"))
        state["initial_backfill"]["completed"] = True
        state["initial_backfill"]["through_commit"] = SHA_ONE
        state["last_sync"] = {
            "range": {
                "base_exclusive": "a" * 40,
                "head_inclusive": SHA_ONE,
                "commit_count": 5,
            },
            "model": "deepseek-flash",
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            "summary": "Initial.",
            "outcome": "no-impact",
            "decisions": [],
            "files_changed": [],
            "recorded_at": "2026-10-18T00:00:00+00:00",
        }
        (self.root / sync.STATE_PATH).write_text(
            json.dumps(state, indent=2) + "\n", encoding="utf-8"
        )
        docs_repo = RealGitRepository(self.root)
        docs_repo.commit("docs base", {"docs/Existing.md": "# Existing\n"})
        snapshot = sync.SourceSnapshot(
            base=SHA_ONE,
            head=SHA_TWO,
            observed_head=SHA_THREE,
            commits=(
                sync.SourceCommit(
                    sha=SHA_TWO,
                    parents=(SHA_ONE,),
                    author="Sync Test",
                    authored_at="2026-10-18T00:00:00+00:00",
                    subject="event",
                    changed_paths=("src/event.c",),
                    patch="Parents: " + SHA_ONE + "\n",
                ),
            ),
            current_files={},
            source_wiki_docs={},
            target_wiki_docs={},
        )
        source = FakeSource(SHA_THREE, snapshot=snapshot)
        github = FakeGithub(
            sync.Lifecycle(action="proceed", remote_sha=None, reason="ready")
        )
        sync.prepare_phase(
            root=self.root,
            work_dir=self.root / "work",
            github=github,
            source=source,
            limits=self.limits,
        )
        prepared = json.loads(
            (self.root / "work/prepared.json").read_text(encoding="utf-8")
        )
        status = json.loads(
            (self.root / "work/status.json").read_text(encoding="utf-8")
        )
        self.assertTrue(source.integration_event)
        self.assertEqual(prepared["range"]["head_inclusive"], SHA_TWO)
        self.assertEqual(prepared["observed_head"], SHA_THREE)
        self.assertEqual(status["prompt_bytes"], sync.serialized_message_bytes(prepared))

    def test_completed_backfill_exact_prompt_limit_requires_action(self) -> None:
        state = json.loads((self.root / sync.STATE_PATH).read_text(encoding="utf-8"))
        state["initial_backfill"]["completed"] = True
        state["initial_backfill"]["through_commit"] = SHA_ONE
        (self.root / sync.STATE_PATH).write_text(
            json.dumps(state, indent=2) + "\n", encoding="utf-8"
        )
        docs_repo = RealGitRepository(self.root)
        docs_repo.commit("docs base", {"docs/Existing.md": "# Existing\n"})
        snapshot = sync.SourceSnapshot(
            base=SHA_ONE,
            head=SHA_TWO,
            observed_head=SHA_THREE,
            commits=(
                sync.SourceCommit(
                    sha=SHA_TWO,
                    parents=(SHA_ONE,),
                    author="Sync Test",
                    authored_at="2026-10-18T00:00:00+00:00",
                    subject="event",
                    changed_paths=("src/event.c",),
                    patch="Parents: " + SHA_ONE + "\n",
                ),
            ),
            current_files={},
            source_wiki_docs={},
            target_wiki_docs={},
        )
        lifecycle = sync.Lifecycle(
            action="proceed", remote_sha=None, reason="ready"
        )
        target_head = docs_repo.git("rev-parse", "HEAD").stdout.strip()
        expected_context = sync._context_payload(
            state, snapshot, lifecycle, target_head
        )
        prompt_bytes = sync.serialized_message_bytes(expected_context)
        work_dir = self.root / "prompt-work"
        state_before = (self.root / sync.STATE_PATH).read_bytes()

        with self.assertRaises(sync.ActionRequired) as raised:
            sync.prepare_phase(
                root=self.root,
                work_dir=work_dir,
                github=FakeGithub(lifecycle),
                source=FakeSource(SHA_THREE, snapshot=snapshot),
                limits=sync.Limits(max_prompt_bytes=prompt_bytes - 1),
            )

        message = str(raised.exception)
        self.assertIn(SHA_TWO, message)
        self.assertIn(f"prepared input is {prompt_bytes} bytes", message)
        self.assertIn("manually reviewed pull request", message)
        self.assertIn("cursor was not advanced", message)
        self.assertEqual((self.root / sync.STATE_PATH).read_bytes(), state_before)
        self.assertFalse((work_dir / "prepared.json").exists())
        self.assertFalse((work_dir / "status.json").exists())

    def test_incomplete_backfill_snapshot_limit_remains_limit_failure(self) -> None:
        work_dir = self.root / "initial-limit-work"
        state_before = (self.root / sync.STATE_PATH).read_bytes()
        with self.assertRaises(sync.LimitFailure):
            sync.prepare_phase(
                root=self.root,
                work_dir=work_dir,
                github=FakeGithub(
                    sync.Lifecycle(
                        action="proceed", remote_sha=None, reason="ready"
                    )
                ),
                source=FakeSource(
                    SHA_TWO,
                    snapshot=sync.LimitFailure("initial range exceeded a limit"),
                ),
                limits=self.limits,
            )
        self.assertEqual((self.root / sync.STATE_PATH).read_bytes(), state_before)
        self.assertFalse((work_dir / "prepared.json").exists())
        self.assertFalse((work_dir / "status.json").exists())

    def test_later_phases_skip_before_reading_credentials(self) -> None:
        work_dir = self.root / "work"
        work_dir.mkdir()
        sync.write_json(work_dir / "status.json", {"status": "no-change"})
        environment = dict(os.environ)
        environment.pop("DEEPSEEK_API_KEY", None)
        environment.pop("GITHUB_TOKEN", None)
        for phase in ("generate", "finalize"):
            with self.subTest(phase=phase):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(MODULE_PATH),
                        phase,
                        "--root",
                        str(self.root),
                        "--work-dir",
                        str(work_dir),
                    ],
                    env=environment,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)


class HistoryRetentionTests(TempDocs):
    def test_batch_history_retains_full_previous_audit_and_is_immutable(self) -> None:
        previous_last_sync = {
            "range": {
                "base_exclusive": "a" * 40,
                "head_inclusive": SHA_ONE,
                "commit_count": 5,
            },
            "model": "deepseek-flash",
            "usage": {"prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 110},
            "summary": "Initial backfill.",
            "outcome": "update",
            "decisions": [
                {
                    "commit": SHA_ONE,
                    "decision": "update",
                    "rationale": "Initial behavior.",
                    "evidence": ["firmware/initial.c"],
                }
            ],
            "files_changed": ["docs/Initial.md"],
            "recorded_at": "2026-10-18T00:00:00+00:00",
        }
        state = {
            "schema_version": 1,
            "source_repository": sync.SOURCE_REPOSITORY,
            "source_branch": sync.SOURCE_BRANCH,
            "target_repository": sync.TARGET_REPOSITORY,
            "target_branch": sync.TARGET_BRANCH,
            "cursor_commit": SHA_ONE,
            "initial_backfill": {
                "through_commit": SHA_ONE,
                "commit_count": 5,
                "completed": True,
            },
            "last_sync": copy.deepcopy(previous_last_sync),
        }
        result = sync.SyncResult(
            summary="One integration event.",
            decisions=(
                sync.SyncDecision(
                    commit=SHA_TWO,
                    decision="no-impact",
                    rationale="No user-facing change.",
                    evidence=("firmware/internal.c",),
                ),
            ),
            files=(),
        )
        next_state = sync._next_state(
            state,
            {
                "range": {
                    "base_exclusive": SHA_ONE,
                    "head_inclusive": SHA_TWO,
                    "commit_count": 1,
                }
            },
            result,
            model="deepseek-flash",
            usage={"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25},
        )

        entry = sync._history_write_entry(self.root, state, next_state)
        self.assertIsNotNone(entry)
        assert entry is not None
        relative, history_text = entry
        self.assertEqual(relative, f".ai-docs/history/{SHA_TWO}.json")
        history = json.loads(history_text)
        self.assertEqual(history["previous_last_sync"], previous_last_sync)
        self.assertEqual(history["last_sync"], next_state["last_sync"])
        self.assertEqual(history["batch_head"], SHA_TWO)

        sync.atomic_write_set(self.root, {relative: history_text})
        history_path = self.root / relative
        original = history_path.read_bytes()
        self.assertIsNone(sync._history_write_entry(self.root, state, next_state))
        self.assertEqual(history_path.read_bytes(), original)

        history_path.write_text('{"different":true}\n', encoding="utf-8")
        conflict = history_path.read_bytes()
        with self.assertRaisesRegex(sync.ActionRequired, "append-only"):
            sync._history_write_entry(self.root, state, next_state)
        self.assertEqual(history_path.read_bytes(), conflict)


class RecentChangesTests(TempDocs):
    def write_feed(self, document: dict[str, object]) -> bytes:
        path = self.root / sync.RECENT_CHANGES_PATH
        path.write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return path.read_bytes()

    def test_append_is_newest_integration_first_idempotent_and_capped(self) -> None:
        seed_sha = f"{100:040x}"
        seed_entries = [
            recent_entry(f"{index + 100:040x}", seed_sha) for index in range(59)
        ]
        self.write_feed(recent_document(seed_entries))

        child = f"{2:040x}"
        merge = f"{3:040x}"
        context = prepared_context(
            [
                prepared_commit(
                    child,
                    subject="feat: exact child subject",
                    authored_at="2026-10-18T11:02:03+02:00",
                ),
                prepared_commit(
                    merge,
                    parents=("b" * 40, child),
                    subject="Merge exact integration subject",
                    authored_at="2026-10-18T12:04:05+02:00",
                ),
            ]
        )
        result = recent_result([(child, "update"), (merge, "no-impact")])

        entry = sync.recent_changes_write_entry(
            self.root,
            context,
            result,
            model="deepseek-flash",
            analyzed_at="2026-10-20T11:12:13+00:00",
        )
        self.assertIsNotNone(entry)
        assert entry is not None
        path, text = entry
        self.assertEqual(path, sync.RECENT_CHANGES_PATH)
        document = json.loads(text)
        self.assertEqual(len(document["entries"]), sync.RECENT_CHANGES_MAX_ENTRIES)
        self.assertEqual(document["latest_analyzed_commit"], merge)
        self.assertEqual(
            [item["commit"] for item in document["entries"][:2]], [merge, child]
        )
        self.assertEqual(document["entries"][0]["subject"], "Merge exact integration subject")
        self.assertEqual(document["entries"][1]["subject"], "feat: exact child subject")
        self.assertEqual(document["entries"][1]["authored_at"], "2026-10-18T11:02:03+02:00")
        self.assertEqual(document["entries"][0]["parents"], ["b" * 40, child])

        feed_path = self.root / path
        feed_path.write_text(text, encoding="utf-8")
        before = feed_path.read_bytes()
        self.assertIsNone(
            sync.recent_changes_write_entry(
                self.root,
                context,
                result,
                model="deepseek-flash",
                analyzed_at="2026-10-21T00:00:00+00:00",
            )
        )
        self.assertEqual(feed_path.read_bytes(), before)

    def test_hostile_text_remains_plain_data(self) -> None:
        commit = f"{4:040x}"
        hostile = '<img src=x onerror="alert(1)"> [x](javascript:alert(2))'
        self.write_feed(
            recent_document([recent_entry(f"{6:040x}", f"{6:040x}")])
        )
        entry = sync.recent_changes_write_entry(
            self.root,
            prepared_context([prepared_commit(commit)]),
            recent_result(
                [(commit, "no-impact")],
                comments={commit: hostile},
            ),
            model="deepseek-flash",
            analyzed_at="2026-10-20T11:12:13+00:00",
        )
        self.assertIsNotNone(entry)
        assert entry is not None
        document = json.loads(entry[1])
        self.assertEqual(document["entries"][0]["comment"], hostile)
        self.assertIsInstance(document["entries"][0]["comment"], str)
        self.assertEqual(
            document["entries"][0]["integration_batch_commit"], commit
        )

    def test_partially_seeded_batch_is_deduplicated_in_batch_order(self) -> None:
        child = f"{11:040x}"
        merge = f"{12:040x}"
        self.write_feed(
            recent_document(
                [
                    recent_entry(
                        merge,
                        merge,
                        parents=("a" * 40, child),
                        subject="Merge already seeded",
                        decision_value="no-impact",
                    )
                ]
            )
        )
        context = prepared_context(
            [
                prepared_commit(child, subject="New child entry"),
                prepared_commit(
                    merge,
                    parents=("a" * 40, child),
                    subject="Merge already seeded",
                ),
            ]
        )
        entry = sync.recent_changes_write_entry(
            self.root,
            context,
            recent_result([(child, "update"), (merge, "no-impact")]),
            model="deepseek-flash",
            analyzed_at="2026-10-20T11:12:13+00:00",
        )
        self.assertIsNotNone(entry)
        assert entry is not None
        entries = json.loads(entry[1])["entries"]
        self.assertEqual([item["commit"] for item in entries], [merge, child])
        self.assertEqual(entries[0]["subject"], "Merge already seeded")

    def test_duplicate_sha_and_invalid_metadata_are_rejected(self) -> None:
        entry = recent_entry(SHA_ONE, SHA_TWO)
        duplicate = recent_document([entry, copy.deepcopy(entry)])
        with self.assertRaisesRegex(sync.ValidationFailure, "duplicate commit"):
            sync.validate_recent_changes(duplicate)

        invalid_date = recent_document([recent_entry(SHA_ONE, SHA_TWO)])
        invalid_date["entries"][0]["authored_at"] = "not a date"
        with self.assertRaisesRegex(sync.ValidationFailure, "authored date"):
            sync.validate_recent_changes(invalid_date)

        invalid_source = recent_document([recent_entry(SHA_ONE, SHA_TWO)])
        invalid_source["source_repository"] = "example/wrong"
        with self.assertRaisesRegex(sync.ValidationFailure, "source repository"):
            sync.validate_recent_changes(invalid_source)

    def test_no_impact_batch_still_writes_feed(self) -> None:
        commit = f"{7:040x}"
        self.write_feed(
            recent_document([recent_entry(f"{8:040x}", f"{8:040x}")])
        )
        entry = sync.recent_changes_write_entry(
            self.root,
            prepared_context([prepared_commit(commit)]),
            recent_result([(commit, "no-impact")]),
            model="deepseek-flash",
            analyzed_at="2026-10-20T11:12:13+00:00",
        )
        self.assertIsNotNone(entry)
        assert entry is not None
        document = json.loads(entry[1])
        self.assertEqual(document["entries"][0]["decision"], "no-impact")
        self.assertEqual(document["entries"][0]["commit"], commit)

    def test_user_impact_merge_remains_an_update_entry(self) -> None:
        merge = f"{9:040x}"
        parent_a = "a" * 40
        parent_b = "b" * 40
        self.write_feed(
            recent_document([recent_entry(f"{10:040x}", f"{10:040x}")])
        )
        entry = sync.recent_changes_write_entry(
            self.root,
            prepared_context(
                [prepared_commit(merge, parents=(parent_a, parent_b))]
            ),
            recent_result([(merge, "update")]),
            model="deepseek-flash",
            analyzed_at="2026-10-20T11:12:13+00:00",
        )
        self.assertIsNotNone(entry)
        assert entry is not None
        merge_entry = json.loads(entry[1])["entries"][0]
        self.assertEqual(merge_entry["decision"], "update")
        self.assertEqual(merge_entry["parents"], [parent_a, parent_b])

    def test_invalid_existing_feed_fails_before_state_or_history_changes(self) -> None:
        state_path = self.root / sync.STATE_PATH
        state_path.write_text('{"authoritative":true}\n', encoding="utf-8")
        history_path = self.root / sync.HISTORY_DIR / f"{SHA_ONE}.json"
        history_path.parent.mkdir()
        history_path.write_text('{"immutable":true}\n', encoding="utf-8")
        self.write_feed(
            recent_document([recent_entry(SHA_ONE, SHA_TWO)])
        )
        feed_path = self.root / sync.RECENT_CHANGES_PATH
        broken = json.loads(feed_path.read_text(encoding="utf-8"))
        broken["entries"][0]["parents"] = ["not-a-sha"]
        feed_path.write_text(json.dumps(broken), encoding="utf-8")
        state_before = state_path.read_bytes()
        history_before = history_path.read_bytes()
        feed_before = feed_path.read_bytes()

        with self.assertRaisesRegex(sync.ValidationFailure, "invalid parent"):
            sync.recent_changes_write_entry(
                self.root,
                prepared_context([prepared_commit(SHA_THREE)]),
                recent_result([(SHA_THREE, "no-impact")]),
                model="deepseek-flash",
                analyzed_at="2026-10-20T11:12:13+00:00",
            )

        self.assertEqual(state_path.read_bytes(), state_before)
        self.assertEqual(history_path.read_bytes(), history_before)
        self.assertEqual(feed_path.read_bytes(), feed_before)


class BootstrapRecentChangesTests(unittest.TestCase):
    def test_checked_in_feed_matches_source_and_keeps_cursor_and_history(self) -> None:
        root = MODULE_PATH.parent.parent
        feed_path = root / sync.RECENT_CHANGES_PATH
        document = json.loads(feed_path.read_text(encoding="utf-8"))
        validated = sync.validate_recent_changes(document)
        self.assertEqual(len(validated["entries"]), 24)
        self.assertEqual(
            validated["latest_analyzed_commit"],
            "bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3",
        )

        by_sha = {entry["commit"]: entry for entry in validated["entries"]}
        readme = by_sha["f20dedfca3a31d5b1552f2a3d967c0a9dd434d65"]
        readme_merge = by_sha["bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3"]
        self.assertEqual(
            readme["subject"],
            "docs: replace inherited README with Capoworks ECU overview",
        )
        self.assertEqual(readme["authored_at"], "2026-10-18T20:25:40+02:00")
        self.assertEqual(
            readme_merge["subject"],
            "Merge pull request #56 from capoworks/docs/capoworks-readme",
        )
        self.assertEqual(
            readme_merge["authored_at"], "2026-10-18T20:26:22+02:00"
        )
        self.assertTrue(
            all(
                "not claimed public" not in entry["comment"].lower()
                for entry in validated["entries"]
            )
        )

        state = sync.load_state(root / sync.STATE_PATH)
        self.assertEqual(
            state["cursor_commit"],
            "825d7fda5c32b7ec3f755be4897775819e8605d1",
        )
        state_before = (root / sync.STATE_PATH).read_bytes()
        history_before = {
            path.name: path.read_bytes()
            for path in sorted((root / sync.HISTORY_DIR).glob("*.json"))
        }
        commits = [
            {
                "sha": entry["commit"],
                "parents": entry["parents"],
                "author": "Sync Test",
                "authored_at": entry["authored_at"],
                "subject": entry["subject"],
                "changed_paths": [],
                "full_diff": "",
            }
            for entry in (readme, readme_merge)
        ]
        result = recent_result(
            [
                (readme["commit"], "no-impact"),
                (readme_merge["commit"], "no-impact"),
            ]
        )
        self.assertIsNone(
            sync.recent_changes_write_entry(
                root,
                {
                    "range": {
                        "base_exclusive": state["cursor_commit"],
                        "head_inclusive": readme_merge["commit"],
                        "commit_count": 2,
                    },
                    "commits": commits,
                },
                result,
                model="deepseek-flash",
                analyzed_at="2026-10-20T12:00:00+00:00",
            )
        )
        self.assertEqual((root / sync.STATE_PATH).read_bytes(), state_before)
        history_after = {
            path.name: path.read_bytes()
            for path in sorted((root / sync.HISTORY_DIR).glob("*.json"))
        }
        self.assertEqual(history_after, history_before)


class ScriptedRunner:
    def __init__(self, handler: object):
        self.handler = handler
        self.calls: list[tuple[list[str], pathlib.Path | None]] = []

    def run(
        self,
        args: list[str],
        *,
        cwd: pathlib.Path | None = None,
        env: object = None,
        max_output_bytes: int = 2_000_000,
        timeout: int | None = None,
    ) -> object:
        self.calls.append((list(args), cwd))
        return self.handler(list(args), cwd, max_output_bytes)


class SourceSafetyTests(unittest.TestCase):
    def make_source(
        self,
        handler: object,
        temporary: pathlib.Path,
        limits: object | None = None,
    ) -> object:
        runner = ScriptedRunner(handler)
        source = sync.SourceRepository(
            runner, temporary, limits or sync.Limits(), source_url="public"
        )
        source._repo = sync.GitRepository(runner, temporary)
        return source

    def test_force_pushed_source_history_is_rejected(self) -> None:
        def handler(args: list[str], cwd: object, maximum: int) -> object:
            if args[:2] == ["git", "rev-parse"]:
                return sync.CommandResult(stdout=(SHA_TWO + "\n").encode(), stderr=b"")
            if "merge-base" in args:
                raise sync.SyncFailure("git merge-base exited with status 1")
            raise AssertionError(args)

        with tempfile.TemporaryDirectory() as temporary:
            source = self.make_source(handler, pathlib.Path(temporary))
            with self.assertRaisesRegex(sync.SyncFailure, "force-pushed history"):
                source.snapshot(SHA_ONE, SHA_TWO)

    def test_merge_base_fatal_status_is_not_treated_as_nonancestor(self) -> None:
        def handler(args: list[str], cwd: object, maximum: int) -> object:
            if "merge-base" in args:
                raise sync.SyncFailure(
                    "git merge-base exited with status 128: fatal repository error"
                )
            raise AssertionError(args)

        with tempfile.TemporaryDirectory() as temporary:
            source = self.make_source(handler, pathlib.Path(temporary))
            with self.assertRaisesRegex(
                sync.SyncFailure, "status 128: fatal repository error"
            ):
                source._is_ancestor(SHA_ONE, SHA_TWO)

    def test_more_than_forty_commits_fails_closed(self) -> None:
        def handler(args: list[str], cwd: object, maximum: int) -> object:
            if args[:2] == ["git", "rev-parse"]:
                return sync.CommandResult(stdout=(SHA_TWO + "\n").encode(), stderr=b"")
            if "merge-base" in args:
                return sync.CommandResult(stdout=b"", stderr=b"")
            if args[:3] == ["git", "rev-list", "--count"]:
                return sync.CommandResult(stdout=b"41\n", stderr=b"")
            raise AssertionError(args)

        with tempfile.TemporaryDirectory() as temporary:
            source = self.make_source(handler, pathlib.Path(temporary))
            with self.assertRaisesRegex(sync.LimitFailure, "maximum is 40"):
                source.snapshot(SHA_ONE, SHA_TWO)

    def test_subprocess_output_truncation_fails_closed(self) -> None:
        runner = sync.CappedRunner()
        with self.assertRaisesRegex(sync.LimitFailure, "output exceeded"):
            runner.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.stdout.write('x' * 100)",
                ],
                max_output_bytes=10,
                timeout=10,
            )

    def test_clone_uses_blobless_partial_clone(self) -> None:
        def handler(args: list[str], cwd: object, maximum: int) -> object:
            self.assertIn("--filter=blob:none", args)
            self.assertNotIn("--depth", args)
            return sync.CommandResult(stdout=b"", stderr=b"")

        with tempfile.TemporaryDirectory() as temporary:
            runner = ScriptedRunner(handler)
            source = sync.SourceRepository(
                runner,
                pathlib.Path(temporary),
                sync.Limits(),
                source_url="public",
            )
            source.clone()
        self.assertEqual(len(runner.calls), 1)

    def test_known_large_source_files_fit_caps_but_oversize_fails(self) -> None:
        known_sizes = {
            "firmware/tunerstudio/tunerstudio.template.ini": 262_086,
            "firmware/integration/fome_config.txt": 123_819,
        }
        limits = sync.Limits()
        self.assertEqual(sum(known_sizes.values()), 385_905)
        self.assertLessEqual(sum(known_sizes.values()), limits.max_current_total_bytes)
        source_size = 0

        def handler(
            args: list[str], cwd: object, maximum: int
        ) -> sync.CommandResult:
            if "cat-file" in args:
                return sync.CommandResult(stdout=f"{source_size}\n".encode(), stderr=b"")
            if args[:2] == ["git", "show"]:
                return sync.CommandResult(
                    stdout=b"x" * source_size, stderr=b""
                )
            raise AssertionError(args)

        with tempfile.TemporaryDirectory() as temporary:
            source = self.make_source(
                handler,
                pathlib.Path(temporary),
                limits,
            )
            source._tree_set = set(known_sizes)
            source._tree_commit = SHA_TWO
            for path, expected_size in known_sizes.items():
                source_size = expected_size
                content = source._file_at_commit(
                    SHA_TWO, path, limits.max_current_file_bytes
                )
                self.assertEqual(len(content.encode("utf-8")), expected_size)
            source_size = limits.max_current_file_bytes + 1
            source._tree_set.add("firmware/oversized.txt")
            with self.assertRaisesRegex(sync.LimitFailure, "limit is 300000"):
                source._file_at_commit(
                    SHA_TWO,
                    "firmware/oversized.txt",
                    limits.max_current_file_bytes,
                )


class RealGitRepository:
    """Small standard-library Git fixture for source-history DAG tests."""

    def __init__(self, root: pathlib.Path) -> None:
        self.root = root
        self.root.mkdir(exist_ok=True)
        self.git("init", "--quiet", "--initial-branch=master")
        self.git("config", "user.name", "Sync Test")
        self.git("config", "user.email", "sync-test@example.com")

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment.update(
            {
                "GIT_AUTHOR_NAME": "Sync Test",
                "GIT_AUTHOR_EMAIL": "sync-test@example.com",
                "GIT_COMMITTER_NAME": "Sync Test",
                "GIT_COMMITTER_EMAIL": "sync-test@example.com",
                "GIT_TERMINAL_PROMPT": "0",
            }
        )
        result = subprocess.run(
            ["git", *args],
            cwd=self.root,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        if check and result.returncode != 0:
            raise AssertionError(
                f"git {' '.join(args)} failed: {result.stderr or result.stdout}"
            )
        return result

    def write(self, path: str, content: str) -> None:
        target = self.root / pathlib.PurePosixPath(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="")

    def commit(self, message: str, files: dict[str, str]) -> str:
        for path, content in files.items():
            self.write(path, content)
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", message)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def checkout(self, branch: str, *, create: bool = False) -> None:
        args = ["switch"]
        if create:
            args.extend(["--create", branch])
        else:
            args.append(branch)
        self.git(*args)

    def merge(
        self,
        branch: str,
        message: str,
        *,
        resolutions: dict[str, str] | None = None,
    ) -> str:
        result = self.git("merge", "--no-ff", "--no-commit", branch, check=False)
        if result.returncode != 0 and not resolutions:
            raise AssertionError(f"merge failed: {result.stderr or result.stdout}")
        for path, content in (resolutions or {}).items():
            self.write(path, content)
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", message)
        return self.git("rev-parse", "HEAD").stdout.strip()


@unittest.skipUnless(shutil.which("git"), "Git is unavailable")
class IntegrationEventGitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temporary.name)
        self.repository = RealGitRepository(self.root / "firmware")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def source(
        self,
        *,
        target_root: pathlib.Path | None = None,
        work_name: str = "source-work",
        limits: sync.Limits | None = None,
    ) -> sync.SourceRepository:
        return sync.SourceRepository(
            sync.CappedRunner(),
            self.root / work_name,
            limits or sync.Limits(),
            source_url=str(self.repository.root),
            target_root=target_root,
        )

    def test_sidebranch_cursor_selects_first_parent_event_and_reads_that_tree(
        self,
    ) -> None:
        base = self.repository.commit("base", {"tracked.txt": "base\n"})
        self.repository.checkout("cursor", create=True)
        cursor = self.repository.commit(
            "cursor-side",
            {
                "tracked.txt": "at-event\n",
                "docs/event.md": "# Event at B\n",
            },
        )
        self.repository.checkout("master")
        master_child = self.repository.commit(
            "master-child", {"master-only.txt": "master\n"}
        )
        event = self.repository.merge("cursor", "merge cursor")
        observed_head = self.repository.commit(
            "later-head",
            {
                "tracked.txt": "at-observed-head\n",
                "docs/event.md": "# Event at H\n",
            },
        )

        source = self.source()
        self.assertEqual(source.resolve_head(), observed_head)
        snapshot = source.snapshot(
            cursor, observed_head, integration_event=True
        )

        expected = self.repository.git(
            "rev-list", "--reverse", "--topo-order", f"{cursor}..{event}"
        ).stdout.splitlines()
        actual = [commit.sha for commit in snapshot.commits]
        self.assertEqual(snapshot.head, event)
        self.assertEqual(snapshot.observed_head, observed_head)
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), len(set(actual)))
        self.assertIn(master_child, actual)
        self.assertNotIn(cursor, actual)
        self.assertEqual(snapshot.current_files["tracked.txt"], "at-event\n")
        self.assertEqual(
            snapshot.source_wiki_docs["docs/event.md"], "# Event at B\n"
        )
        self.assertNotEqual(base, cursor)

    def test_merge_changed_paths_include_resolution_and_first_parent_delta(
        self,
    ) -> None:
        base = self.repository.commit("base", {"shared.txt": "base\n"})
        self.repository.checkout("feature", create=True)
        feature = self.repository.commit(
            "feature", {"shared.txt": "feature\n", "feature.txt": "feature\n"}
        )
        self.repository.checkout("master")
        master = self.repository.commit(
            "master",
            {"shared.txt": "master\n", "master-only.txt": "master\n"},
        )
        merge = self.repository.merge(
            "feature",
            "resolve merge",
            resolutions={"shared.txt": "resolved\n"},
        )

        snapshot = self.source().snapshot(master, merge, integration_event=True)
        merge_commit = next(commit for commit in snapshot.commits if commit.sha == merge)
        self.assertEqual(merge_commit.parents, (master, feature))
        self.assertIn("shared.txt", merge_commit.changed_paths)
        self.assertIn("feature.txt", merge_commit.changed_paths)
        self.assertNotIn("master-only.txt", merge_commit.changed_paths)
        self.assertIn(f"Parents: {master} {feature}", merge_commit.patch)
        self.assertIn("resolved", merge_commit.patch)

    def test_backlog_over_forty_selects_only_the_earliest_event(self) -> None:
        base = self.repository.commit("base", {"base.txt": "base\n"})
        expected_event = ""
        for index in range(45):
            current = self.repository.commit(
                f"change-{index}", {f"changes/{index:02d}.txt": f"{index}\n"}
            )
            if not expected_event:
                expected_event = current
        observed_head = current

        snapshot = self.source().snapshot(
            base, observed_head, integration_event=True
        )
        self.assertEqual(snapshot.head, expected_event)
        self.assertEqual([item.sha for item in snapshot.commits], [expected_event])
        self.assertNotEqual(snapshot.head, snapshot.observed_head)

    def test_incomplete_initial_backfill_retains_whole_range_mode(self) -> None:
        base = self.repository.commit("base", {"base.txt": "base\n"})
        first = self.repository.commit("first", {"first.txt": "first\n"})
        second = self.repository.commit("second", {"second.txt": "second\n"})

        initial = self.source(work_name="initial-work").snapshot(base, second)
        self.assertEqual(initial.head, second)
        self.assertEqual(initial.observed_head, second)
        self.assertEqual([item.sha for item in initial.commits], [first, second])

        event = self.source(work_name="event-work").snapshot(
            base, second, integration_event=True
        )
        self.assertEqual(event.head, first)
        self.assertEqual([item.sha for item in event.commits], [first])

    def test_oversized_event_requires_action_without_advancing_state(self) -> None:
        cursor = self.repository.commit("base", {"base.txt": "base\n"})
        self.repository.checkout("large-event", create=True)
        for index in range(40):
            self.repository.commit(
                f"large-{index}", {f"event/{index:02d}.txt": f"{index}\n"}
            )
        self.repository.checkout("master")
        event = self.repository.merge("large-event", "oversized integration")

        target = self.root / "docs-repository"
        target.mkdir()
        (target / "docs").mkdir()
        docs_repo = RealGitRepository(target)
        docs_repo.commit("docs base", {"docs/Placeholder.md": "# Placeholder\n"})
        state = {
            "schema_version": 1,
            "source_repository": sync.SOURCE_REPOSITORY,
            "source_branch": sync.SOURCE_BRANCH,
            "target_repository": sync.TARGET_REPOSITORY,
            "target_branch": sync.TARGET_BRANCH,
            "cursor_commit": cursor,
            "initial_backfill": {
                "through_commit": cursor,
                "commit_count": 5,
                "completed": True,
            },
            "last_sync": None,
        }
        state_path = target / sync.STATE_PATH
        state_path.parent.mkdir()
        state_path.write_text(json.dumps(state), encoding="utf-8")
        before = state_path.read_bytes()
        github = FakeGithub(
            sync.Lifecycle(
                action="proceed",
                remote_sha=None,
                reason="no bot branch",
            )
        )

        with self.assertRaises(sync.ActionRequired) as raised:
            sync.prepare_phase(
                root=target,
                work_dir=self.root / "oversized-work",
                github=github,
                source=self.source(target_root=target),
                limits=sync.Limits(),
            )
        message = str(raised.exception)
        self.assertIn(event, message)
        self.assertIn("manually reviewed pull request", message)
        self.assertEqual(state_path.read_bytes(), before)
        self.assertFalse((self.root / "oversized-work/prepared.json").exists())

    def test_event_source_file_limit_requires_action_without_ready_artifacts(
        self,
    ) -> None:
        cursor = self.repository.commit("base", {"base.txt": "base\n"})
        self.repository.checkout("large-source", create=True)
        self.repository.commit(
            "large source",
            {"firmware/oversized.c": "x" * 65},
        )
        self.repository.checkout("master")
        event = self.repository.merge("large-source", "large source integration")

        target = self.root / "source-limit-docs"
        target.mkdir()
        (target / "docs").mkdir()
        docs_repo = RealGitRepository(target)
        docs_repo.commit("docs base", {"docs/Placeholder.md": "# Placeholder\n"})
        state = {
            "schema_version": 1,
            "source_repository": sync.SOURCE_REPOSITORY,
            "source_branch": sync.SOURCE_BRANCH,
            "target_repository": sync.TARGET_REPOSITORY,
            "target_branch": sync.TARGET_BRANCH,
            "cursor_commit": cursor,
            "initial_backfill": {
                "through_commit": cursor,
                "commit_count": 5,
                "completed": True,
            },
            "last_sync": None,
        }
        state_path = target / sync.STATE_PATH
        state_path.parent.mkdir()
        state_path.write_text(json.dumps(state), encoding="utf-8")
        before = state_path.read_bytes()
        work_dir = self.root / "source-limit-work"

        with self.assertRaises(sync.ActionRequired) as raised:
            sync.prepare_phase(
                root=target,
                work_dir=work_dir,
                github=FakeGithub(
                    sync.Lifecycle(
                        action="proceed",
                        remote_sha=None,
                        reason="no bot branch",
                    )
                ),
                source=self.source(
                    target_root=target,
                    limits=sync.Limits(max_current_file_bytes=32),
                ),
                limits=sync.Limits(max_current_file_bytes=32),
            )

        message = str(raised.exception)
        self.assertIn(event, message)
        self.assertIn(
            "source file firmware/oversized.c is 65 bytes; the limit is 32",
            message,
        )
        self.assertIn("manually reviewed pull request", message)
        self.assertIn("cursor was not advanced", message)
        self.assertEqual(state_path.read_bytes(), before)
        self.assertFalse((work_dir / "prepared.json").exists())
        self.assertFalse((work_dir / "status.json").exists())


class ModelTransportTests(unittest.TestCase):
    def response(
        self,
        content: object,
        *,
        model: str = "deepseek-flash",
        finish_reason: str | None = "stop",
    ) -> tuple:
        choice: dict[str, object] = {"message": {"content": json.dumps(content)}}
        if finish_reason is not None:
            choice["finish_reason"] = finish_reason
        return api_json(
            {
                "model": model,
                "choices": [choice],
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 10,
                    "total_tokens": 30,
                    "prompt_cache_hit_tokens": 5,
                },
            }
        )

    def test_request_is_json_object_and_actual_usage_is_reported(self) -> None:
        model_payload = {
            "summary": "No impact.",
            "decisions": [decision(SHA_ONE, "no-impact")],
            "files": [],
        }
        transport = FakeTransport([self.response(model_payload)])
        settings = sync.AISettings(
            model="deepseek-flash", max_tokens=500, timeout_seconds=10, retries=1
        )
        client = sync.DeepSeekClient(transport, "secret", settings)
        result = client.generate({"range": {"head_inclusive": SHA_ONE}})
        request = transport.requests[0]
        body = json.loads(request["body"])
        self.assertEqual(body["model"], "deepseek-flash")
        self.assertEqual(body["response_format"], {"type": "json_object"})
        self.assertEqual(body["max_tokens"], 500)
        self.assertEqual(body["thinking"], {"type": "disabled"})
        self.assertEqual(result.usage["total_tokens"], 30)
        self.assertEqual(result.model, "deepseek-flash")

    def test_transient_network_failure_is_retried(self) -> None:
        model_payload = {
            "summary": "No impact.",
            "decisions": [decision(SHA_ONE, "no-impact")],
            "files": [],
        }

        class FlakyTransport(FakeTransport):
            def request(self, *args: object, **kwargs: object) -> tuple:
                if not self.requests:
                    self.requests.append({})
                    raise sync.TransientTransportFailure("temporary")
                return super().request(*args, **kwargs)

        waits: list[float] = []
        transport = FlakyTransport([self.response(model_payload)])
        client = sync.DeepSeekClient(
            transport,
            "secret",
            sync.AISettings(
                model="deepseek-flash", max_tokens=500, timeout_seconds=10, retries=2
            ),
            sleep=waits.append,
        )
        result = client.generate({"range": {"head_inclusive": SHA_ONE}})
        self.assertEqual(result.usage["total_tokens"], 30)
        self.assertEqual(waits, [1])

    def test_missing_usage_is_rejected(self) -> None:
        malformed = {
            "model": "deepseek-flash",
            "choices": [{"finish_reason": "stop", "message": {"content": "{}"}}],
        }
        with self.assertRaisesRegex(sync.ApiFailure, "actual token usage"):
            sync.parse_model_response(malformed)

    def test_length_finish_reason_rejects_valid_json_content(self) -> None:
        model_payload = {
            "summary": "No impact.",
            "decisions": [decision(SHA_ONE, "no-impact")],
            "files": [],
        }
        _, _, data = self.response(model_payload, finish_reason="length")
        with self.assertRaisesRegex(sync.ApiFailure, "finish_reason.*length"):
            sync.parse_model_response(json.loads(data))

    def test_missing_finish_reason_is_rejected(self) -> None:
        model_payload = {
            "summary": "No impact.",
            "decisions": [decision(SHA_ONE, "no-impact")],
            "files": [],
        }
        _, _, data = self.response(model_payload, finish_reason=None)
        with self.assertRaisesRegex(sync.ApiFailure, "missing finish_reason"):
            sync.parse_model_response(json.loads(data))

    def test_exact_serialized_message_boundary_is_shared_with_dispatch_cap(self) -> None:
        context = {
            "range": {"head_inclusive": SHA_ONE},
            "marker": "Capoworks ECU \N{SNOWMAN}",
        }
        messages = sync.build_messages(context)
        serialized = json.dumps(
            messages, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        prompt_bytes = sync.serialized_message_bytes(context)
        self.assertEqual(sync.serialize_messages(messages), serialized)
        self.assertEqual(prompt_bytes, len(serialized))

        model_payload = {
            "summary": "No impact.",
            "decisions": [decision(SHA_ONE, "no-impact")],
            "files": [],
        }
        transport = FakeTransport([self.response(model_payload)])
        client = sync.DeepSeekClient(
            transport,
            "secret",
            sync.AISettings(
                model="deepseek-flash",
                max_tokens=500,
                timeout_seconds=10,
                retries=1,
            ),
            max_prompt_bytes=prompt_bytes,
        )
        client.generate(context)
        self.assertEqual(len(transport.requests), 1)

        too_small_transport = FakeTransport([])
        too_small = sync.DeepSeekClient(
            too_small_transport,
            "secret",
            sync.AISettings(
                model="deepseek-flash",
                max_tokens=500,
                timeout_seconds=10,
                retries=1,
            ),
            max_prompt_bytes=prompt_bytes - 1,
        )
        with self.assertRaisesRegex(
            sync.LimitFailure, f"serialized prompt is {prompt_bytes} bytes"
        ):
            too_small.generate(context)
        self.assertEqual(too_small_transport.requests, [])


class BuildPreviewRecoveryTests(unittest.TestCase):
    def test_dispatch_failure_reports_pull_request_and_manual_command(self) -> None:
        class FailingGithub:
            def dispatch_build_preview(self, *args: object, **kwargs: object) -> None:
                raise sync.ApiFailure("HTTP 500")

        pull = {
            "number": 17,
            "html_url": "https://github.com/capoworks/capoworks-ecu-docs/pull/17",
        }
        with self.assertRaises(sync.ActionRequired) as raised:
            sync._dispatch_build_preview_with_recovery(
                FailingGithub(), pull, SHA_ONE
            )
        message = str(raised.exception)
        self.assertIn(pull["html_url"], message)
        self.assertIn(
            "gh workflow run build-preview.yml "
            "--repo capoworks/capoworks-ecu-docs "
            f"-f ref={SHA_ONE}",
            message,
        )
        self.assertIn("source range are intact", message)

    def test_serialized_messages_prompt_is_capped_before_dispatch(self) -> None:
        transport = FakeTransport([])
        client = sync.DeepSeekClient(
            transport,
            "secret",
            sync.AISettings(
                model="deepseek-chat", max_tokens=500, timeout_seconds=10, retries=1
            ),
        )
        messages = [{"role": "user", "content": "x" * 1_500_000}]
        with mock.patch.object(sync, "build_messages", return_value=messages):
            with self.assertRaisesRegex(
                sync.LimitFailure, "maximum is 1500000"
            ):
                client.generate({"range": {"head_inclusive": SHA_ONE}})
        self.assertEqual(transport.requests, [])


if __name__ == "__main__":
    unittest.main()
