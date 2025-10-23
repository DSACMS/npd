from uuid import UUID

from django.contrib.postgres.search import SearchVector
from django.core.cache import cache
from django.db.models import Q, OuterRef, Subquery
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from .mappings import addressUseMapping, genderMapping
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
from .renderers import FHIRRenderer
from .serializers import (
    BundleSerializer,
    EndpointSerializer,
    LocationSerializer,
    OrganizationSerializer,
    PractitionerRoleSerializer,
    PractitionerSerializer,
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


def parse_identifier(identifier_value):
    """
    Parse an identifier search parameter that should be in the format of "value" OR "system|value".
    Currently only supporting NPI search "NPI|123455".
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

        Sorts by the name of the EndpointInstance
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
        ).order_by('name')

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
        paginated_endpoints = paginator.paginate_queryset(endpoints, request)

        # Serialize the bundle
        serialized_endpoints = EndpointSerializer(
            paginated_endpoints, many=True)
        bundle = BundleSerializer(
            serialized_endpoints, context={"request": request})

        # Set appropriate content type for FHIR responses
        response = paginator.get_paginated_response(bundle.data)

        return response

    def retrieve(self, request, pk=None):
        """
        Return a single endpoint as a FHIR Endpoint resource
        """

        try:
            UUID(pk)
        except (ValueError, TypeError) as e:
            return HttpResponse(f"Endpoint {escape(pk)} not found", status=404)

        endpoint = get_object_or_404(EndpointInstance, pk=pk)

        serialized_endpoint = EndpointSerializer(endpoint)

        # Set appropriate content type for FHIR responses
        response = Response(serialized_endpoint.data)

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
                              enum=addressUseMapping.keys())
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Practitioner resource cannot be found."}
    )
    def list(self, request):
        """
        Return a list of all providers as FHIR Practitioner resources

        Sorts by lastname, firstname
        """
        page_size = default_page_size

        all_params = request.query_params

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
            primary_first_name=Subquery(primary_first_name_subquery)
        ).order_by('primary_last_name','primary_first_name')

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
                    queries = Q(pk__isnull=True)

                    if system:  # specific identifier search requested
                        if system == 'NPI':
                            try:
                                queries = Q(npi__npi=identifier_id)
                            except (ValueError, TypeError):
                                pass
                    else:  # general identifier search requested
                        try:
                            queries |= Q(npi__npi=int(identifier_id))
                        except (ValueError, TypeError):
                            pass

                        queries |= Q(providertootherid__other_id=identifier_id)

                    providers = providers.filter(queries).distinct()
                case 'name':
                    providers = providers.annotate(
                        search=SearchVector('individual__individualtoname__last_name',
                                            'individual__individualtoname__first_name',
                                            'individual__individualtoname__middle_name')
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
                            'individual__individualtoaddress__address__address_us__zipcode', )
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
        paginated_providers = paginator.paginate_queryset(providers, request)

        # Serialize the bundle
        serialized_providers = PractitionerSerializer(
            paginated_providers, many=True)
        bundle = BundleSerializer(
            serialized_providers, context={"request": request})

        # Set appropriate content type for FHIR responses
        response = paginator.get_paginated_response(bundle.data)

        return response

    def retrieve(self, request, pk=None):
        """
        Return a single provider as a FHIR Practitioner resource
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


class FHIRPractitionerRoleViewSet(viewsets.ViewSet):
    """
    ViewSet for FHIR PractitionerRole resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]

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
            createFilterParam('organization.name')
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Practitioner resource cannot be found."}
    )
    def list(self, request):
        """
        Return a list of all providers as FHIR Practitioner resources

        Sorts the list by the name of the location
        """
        page_size = default_page_size

        all_params = request.query_params

        practitionerroles = (
            ProviderToLocation.objects
            .select_related('location')
            .prefetch_related('provider_to_organization')
            .order_by('location__name')
        ).all()

        for param, value in all_params.items():
            match param:
                case 'page_size':
                    try:
                        value = int(value)
                        if value <= max_page_size:
                            page_size = value
                    except:
                        page_size = page_size
                case 'practitioner.name':
                    practitionerroles = practitionerroles.annotate(
                        search=SearchVector(
                            'provider_to_organization__individual__individual__individualtoname__first_name',
                            'provider_to_organization__individual__individual__individualtoname__last_name',
                            'provider_to_organization__individual__individual__individualtoname__middle_name')).filter(search=value)
                case 'practitioner.gender':
                    gender = genderMapping.toNPD(value)
                    practitionerroles = practitionerroles.filter(
                        provider__individual__gender=gender)
                case 'practitioner.practitioner_type':
                    practitionerroles = practitionerroles.annotate(
                        search=SearchVector(
                            'provider_to_organization__providertotaxonomy__nucc_code__display_name')
                    ).filter(search=value)
                case 'organization.name':
                    practitionerroles = practitionerroles.annotate(
                        search=SearchVector(
                            'provider_to_organization__organization__organizationtoname__name')
                    ).filter(search=value)

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_practitionerroles = paginator.paginate_queryset(
            practitionerroles, request)

        # Serialize the bundle
        serialized_practitionerroles = PractitionerRoleSerializer(
            paginated_practitionerroles, many=True, context={"request": request})
        bundle = BundleSerializer(
            serialized_practitionerroles, context={"request": request})

        # Set appropriate content type for FHIR responses
        response = paginator.get_paginated_response(bundle.data)
        response["Content-Type"] = "application/fhir+json"

        return response

    def retrieve(self, request, pk=None):
        """
        Return a single provider as a FHIR Practitioner resource
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
        response["Content-Type"] = "application/fhir+json"

        return response


class FHIROrganizationViewSet(viewsets.ViewSet):
    """
    ViewSet for FHIR Organization resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]

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
                              enum=addressUseMapping.keys())
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Organization resource cannot be found."}
    )
    def list(self, request):
        """
        Return a list of all providers as FHIR Practitioner resources

        Sorts by the name of the organization
        """
        page_size = default_page_size

        all_params = request.query_params

        primary_name_subquery = (
            OrganizationToName.objects
            .filter(organization=OuterRef('pk'), is_primary=True)
            .values('name')[:1]
        )

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
        ).annotate(primary_name=Subquery(primary_name_subquery)).order_by('primary_name')

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
                    queries = Q(pk__isnull=True)

                    if system:  # specific identifier search requested
                        if system == 'NPI':
                            try:
                                queries = Q(
                                    clinicalorganization__npi__npi=int(identifier_id))
                            except (ValueError, TypeError):
                                pass  # TODO: implement validationerror to show users that NPI must be an int
                    else:  # general identifier search requested
                        try:
                            queries |= Q(
                                clinicalorganization__npi__npi=int(identifier_id))
                        except (ValueError, TypeError):
                            pass

                        try:  # need this block in order to pass pydantic validation
                            UUID(identifier_id)
                            queries |= Q(ein__ein_id=identifier_id)
                        except (ValueError, TypeError):
                            pass

                        queries |= Q(
                            clinicalorganization__organizationtootherid__other_id=identifier_id)

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
                            'organization__organizationtoaddress__address__address_us__zipcode', )
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
        paginated_organizations = paginator.paginate_queryset(
            organizations, request)

        # Serialize the bundle
        serialized_organizations = OrganizationSerializer(
            paginated_organizations, many=True)
        bundle = BundleSerializer(
            serialized_organizations, context={"request": request})

        # Set appropriate content type for FHIR responses
        response = paginator.get_paginated_response(bundle.data)

        return response

    def retrieve(self, request, pk=None):
        """
        Return a single provider as a FHIR Practitioner resource
        """
        try:
            UUID(pk)
        except (ValueError, TypeError) as e:
            return HttpResponse(f"Organization {escape(pk)} not found", status=404)

        organization = get_object_or_404(Organization.objects.select_related(
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

        serialized_organization = OrganizationSerializer(organization)

        # Set appropriate content type for FHIR responses
        response = Response(serialized_organization.data)

        return response


class FHIRLocationViewSet(viewsets.ViewSet):
    """
    ViewSet for FHIR Location resources
    """
    renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]

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
                              enum=addressUseMapping.keys())
        ],
        responses={200: "Successful response",
                   404: "Error: The requested Organization resource cannot be found."}
    )
    def list(self, request):
        """
        Return a list of all providers as FHIR Practitioner resources

        Sorts by the name of the location
        """
        page_size = default_page_size

        all_params = request.query_params

        locations = Location.objects.all().prefetch_related(
            'address__address_us', 'address__address_us__state_code'
        ).order_by('name')

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
                    locations = locations.filter(
                        name=value)
                case 'organization_type':
                    locations = locations.annotate(
                        search=SearchVector(
                            'organizationtotaxonomy__nucc_code__display_name')
                    ).filter(search=value)
                case 'address':
                    locations = locations.annotate(
                        search=SearchVector(
                            'address__address_us__delivery_line_1',
                            'address__address_us__delivery_line_2',
                            'address__address_us__city_name',
                            'address__address_us__state_code__abbreviation',
                            'address__address_us__zipcode',)
                    ).filter(search=value)
                case 'address-city':
                    locations = locations.annotate(
                        search=SearchVector(
                            'address__address_us__city_name')
                    ).filter(search=value)
                case 'address-state':
                    locations = locations.annotate(
                        search=SearchVector(
                            'address__address_us__state_code__abbreviation')
                    ).filter(search=value)
                case 'address-postalcode':
                    locations = locations.annotate(
                        search=SearchVector(
                            'address__address_us__zipcode')
                    ).filter(search=value)
                case 'address-use':
                    if value in addressUseMapping.keys():
                        value = addressUseMapping.toNPD(value)
                    else:
                        value = -1
                    locations = locations.filter(
                        address_use_id=value)

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_locations = paginator.paginate_queryset(locations, request)

        # Serialize the bundle
        serialized_locations = LocationSerializer(
            paginated_locations, many=True, context={"request": request})
        bundle = BundleSerializer(
            serialized_locations, context={"request": request})

        # Set appropriate content type for FHIR responses
        response = paginator.get_paginated_response(bundle.data)

        return response

    def retrieve(self, request, pk=None):
        """
        Return a single provider as a FHIR Practitioner resource
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
