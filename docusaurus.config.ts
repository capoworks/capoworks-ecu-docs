import type { Options, ThemeConfig } from '@docusaurus/preset-classic';
import type { Config } from '@docusaurus/types';
import { themes } from 'prism-react-renderer';

const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

const url = 'https://capoworks.github.io';

const config: Config = {
  title: 'Capoworks ECU',
  tagline: 'Free Open Motorsports ECU',
  url,
  baseUrl: '/capoworks-ecu-docs/',

  // strict URL validation
  onBrokenLinks: 'throw',
  onDuplicateRoutes: 'throw',

  noIndex: false, // adds <meta name="robots" content="noindex, nofollow"> to every page
  favicon: 'img/capoworks-logo.png',
  trailingSlash: true, // adds trailing slash to all links for GitHub Pages
  // staticDirectories: ['public', 'static'],

  // GitHub pages deployment config.
  organizationName: 'capoworks',
  projectName: 'capoworks-ecu-docs',

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/', // Serve the docs at the site's root
          sidebarPath: require.resolve('./sidebars.ts'),
          // Remove this to remove the "edit this page" links.
          editUrl: 'https://github.com/capoworks/capoworks-ecu-docs/tree/master',
          remarkPlugins: [require('remark-math')],
          rehypePlugins: [[require('rehype-katex'), { output: 'mathml' }]],
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      } satisfies Options,
    ],
  ],

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
  },

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
      type: 'text/css',
      integrity: 'sha384-odtC+0UGzzFL/6PNoE8rX/SPcQDXBJ+uRepguP4QkPCm2LBxH3FA3y+fKSiJ+AmM',
      crossorigin: 'anonymous',
    },
  ],

  themes: [
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true, // `hashed` is recommended as long-term-cache of index file is possible.
        indexBlog: false,
        docsRouteBasePath: '/',
      },
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        redirects: [
          // Client side redirect addresses specified in INI files (HT & TS)
          // eg. https://capoworks.github.io/capoworks-ecu-docs/r/fuel ->
          // https://capoworks.github.io/capoworks-ecu-docs/category/fuel/
          {
            from: '/r/fuel',
            to: '/category/fuel/',
          },
          {
            from: '/r/vvt',
            to: '/category/vvt/',
          },
          {
            from: '/r/trigger',
            to: '/category/general-sensors/',
          },
          {
            from: '/r/etb',
            to: '/category/etb/',
          },
          {
            from: '/r/tpstps',
            to: '/Fuel/Acceleration/TPS-Based/',
          },
          {
            from: '/r/lua',
            to: '/Advanced-Features/Lua-Scripting/',
          },
          {
            from: '/r/vr',
            to: '/Hardware/Hardware-Circuits/Discrete-VR/',
          },
        ],
      },
    ],
  ],

  themeConfig: {
    image: 'img/capoworks-logo.png',
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Capoworks ECU',
      logo: {
        alt: 'Capoworks logo',
        src: 'img/capoworks-logo.png',
        style: {
          width: 36,
          height: 36,
          marginTop: -1,
          borderRadius: 5,
        },
      },
      hideOnScroll: true,
      items: [
        {
          href: 'https://github.com/capoworks/capoworks-ecu-docs',
          label: 'GitHub',
          position: 'right',
        },
        {
          type: 'search',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Capoworks',
          items: [
            {
              label: 'Firmware',
              href: 'https://github.com/capoworks/capoworks-ecu',
            },
            {
              label: 'Documentation repository',
              href: 'https://github.com/capoworks/capoworks-ecu-docs',
            },
            {
              label: 'Capoworks on GitHub',
              href: 'https://github.com/capoworks',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'Credits and Sources',
              to: '/credits-and-sources/',
            },
          ],
        },
      ],
      copyright:
        'Documentation is available under CC BY-SA 4.0. See the linked Credits and Sources page for attribution.',
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
      additionalLanguages: ['lua'],
    },
  } satisfies ThemeConfig,
};

module.exports = config;
