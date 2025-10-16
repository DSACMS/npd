from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.postgres.search import SearchVector
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import BrowsableAPIRenderer
from django.core.cache import cache
from django.db.models import Q
from uuid import UUID
from .models import Provider, EndpointInstance, ClinicalOrganization, Organization
from .serializers import PractitionerSerializer, OrganizationSerializer, BundleSerializer, EndpointSerializer
from .mappings import genderMapping, addressUseMapping
from .renderers import FHIRRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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


def createFilterParam(field: str, display: str = None, enum: list = None):
    if display is None:
        display = field.replace('_', ' ')
    param = openapi.Parameter(
        field,
        openapi.IN_QUERY,
        description=f"Filter by {display}",
        type=openapi.TYPE_STRING,
    )
    if enum is not None:
        param.enum = enum
    return param


def parse_identifier(identifier_value):
    """
    Parse an identifier search parameter that should be in the format of "value" OR "system|value"
    
    Not sure the best way to document this but currently the only system are NPI, EIN or OtherID which could be anything... 
    I assume there will be more with further iterations so documenting this is a good idea.
    """
    if '|' in identifier_value:
        parts = identifier_value.split('|', 1)
        return (parts[0], parts[1])
    
    return (None, identifier_value)


def index(request):
    return HttpResponse("Connection to npd database: successful")


def health(request):
    return HttpResponse("healthy")


