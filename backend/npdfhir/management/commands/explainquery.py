from django.core.management.base import BaseCommand

from npdfhir.models import Organization, OrganizationByName


class Command(BaseCommand):
    help = "Export a JSON schema, example JSON record, or both for a given FHIR entity"

    def original_query(self):
        return (
            Organization.objects.all()
            .prefetch_related(
                "authorized_official",
                "ein",
                "organizationtoname_set",
                "organizationtoaddress_set",
                "organizationtoaddress_set__address",
                "organizationtoaddress_set__address__address_us",
                "organizationtoaddress_set__address__address_us__state_code",
                "organizationtoaddress_set__address_use",
                "authorized_official__individualtophone_set",
                "authorized_official__individualtoname_set",
                "authorized_official__individualtoemail_set",
                "authorized_official__individualtoaddress_set",
                "authorized_official__individualtoaddress_set__address__address_us",
                "authorized_official__individualtoaddress_set__address__address_us__state_code",
                "clinicalorganization",
                "clinicalorganization__npi",
                "clinicalorganization__organizationtootherid_set",
                "clinicalorganization__organizationtootherid_set__other_id_type",
                "clinicalorganization__organizationtotaxonomy_set",
                "clinicalorganization__organizationtotaxonomy_set__nucc_code",
            )
            .order_by("organizationtoname__name")
        )

    def materialized_view_query(self):
        return (
            OrganizationByName.objects.all()
            .prefetch_related(
                "organization",
                "organization__authorized_official",
                "organization__ein",
                "organization__organizationtoname_set",
                "organization__organizationtoaddress_set",
                "organization__organizationtoaddress_set__address",
                "organization__organizationtoaddress_set__address__address_us",
                "organization__organizationtoaddress_set__address__address_us__state_code",
                "organization__organizationtoaddress_set__address_use",
                "organization__authorized_official__individualtophone_set",
                "organization__authorized_official__individualtoname_set",
                "organization__authorized_official__individualtoemail_set",
                "organization__authorized_official__individualtoaddress_set",
                "organization__authorized_official__individualtoaddress_set__address__address_us",
                "organization__authorized_official__individualtoaddress_set__address__address_us__state_code",
                "organization__clinicalorganization",
                "organization__clinicalorganization__npi",
                "organization__clinicalorganization__organizationtootherid_set",
                "organization__clinicalorganization__organizationtootherid_set__other_id_type",
                "organization__clinicalorganization__organizationtotaxonomy_set",
                "organization__clinicalorganization__organizationtotaxonomy_set__nucc_code",
            )
            .order_by("name")
        )

    def handle(self, *args, **options):
        for query in (self.original_query(), self.materialized_view_query()):
            print("--- QUERY")
            print(query[10:20].query)
            print("--- EXPLAIN")
            print(query[10:20].explain())
            print("---")

        # serializer = OrganizationSerializer(query[10:20], many=True)
        # print(json.dumps(json.loads(JSONRenderer().render(serializer.data)), indent=2))
