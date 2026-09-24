from django.contrib.gis.geos import Point
from rest_framework import serializers
from listings.models import Listing, ListingType


class ListingSerializer(serializers.ModelSerializer):
    # Flat representation for coordinates (easier for API consumers than raw GeoJSON)
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "price",
            "listing_type",
            "bedrooms",
            "latitude",
            "longitude",
            "agent_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        """Include latitude and longitude flat fields in response output."""
        representation = super().to_representation(instance)
        if instance.location:
            # PostGIS Point stores coordinates as Point(longitude, latitude)
            representation["latitude"] = instance.location.y
            representation["longitude"] = instance.location.x
        return representation

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_bedrooms(self, value):
        if value < 0:
            raise serializers.ValidationError("Bedrooms cannot be negative.")
        return value

    def validate_latitude(self, value):
        if value < -90.0 or value > 90.0:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if value < -180.0 or value > 180.0:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value

    def validate(self, attrs):
        """Ensure both latitude and longitude are supplied when creating a listing or updating location."""
        latitude = attrs.get("latitude")
        longitude = attrs.get("longitude")

        # On POST (creation), both coordinates are required
        if self.instance is None:
            if latitude is None or longitude is None:
                raise serializers.ValidationError(
                    {"location": "Both latitude and longitude are required."}
                )
        
        # On PATCH or POST: if one coordinate is supplied, both must be provided together
        if (latitude is not None and longitude is None) or (
            longitude is not None and latitude is None
        ):
            raise serializers.ValidationError(
                {"location": "Both latitude and longitude must be provided together."}
            )

        # Convert valid lat/lng pair into GeoDjango Point
        if latitude is not None and longitude is not None:
            # Point takes (x=longitude, y=latitude)
            attrs["location"] = Point(x=longitude, y=latitude, srid=4326)
            # Remove write_only helper fields so serializer doesn't pass them to Listing model
            attrs.pop("latitude", None)
            attrs.pop("longitude", None)

        return attrs
