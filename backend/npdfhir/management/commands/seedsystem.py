import json
import random

from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from faker import Faker

from npdfhir.tests.fixtures.endpoint import create_endpoint
from npdfhir.tests.fixtures.organization import create_organization
from npdfhir.tests.fixtures.practitioner import create_practitioner


class Command(BaseCommand):
    help = "Create test data for end-to-end specs"

    def generate_npi(self) -> int:
        return random.randint(1123456789, 2987654321)

    def to_json(self, **record) -> str:
        return json.dumps(record, cls=DjangoJSONEncoder, indent=2)

    def generate_sample_organizations(self, qty: int = 25):
        fake = Faker()
        for i in range(qty):
            name = fake.company()
            org = create_organization(
                name=name,
                # not bothering with checksum here
                npi_value=self.generate_npi(),
                authorized_official_first_name=fake.first_name(),
                authorized_official_last_name=fake.last_name(),
                other_state_code=fake.state_abbr(),
                other_issuer=fake.company(),
            )
            self.stdout.write(f"created Organization: {org.id} {name}")

    def handle(self, *args, **options):
        if options.get("seed", None):
            Faker.seed(int(options["seed"]))

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
            # one known NPI
            organization = create_organization(
                name="AAA Test Org", npi_value=1234567893, organization_type="261QP2000X"
            )
            organizationtoname = organization.organizationtoname_set.first()
            self.stdout.write(
                f"created Organization: {self.to_json(id=organization.id, organizationtoname__name=organizationtoname.name)}"
            )
        except IntegrityError:
            organization = None
            self.stdout.write("(organization with NPI 1234567893 already exists)")

        if organization:
            endpoint = create_endpoint(organization=organization)
            self.stdout.write(f"created Endpoint: {self.to_json(id=endpoint.id)}")

        self.generate_sample_organizations(25)
