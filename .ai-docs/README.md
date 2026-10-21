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
   permissions requested by the sync and merge jobs. Unit-test and publication
   validation jobs remain read-only.
4. Protect `master` as required. The workflow may merge its own pull request
   after a separate read-only validation job and an exact merge-preview check
   succeed. It uses the normal GitHub merge API and never bypasses branch
   protection.

The workflow polls every 15 minutes, supports manual `workflow_dispatch`, and
accepts the public `firmware-updated` `repository_dispatch` event from the
firmware repository. GitHub may delay scheduled workflows, so the schedule is
a reliable catch-up path rather than a real-time trigger. A push to `master`
that changes `.ai-docs/state.json` also starts a catch-up run, which covers
manually merged documentation PRs.

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
priority. The largest measured modularity range, 35 commits, has 782,933 diff
bytes, 186 current source files totaling 1,716,653 bytes, and an exact
serialized prompt of 3,019,518 bytes. The defaults accommodate it with explicit
limits of 40 commits, 800,000 diff bytes, 200 current files totaling 2,000,000
bytes, a 300,000-byte per-file cap, and a 3,500,000-byte serialized prompt. These
bounds are finite rather than unlimited. Oversize, truncated, or partially
decoded source material fails the run; it is never silently clipped.

If the chosen integration event exceeds a preparation safety limit, including
its commit count, diff or file caps, current-payload or wiki caps, or the exact
serialized prompt size, the run stops with Action Required. The message names
the exact event SHA `B` and the original limit violation, and requires a
manually reviewed pull request for that event. A divergent branch still needs a
complete single-event audit; the sync does not automatically create checkpoint
subdivisions. It does not advance the cursor or skip the event. During the
initial backfill, limit failures retain their normal fail-closed behavior
instead of this integration-event recovery message.

After an otherwise successful model response fails strict result validation,
the generate phase makes at most one repair request. That request includes the
original evidence plus the rejected result and validation error as explicitly
untrusted metadata. The repair prompt has the same serialized-size cap, and its
complete replacement result must pass the unchanged validator. Usage is summed
across both calls for audit; if the repair also fails, no generation result,
cursor advance, or pull request is produced. API failures and limit violations
are not repaired. When the rejected result contains too many evidence entries,
the trusted repair instruction tells the model to select the best specific
entries within the active evidence limit rather than repeat the oversized
array. Rejected model content remains complete untrusted metadata; it is not
truncated or sanitized.

If source `master` already equals the merged cursor, the run exits without an AI
request. If there are commits but no user-facing impact, the bot still opens a
state-only pull request containing every per-commit no-impact decision. Opening
a PR does not advance the checked-in cursor; the publication merge does.

## Pull-request lifecycle

- An open `automation/firmware-docs` PR causes preparation to skip as pending.
  The publication selector resumes that existing PR instead of asking the
  model to regenerate it.
- The selector accepts only an open, non-draft PR opened by
  `github-actions[bot]`, carrying the sync marker, with the exact target
  repository, automation head branch, `master` base, and sync-bot head commit.
  A foreign repository, human PR, extra commit, changed head, or changed base
  is refused.
- The exact `refs/pull/<number>/merge` tree is fetched and validated against
  current `master`. The diff may change only `docs/**/*.md`,
  `.ai-docs/state.json`, exactly one new
  `.ai-docs/history/<new-cursor>.json`, and optionally
  `.ai-docs/recent-changes.json`. Deletes, renames, symlinks, executable-mode
  changes, configuration, scripts, workflows, dependencies, and credentials
  are outside the whitelist.
- A separate read-only job checks out the selected merge-preview SHA without
  persisted credentials and runs `npm ci`, the complete lint suite, all stdlib
  documentation tests, and the production build. It has no model secret and
  no write token. Pull-request checks created by `GITHUB_TOKEN` are not trusted
  as this gate because GitHub may leave them awaiting approval or expire them.
- A merge job requeries the PR and `master`, rejects any head, base, membership,
  or preview change, and calls the normal REST merge API with the expected head
  SHA. The merge commit must have exactly the validated base and head as its
  parents. The job does not use auto-merge or administrator bypass.
