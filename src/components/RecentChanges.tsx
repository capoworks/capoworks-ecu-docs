import Link from '@docusaurus/Link';
import type { ReactNode } from 'react';
import recentChanges from '../../.ai-docs/recent-changes.json';

type RecentChangesProps = {
  variant?: 'home' | 'full';
};

type ChangeEntry = {
  commit: string;
  subject: string;
  authored_at: string;
  parents: string[];
  comment: string;
  decision: 'update' | 'no-impact';
  model: string;
  analyzed_at: string;
  integration_batch_commit: string;
};

type RecentChangesFeed = {
  latest_analyzed_commit: string;
  latest_analyzed_at: string;
  entries: ChangeEntry[];
};

type GuideLink = {
  to: string;
  label: string;
  friendlyTitle?: string;
};

const SHA_PATTERN = /^[0-9a-f]{40}$/;
const CONVENTIONAL_COMMIT_PREFIX = /^[a-z][a-z0-9-]*(?:\([^)]*\))?!?:\s+/i;
const SOURCE_REPOSITORY = 'capoworks/capoworks-ecu';
const SOURCE_URL = `https://github.com/${SOURCE_REPOSITORY}`;
const feed = recentChanges as RecentChangesFeed;

const GUIDE_LINKS: Record<string, GuideLink> = {
  '8f4fcfb40135fe7e5f15b280f7e05d9863b60f52': {
    to: '/Fuel/Fuel-Settings/VE-Analyze/',
    label: 'VE Analyze guide',
    friendlyTitle: 'Strategy-specific VE Analyze filters',
  },
  '223895c17f82f9fd07bac9e81414661440ac7475': {
    to: '/Fuel/Fuel-Algorithms/Airmass-Models-and-Migration/',
    label: 'Air-mass models and migration',
    friendlyTitle: 'Separate per-cylinder fuel trims',
  },
  eee63c82b531db9bc6fa640c58ad76cf740a2ff0: {
    to: '/Fuel/Fuel-Algorithms/Blended/',
    label: 'SD + Alpha-N blend guide',
    friendlyTitle: 'Independent SD and Alpha-N tuning with air-mass blending',
  },
  '45298b9020a52059c278d3d0ba16bae89b7e6a7f': {
    to: '/Fuel/Fuel-Settings/Load-Sources/',
    label: 'Load sources guide',
    friendlyTitle: 'Independent load sources',
  },
  ea47b68b374a863051e7f0ef62a068a068b138d7: {
    to: '/Ignition/Ignition-Settings/Experimental-Timing/',
    label: 'Experimental ignition timing',
    friendlyTitle: 'Experimental time-budget ignition timing',
  },
  '69f7973f5da52a1d5e6b37a848cc7a88205ac01f': {
    to: '/Ignition/Ignition-Settings/Experimental-Timing/',
    label: 'Experimental ignition timing',
    friendlyTitle: 'Experimental cycle-profile ignition timing',
  },
  '09886f0b28a6e7544becb1fd2221da5527a1e673': {
    to: '/Basic-Features/Idle-Control/Advanced-Idle/',
    label: 'Advanced idle control',
    friendlyTitle: 'Smoother optional idle feedback',
  },
  fef0a82ef6899b7b09c77ad0c9dd4f8996fe1733: {
    to: '/Fuel/Fuel-Algorithms/Airmass-Models-and-Migration/',
    label: 'Air-mass models and migration',
    friendlyTitle: 'Separated air-mass calibration and atomic fuel publication',
  },
  '034ec75bc1e9bf7391eeb0050b13038c0f60e3d7': {
    to: '/Software/Core8-Build-Tools/',
    label: 'Core8 build tools',
    friendlyTitle: 'Portable Core8 build tools',
  },
};

function shortSha(sha: string): string {
  return SHA_PATTERN.test(sha) ? sha.slice(0, 10) : 'invalid SHA';
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) {
    return 'unknown date';
  }
  return new Intl.DateTimeFormat('en', {
    dateStyle: 'medium',
    timeZone: 'UTC',
  }).format(date);
}

function commitLink(sha: string): ReactNode {
  if (!SHA_PATTERN.test(sha)) {
    return <code>{shortSha(sha)}</code>;
  }
  return (
    <a href={`${SOURCE_URL}/commit/${sha}`} rel="noreferrer">
      <code>{shortSha(sha)}</code>
    </a>
  );
}

function entryTitle(entry: ChangeEntry): string {
  const guideTitle = GUIDE_LINKS[entry.commit]?.friendlyTitle;
  if (guideTitle) {
    return guideTitle;
  }

  return entry.subject.replace(CONVENTIONAL_COMMIT_PREFIX, '').trim() || entry.subject;
}

