import html
import time

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot import ckassa, json_worker
from bot.aiogram_bot.markups.user_keyboards import (
    generate_plans_kbd,
    get_confirm_kbd,
    get_main_menu,
    cancel_keyboard,
)
from bot.aiogram_bot.misc.states import BuyPlan
from bot.database.models import User
from bot.database.requests.users import update_user
from bot.texts import (
    PLANS_PART_1_TXT,
    TO_BUY_PLAN_GO_LINK_TXT,
    INCORRECT_PAYMENT_TXT,
    ERROR_PAYMENT_TXT,
    PAYMENT_CONFIRMATION_TXT,
    USE_PART_TXT,
    PLANS_PART_2_TXT,
)
from bot.utils.json_worker import get_plan_by_name
from bot.utils.util import write_error, format_datetime

router = Router()


def get_txt_plans(json_file):
    txt_plans = ""
    for i, plan in enumerate(json_file):
        if plan["price"] == 0:
            continue

        txt_plans += f"{plan['emoji']} <b>Тариф \"{plan['name']}\"</b>\n  - Цена: {plan['price']} RUB / месяц\n  - Запросов в день: GPT {plan['day_reqs']['gpt']} запросов в день | Qwen {plan['day_reqs']['qwen']} запросов в день"
        if i != len(json_file) - 1:
            txt_plans += "\n\n"
    return txt_plans


@router.callback_query(F.data == "show_plans")
async def show_plans(call: types.CallbackQuery, state: FSMContext, user: User):
    """
    Обработчик для вывода тарифов.
    """

    json_file = await json_worker.read("config/plans.json")
    try:
        name = get_plan_by_name(json_file, user.plan)["name"]
    except:
        await update_user(user.user_id, plan="free")
        return
    if user.plan_due_to:
        txt_prev = PLANS_PART_2_TXT.format(
            name,
            user.request_remains["gpt"],
            user.request_remains["qwen"],
            format_datetime(user.plan_due_to),
            get_txt_plans(json_file),
        )
    else:
        txt_prev = PLANS_PART_1_TXT.format(
            name,
            user.request_remains["gpt"],
            user.request_remains["qwen"],
            get_txt_plans(json_file),
        )

    await call.message.edit_text(
        txt_prev, reply_markup=generate_plans_kbd(json_file), parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data and c.data.startswith("plan_"))
async def select_plan(call: types.CallbackQuery, state: FSMContext, user: User):
    json_plans = await json_worker.read("config/plans.json")
    plan_uid = call.data.split("_", 1)[1]
    plan = next((p for p in json_plans if p["uid"] == plan_uid), None)
    if not plan:
        await call.answer("Неверный тариф")
        return

    await state.set_state(BuyPlan.confirmation)
    await state.update_data(plan_uid=plan_uid)

    await call.message.edit_text(
        PAYMENT_CONFIRMATION_TXT.format(html.escape(plan["name"]), plan["price"]),
        reply_markup=get_confirm_kbd(plan_uid),
        parse_mode="HTML",
    )


@router.callback_query(
    BuyPlan.confirmation,
    lambda c: c.data and c.data.startswith("confirm_purchase_"),
)
async def confirm_purchase(call: types.CallbackQuery, state: FSMContext, user: User):
    await call.answer("Ожидайте...")
    plan_uid = call.data.split("_", 2)[-1]
    data = await state.get_data()

    if data.get("plan_uid") != plan_uid:
        await call.message.answer(ERROR_PAYMENT_TXT, reply_markup=get_main_menu(user))
        await state.clear()
        return
    json_plans = await json_worker.read("config/plans.json")

    plan = next((p for p in json_plans if p["uid"] == plan_uid), None)
    if not plan:
        await call.answer(INCORRECT_PAYMENT_TXT, show_alert=True)
        await state.clear()
        return

    try:
        payment_link = await ckassa.create_invoice(
            amount=plan["price"],
            properties=[
                {"name": "ЛИЦЕВОЙ_СЧЕТ", "value": f"{user.user_id}:{plan['uid']}:30"},
                {"name": "ID", "value": int(f"{user.user_id}{int(time.time())}")},
                {"name": "telegram_ID", "value": user.user_id},
            ]
        )
    except Exception as e:
        write_error(e)
        await call.message.answer(ERROR_PAYMENT_TXT, reply_markup=get_main_menu(user))
        await state.clear()
        return
    await state.clear()

    await call.message.edit_text(
        TO_BUY_PLAN_GO_LINK_TXT.format(
            plan["emoji"], plan["name"], plan["price"], payment_link
        ),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

    await call.message.answer(
        USE_PART_TXT, reply_markup=cancel_keyboard, parse_mode="HTML"
    )