- After a successful merge, the job explicitly dispatches `deploy.yml` and
  `ai-docs-sync.yml` on `master`, because a merge made with `GITHUB_TOKEN` may
  suppress the corresponding `push` workflows. The documentation workflow
  handles one integration event per run, so repeated catch-up dispatches make
  bounded progress without creating a large combined PR.
- If deploy dispatch still fails after the merge, the run records the merged
  SHA and failed workflow in its job summary. Later runs check for a deploy run
  on current `master` and retry the missing dispatch without merging again.
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
Generation receives only `DEEPSEEK_API_KEY` and no `GITHUB_TOKEN`; the
publication validation job has `contents: read` and no model secret; and the
merge job has a write token but no model secret.

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

Every initial and repair system prompt includes a trusted quantitative contract
generated from the active run limits. It states that decisions must cover
exactly the listed commits; each decision must contain between one and the
active evidence maximum (eight by default); summary is limited to 4,000
characters; each rationale and evidence item is limited to the active
decision-text maximum (4,000 by default); and file count and UTF-8 byte totals
must fit the active output limits. The defaults allow 50 files, 256,000 UTF-8
bytes per file, and 750,000 UTF-8 bytes in total. `AI_DOCS_MAX_OUTPUT_FILES`
therefore changes both the validator and the contract given to the model.
Preparation and client dispatch serialize the same contract when enforcing the
exact prompt-byte cap.

The PR stores the source range, actual response model, actual token usage, and
all per-commit evidence in `.ai-docs/state.json` and the PR body. Invalid or
oversize output rejects the complete change set before writes.

Finalization also writes an immutable batch audit at
`.ai-docs/history/<batch-head>.json`. It retains the complete previous
`last_sync`, including the initial backfill now present in state, together with
the new batch audit and cursor transition. An existing equal history file is
reused without rewriting it. An existing file with different bytes stops the
run for inspection; history files are append-only.

Finalization also updates the bounded `.ai-docs/recent-changes.json` feed in
the same atomic write set, Git staging, and bot commit. The feed is fixed to
`capoworks/capoworks-ecu`, records the latest analyzed source head, and retains
at most 60 unique commits in newest-integration-first order. Each entry contains
source metadata, the reader-facing AI rationale, its update/no-impact decision,
the actual response model, and analysis time. No-impact and state-only batches
therefore publish an audit entry even when no Markdown guide changes. Existing
feed metadata is strictly validated before any cursor write; an already-seeded
integration batch is left byte-identical so a bootstrap can cover source commits
beyond the automatic cursor without replaying or advancing that cursor.

The homepage and `/recent-changes/` page render this committed JSON statically
through `src/components/RecentChanges.tsx`; there is no browser fetch. React
renders source subjects and AI comments as text, and commit links are built only
from validated full SHAs. The homepage root document and the Recent changes page
are MDX because they import this trusted component. The sync writer remains
limited to `.md` files and rejects new Markdown paths that would collide with an
existing MDX sibling, so future AI documentation proposals cannot replace the
component-backed pages.

Model requests use JSON mode, an explicit bounded `max_tokens` value, and
`thinking: {"type": "disabled"}` so the structured result is not consumed by
the API's default thinking mode.

## Preview checks

GitHub can suppress or require manual approval of pull-request workflow runs
triggered by a PR opened with `GITHUB_TOKEN`. Publication therefore uses the
dedicated read-only validation job described above as its authoritative gate.
The exact merge-preview SHA from that job is what gets linted, tested, and
built; stale jobs or checks from another SHA are never accepted.

After opening a PR, the existing sync workflow still requests a supplemental
`build-preview.yml` dispatch for the exact bot commit. That supplemental run
and its annotated PR checks are not a substitute for the publication
validation job. The preview workflow now runs the same lint suite as well as
the build for manual diagnostics.

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

A later scheduled run sees the open PR and resumes publication validation; it
does not infer validity from an old preview run's `head_sha`, because a manual
dispatch runs from `master` while the build checks out the SHA supplied in
`inputs.ref`.

Do not repair a stopped lifecycle with a blind branch deletion or cursor edit.
Inspect the PR and branch, preserve any human work, and only then choose an
explicit recovery path.
