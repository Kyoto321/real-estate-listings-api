from rest_framework import viewsets
from listings.filters import ListingFilter
from listings.models import Listing
from listings.serializers import ListingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    CRUD & Search ViewSet for property listings.
    Supports attribute filtering (type, price, bedrooms) and PostGIS radius search.
    """

    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filterset_class = ListingFilter
