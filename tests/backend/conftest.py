import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

import pytest
from fastapi.testclient import TestClient
from main import app
from db.mongo import users_collection


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def cleanup_test_users():
    yield
    users_collection.delete_many({"email": {"$regex": "^test_.*@pytest\\.com$"}})
