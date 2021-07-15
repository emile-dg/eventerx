import os
import tempfile

import pytest
from eventerx import app, db


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkdtemp()
    with app.test_client() as client:
        with app.app_content():
            db.init_db()
        yield client

    os.close(db_fd)
    os.unlink(db_path)