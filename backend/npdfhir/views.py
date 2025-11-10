from uuid import UUID

from django.contrib.postgres.search import SearchVector
from django.core.cache import cache
from django.db.models import Q, F, OuterRef, Subquery, Value, CharField
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from .pagination import CustomPaginator
from .renderers import FHIRRenderer
from .mappings import addressUseMapping, genderMapping

from .filters.endpoint_filter_set import EndpointFilterSet
from .filters.location_filter_set import LocationFilterSet
from .filters.organization_filter_set import OrganizationFilterSet
from .filters.practitioner_filter_set import PractitionerFilterSet
from .filters.practitioner_role_filter_set import PractitionerRoleFilterSet

from .models import (
    EndpointInstance,
    ClinicalOrganization,
    Location,
    Organization,
    OrganizationToName,
    Provider,
    ProviderToLocation,
    Individual,
    IndividualToName,
)

from .serializers import (
    BundleSerializer,
    EndpointSerializer,
    LocationSerializer,
    OrganizationSerializer,
    PractitionerRoleSerializer,
    PractitionerSerializer,
    CapabilityStatementSerializer
)

default_page_size = 10
max_page_size = 1000
page_size_param = openapi.Parameter(
    'page_size',
    openapi.IN_QUERY,
    description="Limit the number of results returned per page",
    type=openapi.TYPE_STRING,
    minimum=1,
    maximum=max_page_size,
    default=default_page_size
)

def createSortParam(allowed_sorts):
    return openapi.Parameter(
        '_sort',
        openapi.IN_QUERY,
        description=(
            "Comma-separated list of fields to sort by. "
            "Prefix with `-` for descending order.\n\n"
            f"Allowed fields: {', '.join(allowed_sorts)}"
        ),
        type=openapi.TYPE_STRING,
        required=False,
    )

def createFilterParam(field: str, display: str = None, enum: list = None):
    if display is None:
        display = field.replace('_', ' ').replace('.', ' ')
    param = openapi.Parameter(
        field,
        openapi.IN_QUERY,
        description=f"Filter by {display}",
        type=openapi.TYPE_STRING,
    )
    if enum is not None:
        param.enum = enum
    return param

def get_sort_fields(allowed_sorts, sorts_value):
    sort_fields = []

    for field in sorts_value.split(','):
        cleaned = field.lstrip('-')
        if cleaned in allowed_sorts:
            sort_fields.append(field)
    
    return sort_fields

def get_data_sorted(data,allowed_sorts,sorts_value):
    sort_fields = get_sort_fields(allowed_sorts,sorts_value)

    #Sort data
    if sort_fields:
        return data.order_by(*sort_fields)
    else: 
        return data




def index(request):
    return HttpResponse("Connection to npd database: successful")


def health(request):
    return HttpResponse("healthy")


