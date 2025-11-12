output "domains" {
  value = {
    dev = local.dev
    impl = local.impl
    prod = local.prod
  }
}