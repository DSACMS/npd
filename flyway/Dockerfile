FROM flyway/flyway:10

ADD sql/migrations sql/migrations
ADD sql/reference_data sql/reference_data

# django migrations and reference data are for use on NPD application hosts
# only, not ETL
ADD sql/django_migrations sql/django_migrations
ADD sql/django_reference_data sql/django_reference_data
