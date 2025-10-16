from datetime import datetime
from http import HTTPStatus
import os
from pathlib import Path
from django.test import TestCase
from django.urls import reverse

TEST_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
STATIC_INDEX = TEST_DIR / '..' / 'static' / 'index.html'

class WithoutStaticIndex(TestCase):
    """
    Visiting the index route when no static/index.html asset exists.
    """

    @classmethod
    def setUpTestData(cls):
        if os.path.exists(STATIC_INDEX):
            os.unlink(STATIC_INDEX)

    def test_index_redirects_to_vite_in_development(self):
        """
        When static/index.html doesn't exist, route redirects
        """
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, 'http://localhost:3000/', fetch_redirect_response=False)

class WithStaticIndex(TestCase):
    """
    Visiting the index route when static/index.html asset does exist.
    """

    @classmethod
    def setUpTestData(cls):
        if not os.path.exists(STATIC_INDEX):
            with open(STATIC_INDEX, 'a') as index:
                index.write(f'\n<!-- test content {datetime.now()} -->')

    def test_index_serves_static_file(self):
        """
        When static/index.html exists, route serves it
        """
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'test content', status_code=HTTPStatus.OK)
