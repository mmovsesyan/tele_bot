import json
from datetime import datetime, timedelta

from aiohttp import web
from functools import partial

from bot.aiogram_bot.markups.user_keyboards import get_main_menu
from bot.database.requests.logs import add_log
from bot.database.requests.users import get_user
from bot.texts import PAYMENT_SUCCEED_TXT
from bot.utils.config import CKASSA_WEBHOOKS_PORT
from bot.utils.plans_worker import give_plan
from bot.utils.util import write_error


async def handle_webhook(request, bot):
    try:
        data = await request.json()
        await add_log(user_id=None, message=f"Webhook от CKassa", data=str(data))
        required_fields = ["property", 'state']
        for field in required_fields:
            if field not in data:
                return web.json_response(
                    {"error": f"Missing required field: {field}"},
                    status=400
                )
        try:
            if data['state'] != 'PAYED':
                return web.json_response({"status": "success"}, status=200)
            dat = data['property']['ОПИСАНИЕ']
            id_, plan_name, _ = dat.split(':')
            user_id_ = int(id_)
            p = plan_name
            date_to = (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y')
            plan = await give_plan(id_, p, date_to)
            user = await get_user(user_id_)
            try:
                await bot.send_message(user_id_, PAYMENT_SUCCEED_TXT.format(plan['name'], plan['emoji'], date_to), parse_mode='HTML', reply_markup=get_main_menu(user))
            except Exception as e:
                write_error(e)
                await add_log(user_id=user_id_, message=f"Ошибка при отправке сообщения пользователю", data=e)
                
            
        except Exception as e:
            write_error(e)
            try:
                await add_log(user_id=user_id_, message=f"Ошибка при обработке платежа", data=e)
            except Exception as e:
                await add_log(user_id=0, message=f"Ошибка при обработке платежа", data=e)

            return web.json_response({"status": "error"}, status=500)
        
        return web.json_response({"status": "success"}, status=200)

    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON"}, status=400)


async def init_webhook_app(bot):
    app = web.Application()
    app.router.add_post("/pay/ckassa", partial(handle_webhook, bot=bot))

    runner = web.AppRunner(app)
    await runner.setup()

    ssl_context = None
    site = web.TCPSite(runner, '0.0.0.0', CKASSA_WEBHOOKS_PORT, ssl_context=ssl_context)
    await site.start()
