from fastapi import APIRouter, HTTPException, Response
from passlib.context import CryptContext

from src.dependencies.dependencies import UserIdDep, DBDep
from src.exceptions import ObjectAlreadyExistsException
from src.services.auth import AuthService
from src.schemas.users import UserRequestAdd, UserAdd

router = APIRouter(prefix="/auth", tags=["Авторизация и Аутентификация"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post(path="/login")
async def login_user(db: DBDep, data: UserRequestAdd, response: Response):
    user = await db.user.get_user_with_hashed_password(email=data.email)
    if not user:
        raise HTTPException(status_code=401, detail="User with this email not registration!")
    if not AuthService().verify_password(data.password, user.hash_password):
        raise HTTPException(status_code=401, detail="Password is not correct!")
    access_token = AuthService().create_access_token({"user_id": user.id})
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.post(path="/register")
async def register_user(db: DBDep, data: UserRequestAdd):
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, hash_password=hashed_password)

    try:
        await db.user.add(new_user_data)
        await db.commit()
    except ObjectAlreadyExistsException:
        raise HTTPException(status_code=409, detail="User already exists.")

    return {"Status": "Ok"}


@router.get("/me")
async def get_me(db: DBDep, user_id: UserIdDep):
    user = await db.user.get_one_or_none(id=user_id)
    return user


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"Status": "Ok"}
