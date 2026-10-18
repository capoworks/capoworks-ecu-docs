# AI firmware documentation sync

This directory contains the merged cursor state and operating notes for
`.github/workflows/ai-docs-sync.yml`. The sync reads public history from
`capoworks/capoworks-ecu` and proposes Markdown changes in this repository
(`capoworks/capoworks-ecu-docs`) on the fixed
`automation/firmware-docs` branch.

## Required setup

1. Add the Actions repository secret `DEEPSEEK_API_KEY` under **Settings >
   Secrets and variables > Actions**. Do not put the key in a file, variable,
   command-line option, log, or pull request.
2. Optionally add the repository variable `AI_DOCS_MODEL`. It defaults to
   `deepseek-flash`. The currently supported API choices are
   `deepseek-flash` and `deepseek-v4-pro`. The optional bounded variables
   `AI_DOCS_MAX_TOKENS`, `AI_DOCS_TIMEOUT_SECONDS`, `AI_DOCS_RETRIES`,
   `AI_DOCS_MAX_CURRENT_FILES`, `AI_DOCS_MAX_WIKI_DOCS`, and
   `AI_DOCS_MAX_OUTPUT_FILES` can only reduce or select within hard-coded
   workflow limits.
3. Under **Settings > Actions > General**, allow GitHub Actions to create pull
   requests. If organization policy restricts the default token, explicitly
   allow the `contents: write`, `pull-requests: write`, and `actions: write`
   permissions requested by the sync job. The unit-test job remains read-only.
4. Protect `master` and decide whether the automation branch needs review. The
   workflow never merges its pull request.

The workflow runs every six hours, supports manual `workflow_dispatch`, and
accepts the public `firmware-updated` `repository_dispatch` event from the
firmware repository.

## Initial history and normal operation

The initial merged state starts at source commit
`6b31ebaec865d7ea856b20a3211c7a0310e29ef2`. Its first sync backfills the five
fork commits through `be02e3cdaa2c177d05853a41af6dacc9c0766b77`. Until that
initial backfill is marked complete, the existing whole-range backfill behavior
is retained, including the 40-commit limit and validation of the configured
fifth commit.

After the initial backfill, each documentation pull request covers one
first-parent integration event. A run first resolves and records immutable
source head `H`, verifies that the source clone is exactly `H`, and lists
`cursor..H` in first-parent reverse order. It selects the earliest candidate
`B` for which the merged cursor is an ancestor of `B`, and proves that `B` is an
ancestor of `H`. Remaining commits through `H` stay deferred to later, separate
pull requests.

The complete revision list `cursor..B` is then recomputed without taking a
topological prefix, so every child and merge commit in that integration event
receives exactly one decision. The 40-commit limit applies to this chosen range,
not to the remaining first-parent backlog. Tree and source-file reads use `B`;
they never use `H`, even though the cloned source branch must still equal `H`.
The prepared context and PR body distinguish the `B` range head from observed
`H`, and the merged state advances the cursor only to `B`.

For a merge, changed paths include the first-parent delta plus paths changed by
combined conflict resolution. The merge patch uses a combined diff and records
its parents explicitly. Constituent commits are audited separately. A clean
merge has no additional impact beyond those children; conflict resolutions are
described only when they have their own user-facing effect.

The sync gathers every full commit diff plus bounded, deterministically selected
current source files and relevant source/target wiki documents. Inline files
named `hella_opst.md` and `tunerstudio-protection.md` receive retrieval
priority. Current source files are hard-capped at 300,000 bytes each and
700,000 bytes in aggregate, while the prepared context and serialized model
prompt are hard-capped at 1,500,000 bytes. Oversize, truncated, or partially
decoded source material fails the run; it is never silently clipped. If one
chosen integration event contains more than 40 commits, the run stops with
Action Required, names the exact event SHA `B`, and requires a manually reviewed
pull request for that event. It does not advance the cursor or skip the event.

If source `master` already equals the merged cursor, the run exits before an API
call. If there are commits but no user-facing impact, the bot still opens a
state-only pull request containing every per-commit no-impact decision. This
audit trail and cursor become authoritative only after a human merges the PR.
Opening a PR does not advance the checked-in cursor because `master` does not
contain the bot change yet.

