# NPD Front End
The NPD front end consists of React + TypeScript + Vite, deployed through a docker container. 

### User Interface
The User Interface designs can be found [here](https://www.figma.com/design/YsHkTGfeb8kSm1jCfPAJ0h/National-Provider-Directory-MVP). To the extent possible, we will use components provided by the [CMS Design System](https://design.cms.gov/?theme=core) when building the front end.

### Data
The front end fetches data from the NPD FHIR API. We will create specialized Bundle resources to feed the search results (e.g. `fhir/SearchPractitioner/<npi>` might return a bundle of Practitioner, PractitionerRole, Organization, and Endpoint resources relevant to the given Practitioner). If we find this approach to be insufficient, we will assess additional API endpoints.

## Project Structure
* The src directory contains all front end code
  * The assets folder contains static assets
  * The components folder contains custom components
  * The hooks folder contains data retrieval hooks

## Local Development

### Prerequesites
- [docker](https://www.docker.com/)
- [colima](https://github.com/abiosoft/colima) (if using macOS)
- a postgres database with the npd schema

### Local dev
1. Ensure that either colima (if using macOS) or the docker service is running
2. Ensure that the backend docker container is running
3. Run `docker-compose up --build` initially
4. Happy coding!