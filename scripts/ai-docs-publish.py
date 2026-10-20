#!/usr/bin/env python3
"""Select, validate, merge, and dispatch AI documentation pull requests.

The script is deliberately separate from generation. It only handles the
fixed automation branch and uses the existing sync validators for state,
history, Markdown, and frontmatter. Only Python's standard library is needed.
"""

from __future__ import annotations

import argparse
import base64
import dataclasses
import importlib.util
import json
import logging
import os
import pathlib
import re
import sys
import tempfile
import urllib.parse
from collections.abc import Mapping, Sequence
from typing import Any


LOG = logging.getLogger("ai-docs-publish")
SYNC_SCRIPT = pathlib.Path(__file__).with_name("ai-docs-sync.py")
POLICY_OLD = "This pull request is never merged by automation."
POLICY_NEW = (
    "After generation and isolated validation, automation may merge this pull "
    "request only when the exact merge preview passes the trusted lint, test, "
    "build, history, state, and diff checks. Automation never bypasses branch "
    "protection."
)
HISTORY_RE = re.compile(r"^\.ai-docs/history/([0-9a-f]{40})\.json$")


@dataclasses.dataclass(frozen=True)
class Candidate:
    pr_number: int
    base_sha: str
    head_sha: str
    merge_sha: str

    def as_outputs(self) -> dict[str, str]:
        return {
            "publish": "true",
            "pr_number": str(self.pr_number),
            "base_sha": self.base_sha,
            "head_sha": self.head_sha,
            "merge_sha": self.merge_sha,
        }


@dataclasses.dataclass(frozen=True)
class ChangedPath:
    path: str
    status: str
    old_mode: str
    new_mode: str


@dataclasses.dataclass(frozen=True)
class DispatchFailure(RuntimeError):
    merged_sha: str
    failures: tuple[str, ...]

    def __str__(self) -> str:
        return (
            f"pull request merged as {self.merged_sha}, but explicit workflow "
            "dispatch was incomplete: "
            + "; ".join(self.failures)
            + ". The checked-in cursor is already advanced. A later scheduled "
            "run must retry deploy safely without merging again."
        )


