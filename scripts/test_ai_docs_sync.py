#!/usr/bin/env python3
"""Unit tests for scripts/ai-docs-sync.py using only the standard library."""

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

    def resolve_head(self) -> str:
        return self.head

    def snapshot(self, base: str, head: str) -> object:
        self.snapshot_called = True
        if self.snapshot_value is None:
            raise AssertionError("snapshot should not be called")
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
            model="deepseek-chat",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        )
        self.assertEqual(next_state["cursor_commit"], SHA_TWO)
        self.assertEqual(next_state["last_sync"]["outcome"], "no-impact")
        self.assertTrue(next_state["initial_backfill"]["completed"])
        self.assertEqual(next_state["last_sync"]["decisions"][0]["commit"], SHA_TWO)

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

    def test_more_than_forty_commits_fails_closed(self) -> None:
        commit_lines = "\n".join(f"{index:040x}" for index in range(1, 42)) + "\n"

        def handler(args: list[str], cwd: object, maximum: int) -> object:
            if args[:2] == ["git", "rev-parse"]:
                return sync.CommandResult(stdout=(SHA_TWO + "\n").encode(), stderr=b"")
            if "merge-base" in args:
                return sync.CommandResult(stdout=b"", stderr=b"")
            if "rev-list" in args:
                return sync.CommandResult(stdout=commit_lines.encode(), stderr=b"")
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


class ModelTransportTests(unittest.TestCase):
    def response(self, content: object, *, model: str = "deepseek-chat") -> tuple:
        return api_json(
            {
                "model": model,
                "choices": [{"message": {"content": json.dumps(content)}}],
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
            model="deepseek-chat", max_tokens=500, timeout_seconds=10, retries=1
        )
        client = sync.DeepSeekClient(transport, "secret", settings)
        result = client.generate({"range": {"head_inclusive": SHA_ONE}})
        request = transport.requests[0]
        body = json.loads(request["body"])
        self.assertEqual(body["model"], "deepseek-chat")
        self.assertEqual(body["response_format"], {"type": "json_object"})
        self.assertEqual(body["max_tokens"], 500)
        self.assertEqual(result.usage["total_tokens"], 30)
        self.assertEqual(result.model, "deepseek-chat")

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
                model="deepseek-chat", max_tokens=500, timeout_seconds=10, retries=2
            ),
            sleep=waits.append,
        )
        result = client.generate({"range": {"head_inclusive": SHA_ONE}})
        self.assertEqual(result.usage["total_tokens"], 30)
        self.assertEqual(waits, [1])

    def test_missing_usage_is_rejected(self) -> None:
        malformed = {
            "model": "deepseek-chat",
            "choices": [{"message": {"content": "{}"}}],
        }
        with self.assertRaisesRegex(sync.ApiFailure, "actual token usage"):
            sync.parse_model_response(malformed)


if __name__ == "__main__":
    unittest.main()
