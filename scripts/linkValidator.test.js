const assert = require('node:assert/strict');
const { test } = require('node:test');

const { hasInternalMdLink } = require('./linkValidator');

const cases = [
  {
    name: 'allows external Markdown source links',
    line: '[Changelog](https://github.com/capoworks/capoworks-ecu/blob/master/CHANGELOG.md)',
    expected: false,
  },
  {
    name: 'allows external Markdown links with queries and fragments',
    line: '[Notes](https://github.com/capoworks/capoworks-ecu/CHANGELOG.md?plain=1#latest)',
    expected: false,
  },
  {
    name: 'allows an external Markdown link alongside an internal route',
    line: '[Guide](/software/guide/) and [Notes](https://example.com/CHANGELOG.md)',
    expected: false,
  },
  {
    name: 'rejects an internal Markdown link after an external Markdown link',
    line: '[Notes](https://example.com/CHANGELOG.md) and [Legacy](/software/legacy.md)',
    expected: true,
  },
  {
    name: 'rejects an internal Markdown link anywhere on the line',
    line: '[Guide](/software/guide) and [Legacy](/software/legacy.md)',
    expected: true,
  },
  {
    name: 'rejects relative Markdown links',
    line: '[Guide](../software/guide.md)',
    expected: true,
  },
  {
    name: 'rejects root MDX links with queries and fragments',
    line: '[Guide](/software/guide.mdx?view=full#setup)',
    expected: true,
  },
  {
    name: 'rejects Markdown links with fragments',
    line: '[Guide](guide.md#setup)',
    expected: true,
  },
  {
    name: 'rejects percent-encoded Markdown extensions',
    line: '[Guide](/software/guide%2Emd?plain=1)',
    expected: true,
  },
  {
    name: 'rejects protocol-relative Markdown links',
    line: '[Guide](//example.com/guide.md)',
    expected: true,
  },
  {
    name: 'rejects non-HTTP scheme Markdown links',
    line: '[Guide](ssh://git@example.com/guide.md)',
    expected: true,
  },
  {
    name: 'rejects file URL Markdown links',
    line: '[Guide](file:///srv/guide.md)',
    expected: true,
  },
  {
    name: 'rejects HTTP Markdown links without a host',
    line: '[Guide](https:///guide.md)',
    expected: true,
  },
  {
    name: 'allows source extensions that only appear in a query string',
    line: '[Guide](/software/guide?source=guide.md)',
    expected: false,
  },
  {
    name: 'ignores Markdown links inside inline code',
    line: 'Legacy links such as `(/software/legacy.md)` are rejected.',
    expected: false,
  },
];

for (const { name, line, expected } of cases) {
  test(name, () => {
    assert.equal(hasInternalMdLink(line), expected, line);
  });
}