class FHIREndpointViewSet(viewsets.ViewSet):
    """
    ViewSet for FHIR Endpoint Resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]

    @swagger_auto_schema(
        manual_parameters=[
            page_size_param,
            createFilterParam('name'),
            createFilterParam('connection_type'),
            createFilterParam('payload_type'),
            createFilterParam('status'),
            createFilterParam('organization')
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Endpoint resource cannot be found."}
    )
    def list(self, request):
        """
        Returns a list of all endpoints as FHIR Endpoint resources
        """

        page_size = default_page_size
        all_params = request.query_params

        endpoints = EndpointInstance.objects.all().select_related(
            'endpoint_connection_type',
            'environment_type'
        ).prefetch_related(
            'endpointinstancetopayload_set',
            'endpointinstancetopayload_set__payload_type',
            'endpointinstancetopayload_set__mime_type',
            'endpointinstancetootherid_set'
        )

        for param, value in all_params.items():
            match param:
                case 'page_size':
                    try:
                        value = int(value)
                        if value <= max_page_size:
                            page_size = value
                    except:
                        page_size = page_size
                case 'name':
                    endpoints = endpoints.filter(name__icontains=value)
                case 'connection_type':
                    endpoints = endpoints.filter(
                        endpoint_connection_type__id__icontains=value)
                case 'payload_type':
                    endpoints = endpoints.filter(
                        endpointinstancetopayload__payload_type__id__icontains=value
                    ).distinct()
                case 'status':
                    pass
                case 'organization':
                    pass

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        queryset = paginator.paginate_queryset(endpoints, request)

        # Serialize the bundle
        serializer = EndpointSerializer(queryset, many=True)
        bundle = BundleSerializer(serializer)

        # Set appropriate content type for FHIR responses
        response = paginator.get_paginated_response(bundle.data)

        return response

    def retrieve(self, request, pk=None):
        """
        Return a single endpoint as a FHIR Endpoint resource 
        """

        endpoint = get_object_or_404(EndpointInstance, pk=pk)

        serializer = EndpointSerializer(endpoint)

        # Set appropriate content type for FHIR responses
        response = Response(serializer.data)

        return response


class FHIRPractitionerViewSet(viewsets.ViewSet):
    """
    ViewSet for FHIR Practitioner resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]

    # permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[
            page_size_param,
            createFilterParam('identifier', 'format: value OR system|value -> 12345567 OR NPI|12345567'),
            createFilterParam('name'),
            createFilterParam('gender', enum=genderMapping.keys()),
            createFilterParam('practitioner_type'),
            createFilterParam('address'),
            createFilterParam('address-city', 'city'),
            createFilterParam('address-postalcode', "zip code"),
            createFilterParam(
                'address-state', '2 letter US State abbreviation'),
            createFilterParam('address-use', 'address use',
                              enum=addressUseMapping.keys())
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Practitioner resource cannot be found."}
    )
    def list(self, request):
        """
        Return a list of all providers as FHIR Practitioner resources
        """
        page_size = default_page_size

        all_params = request.query_params

        providers = Provider.objects.all().prefetch_related(
            'npi', 
            'individual', 
            'individual__individualtoname_set', 
            'individual__individualtoaddress_set', 
            'individual__individualtoaddress_set__address__address_us', 
            'individual__individualtoaddress_set__address__address_us__state_code', 
            'individual__individualtoaddress_set__address_use', 
            'individual__individualtophone_set', '' \
            'individual__individualtoemail_set', 
            'providertootherid_set', 
            'providertotaxonomy_set')

        for param, value in all_params.items():
            match param:
                case 'page_size':
                    try:
                        value = int(value)
                        if value <= max_page_size:
                            page_size = value
                    except:
                        page_size = page_size
                case 'identifier':
                    system, identifier_id = parse_identifier(value)
                    queries = None

                    if system: # specific identifier search requested
                        if system == 'NPI':
                            try:
                                queries = Q(npi__npi=identifier_id)
                            except (ValueError, TypeError):
                                pass
                        else:
                            queries = Q(providertootherid__other_id=identifier_id)

                        if queries is None: # force return no results 
                            queries = Q(pk__isnull=True)

                    else: # general identifier search requested
                        queries = Q(pk__isnull=True) # start with empty match
                        queries = Q(providertootherid__other_id=identifier_id) | Q(npi__npi=identifier_id)
                    
                    providers = providers.filter(queries).distinct()
                case 'name':
                    providers = providers.annotate(
                        search=SearchVector('individual__individualtoname__last_name',
                                            'individual__individualtoname__first_name', 'individual__individualtoname__middle_name')
                    ).filter(search=value)
                case 'gender':
                    if value in genderMapping.keys():
                        value = genderMapping.toNPD(value)
                    providers = providers.filter(individual__gender=value)
                case 'practitioner_type':
                    providers = providers.annotate(
                        search=SearchVector(
                            'providertotaxonomy__nucc_code__display_name')
                    ).filter(search=value)
                case 'address':
                    providers = providers.annotate(
                        search=SearchVector(
                            'individual__individualtoaddress__address__address_us__delivery_line_1',
                            'individual__individualtoaddress__address__address_us__delivery_line_2',
                            'individual__individualtoaddress__address__address_us__city_name',
                            'individual__individualtoaddress__address__address_us__state_code__abbreviation',
                            'individual__individualtoaddress__address__address_us__zipcode',)
                    ).filter(search=value)
                case 'address-city':
                    providers = providers.annotate(
                        search=SearchVector(
                            'individual__individualtoaddress__address__address_us__city_name')
                    ).filter(search=value)
                case 'address-state':
                    providers = providers.annotate(
                        search=SearchVector(
                            'individual__individualtoaddress__address__address_us__state_code__abbreviation')
                    ).filter(search=value)
                case 'address-postalcode':
                    providers = providers.annotate(
                        search=SearchVector(
                            'individual__individualtoaddress__address__address_us__zipcode')
                    ).filter(search=value)
                case 'address-use':
                    if value in addressUseMapping.keys():
                        value = addressUseMapping.toNPD(value)
                    else:
                        value = -1
                    providers = providers.filter(
                        individual__individualtoaddress__address_use_id=value)

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        queryset = paginator.paginate_queryset(providers, request)

        # Serialize the bundle
        serializer = PractitionerSerializer(queryset, many=True)
        bundle = BundleSerializer(serializer)

        # Set appropriate content type for FHIR responses
        response = paginator.get_paginated_response(bundle.data)

        return response

    def retrieve(self, request, pk=None):
        """
        Return a single provider as a FHIR Practitioner resource
        """
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

        practitioner = PractitionerSerializer(provider)

        # Set appropriate content type for FHIR responses
        response = Response(practitioner.data)

        return response


