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
