import random
from typing import Literal

import httpx

import random_utils
from behaviors import Behaviors, States, define_behavior
from products import product_manager
from providers import http
from user import user_manager
from utils import create_zip_with_text_content, sleep


@define_behavior(
    Behaviors.login,
    weight=1,
    avaliable_states=[States.logged_out],
)
async def login() -> Literal[States.logged_in]:
    await user_manager.login()
    await product_manager.init_list()
    return States.logged_in


@define_behavior(
    Behaviors.logout,
    weight=0.1,
    avaliable_states=[States.logged_in],
)
async def logout() -> Literal[States.logged_out]:
    await user_manager.logout()
    await product_manager.init_list()
    return States.logged_out


@define_behavior(
    Behaviors.add_address,
    weight=0.5,
    avaliable_states=[States.logged_in],
)
async def add_address() -> None:
    await user_manager.addresss()
    await sleep(random.randint(20, 60))
    await user_manager.add_address()
    await user_manager.addresss()


@define_behavior(
    Behaviors.add_card,
    weight=0.5,
    avaliable_states=[States.logged_in],
)
async def add_card() -> None:
    await user_manager.cards()
    await sleep(random.randint(20, 60))
    await user_manager.add_card()
    await user_manager.cards()


@define_behavior(
    Behaviors.charge,
    weight=1,
    avaliable_states=[States.logged_in],
)
async def charge() -> None:
    await user_manager.charge_balance()


@define_behavior(
    Behaviors.track_order,
    weight=1,
    avaliable_states=[States.logged_in],
)
async def track_order() -> None:
    orders = await product_manager.order_history()
    if orders:
        order = random.choice(orders)
        await sleep(5)
        await product_manager.track_order(order)


@define_behavior(Behaviors.check_review, weight=1)
async def check_review() -> None:
    await product_manager.init_list()
    await sleep(random.randint(5, 60))
    product = product_manager.choose_product()
    await product_manager.get_reviews(product.id)


@define_behavior(Behaviors.write_review, weight=1)
async def write_review() -> None:
    await product_manager.init_list()
    await sleep(random.randint(5, 60))
    product = product_manager.choose_product()
    await product_manager.get_reviews(product.id)
    await sleep(random.randint(20, 60))
    await product_manager.create_review(
        product.id, random_utils.random_string((20, 200))
    )


@define_behavior(
    Behaviors.add_to_basket,
    weight=1.5,
    avaliable_states=[States.logged_in],
)
async def add_to_basket() -> None:
    await product_manager.init_list()
    await sleep(random.randint(5, 60))
    product = product_manager.choose_product()
    await product_manager.add_to_basket(product.id, random.randint(1, 5))


@define_behavior(
    Behaviors.checkout,
    weight=1.2,
    avaliable_states=[States.logged_in],
)
async def checkout() -> None:
    await product_manager.checkout()


@define_behavior(
    Behaviors.complain,
    weight=0.5,
    avaliable_states=[States.logged_in],
)
async def complain() -> None:
    await user_manager.whoami()
    await sleep(random.randint(60, 90))

    upload_file = create_zip_with_text_content(random_utils.random_string((100, 1000)))
    await http.client.post(
        "/file-upload",
        files={"file": (f"{random_utils.random_string()}.zip", upload_file)},
    )

    content = {
        "UserId": user_manager.user.id,
        "message": random_utils.random_string((50, 160)),
    }
    await http.post_api("/api/Complaints", json=content)
    await user_manager.whoami()
