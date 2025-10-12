from http.client import responses


async def test_create_facilities(ac):
    # response_hotels_id = await ac.get("/hotels",
    #                                   params={
    #                                       "date_from": "2025-10-13",
    #                                       "date_to": "2025-10-20",
    #                                   }
    #                                   )
    #
    # assert response_hotels_id.status_code == 200
    # hotel_id = response_hotels_id.json()[0]["id"]
    # assert hotel_id
    #
    # response_room_id = await ac.get(f"/rooms/{hotel_id}",
    #                                   params={
    #                                       "date_from": "2025-10-13",
    #                                       "date_to": "2025-10-20",
    #                                   }
    #                                   )
    # room_id = response_room_id.json()['rooms'][0]["room_id"]
    # assert room_id

    response = await ac.post(
                    url="/facilities",
                    json={"title": "WiFi"}
    )
    assert response.status_code == 200
    print(response.json())
    assert isinstance(response.json(), dict)


async def test_get_facilities(ac):
    response = await ac.get("/facilities")

    assert response.status_code == 200
    print(response.json())
    assert response.json()[0]['title']
    assert isinstance(response.json(), list)