import json

from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError

from npdfhir.tests.fixtures import create_endpoint, create_organization, create_practitioner


class Command(BaseCommand):
    help = "Create test data for end-to-end specs"

    def to_json(self, **record) -> str:
        return json.dumps(record, cls=DjangoJSONEncoder, indent=2)

    def handle(self, *args, **options):
        provider = create_practitioner()
        individualtoname = provider.individual.individualtoname_set.first()

        provider_report = self.to_json(
            individual__id=provider.individual.id,
            individual__individualtoname__first_name=individualtoname.first_name,
            individual__individualtoname__last_name=individualtoname.last_name,
            npi__npi=provider.npi.npi,
        )
        self.stdout.write(f"created Provider: {provider_report}")

        try:
            organization = create_organization(npi_value=1234567893, organization_type="261QP2000X")
            organizationtoname = organization.organizationtoname_set.first()
            self.stdout.write(
                f"created Organization: {self.to_json(id=organization.id, organizationtoname__name=organizationtoname.name)}"
            )
        except IntegrityError:
            organization = None
            self.stdout.write("organization with NPI 1234567893 already exists")

        if organization:
            endpoint = create_endpoint(organization=organization)
            self.stdout.write(f"created Endpoint: {self.to_json(id=endpoint.id)}")
