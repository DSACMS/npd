locals {
  domains = {
    dev = {
      etl       = "etl.dev.cnpd.internal.cms.gov"
      api       = "api.dev.cnpd.internal.cms.gov"
      directory = "dev.cnpd.internal.cms.gov"
      namespace = "dev.cnpd.internal.cms.gov"
    }
    test = {
      etl       = "etl.test.cnpd.internal.cms.gov"
      api       = "api.test.cnpd.internal.cms.gov"
      directory = "test.cnpd.internal.cms.gov"
      namespace = "test.cnpd.internal.cms.gov"
    }
    prod-test = {
      etl       = "etl.prod-test.cnpd.internal.cms.gov"
      api       = "api.prod-test.cnpd.internal.cms.gov"
      directory = "prod-test.cnpd.internal.cms.gov"
      namespace = "prod-test.cnpd.internal.cms.gov"
    }
    prod = {
      etl       = "etl.cnpd.internal.cms.gov"
      api       = "api.directory.cms.gov" # public route
      directory = "directory.cms.gov"     # public route
      namespace = "cnpd.internal.cms.gov"
    }
  }

  api_domain       = local.domains[var.tier]["api"]
  directory_domain = local.domains[var.tier]["directory"]
  etl_domain       = local.domains[var.tier]["etl"]
  namespace_domain = local.domains[var.tier]["namespace"]
}