function EntryMeta({ entry }: { entry: ChangeEntry }): ReactNode {
  const guide = GUIDE_LINKS[entry.commit];
  const isIntegrationMerge = entry.parents.length > 1;
  let badgeLabel = 'Maintenance';
  if (entry.decision === 'update') {
    badgeLabel = 'User-facing change';
  } else if (isIntegrationMerge) {
    badgeLabel = 'Integration audit';
  }

  return (
    <div className="capoRecent__entryMeta">
      <span className={`capoRecent__badge capoRecent__badge--${entry.decision}`}>{badgeLabel}</span>
      <span>
        {commitLink(entry.commit)} · {formatDate(entry.authored_at)}
      </span>
      {isIntegrationMerge && entry.decision === 'update' ? (
        <span className="capoRecent__mergeIndicator">Merge · user impact</span>
      ) : null}
      {guide ? (
        <Link className="capoRecent__guideLink" to={guide.to}>
          {guide.label}
        </Link>
      ) : null}
      <span className="capoRecent__sourceSubject">Source: {entry.subject}</span>
    </div>
  );
}

function EntryBody({ entry }: { entry: ChangeEntry }): ReactNode {
  return (
    <>
      <h3>{entryTitle(entry)}</h3>
      <p>{entry.comment}</p>
    </>
  );
}

function EntryCard({
  entry,
  secondary = false,
}: {
  entry: ChangeEntry;
  secondary?: boolean;
}): ReactNode {
  return (
    <article
      className={`capoRecent__entry ${
        secondary ? 'capoRecent__entry--secondary' : 'capoRecent__entry--feature'
      }`}
    >
      <EntryBody entry={entry} />
      <EntryMeta entry={entry} />
    </article>
  );
}

export default function RecentChanges({ variant = 'full' }: RecentChangesProps): ReactNode {
  const isHome = variant === 'home';
  const visibleEntries = feed.entries.filter((entry) => SHA_PATTERN.test(entry.commit));
  const userImpactEntries = visibleEntries.filter((entry) => entry.decision === 'update');
  const secondaryEntries = visibleEntries.filter((entry) => entry.decision === 'no-impact');
  const primaryEntries = isHome ? userImpactEntries.slice(0, 3) : userImpactEntries;
  const mergeCount = feed.entries.filter((entry) => entry.parents.length > 1).length;
  const nonMergeCount = feed.entries.length - mergeCount;
  const headingId = `recent-changes-${variant}`;

  return (
    <section className={`capoRecent capoRecent--${variant}`} aria-labelledby={headingId}>
      <header className="capoRecent__header">
        <div>
          <p className="capoRecent__eyebrow">Firmware development log</p>
          <h2 id={headingId}>{isHome ? 'Recent changes' : 'Firmware recent changes'}</h2>
        </div>
        <span className="capoRecent__aiBadge">AI-generated · reviewed</span>
      </header>

      <p className="capoRecent__intro">
        {isHome
          ? 'The latest ECU functions and user-facing changes, with practical setup notes and limits.'
          : 'New ECU functions and user-facing behavior first, followed by maintenance and integration audits.'}
      </p>

      <p className="capoRecent__sectionLabel">New functions & user impact</p>

      <div className="capoRecent__list capoRecent__list--primary">
        {primaryEntries.length > 0 ? (
          primaryEntries.map((entry) => <EntryCard entry={entry} key={entry.commit} />)
        ) : (
          <p className="capoRecent__notice">No new user-facing changes in this range.</p>
        )}
      </div>

      {isHome ? (
        <Link className="capoRecent__archiveLink" to="/recent-changes/">
          View all {feed.entries.length} analyzed changes
        </Link>
      ) : null}

      {!isHome && secondaryEntries.length > 0 ? (
        <details className="capoRecent__secondary">
          <summary>
            <span>
              <span className="capoRecent__secondaryLabel">Secondary change log</span>
              <span className="capoRecent__secondaryTitle">Maintenance and integration audits</span>
            </span>
            <span className="capoRecent__secondaryCount">
              {secondaryEntries.length} entries with no user-facing change
            </span>
          </summary>
          <div className="capoRecent__secondaryBody">
            <div className="capoRecent__list">
              {secondaryEntries.map((entry) => (
                <EntryCard entry={entry} key={entry.commit} secondary />
              ))}
            </div>
          </div>
        </details>
      ) : null}

      <details className="capoRecent__sourceCoverage">
        <summary>Source coverage and analyzed head</summary>
        <dl className="capoRecent__coverage">
          <div>
            <dt>Coverage</dt>
            <dd>
              {feed.entries.length} commits · {nonMergeCount} changes · {mergeCount} merge audits
            </dd>
          </div>
          <div>
            <dt>Analyzed head</dt>
            <dd>
              {commitLink(feed.latest_analyzed_commit)} ·{' '}
              <time dateTime={feed.latest_analyzed_at}>{formatDate(feed.latest_analyzed_at)}</time>
            </dd>
          </div>
        </dl>
      </details>

      <footer className="capoRecent__footer">
        <div className="capoRecent__links">
          <a href={SOURCE_URL} rel="noreferrer">
            Firmware source
          </a>
          <a href={`${SOURCE_URL}/commits/${feed.latest_analyzed_commit}`} rel="noreferrer">
            Full change history on GitHub
          </a>
          <Link to="/">Back to documentation home</Link>
        </div>
        <p>
          AI-generated summaries are reviewed before publication. This log is not a firmware release
          approval and does not certify that a build, configuration or hardware setup has been
          validated.
        </p>
      </footer>
    </section>
  );
}
