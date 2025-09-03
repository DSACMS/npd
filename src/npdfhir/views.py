from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.postgres.search import SearchVector
# from djangp.db.models import FilteredRelation, Q
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from .models import Provider, ClinicalOrganization
from .serializers import PractitionerSerializer, ClinicalOrganizationSerializer, BundleSerializer
from .mappings import genderMapping


def index(request):
    return HttpResponse("Connection to npd database: successful")


def health(request):
    return HttpResponse("healthy")


class FHIRPractitionerViewSet(viewsets.ViewSet):
    """
    ViewSet for FHIR Practitioner resources
    """
    # permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Return a list of all providers as FHIR Practitioner resources
        parameters:
            - name: name
              description: Practitioner name
              required: false
              type: string
              paramType: query
            - name: gender
              description: Practitioner gender; Options: (Female, Male, Other)
              required: false
              type: string
              paramType: query
        """
        page_size = 10

        all_params = request.query_params

        # .prefetch_related('individual', 'providertonucctaxonomycode_set', 'providertootheridentifier_set').all() #, 'providertootheridentifier__otheridentifiertype_set'
        providers = Provider.objects.all().prefetch_related(
            'npi', 'individual', 'individual__individualtoname_set', 'providertootherid_set', 'providertotaxonomy_set')

        for param, value in all_params.items():
            if param == 'page_size':
                try:
                    value = int(value)
                    if value <= 1000:
                        page_size = value
                except:
                    page_size = page_size
            if param == 'name':
                providers = providers.annotate(
                    search=SearchVector('individual__individualtoname__last_name',
                                        'individual__individualtoname__first_name', 'individual__individualtoname__middle_name')
                ).filter(search=value)
            if param == 'gender':
                gender = genderMapping.toNDH(value)
                providers = providers.filter(individual__gender_code=gender)
            if param == 'practitioner_type':
                providers = providers.annotate(
                    search=SearchVector(
                        'providertotaxonomy__nucc__display_name')
                ).filter(search=value)
            # if param == 'address-state':
            #    providers = providers.filter(individual__individualtoaddress__address__addressus__fipsstate__abbreviation = value) #fipsstate__abbreviation

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        queryset = paginator.paginate_queryset(providers, request)

        # Serialize the bundle
        serializer = PractitionerSerializer(queryset, many=True)
        bundle = BundleSerializer(serializer)

        # Set appropriate content type for FHIR responses
        response = paginator.get_paginated_response(bundle.data)
        response["Content-Type"] = "application/fhir+json"

        return response

    def retrieve(self, request, pk=None):
        """
        Return a single provider as a FHIR Practitioner resource
        """
        provider = get_object_or_404(Provider, pk=int(pk))

        practitioner = PractitionerSerializer(provider)

        # Set appropriate content type for FHIR responses
        response = Response(practitioner.data)
        response["Content-Type"] = "application/fhir+json"

        return response


class FHIROrganizationViewSet(viewsets.ViewSet):
    """
    ViewSet for FHIR Practitioner resources
    """
    # permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Return a list of all providers as FHIR Practitioner resources
        parameters:
            - name: name
              description: Practitioner name
              required: false
              type: string
              paramType: query
        """
        page_size = 10

        all_params = request.query_params

        organizations = ClinicalOrganization.objects.all().prefetch_related(
            'npi', 'organization', 'organization__organizationtoname_set', 'organizationtootherid_set', 'organizationtotaxonomy_set', 'organization__authorized_official__individualtophone_set', 'organization__authorized_official__individualtoname_set', 'organization__authorized_official__individualtoemail_set')

        for param, value in all_params.items():
            if param == 'page_size':
                try:
                    value = int(value)
                    if value <= 1000:
                        page_size = value
                except:
                    page_size = page_size
            if param == 'name':
                providers = providers.annotate(
                    search=SearchVector('organization__organizationname__name')
                ).filter(search=value)
            if param == 'organization_type':
                providers = providers.annotate(
                    search=SearchVector(
                        'organizationtotaxonomy__nucc__display_name')
                ).filter(search=value)
            # if param == 'address-state':
            #    providers = providers.filter(individual__individualtoaddress__address__addressus__fipsstate__abbreviation = value) #fipsstate__abbreviation

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        queryset = paginator.paginate_queryset(organizations, request)

        # Serialize the bundle
        serializer = ClinicalOrganizationSerializer(queryset, many=True)
        bundle = BundleSerializer(serializer)

        # Set appropriate content type for FHIR responses
        response = paginator.get_paginated_response(bundle.data)
        response["Content-Type"] = "application/fhir+json"

        return response

    def retrieve(self, request, pk=None):
        """
        Return a single provider as a FHIR Practitioner resource
        """
        clinicalorg = get_object_or_404(ClinicalOrganization, pk=int(pk))

        organization = ClinicalOrganizationSerializer(clinicalorg)

        # Set appropriate content type for FHIR responses
        response = Response(organization.data)
        response["Content-Type"] = "application/fhir+json"

        return response
