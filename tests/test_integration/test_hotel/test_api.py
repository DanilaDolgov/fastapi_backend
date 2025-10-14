async def test_get_hotels(ac):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": "2025-10-13",
            "date_to": "2025-10-20",
        },
    )
    assert response.status_code == 200

    print(response.json())
