import pytest


@pytest.mark.parametrize(
    "email, password",
    [("test2025@test.com", "test12345"), ("test2025@test.com", "test12345")],
)
async def test_register_user(email, password, ac, db):
    res_register = await ac.post(
        "/auth/register", json={"email": email, "password": password}
    )

    print(res_register.status_code)
    if res_register.status_code == 200:
        assert res_register.status_code == 200
        assert await db.user.get_one_or_none(email=email) is not None
        assert len(await db.user.get_in_params(email=email)) == 1
    else:
        assert res_register.status_code == 400
        assert len(await db.user.get_in_params(email=email)) == 1


@pytest.mark.parametrize(
    "email, password",
    [
        ("test2025@test.com", "test12345"),
        ("test2025@testS.ru", "test12345"),
        ("test2025@test.com", "54321test"),
    ],
)
async def test_login_user(email, password, ac, db):
    res_login = await ac.post(
        "/auth/login", json={"email": email, "password": password}
    )

    print(res_login.status_code)
    if res_login.status_code == 200:
        assert res_login.json()["access_token"]
        assert res_login.cookies.get("access_token")
        assert res_login.headers["set-cookie"]
    else:
        assert res_login.status_code == 401


@pytest.mark.parametrize("email", [("test2025@test.com",)])
async def test_me_user(email, ac, db):
    res_me = await ac.get("/auth/me")
    user = await db.user.get_one(email=email[0])
    assert res_me.status_code == 200
    assert user.id == res_me.json()["id"]


async def test_logout_user(ac):
    res_logout = await ac.post("/auth/logout")
    assert res_logout.json().get("access_token", None) is None
    assert res_logout.cookies.get("access_token", None) is None
    assert "access_token=" in res_logout.headers.get("set-cookie", None).split(";")[0]