class FHIREndpointViewSet(viewsets.GenericViewSet):
    """
    ViewSet for FHIR Endpoint Resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EndpointFilterSet
    allowed_sorts = ['name', 'address', 'ehr_vendor_name']
    pagination_class = CustomPaginator  


    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        sorts_value = self.request.query_params.get('_sort')
        if sorts_value:
            queryset = get_data_sorted(queryset, self.allowed_sorts, sorts_value)

        return queryset

    @swagger_auto_schema(
        manual_parameters=[
            page_size_param,
            createFilterParam('name'),
            createFilterParam('connection_type'),
            createFilterParam('payload_type'),
            createFilterParam('status'),
            createFilterParam('organization'),
            createSortParam(['name', 'address', 'ehr_vendor_name'])
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Endpoint resource cannot be found."}
    )
    def list(self, request):
        """
        Query a list of interoperability endpoints, represented as a bundle of FHIR Endpoint resources

        Default sort order: ascending endpoint instance name
        """

        endpoints = EndpointInstance.objects.all().prefetch_related(
            'endpoint_connection_type',
            'environment_type',
            'endpointinstancetopayload_set',
            'endpointinstancetopayload_set__payload_type',
            'endpointinstancetopayload_set__mime_type',
            'endpointinstancetootherid_set'
        ).annotate(
            ehr_vendor_name=F('ehr_vendor__name')
        ).order_by('name')

        endpoints = self.filter_queryset(endpoints)
        paginated_endpoints = self.paginate_queryset(endpoints)

        serialized_endpoints = EndpointSerializer(paginated_endpoints, many=True)
        bundle = BundleSerializer(
            serialized_endpoints, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    def retrieve(self, request, pk=None):
        """
        Query a specific endpoint as a FHIR Endpoint resource
        """

        try:
            UUID(pk)
        except (ValueError, TypeError) as e:
            return HttpResponse(f"Endpoint {escape(pk)} not found", status=404)

        endpoint = get_object_or_404(EndpointInstance.objects.prefetch_related(
            'endpoint_connection_type',
            'environment_type',
            'endpointinstancetopayload_set',
            'endpointinstancetopayload_set__payload_type',
            'endpointinstancetopayload_set__mime_type',
            'endpointinstancetootherid_set'
        ), pk=pk)

        serialized_endpoint = EndpointSerializer(endpoint)

        # Set appropriate content type for FHIR responses
        response = Response(serialized_endpoint.data)

        return response


class FHIRPractitionerViewSet(viewsets.GenericViewSet):
    """
    ViewSet for FHIR Practitioner resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PractitionerFilterSet
    pagination_class = CustomPaginator
    

    allowed_sorts = ['primary_last_name', 'primary_first_name', 'npi_value']


    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        sorts_value = self.request.query_params.get('_sort')
        if sorts_value:
            queryset = get_data_sorted(queryset, self.allowed_sorts, sorts_value)

        return queryset

    # permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[
            page_size_param,
            createFilterParam(
                'value (for any type of identifier) OR NPI|value (if searching for an NPI) -> 12345567 OR NPI|12345567'),
            createFilterParam('name'),
            createFilterParam('gender', enum=genderMapping.keys()),
            createFilterParam('practitioner_type'),
            createFilterParam('address'),
            createFilterParam('address-city', 'city'),
            createFilterParam('address-postalcode', "zip code"),
            createFilterParam(
                'address-state', '2 letter US State abbreviation'),
            createFilterParam('address-use', 'address use',
                              enum=addressUseMapping.keys()),
            createSortParam(['primary_last_name', 'primary_first_name', 'npi_value'])
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Practitioner resource cannot be found."}
    )
    def list(self, request):
        """
        Query a list of healthcare providers, represented as a bundle of FHIR Practitioner resources

        Default sort order: ascending last name, first name
        """
        # Subqueries for last_name and first_name of the individual
        primary_last_name_subquery = (
            IndividualToName.objects
            .filter(individual=OuterRef('individual'))
            .order_by('last_name')
            .values('last_name')[:1]
        )

        primary_first_name_subquery = (
            IndividualToName.objects
            .filter(individual=OuterRef('individual'))
            .order_by('first_name')
            .values('first_name')[:1]
        )

        providers = Provider.objects.all().prefetch_related(
            'npi', 'individual', 'individual__individualtoname_set', 'individual__individualtoaddress_set',
            'individual__individualtoaddress_set__address__address_us',
            'individual__individualtoaddress_set__address__address_us__state_code',
            'individual__individualtoaddress_set__address_use', 'individual__individualtophone_set',
            'individual__individualtoemail_set', 'providertootherid_set', 'providertotaxonomy_set'
        ).annotate(
            primary_last_name=Subquery(primary_last_name_subquery),
            primary_first_name=Subquery(primary_first_name_subquery),
            npi_value=F('npi__npi')
        ).order_by('primary_last_name', 'primary_first_name')

        providers = self.filter_queryset(providers)
        paginated_providers = self.paginate_queryset(providers)

        serialized_providers = PractitionerSerializer(
            paginated_providers, many=True)
        bundle = BundleSerializer(
            serialized_providers, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    def retrieve(self, request, pk=None):
        """
        Query a specific provider as a FHIR Practitioner resource
        """
        try:
            UUID(pk)
        except (ValueError, TypeError) as e:
            return HttpResponse(f"Practitioner {escape(pk)} not found", status=404)

        provider = get_object_or_404(
            Provider.objects.prefetch_related(
                'npi',
                'individual',
                'individual__individualtoname_set',
                'individual__individualtoaddress_set',
                'individual__individualtoaddress_set__address__address_us',
                'individual__individualtoaddress_set__address__address_us__state_code',
                'individual__individualtoaddress_set__address_use',
                'individual__individualtophone_set',
                'individual__individualtoemail_set',
                'providertootherid_set',
                'providertotaxonomy_set'
            ),
            individual_id=pk
        )

        serialized_practitioner = PractitionerSerializer(provider)

        # Set appropriate content type for FHIR responses
        response = Response(serialized_practitioner.data)

        return response


class FHIRPractitionerRoleViewSet(viewsets.GenericViewSet):
    """
    ViewSet for FHIR PractitionerRole resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PractitionerRoleFilterSet
    pagination_class = CustomPaginator

    allowed_sorts = ['location_name','practitioner_first_name','practitioner_last_name']


    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        sorts_value = self.request.query_params.get('_sort')
        if sorts_value:
            queryset = get_data_sorted(queryset, self.allowed_sorts, sorts_value)

        return queryset

    # permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[
            page_size_param,
            createFilterParam('active'),
            createFilterParam('role'),
            createFilterParam('practitioner.name'),
            createFilterParam('practitioner.gender', enum=[
                              'Female', 'Male', 'Other']),
            createFilterParam('practitioner.practitioner_type'),
            createFilterParam('organization.name'),
            createSortParam(['location_name','practitioner_first_name','practitioner_last_name'])
        ],
        responses={200: "Successful response",
                   404: "Error: The requested PractitionerRole resource cannot be found."}
    )
    def list(self, request):
        """
        Query a list of relationships between providers, healthcare organizations, and practice locations, represented as a bundle of FHIR PractitionerRole resources

        Default sort order: aschending by location name
        """
        page_size = default_page_size

        all_params = request.query_params

        primary_last_name_subquery = (
            IndividualToName.objects
                .filter(individual=OuterRef('provider_to_organization__individual__individual'))
                .order_by('last_name')
                .values('last_name')[:1]
        )

        primary_first_name_subquery = (
            IndividualToName.objects
                .filter(individual=OuterRef('provider_to_organization__individual__individual'))
                .order_by('first_name')
                .values('first_name')[:1]
        )


        practitionerroles = (
            ProviderToLocation.objects
            .select_related('location')
            .prefetch_related('provider_to_organization')
            .annotate(
                location_name=F('location__name'),
                practitioner_first_name=Subquery(primary_first_name_subquery),
                practitioner_last_name=Subquery(primary_last_name_subquery),
            )
            .order_by('location__name')
        ).all()

        practitionerroles = self.filter_queryset(practitionerroles)
        paginated_practitionerroles = self.paginate_queryset(practitionerroles)

        serialized_practitionerroles = PractitionerRoleSerializer(
            paginated_practitionerroles, many=True, context={"request": request})
        bundle = BundleSerializer(
            serialized_practitionerroles, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    def retrieve(self, request, pk=None):
        """
        Query a specific relationship between providers, healthcare organizations, and practice locations, represented as a FHIR PractitionerRole resource
        """
        try:
            UUID(pk)
        except (ValueError, TypeError) as e:
            return HttpResponse(f"PractitionerRole {escape(pk)} not found", status=404)

        practitionerrole = get_object_or_404(ProviderToLocation, pk=pk)

        serialized_practitionerrole = PractitionerRoleSerializer(
            practitionerrole, context={"request": request})

        # Set appropriate content type for FHIR responses
        response = Response(serialized_practitionerrole.data)

        return response


class FHIROrganizationViewSet(viewsets.GenericViewSet):
    """
    ViewSet for FHIR Organization resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrganizationFilterSet
    pagination_class = CustomPaginator

    allowed_sorts = ['primary_name']


    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        sorts_value = self.request.query_params.get('_sort')
        if sorts_value:
            queryset = get_data_sorted(queryset, self.allowed_sorts, sorts_value)

        return queryset

    # permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[
            page_size_param,
            createFilterParam('name'),
            createFilterParam(
                'identifier', 'format: value (for any type of identifier) OR NPI|value (if searching for an NPI) -> 12345567 OR NPI|12345567'),
            createFilterParam('organization_type'),
            createFilterParam('address'),
            createFilterParam('address-city', 'city'),
            createFilterParam('address-postalcode', "zip code"),
            createFilterParam(
                'address-state', '2 letter US State abbreviation'),
            createFilterParam('address-use', 'address use',
                              enum=addressUseMapping.keys()),
            createSortParam(['primary_name'])
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Organization resource cannot be found."}
    )
    def list(self, request):
        """
        Query a list of organizations, represented as a bundle of FHIR Practitioner resources

        Default sort order: ascending by organization name
        """
        primary_name_subquery = (
            OrganizationToName.objects
            .filter(organization=OuterRef('pk'), is_primary=True)
            .values('name')[:1]
        )

        organizations = Organization.objects.all().prefetch_related(
            'authorized_official',
            'ein',
            'organizationtoname_set',
            'organizationtoaddress_set',
            'organizationtoaddress_set__address',
            'organizationtoaddress_set__address__address_us',
            'organizationtoaddress_set__address__address_us__state_code',
            'organizationtoaddress_set__address_use',

            'authorized_official__individualtophone_set',
            'authorized_official__individualtoname_set',
            'authorized_official__individualtoemail_set',
            'authorized_official__individualtoaddress_set',
            'authorized_official__individualtoaddress_set__address__address_us',
            'authorized_official__individualtoaddress_set__address__address_us__state_code',

            'clinicalorganization',
            'clinicalorganization__npi',
            'clinicalorganization__organizationtootherid_set',
            'clinicalorganization__organizationtootherid_set__other_id_type',
            'clinicalorganization__organizationtotaxonomy_set',
            'clinicalorganization__organizationtotaxonomy_set__nucc_code'
        ).annotate(primary_name=Subquery(primary_name_subquery)).order_by('primary_name')

        organizations = self.filter_queryset(organizations)
        paginated_organizations = self.paginate_queryset(organizations)

        serialized_organizations = OrganizationSerializer(
            paginated_organizations, many=True)
        bundle = BundleSerializer(
            serialized_organizations, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    def retrieve(self, request, pk=None):
        """
        Query a specific organization, represented as a FHIR Organization resource
        """
        try:
            UUID(pk)
        except (ValueError, TypeError) as e:
            return HttpResponse(f"Organization {escape(pk)} not found", status=404)

        organization = get_object_or_404(Organization.objects.prefetch_related(
            'authorized_official',
            'ein',
            'organizationtoname_set',
            'organizationtoaddress_set',
            'organizationtoaddress_set__address',
            'organizationtoaddress_set__address__address_us',
            'organizationtoaddress_set__address__address_us__state_code',
            'organizationtoaddress_set__address_use',

            'authorized_official__individualtophone_set',
            'authorized_official__individualtoname_set',
            'authorized_official__individualtoemail_set',
            'authorized_official__individualtoaddress_set',
            'authorized_official__individualtoaddress_set__address__address_us',
            'authorized_official__individualtoaddress_set__address__address_us__state_code',

            'clinicalorganization',
            'clinicalorganization__npi',
            'clinicalorganization__organizationtootherid_set',
            'clinicalorganization__organizationtootherid_set__other_id_type',
            'clinicalorganization__organizationtotaxonomy_set',
            'clinicalorganization__organizationtotaxonomy_set__nucc_code'
        ),
            pk=pk)

        serialized_organization = OrganizationSerializer(organization)

        # Set appropriate content type for FHIR responses
        response = Response(serialized_organization.data)

        return response


class FHIRLocationViewSet(viewsets.GenericViewSet):
    """
    ViewSet for FHIR Location resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LocationFilterSet
    pagination_class = CustomPaginator

    allowed_sorts = ['organization_name','address_full','name']


    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        sorts_value = self.request.query_params.get('_sort')
        if sorts_value:
            queryset = get_data_sorted(queryset, self.allowed_sorts, sorts_value)

        return queryset

    # permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[
            page_size_param,
            createFilterParam('name'),
            createFilterParam('address'),
            createFilterParam('address-city', 'city'),
            createFilterParam('address-postalcode', "zip code"),
            createFilterParam(
                'address-state', '2 letter US State abbreviation'),
            createFilterParam('address-use', 'address use',
                              enum=addressUseMapping.keys()),
            createSortParam(['primary_name'])
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Location resource cannot be found."}
    )
    def list(self, request):
        """
        Query a list of healthcare practice locations, represented as bundle of FHIR Location resources

        Default sort order: ascending by location name
        """
        locations = (
            Location.objects.all()
            .select_related(
                "organization",
                "address__address_us",
                "address__address_us__state_code",
            )
            .annotate(
                organization_name=F("organization__organizationtoname__name"),
                address_full=Concat(
                    F("address__address_us__delivery_line_1"),
                    Value(", "),
                    F("address__address_us__city_name"),
                    Value(", "),
                    F("address__address_us__state_code__abbreviation"),
                    Value(" "),
                    F("address__address_us__zipcode"),
                    output_field=CharField(),
                ),
            ).order_by('name')
        )

        locations = self.filter_queryset(locations)
        paginated_locations = self.paginate_queryset(locations)

        # Serialize the bundle
        serialized_locations = LocationSerializer(
            paginated_locations, many=True, context={"request": request})
        bundle = BundleSerializer(
            serialized_locations, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    def retrieve(self, request, pk=None):
        """
        Query a specific healthcare practice location as a FHIR Location resource
        """
        try:
            UUID(pk)
        except (ValueError, TypeError) as e:
            return HttpResponse(f"Location {escape(pk)} not found", status=404)

        location = get_object_or_404(Location, pk=pk)

        serialized_location = LocationSerializer(
            location, context={"request": request})

        # Set appropriate content type for FHIR responses
        response = Response(serialized_location.data)

        return response


class FHIRCapabilityStatementView(APIView):
    """
    ViewSet for FHIR Practitioner resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]

    @swagger_auto_schema(
        responses={200: "Successful response",
                   404: "Error: The requested CapabilityStatement resource cannot be found."}
    )
    def get(self, request):
        """
        Query metadata about this FHIR instance, represented as FHIR CapabilityStatement resource
        """
        serializer = CapabilityStatementSerializer(
            context={"request": request})
        response = serializer.to_representation(None)

        return Response(response)
