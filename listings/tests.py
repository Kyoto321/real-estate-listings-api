import uuid
from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.test import APITestCase
from listings.models import Listing


class ListingAPITestCase(APITestCase):
    def setUp(self):
        self.agent_id = str(uuid.uuid4())
        # Victoria Island, Lagos (6.4281, 3.4219)
        self.vi_listing = Listing.objects.create(
            title="VI Luxury Apartment",
            price=150000.00,
            listing_type="rent",
            bedrooms=2,
            location=Point(3.4219, 6.4281, srid=4326),
            agent_id=self.agent_id,
        )
        # Ikoyi (~3.5km from VI: 6.4549, 3.4246)
        self.ikoyi_listing = Listing.objects.create(
            title="Ikoyi Mansion",
            price=850000.00,
            listing_type="sale",
            bedrooms=4,
            location=Point(3.4246, 6.4549, srid=4326),
            agent_id=self.agent_id,
        )
        # Ikeja (~20km from VI: 6.6018, 3.3515)
        self.ikeja_listing = Listing.objects.create(
            title="Ikeja Studio",
            price=50000.00,
            listing_type="rent",
            bedrooms=1,
            location=Point(3.3515, 6.6018, srid=4326),
            agent_id=self.agent_id,
        )

    def test_create_listing_success(self):
        payload = {
            "title": "Lekki Phase 1 Villa",
            "price": "300000.00",
            "listing_type": "sale",
            "bedrooms": 3,
            "latitude": 6.4474,
            "longitude": 3.4723,
            "agent_id": str(uuid.uuid4()),
        }
        response = self.client.post("/api/listings/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Lekki Phase 1 Villa")
        self.assertEqual(response.data["latitude"], 6.4474)
        self.assertEqual(response.data["longitude"], 3.4723)

    def test_create_listing_validation_error(self):
        payload = {
            "title": "Invalid Price Listing",
            "price": "-500.00",
            "listing_type": "rent",
            "bedrooms": 2,
            "latitude": 6.4281,
            "longitude": 3.4219,
            "agent_id": str(uuid.uuid4()),
        }
        response = self.client.post("/api/listings/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_retrieve_listing(self):
        url = f"/api/listings/{self.vi_listing.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "VI Luxury Apartment")

    def test_update_listing(self):
        url = f"/api/listings/{self.vi_listing.id}/"
        payload = {"price": "175000.00"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["price"]), 175000.00)

    def test_delete_listing(self):
        url = f"/api/listings/{self.vi_listing.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Listing.objects.filter(id=self.vi_listing.id).exists())

    def test_attribute_filtering(self):
        response = self.client.get("/api/listings/?type=rent&min_price=100000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "VI Luxury Apartment")

    def test_postgis_radius_search(self):
        # Radius search 5km from Victoria Island (6.4281, 3.4219)
        response = self.client.get("/api/listings/?latitude=6.4281&longitude=3.4219&radius=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        titles = [item["title"] for item in response.data["results"]]
        # Should return VI Luxury Apartment first (closest), then Ikoyi Mansion
        self.assertEqual(titles, ["VI Luxury Apartment", "Ikoyi Mansion"])

    def test_postgis_radius_search_larger_distance(self):
        # Radius search 25km from Victoria Island should include Ikeja
        response = self.client.get("/api/listings/?latitude=6.4281&longitude=3.4219&radius=25")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
