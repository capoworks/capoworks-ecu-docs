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

const SHA_PATTERN = /^[0-9a-f]{40}$/;
const SOURCE_REPOSITORY = 'capoworks/capoworks-ecu';
const SOURCE_URL = `https://github.com/${SOURCE_REPOSITORY}`;
const feed = recentChanges as RecentChangesFeed;

const GUIDE_LINKS: Record<string, { to: string; label: string }> = {
  '8f4fcfb40135fe7e5f15b280f7e05d9863b60f52': {
    to: '/Fuel/Fuel-Settings/VE-Analyze/',
    label: 'VE Analyze guide',
  },
  '223895c17f82f9fd07bac9e81414661440ac7475': {
    to: '/Fuel/Fuel-Algorithms/Airmass-Models-and-Migration/',
    label: 'Air-mass models and migration',
  },
  eee63c82b531db9bc6fa640c58ad76cf740a2ff0: {
    to: '/Fuel/Fuel-Algorithms/Blended/',
    label: 'SD + Alpha-N blend guide',
  },
  '45298b9020a52059c278d3d0ba16bae89b7e6a7f': {
    to: '/Fuel/Fuel-Settings/Load-Sources/',
    label: 'Load sources guide',
  },
  ea47b68b374a863051e7f0ef62a068a068b138d7: {
    to: '/Ignition/Ignition-Settings/Experimental-Timing/',
    label: 'Experimental ignition timing',
  },
  '69f7973f5da52a1d5e6b37a848cc7a88205ac01f': {
    to: '/Ignition/Ignition-Settings/Experimental-Timing/',
    label: 'Experimental ignition timing',
  },
  '09886f0b28a6e7544becb1fd2221da5527a1e673': {
    to: '/Basic-Features/Idle-Control/Advanced-Idle/',
    label: 'Advanced idle control',
  },
  fef0a82ef6899b7b09c77ad0c9dd4f8996fe1733: {
    to: '/Fuel/Fuel-Algorithms/Airmass-Models-and-Migration/',
    label: 'Air-mass models and migration',
  },
  '034ec75bc1e9bf7391eeb0050b13038c0f60e3d7': {
    to: '/Software/Core8-Build-Tools/',
    label: 'Core8 build tools',
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

function EntryMeta({ entry }: { entry: ChangeEntry }): ReactNode {
  const guide = GUIDE_LINKS[entry.commit];
  return (
    <div className="capoRecent__entryMeta">
      <span className={`capoRecent__badge capoRecent__badge--${entry.decision}`}>
        {entry.decision === 'update' ? 'Documentation update' : 'Maintenance'}
      </span>
      <span>
        {commitLink(entry.commit)} · {formatDate(entry.authored_at)}
      </span>
      {entry.parents.length > 1 ? <span>Integration merge</span> : null}
      {guide ? (
        <Link className="capoRecent__guideLink" to={guide.to}>
          {guide.label}
        </Link>
      ) : null}
    </div>
  );
}

function EntryBody({ entry }: { entry: ChangeEntry }): ReactNode {
  return (
    <>
      <h4>{entry.subject}</h4>
      <p>{entry.comment}</p>
      {entry.parents.length > 1 && entry.decision === 'update' ? (
        <p className="capoRecent__mergeNotice">
          This merge has a separate documented user-facing effect; do not treat it as a clean
          integration audit.
        </p>
      ) : null}
    </>
  );
}

export default function RecentChanges({ variant = 'full' }: RecentChangesProps): ReactNode {
  const isHome = variant === 'home';
  const entries = isHome
    ? feed.entries.filter((entry) => entry.parents.length <= 1).slice(0, 3)
    : feed.entries;
  const visibleEntries = entries.filter((entry) => SHA_PATTERN.test(entry.commit));
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
          ? 'The latest documented firmware changes, with a short explanation of their user impact.'
          : 'Recent Capoworks ECU source integrations and their reader-facing impact.'}
      </p>

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

      {!isHome ? (
        <p className="capoRecent__notice">
          Merge audits are collapsed to keep the log readable. A merge marked as a documentation
          update is expanded because it carries a separate user-facing effect.
        </p>
      ) : null}

      <div className="capoRecent__list">
        {visibleEntries.map((entry) =>
          !isHome && entry.parents.length > 1 ? (
            <details
              className="capoRecent__entry capoRecent__entry--merge"
              key={entry.commit}
              open={entry.decision === 'update'}
            >
              <summary>
                <span className="capoRecent__mergeTitle">{entry.subject}</span>
                <EntryMeta entry={entry} />
              </summary>
              <div className="capoRecent__mergeBody">
                <EntryBody entry={entry} />
              </div>
            </details>
          ) : (
            <article className="capoRecent__entry" key={entry.commit}>
              <EntryBody entry={entry} />
              <EntryMeta entry={entry} />
            </article>
          ),
        )}
      </div>

      <footer className="capoRecent__footer">
        <div className="capoRecent__links">
          <a href={SOURCE_URL} rel="noreferrer">
            Firmware source
          </a>
          <a href={`${SOURCE_URL}/commits/${feed.latest_analyzed_commit}`} rel="noreferrer">
            Full change history on GitHub
          </a>
          {isHome ? (
            <Link to="/recent-changes/">View all recent changes</Link>
          ) : (
            <Link to="/">Back to documentation home</Link>
          )}
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
