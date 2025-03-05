from aiogram.fsm.state import StatesGroup, State


class BuyPlan(StatesGroup):
    confirmation = State()


class Dialog(StatesGroup):
    message = State()


class CreatePromo(StatesGroup):
    promo = State()


class EnterPromo(StatesGroup):
    promo = State()
    confirm = State()


class BanUser(StatesGroup):
    uid = State()
    confirmation = State()


class MassSend(StatesGroup):
    msg = State()
    confirmation = State()


class AddAdmin(StatesGroup):
    uid = State()


class ChangePlans(StatesGroup):
    new_plans = State()


class GetInfo(StatesGroup):
    uid = State()


class VideoGeneration(StatesGroup):
    prompt = State()

class ImageGeneration(StatesGroup):
    prompt = State()
