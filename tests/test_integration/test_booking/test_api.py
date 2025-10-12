
# room_id: int
#     date_from: date
#     date_to: date
async def test_booking_add(db, authenticated_ac):
    room_id = (await db.rooms.get_all())[0].id
    response = await authenticated_ac.post("/booking",
                                           json={
                                               "room_id": room_id,
                                               "date_from": "2025-10-21",
                                               "date_to": "2025-10-22"
                                           })
    assert response.status_code == 200
    assert response.json()['Status'] == 'Ok'
    assert response.json()['data']
    assert isinstance(response.json(), dict)

