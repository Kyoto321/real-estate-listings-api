# Real Estate Property Listings API

A production-minded, high-performance RESTful API for property listings built with **Python 3.12**, **Django REST Framework (DRF)**, and **PostgreSQL / PostGIS**.

Supports full CRUD capabilities, attribute filtering, pagination, strict input validation, and **Geospatial Radius Search** ordered by proximity using PostGIS spatial indexes.

---

## Tech Stack & Architecture

- **Framework**: Django 5.1 & Django REST Framework 3.15
- **Database**: PostgreSQL 16 + PostGIS 3.4 (`django.contrib.gis`)
- **Geospatial Engine**: PostGIS `geography` type (`PointField(srid=4326, geography=True)`) using Spatial GiST indexing
- **Environment & Containerization**: Docker & Docker Compose
- **Testing**: `pytest` & `pytest-django`

---

## Project Structure

```text
realEstate/
├── config/             # Project settings, WSGI, root URLs
│   ├── settings.py
│   └── urls.py
├── listings/           # Core domain app
│   ├── models.py       # Listing model with PostGIS PointField & CheckConstraints
│   ├── serializers.py  # DRF serializer with flat (lat, lng) mapping & validation
│   ├── views.py        # ListingViewSet for CRUD & filtering
│   ├── filters.py      # ListingFilter (Attribute filters + PostGIS radius search)
│   ├── urls.py         # DRF DefaultRouter routes
│   └── tests.py        # Comprehensive unit & integration tests
├── docker-compose.yml  # Multi-container orchestration (Django + PostGIS)
├── Dockerfile          # Debian-slim image with GDAL/GEOS system libraries
├── requirements.txt    # Python dependencies
├── pytest.ini          # Pytest runner configuration
└── README.md
```

---

## Setup & Running with Docker

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### 1. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` values:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgis://postgres:postgres@db:5432/realestate_db
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,testserver
```

### 2. Launch Containers
Build and start the PostGIS database and Django web container:
```bash
docker-compose up --build
```
The API server will run at **`http://localhost:8001/`**.

### 3. Run Database Migrations
In a second terminal:
```bash
docker-compose exec web python manage.py migrate
```

---

## Running Tests

Run the test suite inside the container using `pytest` or Django test runner:

```bash
# Run tests with Pytest
docker-compose exec web pytest

# Or run with Django test runner
docker-compose exec web python manage.py test
```

---

## API Endpoints & Usage

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/listings/` | Create a new property listing |
| `GET` | `/api/listings/` | List, page, search, and filter listings |
| `GET` | `/api/listings/{id}/` | Retrieve detail of a single listing |
| `PATCH` | `/api/listings/{id}/` | Partial update a listing |
| `PUT` | `/api/listings/{id}/` | Full update a listing |
| `DELETE` | `/api/listings/{id}/` | Delete a listing |

---

### Example Requests

#### 1. Create a Listing (`POST /api/listings/`)
```bash
curl -X POST http://localhost:8001/api/listings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Victoria Island Penthouse",
    "price": "250000.00",
    "listing_type": "sale",
    "bedrooms": 3,
    "latitude": 6.4281,
    "longitude": 3.4219,
    "agent_id": "76fef760-4871-4eb8-8eaa-128a9787c6fb"
  }'
```
**Response (201 Created)**:
```json
{
  "id": "88c3cac9-cb7f-493a-af4f-3d0967bb9763",
  "title": "Victoria Island Penthouse",
  "price": "250000.00",
  "listing_type": "sale",
  "bedrooms": 3,
  "latitude": 6.4281,
  "longitude": 3.4219,
  "agent_id": "76fef760-4871-4eb8-8eaa-128a9787c6fb",
  "created_at": "2026-09-23T12:12:14.884430-05:00",
  "updated_at": "2026-09-23T12:12:14.884482-05:00"
}
```

#### 2. Attribute Search & Filtering (`GET /api/listings/`)
Filter by `type` (`rent`/`sale`/`shortlet`), `min_price`, `max_price`, and `bedrooms`:
```bash
curl "http://localhost:8001/api/listings/?type=sale&min_price=100000&max_price=300000&bedrooms=3"
```

#### 3. Geospatial Radius Search (`GET /api/listings/`)
Find listings within `radius` kilometers of a given `latitude` and `longitude`:
```bash
curl "http://localhost:8001/api/listings/?latitude=6.4281&longitude=3.4219&radius=5"
```
*Note: Radius search results are automatically annotated with distance and sorted by proximity (nearest listings first).*

---

## Design Decisions

1. **PostGIS `geography` Column**: Using `PointField(srid=4326, geography=True)` calculates true geodesic distances in meters on the WGS 84 ellipsoid, backed by PostGIS spatial GiST indexing (`ST_DWithin`).
2. **Flat Coordinate API Interface**: The API exposes `latitude` and `longitude` flat fields instead of raw GeoJSON objects, providing a developer-friendly REST interface.
3. **Database Guardrails**: Price positivity (`price > 0`) is enforced at both the DRF serializer layer and the PostgreSQL database level (`CheckConstraint`).
4. **UUID Primary Keys**: Prevents sequential ID enumeration attacks and works seamlessly across distributed architectures.

---

## Future Improvements (With More Time)

1. **Authentication & Authorization**: Add JWT (`djangorestframework-simplejwt`) for agent-based ownership permissions (agents can edit/delete only their own listings).
2. **API Documentation**: Add OpenAPI / Swagger spec generation via `drf-spectacular`.
3. **Caching**: Redis caching for popular geospatial search bounding boxes and frequency-filtered queries.
4. **Rate Limiting**: Throttling on search endpoints (`ScopedRateThrottle`) to prevent abuse.
