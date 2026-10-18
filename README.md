# Capoworks ECU Documentation

This repository contains the source for the
[Capoworks ECU documentation](https://capoworks.github.io/capoworks-ecu-docs/).

The site is an independent fork that uses the FOME Wiki as its initial documentation source. It is
not affiliated with or endorsed by FOME. See [ATTRIBUTION.md](ATTRIBUTION.md) for source, authorship,
history, and license information.

## Development

Capoworks ECU documentation is built using [Docusaurus 3](https://docusaurus.io/).

### Installation

Required [Node.js](https://nodejs.dev/) is defined in [.nvmrc](/.nvmrc). If you use [nvm](https://github.com/nvm-sh/nvm), run `nvm use` to switch to the correct version.

To install the dependencies locked by this repository, run:

```bash
npm ci
```

### Local Development

```bash
npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.
The site is served at <http://localhost:3000/capoworks-ecu-docs/> by default.

Docusaurus guides: [https://docusaurus.io/docs/category/guides](https://docusaurus.io/docs/category/guides)

#### Lint code

```bash
npm run lint

npm run lint:fix
```

### Build

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

### Redirection

Some addresses have client-side redirection set up here:
[docusaurus.config.ts](docusaurus.config.ts) (section `redirects: [...]`).

Those addresses come from the INI files (TS & HT). This gives more flexibility when wiki pages are moved or renamed.

Example:

```bash
https://capoworks.github.io/capoworks-ecu-docs/r/fuel -> https://capoworks.github.io/capoworks-ecu-docs/category/fuel/
```

## Firmware and INI guidance

The [Capoworks firmware repository](https://github.com/capoworks/capoworks-ecu) is the source for
Capoworks firmware. This documentation repository does not bundle firmware.

Some inherited pages may still link to upstream FOME firmware releases. Firmware `.ini` help links
may still open the upstream FOME wiki; those links need a future update in the firmware repository.

## Attribution

The imported documentation remains available under CC BY-SA 4.0. Source links, contributor
attribution, and the preservation of Git history are documented in [ATTRIBUTION.md](ATTRIBUTION.md).
