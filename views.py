# views.py
from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import User, Message
from passlib.context import CryptContext
from database import get_db
from pydantic import BaseModel


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class LoginForm(BaseModel):
    email: str
    password: str


class MessageCreate(BaseModel):
    user_id: int
    content: str


async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email, username=user.username, password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return JSONResponse(
        status_code=201, content={"message": "User created successfully"}
    )


async def login(login_data: LoginForm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not pwd_context.verify(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return JSONResponse(
        status_code=200, content={"message": "Login successful", "user": user.id}
    )


async def get_messages(db: Session = Depends(get_db)):
    messages = db.query(Message).all()
    messages_data = []

    for message in messages:
        message_dict = {
            "id": message.id,
            "sender_id": message.sender_id,
            "sender": message.sender.username,
            "online": message.sender.online,
            "content": message.content,
        }
        messages_data.append(message_dict)
    return JSONResponse(status_code=200, content={"data": messages_data})


async def delete_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.id == message_id).first()

    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    db.delete(message)
    db.commit()

    return JSONResponse(
        status_code=200, content={"message": "Message Deleted Successfully"}
    )


async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    users_data = []

    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "online": user.online,
        }
        users_data.append(user_dict)

    return JSONResponse(status_code=200, content={"users": users_data})


async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = {"username": user.username, "email": user.email, "id": user.id}
    return JSONResponse(status_code=200, content={"user": user_dict})