## Pull-request lifecycle

- An open `automation/firmware-docs` PR causes later runs to skip as pending.
  Once it is merged, the next run catches up from the updated master cursor.
- A closed, unmerged bot PR stops the workflow for an explicit human decision.
  It is not treated as an opening to replace the branch.
- A bot branch with no recognizable PR history, or with commits newer than its
  last merged PR, is unknown work and also stops for inspection.
- If the last bot PR merged and the branch is gone, the next run safely recreates
  the fixed branch and rescans from the merged master cursor.
- A force-push to the bot branch is prevented with `--force-with-lease`; a
  concurrent or human update makes the push fail instead of being overwritten.

The fixed commits use identity `ai-docs-sync[bot]`. The checkout does not persist
credentials. Both prepare and finalize receive the same job-scoped `GITHUB_TOKEN`
with `contents`, pull-request, and Actions write permissions; prepare uses it only
for read-only API operations, while finalize writes and opens the pull request.
Generation receives only `DEEPSEEK_API_KEY` and no `GITHUB_TOKEN`; separate build
workflows have `contents: read` and no model secret.

## Validation and trust boundary

Source commits, diffs, source files, and wiki documents are untrusted data. The
model is instructed not to follow instructions embedded in them. No firmware
source, generated MDX, npm command, or build is executed in a step that has the
model key or write token.

The model must return a strict JSON object with a summary, exactly one decision
for every source commit in order, evidence for every decision, and complete file
replacements. All output is validated before any file is written:

- only normalized `docs/**/*.md` paths;
- no absolute paths, traversal, backslashes, deletion, symlinks, or
  case-insensitive duplicates;
- complete replacement content within file/count/byte limits;
- byte-for-byte preservation of existing frontmatter;
- only safely scalar allowlisted frontmatter on new files;
- safe Markdown with no executable imports, exports, JSX, HTML, MDX expressions,
  or dangerous link schemes outside fenced code blocks.

The PR stores the source range, actual response model, actual token usage, and
all per-commit evidence in `.ai-docs/state.json` and the PR body. Invalid or
oversize output rejects the complete change set before writes.

Finalization also writes an immutable batch audit at
`.ai-docs/history/<batch-head>.json`. It retains the complete previous
`last_sync`, including the initial backfill now present in state, together with
the new batch audit and cursor transition. An existing equal history file is
reused without rewriting it. An existing file with different bytes stops the
run for inspection; history files are append-only.

Model requests use JSON mode, an explicit bounded `max_tokens` value, and
`thinking: {"type": "disabled"}` so the structured result is not consumed by
the API's default thinking mode.

## Preview dispatch limitation

GitHub can suppress or require manual approval of pull-request workflow runs
triggered by a PR opened with `GITHUB_TOKEN`, so do not rely on them starting
automatically. After opening the PR, the workflow explicitly dispatches
`build-preview.yml` on `master` with the exact bot commit SHA in an input named
`ref`. The read-only preview workflow must honor that manual `ref`. This
supplemental dispatch does not create, attach, or satisfy required pull-request
status checks; approving PR checks is a separate action. Branch protection must
not assume otherwise.

The integrated preview workflow validates that `inputs.ref` is a full commit
SHA and checks out that exact revision. If PR creation succeeds but the
supplemental dispatch fails, the workflow exits with an Action Required error
containing the PR URL and exact recovery command. The PR, bot branch, and
prepared source range remain intact. Retry the preview manually with the SHA
from that error:

```bash
gh workflow run build-preview.yml --repo capoworks/capoworks-ecu-docs \
  -f ref=<40-character-bot-commit-sha>
```

A later scheduled run sees the open PR and skips as pending; it does not try to
infer dispatch completion from a workflow run's `head_sha`, because a manual
dispatch runs from `master` while the build checks out the SHA supplied in
`inputs.ref`.

Do not repair a stopped lifecycle with a blind branch deletion or cursor edit.
Inspect the PR and branch, preserve any human work, and only then choose an
explicit recovery path.
