# npdfhir
Django backend that provides a FHIR API for accessing data from the npd database.

## Project structure
* The npdfhir directory contains code that drives the api
* The app directory contains code that controls the overall application
* The root directory contains code for deploying the application within a docker container


## Contributing to the API
### Prerequesites
- [docker](https://www.docker.com/)
- [colima](https://github.com/abiosoft/colima) (if using macOS)
- a postgres database with the npd schema

### Local dev
1. Ensure that either colima (if using macOS) or the docker service is running
2. Create a `.env` file in this directory, following the template of the `.env_template` file
    * n.b. ensure that NPD_DB_HOST is set to `db` if using a local postgres instance.
3. Run `docker-compose up --build` initially and following any changes
4. Happy coding!

### Running Tests
1. Ensure that you have a running local postgres instance 
2. Make sure that you have a working `.env` file as described above
3. Make sure all python dependencies are installed in a venv or otherwise
4. Navigate to the `backend/` directory and run `./manage.py test`


## Understanding the Flow of Data through the FHIR API
![Flowchart](practitioner_data_flow.png)