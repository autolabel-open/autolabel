import asyncio
import random
from typing import cast

from pydantic import BaseModel

import random_utils
from providers import http
from utils import sleep


class User(BaseModel):
    id: int
    email: str
    password: str
    security_question: dict
    security_answer: str
    token: str = ""
    bid: int = 0

    def login_payload(self) -> dict[str, str]:
        return self.model_dump(include={"email", "password"})


class UserManager:
    def __init__(self) -> None:
        self._user: User | None = None
        self.logged_in: bool = False

    @property
    def user(self) -> User:
        assert self._user, "Please use register() to init user"
        return self._user

    async def register(self) -> None:
        res = await http.get_api("/api/SecurityQuestions")
        security_questions = cast(list[dict[str, str]], res)
        password = random_utils.random_string(10)
        payload = {
            "email": random_utils.random_email(),
            "password": password,
            "passwordRepeat": password,
            "securityQuestion": random.choice(security_questions),
            "securityAnswer": random_utils.random_string(),
        }
        res = await http.post_api("/api/Users", json=payload)
        self._user = User(
            id=cast(dict[str, int], res)["id"],
            email=payload["email"],
            password=password,
            security_question=payload["securityQuestion"],
            security_answer=payload["securityAnswer"],
        )

    async def login(self) -> None:
        await self.whoami()
        await self.whoami()
        res = await http.post_rest("/rest/user/login", json=self.user.login_payload())
        login_res = cast(dict, res)
        token = login_res["authentication"]["token"]
        self.user.token = token
        self.user.bid = login_res["authentication"]["bid"]
        http.client.cookies.set("token", token)
        http.client.headers["Authorization"] = f"Bearer {token}"

    async def whoami(self) -> bool:
        res = await http.get_rest("/rest/user/whoami")
        user = cast(dict[str, dict], res)["user"]
        self.logged_in = "id" in user and user["id"] == self.user.id
        return self.logged_in

    async def logout(self) -> None:
        await http.get_rest("/rest/saveLoginIp")
        http.client.cookies.clear()
        del http.client.headers["Authorization"]

    async def addresss(self) -> list[dict]:
        res = await http.get_api("/api/Addresss")
        return cast(list[dict], res)

    async def add_address(self) -> None:
        address = {
            "country": random_utils.random_string((5, 10)),
            "fullName": random_utils.random_string((5, 10)),
            "mobileNum": random.randint(1000000, 9999999999),
            "zipCode": random_utils.random_string((5, 8)),
            "streetAddress": random_utils.random_string(),
            "city": random_utils.random_string((5, 10)),
            "state": random_utils.random_string((5, 10)),
        }
        await http.post_api("/api/Addresss", json=address)

    async def choose_address(self) -> dict:
        while True:
            addresss = await user_manager.addresss()
            await sleep(random.randint(1, 5))
            if not addresss or random.random() > 0.7:
                await user_manager.add_address()
            else:
                return random.choice(addresss)

    async def cards(self) -> list[dict]:
        res = await http.get_api("/api/Cards")
        return cast(list[dict], res)

    async def add_card(self) -> None:
        card = {
            "fullName": random_utils.random_string((5, 10)),
            "cardNum": random.randint(1000000000000000, 9999999999999999),
            "expMonth": str(random.choice(list(range(1, 13)))),
            "expYear": f"20{random.choice(list(range(80, 99)))}",
        }
        await http.post_api("/api/Cards", json=card)

    async def choose_card(self) -> dict:
        while True:
            cards = await user_manager.cards()
            await sleep(random.randint(1, 5))
            if not cards or random.random() > 0.7:
                await user_manager.add_card()
            else:
                return random.choice(cards)

    async def balance(self) -> float:
        res = await http.get_api("/rest/wallet/balance")
        return cast(float, res)

    async def charge_balance(self) -> None:
        await asyncio.gather(
            self.balance(),
            http.get_rest("/rest/admin/application-configuration"),
        )
        card = await self.choose_card()
        amount = random.random() * 1000
        await http.put_api(
            "/rest/wallet/balance", json={"balance": amount, "paymentId": card["id"]}
        )
        await self.balance()


user_manager = UserManager()
