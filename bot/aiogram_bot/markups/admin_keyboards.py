from aiogram import types

from bot.texts import STATS_BTN, CREATE_PROMO_BTN, BAN_USER_BTN, BACK_TO_MAIN_MENU_BTN, OK_BTN, BACK_BTN, MASS_MAIL_BTN, \
    ADD_ADMIN_BTN, CHANGE_PRICE_BTN, UPLOAD_USERS_BTN, FIND_USER_BTN, PLAN_REQUESTS_BTN

admin_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [types.InlineKeyboardButton(text=MASS_MAIL_BTN, callback_data="mass_send")],
        [types.InlineKeyboardButton(text=PLAN_REQUESTS_BTN, callback_data="plan_requests")],
        [types.InlineKeyboardButton(text=ADD_ADMIN_BTN, callback_data="add_admin")],
        [types.InlineKeyboardButton(text=CHANGE_PRICE_BTN, callback_data="change_prices")],
        [types.InlineKeyboardButton(text=UPLOAD_USERS_BTN, callback_data="upload_users")],
        [types.InlineKeyboardButton(text=FIND_USER_BTN, callback_data="get_info")],
        [types.InlineKeyboardButton(text=STATS_BTN, callback_data="show_stats")],
        [types.InlineKeyboardButton(text=CREATE_PROMO_BTN, callback_data="create_promocode")],
        [types.InlineKeyboardButton(text=BAN_USER_BTN, callback_data="ban_user")],
        [types.InlineKeyboardButton(text=BACK_TO_MAIN_MENU_BTN, callback_data="back_to_main_menu")],
    ]
)

mass_mail_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [types.InlineKeyboardButton(text=OK_BTN, callback_data="ok")],
        [types.InlineKeyboardButton(text=BACK_BTN, callback_data="cancel")],
    ]
)
