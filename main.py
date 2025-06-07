from fastapi import FastAPI
from fastapi import FastAPI, Query, Body
from fastapi.openapi.docs import get_swagger_ui_html
from typing import Optional
import uvicorn

app = FastAPI(docs_url=None)

hotels = [
    {"id": 1, "title": "Sochi", "name": "Sochi", "address": "RUSSIA, KRASNODARSKII KRAI, SOCHI", "phone": 7999999999},
    {"id": 2, "title": "Дубай", "name": "Дубай", "address": "UAE, DUBAI", "phone": 97100000000},
]


@app.get("/")
def func():
    return "Hello World!!!!!!!!!!"


@app.get("/hotels")
def get_hotels(
        id: int | None = Query(None, description="Айдишник"),
        title: str | None = Query(None, description="Название отеля"),
):
    hotels_ = []
    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        hotels_.append(hotel)
    return hotels_


@app.delete("/hotels/{hotel_id}")
def delete_hotels(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {'Status': 'Ok'}


@app.post("/hotels")
def create_hotels(
        title: str = Body(embed=True)
):
    global hotels
    hotels.append(
        {
            "id": hotels[-1]["id"] + 1,
            "title": title
        }
    )
    return {'Status': 'Ok'}


@app.put("/hotels/{hotel_id}")
def update_hotel(
        hotel_id: int,
        title: str = Body(embed=True),
        name: str = Body(embed=True),
        address: str = Body(embed=True),
        phone: int = Body(embed=True)
):
    global hotels
    hotels = [{**hotel, "title": title, "name": name, "address": address, "phone": phone} if
              hotel["id"] == hotel_id else hotel for hotel in hotels]
    return {"Status": "Ok"}


@app.patch("/hotels/{hotel_id}")
def update_patch_hotel(
        hotel_id: int,
        title: Optional[str] = Body(default=None),
        name: Optional[str] = Body(default=None),
        address: Optional[str] = Body(default=None),
        phone: Optional[int] = Body(default=None)

):
    global hotels
    hotels = [
        {
            **hotel,
            "title": title if title is not None else hotel["title"],
            "name": name if name is not None else hotel["name"],
            "address": address if address is not None else hotel["address"],
            "phone": phone if phone is not None else hotel["phone"]
        } if hotel["id"] == hotel_id else hotel
        for hotel in hotels
    ]
    return {"Status": "Ok"}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
