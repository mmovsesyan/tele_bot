from aiogram import types

from bot.database.models import User
from bot.texts import GET_OFFER_BTN, PLANS_BTN, START_DIALOG_BTN, ENTER_PROMO_BTN, REF_BTN, \
    ADMIN_JOIN_BTN, PLANS_BUY_PART_BTN, BACK_BTN, SETTINGS_BTN, CANCEL_BTN, BUY_BTN, CHOICED_MODEL_PART_TXT, \
    STOP_DIALOG_BTN, INFO_BTN, GPT_MODEL_BTN, QWEN_MODEL_BTN, VIDEO_GENERATION_BTN, BUY_VIDEO_JOIN_BTN, \
    VIDEO_PLANS_BUY_PART_BTN, CLAUDE_MODEL_BTN, BUY_IMAGE_JOIN_BTN, IMAGE_GENERATION_BTN, IMAGE_PLANS_BUY_PART_BTN
from bot.utils.config import ADMIN_IDS


def get_main_menu(user: User):
    kbd = [

        [types.InlineKeyboardButton(text=START_DIALOG_BTN, callback_data="start_dialog")],
        # [types.InlineKeyboardButton(text=VIDEO_GENERATION_BTN, callback_data="video_generation")],
        [types.InlineKeyboardButton(text=IMAGE_GENERATION_BTN, callback_data="image_generation")],
        [types.InlineKeyboardButton(text=PLANS_BTN, callback_data="show_plans")],
        [types.InlineKeyboardButton(text=INFO_BTN, callback_data="show_info"),
         types.InlineKeyboardButton(text=GET_OFFER_BTN, callback_data="get_offer")],
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
    _kbd.append([types.InlineKeyboardButton(text=BUY_IMAGE_JOIN_BTN, callback_data="image_buy")])
    # _kbd.append([types.InlineKeyboardButton(text=BUY_VIDEO_JOIN_BTN, callback_data="video_buy")])
    _kbd.append([types.InlineKeyboardButton(text=BACK_BTN, callback_data="main_menu")])
    plans_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=_kbd
    )
    return plans_keyboard


def vid_img_plans_kbd(json_data, type_: str, type_2: str):
    _kbd = []
    btn_text = VIDEO_PLANS_BUY_PART_BTN if type_2 == 'video' else IMAGE_PLANS_BUY_PART_BTN
    for plan in json_data:
        _kbd.append([types.InlineKeyboardButton(text=btn_text.format(plan[type_2], plan['usd_price']),
                                                callback_data=f"{type_}:{plan['uid']}")])
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
    gpt_text = f"{CHOICED_MODEL_PART_TXT if user.current_model == 'gpt' else ''}" + GPT_MODEL_BTN
    qwen_text = f"{CHOICED_MODEL_PART_TXT if user.current_model == 'qwen' else ''}" + QWEN_MODEL_BTN
    claude_text = f"{CHOICED_MODEL_PART_TXT if user.current_model == 'claude' else ''}" + CLAUDE_MODEL_BTN
    confirmation_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=gpt_text, callback_data=f"change_model_to:gpt"),
         types.InlineKeyboardButton(text=qwen_text, callback_data="change_model_to:qwen"),
         types.InlineKeyboardButton(text=claude_text, callback_data="change_model_to:claude")],
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