def _load_sync_module():
    spec = importlib.util.spec_from_file_location("ai_docs_sync_core", SYNC_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the existing sync implementation")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SYNC = _load_sync_module()


class PublishGitHubClient(SYNC.GitHubClient):
    def open_automation_pulls(self) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode(
            {
                "head": f"{SYNC.TARGET_REPOSITORY.split('/', 1)[0]}:{SYNC.BOT_BRANCH}",
                "base": SYNC.TARGET_BRANCH,
                "state": "open",
                "per_page": "100",
            }
        )
        _, payload = self._request(
            "GET",
            f"/repos/{SYNC.TARGET_REPOSITORY}/pulls?{query}",
            expected={200},
        )
        if not isinstance(payload, list) or not all(
            isinstance(pull, dict) for pull in payload
        ):
            raise SYNC.ApiFailure("GitHub open-pull list response is malformed")
        return payload

    def pull(self, number: int) -> dict[str, Any]:
        _, payload = self._request(
            "GET",
            f"/repos/{SYNC.TARGET_REPOSITORY}/pulls/{number}",
            expected={200},
        )
        if not isinstance(payload, dict):
            raise SYNC.ApiFailure("GitHub pull response is malformed")
        return payload

    def update_pull_body(self, number: int, body: str) -> None:
        self._request(
            "PATCH",
            f"/repos/{SYNC.TARGET_REPOSITORY}/pulls/{number}",
            {"body": body},
            expected={200},
        )

    def merge_pull(self, number: int, head_sha: str) -> dict[str, Any]:
        _, payload = self._request(
            "PUT",
            f"/repos/{SYNC.TARGET_REPOSITORY}/pulls/{number}/merge",
            {"merge_method": "merge", "sha": head_sha},
            expected={200},
        )
        if not isinstance(payload, dict):
            raise SYNC.ApiFailure("GitHub merge response is malformed")
        return payload

    def dispatch(self, workflow: str) -> None:
        encoded = urllib.parse.quote(workflow, safe="")
        self._request(
            "POST",
            f"/repos/{SYNC.TARGET_REPOSITORY}/actions/workflows/{encoded}/dispatches",
            {"ref": SYNC.TARGET_BRANCH},
            expected={204},
        )

    def workflow_runs(self, workflow: str) -> list[dict[str, Any]]:
        encoded = urllib.parse.quote(workflow, safe="")
        query = urllib.parse.urlencode(
            {"branch": SYNC.TARGET_BRANCH, "per_page": "20"}
        )
        _, payload = self._request(
            "GET",
            f"/repos/{SYNC.TARGET_REPOSITORY}/actions/workflows/{encoded}/runs?{query}",
            expected={200},
        )
        if not isinstance(payload, dict):
            raise SYNC.ApiFailure("GitHub workflow-runs response is malformed")
        runs = payload.get("workflow_runs")
        if not isinstance(runs, list) or not all(isinstance(run, dict) for run in runs):
            raise SYNC.ApiFailure("GitHub workflow-runs list is malformed")
        return runs


def _client() -> PublishGitHubClient:
    return PublishGitHubClient(
        SYNC.UrllibTransport(),
        os.environ.get("GITHUB_TOKEN", ""),
        api_url=os.environ.get("GITHUB_API_URL", "https://api.github.com"),
    )


def _require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SYNC.SHA_RE.fullmatch(value):
        raise SYNC.ValidationFailure(f"{label} is not a full commit id")
    return value


def _require_number(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise SYNC.ValidationFailure(f"{label} is not a positive integer")
    return value


def validate_pull_metadata(
    pull: Mapping[str, Any], current_master: str
) -> Candidate:
    """Validate all server-controlled PR membership and identity fields."""

    number = _require_number(pull.get("number"), "pull request number")
    if pull.get("state") != "open" or pull.get("merged_at") is not None:
        raise SYNC.ValidationFailure(f"pull request #{number} is not open and unmerged")
    if pull.get("draft") is not False:
        raise SYNC.ValidationFailure(f"pull request #{number} must not be a draft")
    user = pull.get("user")
    if not isinstance(user, Mapping) or user.get("login") != "github-actions[bot]":
        raise SYNC.ValidationFailure(
            f"pull request #{number} was not opened by github-actions[bot]"
        )
    head = pull.get("head")
    base = pull.get("base")
    if not isinstance(head, Mapping) or not isinstance(base, Mapping):
        raise SYNC.ValidationFailure(f"pull request #{number} refs are malformed")
    head_repo = head.get("repo")
    base_repo = base.get("repo")
    if (
        not isinstance(head_repo, Mapping)
        or head_repo.get("full_name") != SYNC.TARGET_REPOSITORY
        or head.get("ref") != SYNC.BOT_BRANCH
    ):
        raise SYNC.ValidationFailure(
            f"pull request #{number} has the wrong head repository or branch"
        )
    if (
        not isinstance(base_repo, Mapping)
        or base_repo.get("full_name") != SYNC.TARGET_REPOSITORY
        or base.get("ref") != SYNC.TARGET_BRANCH
    ):
        raise SYNC.ValidationFailure(
            f"pull request #{number} has the wrong base repository or branch"
        )
    base_sha = _require_sha(base.get("sha"), "pull request base")
    head_sha = _require_sha(head.get("sha"), "pull request head")
    current_master = _require_sha(current_master, "current target master")
    body = pull.get("body")
    if not isinstance(body, str) or SYNC.PR_MARKER not in body.splitlines():
        raise SYNC.ValidationFailure(f"pull request #{number} lacks the sync marker")
    merge_sha = pull.get("merge_commit_sha")
    if merge_sha is not None:
        merge_sha = _require_sha(merge_sha, "pull request merge preview")
    return Candidate(number, current_master, head_sha, merge_sha or "")


def _git_env(token: str) -> dict[str, str]:
    encoded = base64.b64encode(f"x-access-token:{token}".encode("ascii")).decode(
        "ascii"
    )
    env = dict(os.environ)
    env.update(
        {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
            "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {encoded}",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    return env


def _git(
    runner: SYNC.CappedRunner,
    root: pathlib.Path,
    args: Sequence[str],
    *,
    token: str | None = None,
    max_output_bytes: int = 2_000_000,
) -> bytes:
    result = runner.run(
        ["git", *args],
        cwd=root,
        env=_git_env(token) if token else None,
        max_output_bytes=max_output_bytes,
        timeout=120,
    )
    return result.stdout


def _git_text(
    runner: SYNC.CappedRunner, root: pathlib.Path, args: Sequence[str]
) -> str:
    return _git(runner, root, args, max_output_bytes=64_000).decode("utf-8", "strict")


def _fetch_candidate(
    runner: SYNC.CappedRunner,
    root: pathlib.Path,
    token: str,
    number: int,
    base_sha: str,
    head_sha: str,
) -> str:
    _require_number(number, "pull request number")
    _require_sha(base_sha, "pull request base")
    _require_sha(head_sha, "pull request head")
    refs = (
        f"+refs/heads/{SYNC.TARGET_BRANCH}:refs/ai-docs/publish/master",
        f"+refs/pull/{number}/head:refs/ai-docs/publish/head",
        f"+refs/pull/{number}/merge:refs/ai-docs/publish/merge",
    )
    _git(runner, root, ["fetch", "--no-tags", "origin", *refs], token=token)
    fetched_base = _git_text(
        runner, root, ["rev-parse", "refs/ai-docs/publish/master"]
    ).strip()
    fetched_head = _git_text(
        runner, root, ["rev-parse", "refs/ai-docs/publish/head"]
    ).strip()
    merge_sha = _git_text(
        runner, root, ["rev-parse", "refs/ai-docs/publish/merge"]
    ).strip()
    if fetched_base != base_sha or fetched_head != head_sha:
        raise SYNC.ValidationFailure("pull request refs changed while being fetched")
    return _require_sha(merge_sha, "pull request merge preview")


def _fetch_master(
    runner: SYNC.CappedRunner, root: pathlib.Path, token: str
) -> str:
    _git(
        runner,
        root,
        [
            "fetch",
            "--no-tags",
            "origin",
            f"+refs/heads/{SYNC.TARGET_BRANCH}:refs/ai-docs/publish/master",
        ],
        token=token,
    )
    return _require_sha(
        _git_text(
            runner, root, ["rev-parse", "refs/ai-docs/publish/master"]
        ).strip(),
        "fetched target master",
    )


def _parents(
    runner: SYNC.CappedRunner, root: pathlib.Path, commit: str
) -> tuple[str, ...]:
    line = _git_text(runner, root, ["show", "-s", "--format=%P", commit]).strip()
    parents = tuple(line.split()) if line else ()
    if not all(SYNC.SHA_RE.fullmatch(parent) for parent in parents):
        raise SYNC.ValidationFailure(f"commit {commit} has malformed parents")
    return parents


def _commit_identity(
    runner: SYNC.CappedRunner, root: pathlib.Path, commit: str
) -> tuple[str, str]:
    line = _git_text(runner, root, ["show", "-s", "--format=%an%x00%ae", commit])
    fields = line.rstrip("\n").split("\0")
    if len(fields) != 2:
        raise SYNC.ValidationFailure(f"commit {commit} identity is malformed")
    return fields[0], fields[1]


def _read_git_file(
    runner: SYNC.CappedRunner, root: pathlib.Path, commit: str, path: str
) -> bytes:
    pure = pathlib.PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts or "\0" in path:
        raise SYNC.ValidationFailure(f"unsafe changed path: {path!r}")
    return _git(
        runner,
        root,
        ["cat-file", "blob", f"{commit}:{path}"],
        max_output_bytes=2_000_000,
    )


def _tree_sha(
    runner: SYNC.CappedRunner, root: pathlib.Path, commit: str
) -> str:
    return _require_sha(
        _git_text(runner, root, ["show", "-s", "--format=%T", commit]).strip(),
        f"commit {commit} tree",
    )


def _parse_raw_diff(data: bytes) -> tuple[ChangedPath, ...]:
    tokens = data.split(b"\0")
    if tokens and tokens[-1] == b"":
        tokens.pop()
    if len(tokens) % 2:
        raise SYNC.ValidationFailure("candidate diff is malformed")
    changed: list[ChangedPath] = []
    seen: set[str] = set()
    for index in range(0, len(tokens), 2):
        try:
            header = tokens[index].decode("ascii")
            path = tokens[index + 1].decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise SYNC.ValidationFailure("candidate diff has invalid encoding") from exc
        fields = header.split(" ")
        if len(fields) != 5 or not fields[0].startswith(":"):
            raise SYNC.ValidationFailure("candidate raw diff header is malformed")
        old_mode, new_mode, _, _, status = (
            fields[0][1:],
            fields[1],
            fields[2],
            fields[3],
            fields[4],
        )
        if path in seen:
            raise SYNC.ValidationFailure(f"candidate diff repeats path {path}")
        seen.add(path)
        changed.append(ChangedPath(path, status, old_mode, new_mode))
    return tuple(changed)


def _materialize_base_docs(
    sync_module: Any,
    runner: SYNC.CappedRunner,
    root: pathlib.Path,
    base_sha: str,
    destination: pathlib.Path,
) -> pathlib.Path:
    """Create a small, non-executing view of the selected base docs."""

    docs_root = destination / "docs"
    docs_root.mkdir()
    raw = _git(
        runner,
        root,
        ["ls-tree", "-r", "-z", "--full-tree", base_sha, "--", "docs"],
        max_output_bytes=4_000_000,
    )
    seen: set[str] = set()
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, path_bytes = record.split(b"\t", 1)
            mode_bytes, kind_bytes, object_bytes = metadata.split(b" ", 2)
            mode = mode_bytes.decode("ascii")
            kind = kind_bytes.decode("ascii")
            object_sha = object_bytes.decode("ascii")
            path = path_bytes.decode("utf-8", "strict")
        except (UnicodeDecodeError, ValueError) as exc:
            raise SYNC.ValidationFailure(
                "selected base documentation tree is malformed"
            ) from exc
        pure = pathlib.PurePosixPath(path)
        if (
            pure.is_absolute()
            or not pure.parts
            or pure.parts[0] != "docs"
            or any(part in {"", ".", ".."} for part in pure.parts)
        ):
            raise SYNC.ValidationFailure(
                f"selected base documentation path is unsafe: {path!r}"
            )
        if path == "docs":
            raise SYNC.ValidationFailure(
                "selected base documentation root is not a directory"
            )
        if path in seen:
            raise SYNC.ValidationFailure(
                f"selected base documentation path is repeated: {path!r}"
            )
        seen.add(path)
        if kind != "blob" or mode not in {"100644", "100755", "120000"}:
            raise SYNC.ValidationFailure(
                f"selected base documentation entry is unsupported: {path!r}"
            )
        if not SYNC.SHA_RE.fullmatch(object_sha):
            raise SYNC.ValidationFailure(
                f"selected base documentation object is malformed: {path!r}"
            )
        if pure.suffix.lower() not in {".md", ".mdx"} and mode != "120000":
            continue
        target = destination.joinpath(*pure.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        content = _git(
            runner,
            root,
            ["cat-file", "blob", object_sha],
            max_output_bytes=2_000_000,
        )
        if mode == "120000":
            try:
                os.symlink(content, target)
            except (OSError, ValueError) as exc:
                raise sync_module.ValidationFailure(
                    f"could not materialize selected base documentation link: {path!r}"
                ) from exc
        else:
            target.write_bytes(content)
    return docs_root


def _load_state_bytes(
    sync_module: Any, data: bytes
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ai-docs-state-") as directory:
        path = pathlib.Path(directory) / "state.json"
        path.write_bytes(data)
        return sync_module.load_state(path)


def _json_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8", "strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SYNC.ValidationFailure(f"{label} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise SYNC.ValidationFailure(f"{label} must be a JSON object")
    return value


def _validate_markdown_change(
    sync_module: Any,
    root: pathlib.Path,
    status: str,
    path: str,
    current: str | None,
    candidate: str,
) -> None:
    docs_root = root / "docs"
    normalized = sync_module.normalize_doc_path(path, docs_root)
    if normalized != path:
        raise SYNC.ValidationFailure(f"document path is not normalized: {path}")
    if status == "A":
        if current is not None:
            raise SYNC.ValidationFailure(f"added document already exists: {path}")
        sync_module.validate_new_frontmatter(candidate)
        _, body = sync_module.split_frontmatter(candidate)
    elif status == "M":
        if current is None:
            raise SYNC.ValidationFailure(f"modified document is missing: {path}")
        if candidate == current:
            raise SYNC.ValidationFailure(f"candidate document is unchanged: {path}")
        current_frontmatter, _ = sync_module.split_frontmatter(current)
        new_frontmatter, body = sync_module.split_frontmatter(candidate)
        if current_frontmatter != new_frontmatter:
            raise SYNC.ValidationFailure(
                f"existing frontmatter must be preserved byte-for-byte: {path}"
            )
    else:
        raise SYNC.ValidationFailure(f"unsupported document status {status}: {path}")
    sync_module.validate_markdown_body(body, path)
    if not body.strip():
        raise SYNC.ValidationFailure(f"document body must not be empty: {path}")


def _validate_state_transition(
    sync_module: Any,
    runner: SYNC.CappedRunner,
    root: pathlib.Path,
    base_sha: str,
    merge_sha: str,
    changed: Sequence[ChangedPath],
) -> None:
    prior_bytes = _read_git_file(runner, root, base_sha, sync_module.STATE_PATH)
    next_bytes = _read_git_file(runner, root, merge_sha, sync_module.STATE_PATH)
    prior = _load_state_bytes(sync_module, prior_bytes)
    next_state = _load_state_bytes(sync_module, next_bytes)
    sync_module._validate_next_state(next_state)
    cursor = next_state["cursor_commit"]
    if cursor == prior["cursor_commit"]:
        raise SYNC.ValidationFailure("candidate state did not advance the cursor")
    if next_state["initial_backfill"] != prior["initial_backfill"]:
        raise SYNC.ValidationFailure("candidate changed initial backfill metadata")
    last_sync = next_state.get("last_sync")
    if not isinstance(last_sync, dict):
        raise SYNC.ValidationFailure("candidate last_sync is malformed")
    sync_module._require_exact_keys(
        last_sync,
        {
            "range",
            "model",
            "usage",
            "summary",
            "outcome",
            "decisions",
            "files_changed",
            "recorded_at",
        },
        "candidate last_sync",
    )
    range_data = last_sync.get("range")
    if not isinstance(range_data, dict):
        raise SYNC.ValidationFailure("candidate last_sync range is malformed")
    if (
        range_data.get("base_exclusive") != prior["cursor_commit"]
        or range_data.get("head_inclusive") != cursor
        or not isinstance(range_data.get("commit_count"), int)
        or isinstance(range_data.get("commit_count"), bool)
        or not 1 <= range_data["commit_count"] <= 40
    ):
        raise SYNC.ValidationFailure("candidate state range is incoherent")

    docs = [
        change.path
        for change in changed
        if change.path.startswith("docs/") and change.path.endswith(".md")
    ]
    files_changed = last_sync.get("files_changed")
    if not isinstance(files_changed, list) or not all(
        isinstance(path, str) for path in files_changed
    ):
        raise SYNC.ValidationFailure("candidate files_changed is malformed")
    if len(docs) != len(set(docs)) or sorted(docs) != sorted(files_changed):
        raise SYNC.ValidationFailure(
            "candidate document diff does not match state files_changed"
        )

    decisions = last_sync.get("decisions")
    summary = last_sync.get("summary")
    if not isinstance(decisions, list) or not isinstance(summary, str):
        raise SYNC.ValidationFailure("candidate sync result is malformed")
    commit_shas = [
        decision.get("commit") if isinstance(decision, dict) else None
        for decision in decisions
    ]
    if not commit_shas or not all(
        isinstance(sha, str) and SYNC.SHA_RE.fullmatch(sha) for sha in commit_shas
    ):
        raise SYNC.ValidationFailure("candidate decision commits are malformed")
    if len(commit_shas) != len(set(commit_shas)):
        raise SYNC.ValidationFailure("candidate decision commits are not unique")
    if len(decisions) != range_data["commit_count"]:
        raise SYNC.ValidationFailure(
            "candidate decision count does not match the state range"
        )
    model = last_sync.get("model")
    usage = last_sync.get("usage")
    if not isinstance(model, str) or not model.strip() or len(model) > 100:
        raise SYNC.ValidationFailure("candidate model is malformed")
    if not isinstance(usage, dict) or not usage or not all(
        isinstance(key, str)
        and isinstance(value, int)
        and not isinstance(value, bool)
        for key, value in usage.items()
    ):
        raise SYNC.ValidationFailure("candidate usage is malformed")
    sync_module._validate_timestamp(
        last_sync.get("recorded_at"), "candidate recorded date"
    )
    docs_content = [
        _read_git_file(runner, root, merge_sha, path).decode("utf-8", "strict")
        for path in docs
    ]
    payload = {
        "summary": summary,
        "decisions": decisions,
        "files": [
            {"path": path, "content": content}
            for path, content in zip(docs, docs_content)
        ],
    }
    with tempfile.TemporaryDirectory(prefix="ai-docs-base-docs-") as directory:
        base_docs = _materialize_base_docs(
            sync_module,
            runner,
            root,
            base_sha,
            pathlib.Path(directory),
        )
        validated = sync_module.validate_sync_result(
            payload, commit_shas, base_docs, sync_module.Limits()
        )
    if [file.path for file in validated.files] != docs:
        raise SYNC.ValidationFailure("validated document set changed unexpectedly")
    expected_outcome = "update" if docs else "no-impact"
    if last_sync.get("outcome") != expected_outcome:
        raise SYNC.ValidationFailure("candidate outcome does not match its documents")

    history_changes = [
        change
        for change in changed
        if HISTORY_RE.fullmatch(change.path) is not None
    ]
    if len(history_changes) != 1 or history_changes[0].status != "A":
        raise SYNC.ValidationFailure(
            "candidate must add exactly one immutable history record"
        )
    history_path = history_changes[0].path
    if history_path != f"{sync_module.HISTORY_DIR}/{cursor}.json":
        raise SYNC.ValidationFailure("history filename does not match the new cursor")
    history_bytes = _read_git_file(runner, root, merge_sha, history_path)
    expected_history = sync_module._history_text(
        sync_module._history_record(prior, next_state)
    ).encode("utf-8")
    if history_bytes != expected_history:
        raise SYNC.ValidationFailure(
            "history record does not exactly describe the state transition"
        )

    feed_changes = [
        change
        for change in changed
        if change.path == sync_module.RECENT_CHANGES_PATH
    ]
    if feed_changes:
        if len(feed_changes) != 1 or feed_changes[0].status != "M":
            raise SYNC.ValidationFailure("recent changes feed change is invalid")
        feed = _json_bytes(
            _read_git_file(
                runner, root, merge_sha, sync_module.RECENT_CHANGES_PATH
            ),
            "recent changes feed",
        )
        sync_module.validate_recent_changes(feed)
        if feed.get("latest_analyzed_commit") != cursor:
            raise SYNC.ValidationFailure(
                "recent changes feed does not name the new cursor"
            )


def validate_candidate_diff(
    runner: SYNC.CappedRunner,
    root: pathlib.Path,
    *,
    base_sha: str,
    head_sha: str,
    merge_sha: str,
) -> Candidate:
    """Validate a fetched merge preview without checking out its tree."""

    merge_parents = _parents(runner, root, merge_sha)
    if merge_parents != (base_sha, head_sha):
        raise SYNC.ValidationFailure(
            "merge preview parents must be exactly the current base and PR head"
        )
    head_parents = _parents(runner, root, head_sha)
    if len(head_parents) != 1:
        raise SYNC.ValidationFailure("automation PR head must be one bot commit")
    _git(
        runner,
        root,
        ["merge-base", "--is-ancestor", head_parents[0], base_sha],
    )
    unique_commits = _git_text(
        runner, root, ["rev-list", "--count", f"{base_sha}..{head_sha}"]
    ).strip()
    if unique_commits != "1":
        raise SYNC.ValidationFailure(
            "automation PR must contain exactly one commit beyond current master"
        )
    if _commit_identity(runner, root, head_sha) != (
        SYNC.COMMIT_NAME,
        SYNC.COMMIT_EMAIL,
    ):
        raise SYNC.ValidationFailure(
            "automation PR head commit identity is not the sync bot"
        )
    parent_state = _read_git_file(
        runner, root, head_parents[0], SYNC.STATE_PATH
    )
    base_state = _read_git_file(runner, root, base_sha, SYNC.STATE_PATH)
    if parent_state != base_state:
        raise SYNC.ValidationFailure(
            "automation PR was generated from a different state; regenerate it"
        )

    raw = _git(
        runner,
        root,
        ["diff", "--raw", "-z", "--no-renames", base_sha, merge_sha, "--"],
    )
    changed = _parse_raw_diff(raw)
    if not changed:
        raise SYNC.ValidationFailure("automation PR has no candidate changes")
    allowed: list[ChangedPath] = []
    for change in changed:
        if change.status not in {"A", "M"}:
            raise SYNC.ValidationFailure(
                f"candidate delete, rename, or type change is forbidden: {change.path}"
            )
        if change.old_mode not in {"000000", "100644"} or change.new_mode != "100644":
            raise SYNC.ValidationFailure(
                f"candidate mode change or symlink is forbidden: {change.path}"
            )
        if change.path == SYNC.STATE_PATH:
            if change.status != "M":
                raise SYNC.ValidationFailure("state.json must be modified, not added")
            allowed.append(change)
            continue
        if change.path == SYNC.RECENT_CHANGES_PATH:
            allowed.append(change)
            continue
        if HISTORY_RE.fullmatch(change.path):
            allowed.append(change)
            continue
        if change.path.startswith("docs/") and change.path.endswith(".md"):
            current_bytes = (
                _read_git_file(runner, root, base_sha, change.path)
                if change.status == "M"
                else None
            )
            candidate_bytes = _read_git_file(runner, root, merge_sha, change.path)
            try:
                current = (
                    current_bytes.decode("utf-8", "strict")
                    if current_bytes is not None
                    else None
                )
                candidate = candidate_bytes.decode("utf-8", "strict")
            except UnicodeDecodeError as exc:
                raise SYNC.ValidationFailure(
                    f"candidate document is not UTF-8: {change.path}"
                ) from exc
            _validate_markdown_change(
                SYNC, root, change.status, change.path, current, candidate
            )
            allowed.append(change)
            continue
        raise SYNC.ValidationFailure(
            f"candidate path is outside the publication whitelist: {change.path}"
        )
    if not any(change.path == SYNC.STATE_PATH for change in allowed):
        raise SYNC.ValidationFailure("candidate did not modify state.json")
    _validate_state_transition(
        SYNC, runner, root, base_sha, merge_sha, allowed
    )
    return Candidate(0, base_sha, head_sha, merge_sha)


def validate_fetched_candidate(
    *,
    runner: SYNC.CappedRunner,
    root: pathlib.Path,
    token: str,
    number: int,
    current_master: str,
    pull: Mapping[str, Any],
) -> Candidate:
    metadata = validate_pull_metadata(pull, current_master)
    merge_sha = _fetch_candidate(
        runner, root, token, number, metadata.base_sha, metadata.head_sha
    )
    declared_merge = pull.get("merge_commit_sha")
    if declared_merge is not None and declared_merge != merge_sha:
        raise SYNC.ValidationFailure("pull request merge preview SHA changed")
    validated = validate_candidate_diff(
        runner,
        root,
        base_sha=metadata.base_sha,
        head_sha=metadata.head_sha,
        merge_sha=merge_sha,
    )
    return dataclasses.replace(validated, pr_number=number)


def _write_github_file(name: str, lines: Sequence[str]) -> None:
    path_value = os.environ.get(name)
    if not path_value:
        return
    path = pathlib.Path(path_value)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("".join(f"{line}\n" for line in lines))


def _summary(lines: Sequence[str]) -> None:
    _write_github_file("GITHUB_STEP_SUMMARY", ["## AI docs publication", "", *lines])


def _select_outputs(values: Mapping[str, str]) -> None:
    for key, value in values.items():
        if "\n" in value or "\r" in value:
            raise SYNC.ValidationFailure(f"invalid GitHub output {key}")
    _write_github_file("GITHUB_OUTPUT", [f"{key}={value}" for key, value in values.items()])


def select_phase(
    *, root: pathlib.Path, work_dir: pathlib.Path, github: PublishGitHubClient
) -> Candidate | None:
    status_path = work_dir / "status.json"
    status = SYNC.read_json(status_path)
    if not isinstance(status, dict) or status.get("status") not in {
        "ready",
        "pending",
        "no-change",
    }:
        raise SYNC.ValidationFailure("sync status is not a known publication state")
    if status["status"] == "no-change":
        _select_outputs({"publish": "false", "pr_number": "0"})
        _summary(["No pending candidate; source cursor is current."])
        return None

    current_master = github.branch_sha(SYNC.TARGET_REPOSITORY, SYNC.TARGET_BRANCH)
    if current_master is None:
        raise SYNC.ApiFailure("target master branch is missing")
    pulls = github.open_automation_pulls()
    if not pulls:
        _select_outputs({"publish": "false", "pr_number": "0"})
        _summary(["No open automation pull request; nothing was validated or published."])
        return None
    if len(pulls) != 1:
        raise SYNC.ValidationFailure(
            "expected at most one open automation pull request"
        )
    pull = pulls[0]
    number = _require_number(pull.get("number"), "pull request number")
    try:
        candidate = validate_fetched_candidate(
            runner=SYNC.CappedRunner(),
            root=root,
            token=github.token,
            number=number,
            current_master=current_master,
            pull=pull,
        )
    except SYNC.ActionRequired:
        raise
    except SYNC.SyncFailure:
        raise
    latest_master = github.branch_sha(SYNC.TARGET_REPOSITORY, SYNC.TARGET_BRANCH)
    latest_pull = github.pull(number)
    latest_metadata = validate_pull_metadata(latest_pull, latest_master or "")
    if (
        latest_master != candidate.base_sha
        or latest_metadata.head_sha != candidate.head_sha
        or latest_metadata.base_sha != candidate.base_sha
        or (
            latest_metadata.merge_sha
            and latest_metadata.merge_sha != candidate.merge_sha
        )
    ):
        raise SYNC.ValidationFailure(
            "pull request head, target branch, or merge preview changed during validation"
        )
    _select_outputs(candidate.as_outputs())
    _summary(
        [
            f"Candidate PR: #{candidate.pr_number}",
            f"Base: `{candidate.base_sha}`",
            f"Head: `{candidate.head_sha}`",
            f"Merge preview: `{candidate.merge_sha}`",
            "The exact preview diff and state transition passed trusted validation.",
        ]
    )
    LOG.info(
        "selected pull request #%s (%s) for bounded validation",
        candidate.pr_number,
        candidate.merge_sha,
    )
    return candidate


def _canonical_policy_body(body: str) -> str:
    if POLICY_OLD in body:
        return body.replace(POLICY_OLD, POLICY_NEW)
    return body


def merge_phase(
    *,
    root: pathlib.Path,
    github: PublishGitHubClient,
    expected: Candidate,
) -> int:
    runner = SYNC.CappedRunner()
    current_master = github.branch_sha(SYNC.TARGET_REPOSITORY, SYNC.TARGET_BRANCH)
    if current_master is None:
        raise SYNC.ApiFailure("target master branch is missing")
    pull = github.pull(expected.pr_number)
    metadata = validate_pull_metadata(pull, current_master)
    if metadata.base_sha != expected.base_sha:
        raise SYNC.ValidationFailure("target master changed since candidate selection")
    if metadata.head_sha != expected.head_sha:
        raise SYNC.ValidationFailure("pull request head changed since candidate selection")
    if pull.get("mergeable") is not True:
        raise SYNC.ValidationFailure("pull request is not currently mergeable")

    refreshed = validate_fetched_candidate(
        runner=runner,
        root=root,
        token=github.token,
        number=expected.pr_number,
        current_master=current_master,
        pull=pull,
    )
    if refreshed != expected:
        raise SYNC.ValidationFailure(
            "pull request membership or merge preview changed since validation"
        )
    body = pull.get("body")
    if not isinstance(body, str):
        raise SYNC.ValidationFailure("pull request body is malformed")
    canonical = _canonical_policy_body(body)
    if canonical != body:
        github.update_pull_body(expected.pr_number, canonical)

    response = github.merge_pull(expected.pr_number, expected.head_sha)
    merged_sha = response.get("sha")
    if response.get("merged") is not True:
        raise SYNC.ApiFailure("GitHub did not confirm the pull request merge")
    merged_sha = _require_sha(merged_sha, "merged commit")
    current_after = github.branch_sha(SYNC.TARGET_REPOSITORY, SYNC.TARGET_BRANCH)
    if current_after != merged_sha:
        raise SYNC.ApiFailure(
            "target master no longer equals the merge result; refusing to dispatch"
        )
    fetched_master = _fetch_master(runner, root, github.token)
    if fetched_master != merged_sha:
        raise SYNC.ApiFailure("fetched target master does not equal the merge result")
    if _parents(runner, root, merged_sha) != (expected.base_sha, expected.head_sha):
        raise SYNC.ApiFailure("merged commit parents do not match the validated preview")
    if _tree_sha(runner, root, expected.merge_sha) != _tree_sha(
        runner, root, merged_sha
    ):
        raise SYNC.ApiFailure(
            "merged commit tree does not match the validated merge preview"
        )

    failures: list[str] = []
    for workflow in ("deploy.yml", "ai-docs-sync.yml"):
        try:
            github.dispatch(workflow)
            LOG.info("dispatched %s on master after merging %s", workflow, merged_sha)
        except SYNC.SyncFailure as exc:
            failures.append(f"{workflow}: {exc}")
    if failures:
        raise DispatchFailure(merged_sha, tuple(failures))
    _summary(
        [
            f"Merged PR #{expected.pr_number}",
            f"Merge commit: `{merged_sha}`",
            "Dispatched `deploy.yml` and `ai-docs-sync.yml` on `master`.",
        ]
    )
    return 0


def recover_phase(*, root: pathlib.Path, github: PublishGitHubClient) -> int:
    """Retry a missing deployment for the current master commit only."""

    current_master = github.branch_sha(SYNC.TARGET_REPOSITORY, SYNC.TARGET_BRANCH)
    if current_master is None:
        raise SYNC.ApiFailure("target master branch is missing")
    runs = github.workflow_runs("deploy.yml")
    matching = [
        run
        for run in runs
        if run.get("head_sha") == current_master and run.get("event") != "pull_request"
    ]
    if any(
        run.get("status") in {"queued", "in_progress", "requested", "waiting"}
        or run.get("conclusion") == "success"
        for run in matching
    ):
        LOG.info("deploy run already exists for %s", current_master)
        return 0
    github.dispatch("deploy.yml")
    LOG.info("retried deploy dispatch for already-merged master %s", current_master)
    _summary(
        [
            f"Retried `deploy.yml` for `{current_master}`.",
            "No documentation pull request was merged by recovery.",
        ]
    )
    return 0


def public_candidate(*, expected: Candidate) -> Candidate:
    return Candidate(
        _require_number(expected.pr_number, "pull request number"),
        _require_sha(expected.base_sha, "validated base"),
        _require_sha(expected.head_sha, "validated head"),
        _require_sha(expected.merge_sha, "validated merge preview"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    select = subparsers.add_parser("select")
    select.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    select.add_argument(
        "--work-dir",
        type=pathlib.Path,
        default=pathlib.Path(
            os.environ.get("AI_DOCS_WORK_DIR")
            or pathlib.Path(tempfile.gettempdir()) / "ai-docs-sync"
        ),
    )
    merge = subparsers.add_parser("merge")
    merge.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    merge.add_argument("--pr-number", type=int, required=True)
    merge.add_argument("--base-sha", required=True)
    merge.add_argument("--head-sha", required=True)
    merge.add_argument("--merge-sha", required=True)
    recover = subparsers.add_parser("recover")
    recover.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    root = args.root.resolve(strict=True)
    repository = os.environ.get("GITHUB_REPOSITORY")
    try:
        if repository != SYNC.TARGET_REPOSITORY:
            raise SYNC.ActionRequired(
                f"workflow is running for {repository!r}, expected "
                f"{SYNC.TARGET_REPOSITORY!r}"
            )
        github = _client()
        if args.command == "select":
            select_phase(root=root, work_dir=args.work_dir, github=github)
            return 0
        if args.command == "merge":
            candidate = public_candidate(
                expected=Candidate(
                    args.pr_number, args.base_sha, args.head_sha, args.merge_sha
                )
            )
            return merge_phase(root=root, github=github, expected=candidate)
        if args.command == "recover":
            return recover_phase(root=root, github=github)
        raise AssertionError("unreachable command")
    except DispatchFailure as exc:
        _summary([f"Recovery required after merge `{exc.merged_sha}`."])
        LOG.error("MERGE RECOVERY REQUIRED: %s", exc)
        return 1
    except SYNC.ActionRequired as exc:
        LOG.error("ACTION REQUIRED: %s", exc)
        return 2
    except (SYNC.SyncFailure, OSError) as exc:
        LOG.error("publication refused: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
