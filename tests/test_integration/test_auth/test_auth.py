from src.services.auth import AuthService


def test_decode_and_encode_jwt_token():
    data = {"user_id": 1}
    jwt_token = AuthService().create_access_token(data=data)

    assert jwt_token
    assert isinstance(jwt_token, str)

    jwt_token_encode =  AuthService().encode_token(jwt_token)

    assert isinstance(jwt_token_encode, dict)
    assert jwt_token_encode["user_id"] == data["user_id"]