import time

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot import json_worker
from bot.aiogram_bot.markups.user_keyboards import (
    generate_plans_kbd,
    get_confirm_kbd,
    get_main_menu,
    cancel_keyboard, vid_img_plans_kbd,
)
from bot.aiogram_bot.misc.states import BuyPlan
from bot.database.models import User
from bot.database.requests.plan_requests import create_plan_request
from bot.database.requests.users import update_user
from bot.texts import (
    PLANS_PART_1_TXT,
    TO_BUY_PLAN_GO_LINK_TXT,
    INCORRECT_PAYMENT_TXT,
    ERROR_PAYMENT_TXT,
    PAYMENT_CONFIRMATION_TXT,
    USE_PART_TXT,
    PLANS_PART_2_TXT, VIDEO_PLANS_TXT, VIDEO_PAYMENT_CONFIRMATION_TXT, TO_BUY_VIDEO_GO_LINK_TXT,
    IMAGE_PAYMENT_SUCCEED_TXT, TO_BUY_IMAGE_GO_LINK_TXT, IMAGE_PLANS_TXT, IMAGE_PAYMENT_CONFIRMATION_TXT,
)
from bot.utils.json_worker import get_plan_by_name
from bot.utils.util import write_error, format_datetime, convert_to_usd

router = Router()


def get_txt_plans(json_file):
    txt_plans = ""
    for i, plan in enumerate(json_file):
        if plan["price"] == 0:
            continue
        txt_plans += f"{plan['emoji']} <b>Тариф \"{plan['name']}\"</b>\n  - Цена: {plan['price']} RUB / месяц\n  - Запросов в день: {plan['day_reqs']['gpt']} (на каждую модель)"
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
            user.request_remains["claude"],
            format_datetime(user.plan_due_to),
            user.image_gens,
            get_txt_plans(json_file),
        )
    else:
        txt_prev = PLANS_PART_1_TXT.format(
            name,
            user.request_remains["gpt"],
            user.request_remains["qwen"],
            user.request_remains["claude"],
            user.image_gens,
            get_txt_plans(json_file),
        )

    await call.message.edit_text(
        txt_prev, reply_markup=generate_plans_kbd(json_file), parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data and c.data.startswith("plan_"))
@router.callback_query(lambda c: c.data and c.data.startswith("image_plan:"))
async def select_plan(call: types.CallbackQuery, state: FSMContext, user: User):
    if call.data.startswith("plan_"):
        type_ = 'default'
        json_plans = await json_worker.read("config/plans.json")
        plan_uid = call.data.split("_", 1)[1]
        plan = next((p for p in json_plans if p["uid"] == plan_uid), None)
        answer_txt = PAYMENT_CONFIRMATION_TXT.format(plan["name"], plan["price"])

    elif call.data.startswith("image_plan:"):
        type_ = 'image'
        plan_uid = call.data.split(":")[1]
        json_plans = await json_worker.read("config/image_plans.json")
        plan = next((p for p in json_plans if p["uid"] == plan_uid), None)
        answer_txt = IMAGE_PAYMENT_CONFIRMATION_TXT.format(plan["images"], plan["usd_price"])
    if not plan:
        await call.answer("Неверный тариф")
        return

    await state.set_state(BuyPlan.confirmation)
    await state.update_data(plan_uid=plan_uid, type_=type_)

    await call.message.edit_text(
        answer_txt,
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
    type_ = data.get("type_")
    if type_ == 'default':
        json_plans = await json_worker.read("config/plans.json")
    elif type_ == 'image':
        json_plans = await json_worker.read("config/image_plans.json")

    plan = next((p for p in json_plans if p["uid"] == plan_uid), None)
    if type_ == 'default':
        price = plan['price']
        desc = f"{user.user_id}:{plan['uid']}:30"
    elif type_ == 'image':
        price = await convert_to_usd(plan['usd_price'], 'USD')
        desc = f"i:{user.user_id}:{plan['uid']}"

    if not plan:
        await call.answer(INCORRECT_PAYMENT_TXT, show_alert=True)
        await state.clear()
        return

    req = await create_plan_request(user.user_id, plan_uid, type_)
    await state.clear()

    await call.message.edit_text(
        f"⏳ <b>Заявка #{req.id} отправлена на рассмотрение.</b>\n"
        f"План: {plan['name']}\n"
        f"Ожидайте подтверждения от администратора.",
        parse_mode="HTML"
    )

    await call.message.answer(
        USE_PART_TXT, reply_markup=cancel_keyboard, parse_mode="HTML"
    )

    # Уведомление админам
    from bot.utils.config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        try:
            await call.bot.send_message(
                admin_id,
                f"📥 <b>Новая заявка на тариф #{req.id}</b>\n"
                f"Пользователь: {user.user_id} (@{user.username or 'нет'})\n"
                f"Тариф: {plan['name']}\n"
                f"Тип: {type_}",
                parse_mode="HTML"
            )
        except Exception:
            pass


@router.callback_query(F.data == "image_buy")
async def image_buy_join(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()

    json_file = await json_worker.read("config/image_plans.json")
    plans = []
    for el in json_file:
        plans.append(f"👉 <b>{el['images']} изображений</b> за {el['usd_price']} USD")
    final_txt = IMAGE_PLANS_TXT + '\n'.join(plans)
    await call.message.answer(final_txt, parse_mode='HTML', reply_markup=vid_img_plans_kbd(json_file, 'image_plan', 'images'))
