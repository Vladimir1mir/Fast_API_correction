import tempfile
import unittest
from pathlib import Path

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.app import app as fastapi_app
from app.models import Base
from app.routes.dependencies import get_db_session


class AdvertisementAPITestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.db"
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        async def override_get_db_session():
            async with self.session_factory() as session:
                yield session

        fastapi_app.dependency_overrides[get_db_session] = override_get_db_session
        self.client = AsyncClient(
            transport=ASGITransport(app=fastapi_app),
            base_url="http://testserver",
        )

    async def asyncTearDown(self):
        await self.client.aclose()
        fastapi_app.dependency_overrides.clear()
        await self.engine.dispose()
        self.temp_dir.cleanup()

    async def create_advertisement(self, **payload):
        response = await self.client.post("/advertisement", json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    async def test_openapi_contract(self):
        response = await self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()

        self.assertEqual(
            set(body["paths"].keys()),
            {"/advertisement", "/advertisement/{advertisement_id}"},
        )
        schema = body["components"]["schemas"]["GetAdvertisementResponse"]["properties"]
        self.assertIn("title", schema)
        self.assertNotIn("name", schema)

    async def test_crud_lifecycle(self):
        created = await self.create_advertisement(
            title="Bike sale",
            description="Red bike in good condition",
            price=100,
            author="Petya Pypkin",
        )
        advertisement_id = created["id"]

        get_response = await self.client.get(f"/advertisement/{advertisement_id}")
        self.assertEqual(get_response.status_code, 200, get_response.text)
        advertisement = get_response.json()
        self.assertEqual(advertisement["title"], "Bike sale")
        self.assertEqual(advertisement["description"], "Red bike in good condition")
        self.assertEqual(advertisement["price"], 100)
        self.assertEqual(advertisement["author"], "Petya Pypkin")
        self.assertIn("date_of_creation", advertisement)

        patch_response = await self.client.patch(
            f"/advertisement/{advertisement_id}",
            json={"title": "Bike sale updated", "price": 120},
        )
        self.assertEqual(patch_response.status_code, 200, patch_response.text)
        updated = patch_response.json()
        self.assertEqual(updated["id"], advertisement_id)
        self.assertEqual(updated["title"], "Bike sale updated")
        self.assertEqual(updated["price"], 120)
        self.assertEqual(updated["description"], "Red bike in good condition")

        delete_response = await self.client.delete(f"/advertisement/{advertisement_id}")
        self.assertEqual(delete_response.status_code, 200, delete_response.text)
        self.assertEqual(delete_response.json(), {"status": "ok"})

        missing_response = await self.client.get(f"/advertisement/{advertisement_id}")
        self.assertEqual(missing_response.status_code, 404, missing_response.text)
        self.assertEqual(missing_response.json(), {"detail": "Advertisement not found"})

    async def test_search_filters(self):
        first = await self.create_advertisement(
            title="Bike sale",
            description="Red bike in good condition",
            price=100,
            author="Petya Pypkin",
        )
        second = await self.create_advertisement(
            title="Laptop sale",
            description="Gaming laptop with RTX",
            price=1500,
            author="Vasya Pupkin",
        )

        all_response = await self.client.get("/advertisement")
        self.assertEqual(all_response.status_code, 200, all_response.text)
        self.assertEqual(len(all_response.json()), 2)

        author_response = await self.client.get("/advertisement", params={"author": "Petya"})
        self.assertEqual(author_response.status_code, 200, author_response.text)
        self.assertEqual([item["id"] for item in author_response.json()], [first["id"]])

        title_response = await self.client.get("/advertisement", params={"title": "bike"})
        self.assertEqual(title_response.status_code, 200, title_response.text)
        self.assertEqual([item["id"] for item in title_response.json()], [first["id"]])

        price_response = await self.client.get(
            "/advertisement",
            params={"price_min": 200, "price_max": 2000},
        )
        self.assertEqual(price_response.status_code, 200, price_response.text)
        self.assertEqual([item["id"] for item in price_response.json()], [second["id"]])

        combined_response = await self.client.get(
            "/advertisement",
            params={"author": "Vasya", "title": "laptop"},
        )
        self.assertEqual(combined_response.status_code, 200, combined_response.text)
        self.assertEqual([item["id"] for item in combined_response.json()], [second["id"]])

        empty_response = await self.client.get("/advertisement", params={"author": "No such author"})
        self.assertEqual(empty_response.status_code, 200, empty_response.text)
        self.assertEqual(empty_response.json(), [])

    async def test_create_validation_errors(self):
        empty_title_response = await self.client.post(
            "/advertisement",
            json={
                "title": "",
                "description": "Valid description",
                "price": 100,
                "author": "Petya Pypkin",
            },
        )
        self.assertEqual(empty_title_response.status_code, 422, empty_title_response.text)

        blank_title_response = await self.client.post(
            "/advertisement",
            json={
                "title": " ",
                "description": "Valid description",
                "price": 100,
                "author": "Petya Pypkin",
            },
        )
        self.assertEqual(blank_title_response.status_code, 422, blank_title_response.text)

        empty_author_response = await self.client.post(
            "/advertisement",
            json={
                "title": "Valid title",
                "description": "Valid description",
                "price": 100,
                "author": "",
            },
        )
        self.assertEqual(empty_author_response.status_code, 422, empty_author_response.text)

        blank_author_response = await self.client.post(
            "/advertisement",
            json={
                "title": "Valid title",
                "description": "Valid description",
                "price": 100,
                "author": " ",
            },
        )
        self.assertEqual(blank_author_response.status_code, 422, blank_author_response.text)

        negative_price_response = await self.client.post(
            "/advertisement",
            json={
                "title": "Valid title",
                "description": "Valid description",
                "price": -1,
                "author": "Petya Pypkin",
            },
        )
        self.assertEqual(negative_price_response.status_code, 422, negative_price_response.text)

    async def test_patch_validation_errors(self):
        created = await self.create_advertisement(
            title="Bike sale",
            description="Red bike in good condition",
            price=100,
            author="Petya Pypkin",
        )
        advertisement_id = created["id"]

        empty_title_response = await self.client.patch(
            f"/advertisement/{advertisement_id}",
            json={"title": ""},
        )
        self.assertEqual(empty_title_response.status_code, 422, empty_title_response.text)

        blank_description_response = await self.client.patch(
            f"/advertisement/{advertisement_id}",
            json={"description": " "},
        )
        self.assertEqual(blank_description_response.status_code, 422, blank_description_response.text)

        negative_price_response = await self.client.patch(
            f"/advertisement/{advertisement_id}",
            json={"price": -1},
        )
        self.assertEqual(negative_price_response.status_code, 422, negative_price_response.text)

    async def test_search_price_range_validation_error(self):
        response = await self.client.get(
            "/advertisement",
            params={"price_min": 500, "price_max": 100},
        )
        self.assertEqual(response.status_code, 422, response.text)
