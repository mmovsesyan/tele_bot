from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.misc.middlewares import admin_middleware, include_middlewares
from bot.database.requests.plan_requests import get_pending_requests, approve_request, reject_request, get_request_by_id
from bot.database.requests.users import get_user
from bot.utils.plans_worker import give_plan
from bot.utils.config import TIMEZONE
from bot.utils.util import format_datetime

router = Router()
include_middlewares(router, admin_middleware)


@router.callback_query(F.data == "plan_requests")
async def show_plan_requests(call: types.CallbackQuery, state: FSMContext):
    requests = await get_pending_requests()
    if not requests:
        await call.answer("Нет ожидающих заявок", show_alert=True)
        return

    for req in requests:
        user = await get_user(req.user_id)
        username = f"@{user.username}" if user and user.username else "нет username"
        kbd = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_req:{req.id}"),
                types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_req:{req.id}"),
            ]
        ])
        await call.message.answer(
            f"📥 <b>Заявка #{req.id}</b>\n"
            f"Пользователь: <code>{req.user_id}</code> {username}\n"
            f"Тариф: <b>{req.plan_uid}</b>\n"
            f"Тип: {req.type_}\n"
            f"Дата: {req.created_at.strftime('%d.%m.%Y %H:%M') if req.created_at else '-'}",
            parse_mode="HTML",
            reply_markup=kbd,
        )
    await call.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("approve_req:"))
async def approve_plan_request(call: types.CallbackQuery, state: FSMContext):
    req_id = int(call.data.split(":")[1])
    req = await get_request_by_id(req_id)
    if not req or req.status != 'pending':
        await call.answer("Заявка не найдена или уже обработана", show_alert=True)
        return

    await approve_request(req_id)
    plan = await give_plan(req.user_id, req.plan_uid, None)

    user = await get_user(req.user_id)
    if user:
        try:
            await call.bot.send_message(
                req.user_id,
                f"✅ <b>Ваша заявка #{req_id} одобрена!</b>\n"
                f"Тариф <b>{plan['name']}</b> активирован до {format_datetime(user.plan_due_to)}.",
                parse_mode="HTML",
            )
        except Exception:
            pass

    await call.message.edit_text(
        call.message.html_text + "\n\n✅ <b>ОДОБРЕНО</b>",
        parse_mode="HTML",
    )
    await call.answer("Заявка одобрена")


@router.callback_query(lambda c: c.data and c.data.startswith("reject_req:"))
async def reject_plan_request(call: types.CallbackQuery, state: FSMContext):
    req_id = int(call.data.split(":")[1])
    req = await get_request_by_id(req_id)
    if not req or req.status != 'pending':
        await call.answer("Заявка не найдена или уже обработана", show_alert=True)
        return

    await reject_request(req_id)

    try:
        await call.bot.send_message(
            req.user_id,
            f"❌ <b>Ваша заявка #{req_id} отклонена.</b>\n"
            f"Обратитесь к администратору для уточнения.",
            parse_mode="HTML",
        )
    except Exception:
        pass

    await call.message.edit_text(
        call.message.html_text + "\n\n❌ <b>ОТКЛОНЕНО</b>",
        parse_mode="HTML",
    )
    await call.answer("Заявка отклонена")
