import uuid
from django.contrib.gis.db import models as gis_models
from django.db import models


class ListingType(models.TextChoices):
    RENT = "rent", "Rent"
    SALE = "sale", "Sale"
    SHORTLET = "shortlet", "Shortlet"


class Listing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    listing_type = models.CharField(max_length=20, choices=ListingType.choices)
    bedrooms = models.PositiveSmallIntegerField()

    # Spatial geography point field storing (longitude, latitude) in SRID 4326 (WGS 84 spheroid)
    location = gis_models.PointField(srid=4326, geography=True)

    agent_id = models.UUIDField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # Compound index for common search combination: type + bedrooms
            models.Index(fields=["listing_type", "bedrooms"]),
            # Index for price filtering & range queries
            models.Index(fields=["price"]),
        ]
        constraints = [
            # Ensure price cannot be 0 or negative at the database level
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="listing_price_must_be_positive",
            ),
        ]

    def __str__(self):
        return f"{self.title} ({self.listing_type} - ${self.price})"
