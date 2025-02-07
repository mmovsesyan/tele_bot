from aiogram import types

from bot.database.models import User
from bot.texts import PLANS_BTN, START_DIALOG_BTN, AUTOPAY_SWITCH_BTN, ENTER_PROMO_BTN, REF_BTN, \
    ADMIN_JOIN_BTN, PLANS_BUY_PART_BTN, BACK_BTN, SETTINGS_BTN, CANCEL_BTN, BUY_BTN, CHOICED_MODEL_PART_TXT, \
    STOP_DIALOG_BTN, INFO_BTN, GPT_MODEL_BTN, QWEN_MODEL_BTN
from bot.utils.config import ADMIN_IDS


def get_main_menu(user: User):
    kbd = [

        [types.InlineKeyboardButton(text=START_DIALOG_BTN, callback_data="start_dialog")],
        [types.InlineKeyboardButton(text=PLANS_BTN, callback_data="show_plans")],
        [types.InlineKeyboardButton(text=INFO_BTN, callback_data="show_info"),
         types.InlineKeyboardButton(text=AUTOPAY_SWITCH_BTN, callback_data="switch_autopay")],
        [types.InlineKeyboardButton(text=ENTER_PROMO_BTN, callback_data="enter_promo"),
         types.InlineKeyboardButton(text=SETTINGS_BTN, callback_data="show_settings")],
        [types.InlineKeyboardButton(text=REF_BTN, callback_data="show_ref")],
    ]

    if user.user_id in ADMIN_IDS or user.is_admin:
        kbd.append([types.InlineKeyboardButton(text=ADMIN_JOIN_BTN, callback_data="join_admin")])
    main_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=kbd
    )
    return main_keyboard


# ----------------------------------------------------------------------------------------------------------------------

def generate_plans_kbd(json_data):
    _kbd = []
    for plan in json_data:
        if plan['price'] == 0:
            continue
        _kbd.append([types.InlineKeyboardButton(text=PLANS_BUY_PART_BTN.format(plan['name'], plan['price']),
                                                callback_data=f"plan_{plan['uid']}")])
    _kbd.append([types.InlineKeyboardButton(text=BACK_BTN, callback_data="main_menu")])
    plans_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=_kbd
    )
    return plans_keyboard


def get_confirm_kbd(plan_uid):
    confirmation_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=BUY_BTN, callback_data=f"confirm_purchase_{plan_uid}")],
        [types.InlineKeyboardButton(text=CANCEL_BTN, callback_data="cancel_purchase")]
    ])
    return confirmation_keyboard


def get_settings_kbd(user: User):
    gpt_text = f"{'' if user.current_model == 'qwen' else CHOICED_MODEL_PART_TXT}" + GPT_MODEL_BTN
    qwen_text = f"{'' if user.current_model == 'gpt' else CHOICED_MODEL_PART_TXT}" + QWEN_MODEL_BTN
    confirmation_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=gpt_text, callback_data=f"change_model_to:gpt"),
         types.InlineKeyboardButton(text=qwen_text, callback_data="change_model_to:qwen")],
        [types.InlineKeyboardButton(text=BACK_BTN, callback_data=f"main_menu")],
    ])
    return confirmation_keyboard


stop_dialog_keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [types.KeyboardButton(text=STOP_DIALOG_BTN)]
    ]
)

cancel_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text=BACK_BTN, callback_data="cancel")]
])
