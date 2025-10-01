# Next NPD Infrastructure

Non-prod is divided into two tiers:
- `dev`
- `test`

Production is `prod`.

## Update Cadence

- The `dev` environment is to be updated whenever updates to `main` are merged
- `test` / `uat` is updated whenever a release is cut
- Releasing to `prod` is manual, requires sign-off from the PM and eng team

## Naming Conventions

The naming scheme should be consistent but not too verbose

`{project-name}-${region}-${tier}-${description}-${index?}`

Some examples:

```bash
npd-east-dev-fhir-api
npd-east-test-fhir-api
npd-east-dev-fhir-database
npd-east-test-fhir-database-replica-1
npd-east-dev-load-fips-bronze-job
```

## Infrastructure Diagram

![NPD Infrastructure.drawio.png](NPD%20Infrastructure.drawio.png)

## Usage

### Deploy (manual) (dev by default)

1. Create Terraform backend S3 bucket if it doesn't already exist
2. Create `.env` file using `.env.template` as starting point
3. `terraform apply`, evaluate the plan, then apply if it all looks good!