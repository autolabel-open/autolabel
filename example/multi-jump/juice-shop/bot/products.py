import asyncio
import random
from datetime import datetime
from typing import Any, cast

from pydantic import BaseModel, Field

from providers import http
from user import user_manager
from utils import empty_coro, sleep


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    deluxe_price: float | None = Field(default=None, serialization_alias="deluxePrice")
    image: str
    quantity: int = 0
    limit_per_user: int | None = Field(default=None, serialization_alias="limitPerUser")


class BasketItem(BaseModel):
    id: int
    quantity: int
    product: Product


class ProductManager:
    def __init__(self) -> None:
        self.products: dict[int, Product] = {}

    async def init_list(self) -> list[Product]:
        res = await http.get_api("/rest/products/search?q=")
        products = [Product.model_validate(p) for p in cast(list[dict], res)]
        self.products = {p.id: p for p in products}

        res = await http.get_api("/api/Quantitys")
        for quantity_data in cast(list[dict], res):
            product = self.products.get(quantity_data["id"])
            if product:
                product.quantity = quantity_data["quantity"]
                product.limit_per_user = quantity_data["limitPerUser"]
        await self.get_product_pics(products)
        return products

    @staticmethod
    async def get_product_pics(products: list[Product]) -> None:
        await asyncio.gather(
            *[
                http.client.get(f"/assets/public/images/products/{p.image}")
                for p in products[
                    : random.randint(min(12, len(products)), len(products))
                ]
            ]
        )

    def choose_product(self, id_: int | None = None) -> Product:
        if id_:
            return self.products[id_]
        return random.choice(list(self.products.values()))

    async def get_reviews(self, product_id: int) -> list[dict]:
        await user_manager.whoami()
        res = await http.get_api(f"/rest/products/{product_id}/reviews")
        return cast(list[dict], res)

    async def create_review(self, product_id: int, content: str) -> list[dict]:
        logged_in = await user_manager.whoami()
        await http.put_api(
            f"/rest/products/{product_id}/reviews",
            json={
                "author": user_manager.user.email if logged_in else "Anonymous",
                "message": content,
            },
        )
        return await self.get_reviews(product_id)

    async def get_basket(self) -> list[BasketItem]:
        res = await http.get_api(f"/rest/basket/{user_manager.user.bid}")
        basket: list[BasketItem] = []
        for product in cast(dict[str, Any], res)["Products"]:
            product = product["BasketItem"]
            basket.append(
                BasketItem(
                    id=product["id"],
                    quantity=product["quantity"],
                    product=self.products[product["ProductId"]],
                )
            )
        return basket

    async def add_to_basket(self, product_id: int, quantity: int) -> None:
        await self.get_basket()
        quantity = min(
            quantity,
            self.products[product_id].quantity,
            self.products[product_id].limit_per_user or 1145141919810,
        )
        if not quantity:
            return
        try:
            await http.post_api(
                "/api/BasketItems",
                json={
                    "ProductId": product_id,
                    "BasketId": str(user_manager.user.bid),
                    "quantity": quantity,
                },
            )
        except http.RequestFailedError:
            pass
        else:
            await http.get_api(
                f"/api/Products/{product_id}",
                params={"d": datetime.now().strftime("%a %b %d %Y")},
            )
        await self.get_basket()

    async def checkout(self) -> None:
        # basket page
        basket = await self.get_basket()
        await user_manager.whoami()
        await sleep(random.randint(1, 5))
        if not basket:
            return

        # addr page
        address = await user_manager.choose_address()
        await http.get_api(f"/api/Addresss/{address['id']}")

        # delivery page
        res = await http.get_api("/api/Deliverys")
        delivery = random.choice(cast(list[dict], res))
        await http.get_api(f"/api/Deliverys/{delivery['id']}")
        await sleep(random.randint(1, 5))

        # pay page
        balance, _, _ = await asyncio.gather(
            user_manager.balance(),
            http.get_rest("/rest/admin/application-configuration"),
            user_manager.cards(),
        )
        total_cost = 0
        for item in basket:
            total_cost += item.product.price * item.quantity
        use_balance = total_cost <= balance
        if not use_balance:
            card = await user_manager.choose_card()
        else:
            # 选卡那里会 sleep 一下，不用卡就要补一下
            await sleep(random.randint(1, 5))

        # final page
        await asyncio.gather(
            self.get_basket(),
            user_manager.whoami(),
            http.get_api(f"/api/Addresss/{address['id']}"),
            http.get_api(f"/api/Deliverys/{delivery['id']}"),
            (
                http.get_api(f"/api/Cards/{card['id']}")
                if not use_balance
                else empty_coro()
            ),
        )
        await self.get_product_pics([item.product for item in basket])
        await sleep(random.randint(1, 5))

        # submit
        res = await http.post_rest(
            f"/rest/basket/{user_manager.user.bid}/checkout",
            json={
                "couponData": "bnVsbA==",  # btoa(sessionStorage.getItem('couponDetails')) when no couponDetails
                "orderDetails": {
                    "paymentId": str(card["id"]) if not use_balance else "wallet",
                    "addressId": str(address["id"]),
                    "deliveryMethodId": str(delivery["id"]),
                },
            },
        )
        order_id = cast(dict[str, str], res)["orderConfirmation"]
        await asyncio.gather(
            self.get_basket(),
            http.get_api(
                f"/rest/track-order/{order_id}",
            ),
            http.get_rest("/rest/admin/application-configuration"),
            http.get_api(f"/api/Addresss/{address['id']}"),
        )

    async def order_history(self) -> list[dict]:
        res = await http.get_api("/rest/order-history")
        return cast(list[dict], res)

    async def track_order(self, order: dict) -> dict:
        res = await http.get_api(f"/rest/track-order/{order['orderId']}")
        return cast(dict, res)


product_manager = ProductManager()
