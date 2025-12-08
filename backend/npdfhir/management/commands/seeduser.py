from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

# from fhir.resources.R4B import organization, practitioner


class Command(BaseCommand):
    help = "Create a developer@cms.hhs.gov in the Developers group"

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(username="developer@cms.hhs.gov")
        user.set_password("password123")

        group, _ = Group.objects.get_or_create(name="Developers")
        user.groups.add(group)

        user.save()
        group.save()

        self.stdout.write("Created developer@cms.hhs.gov account and added to Developer group")
