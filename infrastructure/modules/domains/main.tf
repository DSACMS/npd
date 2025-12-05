locals {
  domains = {
    dev = {
      etl       = "etl.dev.cnpd.internal.cms.gov"
      api       = "api.dev.cnpd.internal.cms.gov"
      directory = "dev.cnpd.internal.cms.gov"
    }
    test = {
      etl       = "etl.test.cnpd.internal.cms.gov"
      api       = "api.test.cnpd.internal.cms.gov"
      directory = "test.cnpd.internal.cms.gov"
    }
    prod = {
      etl       = "etl.cnpd.internal.cms.gov"
      api       = "api.directory.cms.gov" # public route
      directory = "directory.cms.gov"     # public route
    }
  }
  api_domain       = local.domains[var.tier]["api"]
  directory_domain = local.domains[var.tier]["directory"]
  etl_domain       = local.domains[var.tier]["etl"]
}
