# NPD Front End

The NPD front end consists of React + TypeScript + Vite, deployed as static assets and developed as part of the NPD `backend/` Django application.

### User Interface

User Interface designs can be found [in Figma, here](https://www.figma.com/design/YsHkTGfeb8kSm1jCfPAJ0h/National-Provider-Directory-MVP).

To the extent possible, we will use components provided by the [CMS Design System](https://design.cms.gov/?theme=core) when building the front end.

### Data

The front end fetches data from the NPD FHIR API. We will create specialized Bundle resources to feed the search results. For example, `/fhir/SearchPractitioner/<npi>` might return a bundle of Practitioner, PractitionerRole, Organization, and Endpoint resources relevant to the given Practitioner.

If we find this approach to be insufficient, we will assess additional API endpoints.

## Project Structure

- The `src` directory contains all front end code
  - `assets/` contains static assets
  - `components/` contains custom components
  - `hooks/` contains custom hook implementations
  - `i18n/en/` contains translation / static content definition files

### Static Content

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

## Local Development

### Prerequesites

- [docker](https://www.docker.com/) or other suitable container runner
- a running instance of the npd backend

### Local dev

From the `npd` project root:

1. Ensure that a suitable docker service is running
1. Run `docker compose up --build` to launch the backend and frontend applications
   - If you want to run the application backend and frontend separately, you can do that with:
     ```console
     ~/npd $ docker compose up -d django-web
     ~/npd $ docker compose up -d web
     ```
1. Happy coding!

### Adding Dependencies

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
