import json

import boto3

from django.conf import settings
from django_vite.core.asset_loader import ManifestClient, DjangoViteAppClient

class S3ManifestClient(ManifestClient):
    def load_manifest(self):
        s3 = boto3.client("s3")
        res = s3.get_object(Bucket=settings.FRONTEND_S3_BUCKET, Key='manifest.json')
        manifest_content = res["Body"].read()
        return json.loads(manifest_content)

class S3DjangoViteAppClient(DjangoViteAppClient):
    ManifestClient = S3ManifestClient
