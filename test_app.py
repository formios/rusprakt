import pytest
from app import create_app
from models import db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_and_get_note(client):
    response = client.post('/api/notes', json={
        'title': 'Тестовая заметка',
        'content': 'Текст для теста'
    })
    assert response.status_code == 201

    get_response = client.get('/api/notes')
    assert get_response.status_code == 200