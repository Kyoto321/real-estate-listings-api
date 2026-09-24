import uuid
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from listings.models import Listing, ListingType


class Command(BaseCommand):
    help = "Seeds the database with sample property listings for testing and evaluation."

    def handle(self, *args, **options):
        self.stdout.write("Seeding listings...")

        # Clear existing listings
        Listing.objects.all().delete()

        agent_1 = uuid.uuid4()
        agent_2 = uuid.uuid4()

        sample_listings = [
            # Victoria Island, Lagos
            {
                "title": "Luxury Penthouse in Victoria Island",
                "price": 250000.00,
                "listing_type": ListingType.SALE,
                "bedrooms": 4,
                "location": Point(3.4219, 6.4281, srid=4326),
                "agent_id": agent_1,
            },
            {
                "title": "Modern 2-Bed Serviced Flat in VI",
                "price": 120000.00,
                "listing_type": ListingType.RENT,
                "bedrooms": 2,
                "location": Point(3.4250, 6.4310, srid=4326),
                "agent_id": agent_1,
            },
            # Ikoyi (~3-4 km from VI)
            {
                "title": "Waterfront Villa in Ikoyi",
                "price": 850000.00,
                "listing_type": ListingType.SALE,
                "bedrooms": 5,
                "location": Point(3.4246, 6.4549, srid=4326),
                "agent_id": agent_2,
            },
            {
                "title": "Shortlet Executive Suite in Ikoyi",
                "price": 45000.00,
                "listing_type": ListingType.SHORTLET,
                "bedrooms": 1,
                "location": Point(3.4300, 6.4520, srid=4326),
                "agent_id": agent_2,
            },
            # Lekki Phase 1 (~8 km from VI)
            {
                "title": "Contemporary Duplex in Lekki Phase 1",
                "price": 350000.00,
                "listing_type": ListingType.SALE,
                "bedrooms": 4,
                "location": Point(3.4723, 6.4474, srid=4326),
                "agent_id": agent_1,
            },
            # Ikeja (~20 km from VI)
            {
                "title": "Cosy 3-Bed Apartment in GRA Ikeja",
                "price": 95000.00,
                "listing_type": ListingType.RENT,
                "bedrooms": 3,
                "location": Point(3.3515, 6.6018, srid=4326),
                "agent_id": agent_2,
            },
            {
                "title": "Studio Flat near Ikeja City Mall",
                "price": 35000.00,
                "listing_type": ListingType.SHORTLET,
                "bedrooms": 1,
                "location": Point(3.3580, 6.6050, srid=4326),
                "agent_id": agent_1,
            },
        ]

        listings = [Listing(**item) for item in sample_listings]
        Listing.objects.bulk_create(listings)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully seeded {len(listings)} sample listings!")
        )
