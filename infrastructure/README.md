# NPD Infrastructure

## Infrastructure Diagram

![npd-infrastructure-diagram-prod.drawio.png](npd-infrastructure-diagram-prod.drawio.png)

## Update Cadence

- The `dev` environment is to be updated whenever updates to `main` are merged
- `test` / `uat` is updated whenever a release is cut
- Releasing to `prod` is manual, requires sign-off from the PM and eng team

## Naming Conventions

The naming scheme for resources should be consistent but not too verbose.

`{project-name}-${region}-${tier}-${description}-${index?}`

Non-prod is divided into two tiers:
- `dev`
- `test`

Production is `prod`.

Some examples:

```bash
npd-east-dev-fhir-api
npd-east-test-fhir-api
npd-east-dev-fhir-database
npd-east-test-fhir-database-replica-1
npd-east-dev-load-fips-bronze-job
```

## Usage

### Deploy (manual)

1. Create an environment specific `.env` file, using `.env.template` as a reference
```
   (one of)
   .env.dev
   .env.test
   .env.prod
```
2. Assume an AWS Role using `./ctkey.sh`
```
    (one of)
    ./ctkey.sh dev
    ./ctkey.sh test
    ./ctkey.sh prod
```
3. Initialize terraform
```
    (one of)
    terraform -chdir=envs/dev init
    terraform -chdir=envs/test init
    terraform -chdir=envs/prod init
```
4. Deploy resources using terraform
```
    (one of)
    terraform -chdir=envs/dev apply
    terraform -chdir=envs/test apply
    terraform -chdir=envs/prod apply
```
