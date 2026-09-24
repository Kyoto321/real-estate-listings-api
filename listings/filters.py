import django_filters
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework.exceptions import ValidationError
from listings.models import Listing, ListingType


class ListingFilter(django_filters.FilterSet):
    type = django_filters.ChoiceFilter(field_name="listing_type", choices=ListingType.choices)
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    bedrooms = django_filters.NumberFilter(field_name="bedrooms")

    # Virtual query parameters for radius search
    latitude = django_filters.NumberFilter(method="filter_by_radius")
    longitude = django_filters.NumberFilter(method="filter_by_radius")
    radius = django_filters.NumberFilter(method="filter_by_radius")

    class Meta:
        model = Listing
        fields = ["type", "min_price", "max_price", "bedrooms"]

    def filter_by_radius(self, queryset, name, value):
        """
        Geospatial search for listings within `radius` kilometers of (latitude, longitude).
        Ensures all 3 parameters are supplied together and validates values.
        """
        # Guard to prevent running the spatial query 3 times (once per field)
        if getattr(self, "_radius_filtered", False):
            return queryset
        self._radius_filtered = True

        params = self.request.query_params
        lat_raw = params.get("latitude")
        lng_raw = params.get("longitude")
        radius_raw = params.get("radius")

        # If none of the geo params are provided, return unfiltered queryset
        if not lat_raw and not lng_raw and not radius_raw:
            return queryset

        # Require all 3 parameters together
        if not (lat_raw and lng_raw and radius_raw):
            raise ValidationError(
                {"geo_search": "To perform a radius search, 'latitude', 'longitude', and 'radius' (in km) must all be provided."}
            )

        try:
            lat = float(lat_raw)
            lng = float(lng_raw)
            radius_km = float(radius_raw)
        except ValueError:
            raise ValidationError({"geo_search": "Latitude, longitude, and radius must be valid numbers."})

        if lat < -90.0 or lat > 90.0 or lng < -180.0 or lng > 180.0:
            raise ValidationError({"geo_search": "Latitude must be between -90 and 90, and longitude between -180 and 180."})

        if radius_km <= 0:
            raise ValidationError({"geo_search": "Radius must be greater than zero."})

        # Create PostGIS Point (x=longitude, y=latitude)
        origin_point = Point(x=lng, y=lat, srid=4326)

        # Use PostGIS `dwithin` spatial lookup with GeoDjango's Distance object
        # Annotate distance so results are sorted by proximity
        return (
            queryset.filter(location__dwithin=(origin_point, D(km=radius_km)))
            .annotate(distance=Distance("location", origin_point))
            .order_by("distance")
        )
