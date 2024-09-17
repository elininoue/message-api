from fastapi.testclient import TestClient

from .main import app, MAXIMUM_REQUEST_LIMIT

client = TestClient(app)


# Tests for submitting messages


def test_submit_valid_message():
    response = client.post(
        "/v1/messages/",
        json={
            "recipient": "someone",
            "sender": "someonelse",
            "content": "Hello. How are you?",
        },
    )
    assert response.status_code == 200


def test_submit_message_without_recipient():
    response = client.post(
        "/v1/messages/",
        json={
            "sender": "someonelse",
            "content": "This message is for anyone",
        },
    )
    assert response.status_code == 422


def test_submit_message_without_sender():
    response = client.post(
        "/v1/messages/",
        json={
            "recipient": "someone",
            "content": "This is an anonymous message",
        },
    )
    assert response.status_code == 422


# Tests for fetching messages


def test_fetch_new_messages():
    client.post(
        "/v1/messages/",
        json={
            "recipient": "testuser1",
            "sender": "testuser2",
            "content": "msg1",
        },
    )
    client.post(
        "/v1/messages/",
        json={
            "recipient": "testuser1",
            "sender": "testuser2",
            "content": "msg2",
        },
    )
    response = client.get("/v1/messages/testuser1?new_only=true")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_fetch_with_negative_offset():
    response = client.get("/v1/messages/testuser1?offset=-3")
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid offset. Offset needs to be a positive integer."
    }


def test_fetch_too_many_messages():
    response = client.get("/v1/messages/testuser1?limit=502")
    assert response.status_code == 400
    assert response.json() == {
        "detail": f"Too many messages requested. The maximum limit is {MAXIMUM_REQUEST_LIMIT}."
    }


# Tests for deleting messages


def test_delete_one_message():
    client.post(
        "/v1/messages/",
        json={
            "recipient": "testuser1",
            "sender": "testuser2",
            "content": "msg1",
        },
    )
    client.post(
        "/v1/messages/",
        json={
            "recipient": "testuser1",
            "sender": "testuser2",
            "content": "msg2",
        },
    )

    id_to_delete = client.get("/v1/messages/testuser1?limit=1").json()[0]["id"]
    response = client.delete(f"/v1/messages/{id_to_delete}")
    new_id = client.get("/v1/messages/testuser1?limit=1").json()[0]["id"]
    assert id_to_delete != new_id
    assert response.status_code == 204


def test_delete_multiple_messages():
    client.post(
        "/v1/messages/",
        json={
            "recipient": "testuser1",
            "sender": "testuser2",
            "content": "msg1",
        },
    )
    client.post(
        "/v1/messages/",
        json={
            "recipient": "testuser1",
            "sender": "testuser2",
            "content": "msg2",
        },
    )

    ids_to_delete = list()

    for message in client.get("/v1/messages/testuser1").json():
        ids_to_delete.append(message["id"])

    print(ids_to_delete)
    response = client.post(
        "/v1/messages/delete/",
        json={"ids": ids_to_delete},
    )

    assert client.get("/v1/messages/testuser1").json() == []
    assert response.json() == {"total": len(ids_to_delete)}


def test_delete_non_existing_message():
    greatest_id = client.post(
        "/v1/messages/",
        json={
            "recipient": "testuser1",
            "sender": "testuser2",
            "content": "msg1",
        },
    ).json()["id"]

    response = client.delete(f"/v1/messages/{greatest_id+1}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Message not found"}
