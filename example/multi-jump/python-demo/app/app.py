import hook

print("we need to import hooks first")

import asyncio
import logging
import os
from uuid import uuid4

from fastapi import FastAPI, Path, Request, exceptions
from hypercorn.asyncio import serve
from hypercorn.config import Config
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware


class User(BaseModel):
    username: str
    password: str


class Item(BaseModel):
    name: str
    price: float


admin = User(username="admin", password="123456")
users: dict[str, User] = {"admin": admin}
user_accounts: dict[str, float] = {}

items = [Item(name="Xiaomi 14", price=3999), Item(name="Huawei Mate 60", price=5699)]

logger = logging.getLogger("demo")
os.makedirs("/tmp/logs", exist_ok=True)
fh = logging.FileHandler("/tmp/logs/admin_access.log", "w")
fh.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s"
    )
)
logger.addHandler(fh)
logger.setLevel(logging.INFO)

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="666",
)


@app.get("/items")
async def get_items() -> list[Item]:
    return items


@app.post("/register")
async def register(user: User) -> str:
    new_user = User.model_validate(user.model_dump())
    users[user.username] = new_user
    return "success"


@app.post("/login")
async def login(user: User, request: Request) -> str:
    real_user = users.get(user.username)
    if not real_user:
        raise exceptions.HTTPException(404)
    if real_user.password != user.password:
        raise exceptions.HTTPException(403)

    request.session["userid"] = real_user.username
    # request.state.set_cookie = True

    user_accounts.setdefault(real_user.username, 0)

    return "success"


@app.get("/charge/{money}")
async def charge(request: Request, money: float) -> float:
    username = request.session.get("userid")
    if not username or username not in users:
        raise exceptions.HTTPException(403)

    user_accounts[username] += money
    return user_accounts[username]


@app.get("/balance")
async def get_balance(request: Request) -> float:
    username = request.session.get("userid")
    if not username or username not in users:
        raise exceptions.HTTPException(403)

    return user_accounts[username]


@app.get("/buy/{name}")
async def buy(request: Request, name: str):
    username = request.session.get("userid")
    print(username)
    if not username or username not in users:
        raise exceptions.HTTPException(403)

    try:
        item = next(filter(lambda i: i.name == name, items))
    except:
        raise exceptions.HTTPException(404)
    if user_accounts[username] < item.price:
        raise exceptions.HTTPException(401)
    user_accounts[username] -= item.price
    return {"balance": user_accounts[username], "item": item}


@app.post("/admin/login")
async def admin_login(user: User, request: Request) -> str:
    real_user = users.get(user.username)
    if not real_user or user.username != "admin":
        raise exceptions.HTTPException(404)
    if real_user.password != user.password:
        raise exceptions.HTTPException(403)

    logger.info(f"admin {user.username} login")
    request.session["userid"] = real_user.username
    return "success"


@app.get("/solve/{expr:path}")
async def solve(request: Request, expr: str = Path(...)):
    username = request.session.get("userid")
    if not username or not (user := users.get(username)) or user.username != "admin":
        raise exceptions.HTTPException(403)

    logger.info(f"admin {user.username} solve {expr}")
    return eval(expr)


@app.post("/admin/edit")
async def edit_items(request: Request, new_items: list[Item]) -> list[Item]:
    global items
    username = request.session.get("userid")
    if not username or not (user := users.get(username)) or user.username != "admin":
        raise exceptions.HTTPException(403)

    logger.info(f"admin {user.username} edited items")
    items = new_items
    return new_items


if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    config.accesslog = "-"
    config.keep_alive_timeout = 10
    config.workers = 4
    asyncio.run(serve(app, config))  # type: ignore
