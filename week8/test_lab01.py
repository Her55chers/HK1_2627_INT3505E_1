"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema
pyt
Do not depend on test execution order. Fixtures: client, app, sample_book.
"""
# A. GET /books on an empty DB returns an empty array 
def test_list_books_empty_returns_empty_array(client):
    response = client.get("/books")
 
    assert response.status_code == 200
    assert response.is_json
    body = response.get_json()
    assert body is not None          # not null
    assert isinstance(body, list)    # an array
    assert body == []                # and it is empty
 
 
# B. GET /books/<id> with a non-existent id returns 404 + code NOT_FOUND
def test_get_missing_book_returns_404_not_found(client):
    response = client.get("/books/9999")
 
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["code"] == "NOT_FOUND"
 
 
# C. POST /books without title returns 400 and "title" appears in errors
def test_create_book_without_title_returns_400_with_title_error(client):
    response = client.post("/books", json={"author": "J.J. Geewax"})
 
    assert response.status_code == 400
    body = response.get_json()
    assert body["code"] == "VALIDATION_ERROR"
    assert "errors" in body
    error_fields = [err["field"] for err in body["errors"]]
    assert "title" in error_fields
 
 
# D. Create, delete, then GET the same id -> 404
def test_get_after_delete_returns_404(client):
    created = client.post(
        "/books", json={"title": "API Design Patterns", "author": "J.J. Geewax"}
    )
    assert created.status_code == 201
    book_id = created.get_json()["id"]
 
    # sanity check: the book really exists before deleting
    assert client.get(f"/books/{book_id}").status_code == 200
 
    deleted = client.delete(f"/books/{book_id}")
    assert deleted.status_code == 204
 
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"