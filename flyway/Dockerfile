FROM flyway/flyway:10

ADD sql/migrations sql/migrations
ADD sql/reference_data sql/reference_data

# django_migrations are for use on NPD application hosts only, not ETL
ADD sql/django_migrations sql/django_migrations
