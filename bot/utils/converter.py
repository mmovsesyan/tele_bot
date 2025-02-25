import aiohttp


class APIException(Exception):
    pass


class CurrencyConverter:
    @staticmethod
    async def get_price(base, quote, amount):
        if base == quote:
            raise APIException("Нельзя конвертировать одну и ту же валюту.")

        url = f"https://api.coingate.com/v2/rates/merchant/{base}/{quote}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise APIException("Ошибка при запросе к API.")
                rate = await response.text()

        try:
            rate = float(rate)
        except ValueError:
            pass

        if isinstance(rate, float):
            return float(rate) * float(amount)
        else:
            raise APIException("Ошибка при обработке курса.")
