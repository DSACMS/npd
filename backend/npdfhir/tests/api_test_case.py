from rest_framework.test import APITestCase as DrfAPITestCase, APIClient
from django.contrib.auth.models import User
from ..cache import cacheData as cacheData
# I can't explain why, but we need to import cacheData here. I think we can
# remove this once we move to the docker db setup. By using "import thing as
# thing", we silence "imported but unused" and "not accessed" warnings.


class APITestCase(DrfAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")
        cls.user.set_password("nothing")
        return super().setUpTestData()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
