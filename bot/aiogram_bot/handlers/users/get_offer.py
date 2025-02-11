from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(F.data == "get_offer")
async def f(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer_document(types.FSInputFile('src/Оферта.pdf'))