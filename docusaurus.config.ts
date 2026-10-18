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
  favicon: 'img/icons/favicon.ico',
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
    image: 'img/icons/android-chrome-512x512.png',
    colorMode: {
      defaultMode: 'dark',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Capoworks ECU',
      logo: {
        alt: 'Capoworks ECU logo',
        src: 'img/capoworks-logo.svg',
        style: {
          height: 34,
          marginTop: -2,
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
          title: 'FOME community',
          items: [
            {
              label: 'Discord',
              href: 'https://discord.gg/EEg2fbhQD4',
            },
            {
              label: 'Facebook',
              href: 'https://www.facebook.com/profile.php?id=100088049271157',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Original FOME Wiki',
              href: 'https://wiki.fome.tech',
              target: '_blank',
            },
            {
              label: 'Capoworks firmware',
              href: 'https://github.com/capoworks/capoworks-ecu',
            },
            {
              label: 'Capoworks on GitHub',
              href: 'https://github.com/capoworks',
            },
          ],
        },
      ],
      // copyright: `Copyright © ${new Date().getFullYear()} FOME`,
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
      additionalLanguages: ['lua'],
    },
  } satisfies ThemeConfig,
};

module.exports = config;
