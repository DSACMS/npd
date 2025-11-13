locals {
  domains = {
    dev = {
      etl       = "etl.dev.directory.internal.cms.gov"
      api       = "api.dev.directory.internal.cms.gov"
      directory = "dev.directory.internal.cms.gov"
    }
    impl = {
      etl       = "etl.impl.directory.internal.cms.gov"
      api       = "api.impl.directory.internal.cms.gov"
      directory = "impl.directory.internal.cms.gov"
    }
    prod = {
      etl       = "etl.directory.internal.cms.gov"
      api       = "api.directory.cms.gov" # public route
      directory = "directory.cms.gov" # public route
    }
  }
  api_domain = local.domains[var.tier]["api"]
  directory_domain = local.domains[var.tier]["directory"]
  etl_domain = local.domains[var.tier]["etl"]
}