class FHIROrganizationViewSet(viewsets.ViewSet):
    """
    ViewSet for FHIR Practitioner resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]

    # permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[
            page_size_param,
            createFilterParam('name'),
            createFilterParam('identifier', 'format: value OR system|value -> 12345567 OR NPI|12345567'),
            createFilterParam('organization_type'),
            createFilterParam('address'),
            createFilterParam('address-city', 'city'),
            createFilterParam('address-postalcode', "zip code"),
            createFilterParam(
                'address-state', '2 letter US State abbreviation'),
            createFilterParam('address-use', 'address use',
                              enum=addressUseMapping.keys())
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Organization resource cannot be found."}
    )
    def list(self, request):
        """
        Return a list of all providers as FHIR Practitioner resources
        """
        page_size = default_page_size

        all_params = request.query_params

        organizations = Organization.objects.all().select_related(
            'authorized_official',
            'ein'
        ).prefetch_related(
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
        )

        for param, value in all_params.items():
            match param:
                case 'page_size':
                    try:
                        value = int(value)
                        if value <= max_page_size:
                            page_size = value
                    except:
                        page_size = page_size
                case 'name':
                    organizations = organizations.annotate(
                        search=SearchVector(
                            'organizationtoname__name')
                    ).filter(search=value)
                case 'identifier':
                    system, identifier_id = parse_identifier(value)
                    queries = None

                    if system: # specific identifier search requested
                        if system == 'NPI':
                            try:
                                queries = Q(clinicalorganization__npi__npi=int(identifier_id))
                            except (ValueError, TypeError):
                                pass
                        elif system == 'EIN':
                            try: # need this block in order to pass pydantic validation
                                UUID(identifier_id)
                                queries = Q(ein__ein_id=identifier_id)
                            except (ValueError, TypeError):
                                pass
                        else:
                            queries = Q(clinicalorganization__organizationtootherid__other_id=identifier_id)

                        if queries is None: # force return no results 
                            queries = Q(pk__isnull=True)

                    else: # general identifier search requested
                        queries = Q(pk__isnull=True) # start with empty queryset

                        try:
                            queries |= Q(clinicalorganization__npi__npi=int(identifier_id))
                        except (ValueError, TypeError):
                            pass

                        try: # need this block in order to pass pydantic validation
                            UUID(identifier_id)
                            queries |= Q(ein__ein_id=identifier_id)
                        except (ValueError, TypeError):
                            pass

                        queries |= Q(clinicalorganization__organizationtootherid__other_id=identifier_id)
                    
                    organizations = organizations.filter(queries).distinct()
                case 'organization_type':
                    organizations = organizations.annotate(
                        search=SearchVector(
                            'clinicalorganization__organizationtotaxonomy__nucc_code__display_name')
                    ).filter(search=value)
                case 'address':
                    organizations = organizations.annotate(
                        search=SearchVector(
                            'organization__organizationtoaddress__address__address_us__delivery_line_1',
                            'organization__organizationtoaddress__address__address_us__delivery_line_2',
                            'organization__organizationtoaddress__address__address_us__city_name',
                            'organization__organizationtoaddress__address__address_us__state_code__abbreviation',
                            'organization__organizationtoaddress__address__address_us__zipcode',)
                    ).filter(search=value)
                case 'address-city':
                    organizations = organizations.annotate(
                        search=SearchVector(
                            'organization__organizationtoaddress__address__address_us__city_name')
                    ).filter(search=value)
                case 'address-state':
                    organizations = organizations.annotate(
                        search=SearchVector(
                            'organization__organizationtoaddress__address__address_us__state_code__abbreviation')
                    ).filter(search=value)
                case 'address-postalcode':
                    organizations = organizations.annotate(
                        search=SearchVector(
                            'organization__organizationtoaddress__address__address_us__zipcode')
                    ).filter(search=value)
                case 'address-use':
                    if value in addressUseMapping.keys():
                        value = addressUseMapping.toNPD(value)
                    else:
                        value = -1
                    organizations = organizations.filter(
                        organization__organizationtoaddress__address_use_id=value)

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        queryset = paginator.paginate_queryset(organizations, request)

        # Serialize the bundle
        serializer = OrganizationSerializer(queryset, many=True)
        bundle = BundleSerializer(serializer)

        # Set appropriate content type for FHIR responses
        response = paginator.get_paginated_response(bundle.data)

        return response

    def retrieve(self, request, pk=None):
        """
        Return a single provider as a FHIR Practitioner resource
        """
        clinicalorg = get_object_or_404(Organization.objects.select_related(
            'authorized_official',
            'ein'
        ).prefetch_related(
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

        organization = OrganizationSerializer(clinicalorg)

        # Set appropriate content type for FHIR responses
        response = Response(organization.data)

        return response
