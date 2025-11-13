# NPD Front End

- [NPD Front End](#npd-front-end)
  - [System description](#system-description)
    - [User interface](#user-interface)
    - [Data](#data)
  - [Project structure](#project-structure)
    - [Static content](#static-content)
  - [Local development](#local-development)
    - [Prerequesites](#prerequesites)
    - [Running the frontend app](#running-the-frontend-app)
      - [Option 1: vite dev server](#option-1-vite-dev-server)
      - [Option 2: build assets for the backend](#option-2-build-assets-for-the-backend)
  - [Adding dependencies](#adding-dependencies)


The NPD front end consists of React + TypeScript built by vite.dev, deployed as static assets and developed as part of the NPD `backend/` Django application.

## System description

### User interface

User Interface designs can be found [in Figma, here](https://www.figma.com/design/YsHkTGfeb8kSm1jCfPAJ0h/National-Provider-Directory-MVP).

To the extent possible, we will use components provided by the [CMS Design System](https://design.cms.gov/?theme=core) or the [US Web Design System (USWDS)](https://designsystem.digital.gov/) when building the front end.

### Data

The front end fetches data from the NPD FHIR API.

If we find this approach to be insufficient, we will assess additional API endpoints.

## Project structure

- The `src` directory contains all front end code
  - `assets/` contains static assets
  - `components/` contains custom components
  - `hooks/` contains custom hook implementations
  - `pages/` top level page components
  - `i18n/en/` contains translation / static content definition files

### Static content

Any static content which appears on a page as part of a React HTML or other component tag should be stored in the appropriate `src/i18/**/*.json` source file and accessed via the [react-i18next](https://react.i18next.com/) `t()` function. This allows us to isolate content from behavior and will allow for easier translation in the future, should the need arise.

We recommend using the `useTranslation` hook to access the `t()` function. For example:

```tsx
const MyComponent = () => {
  const { t } = useTranslation()

  return (
    <div className="ds-u-display--flex">
      <p>{t("component.disclaimer")}</p>
      <p><a href="#">{t("component.link")}</a></p>
    </div>
  )
}
```

For larger or full-page content, we're using Markdown files, conventionally named `*.content.md`, loaded with the `?raw` query supported by vite.

```tsx
import Markdown from 'react-markdown'

import content from './MyPage.content.md?raw'

const MyPage = () => {

  return (
    <div className="usa-prose">
      <Markdown>{ content }</Markdown>
    </div>
  )
}
```

And `MyPage.content.md`:

````markdown
## This is a page

It has text in headings and paragraphs.

You can use `inline code` or write in blocks:

```py
import code
code.blocks()
```

[Links work](#data) just like in markdown.
````

## Local development

### Prerequesites

- [docker](https://www.docker.com/) or other suitable container runner
- a running instance of the npd backend: `docker compose up django-web`

### Running the frontend app

There are two options for running the frontend application in development. Each has a time and a place

#### Option 1: vite dev server

From the `npd` project root:

1. Run the frontend vite dev server
    - in docker with: `docker compose up web`
    - on host with: `cd frontend; npm run dev`
3. Visit http://localhost:3000 in your browser

**Limitations:**

- requires CORS and CSRF workarounds for API requests and `<form action="..." method="POST">` posting across domains (`localhost:3000` in the browser sending to the server at `localhost:8000`)

**Benefits**:

- nearly instantaneous reloading of changed components and styles

#### Option 2: build assets for the backend

At present, NPD deployment involves compiling the frontend assets into the `backend/provider_directory/static` directory and then building an image with the resulting static assets present.

You can simulate this setup by using the `npm run watch` command to build frontend assets and serve them from the backend application.

From the `npd` project root:

1. Run the frontend server in build + watch mode:
    - in docker with: `docker compose run --rm web npm run watch`
    - on host with: `cd frontend; npm run watch`
2. Visit http://localhost:8000 in your browser

**Limitations:**

- rebuilds the entire frontend app on changes, takes around 3 seconds
- requires manual page reload when assests are rebuilt
- assets are deleted when the backend test suite runs

**Benefits:**

- matches the deploy project setup
- plain HTML form POST works as expected

## Adding dependencies

Because of our current frontend docker compose setup, new dependencies **MUST** be installed with `docker compose run web npm install`. They will not be picked up by `docker compose build web` or `docker compose up --build web`.

The reason is that we are mounting a virtual docker compose volume in place of the container's `/app/node_modules` directory, but `docker compose build` doesn't know about _runtime_ volume mounts, only _host_ and _base image_ mounts, so it cannot update the docker compose virtual volume, only the directory which is present inside the image during the build process.

For us, this means that if you are running in docker containers with `docker compose` and want to add a frontend dependency, you'll need to make sure they are added inside the running container with `docker compose run npm install`, as well as outside (on your host machine) if you need that for editor support or to run `npm` commands on host.

```sh
# install and save a new dependency on host, to make the editor tooling happy
cd frontend
npm install --save i18next

# in docker, to make the image happy
docker compose run --rm web npm install
```

Likewise, if `package.json` has been updated since you last fetched project updates, you'll need to run:

```sh
# after `git pull` when frontend/package.json has been updated
docker compse run --rm web npm install
```

to refresh your local frontend docker compose `web` service.
