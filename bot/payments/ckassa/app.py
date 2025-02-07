import httpx
import ssl
from typing import Dict, Any, Optional


class CKassa:
    def __init__(
            self,
            base_url: str,
            shop_token: str,
            sec_key: str,
            provider_code: str,
            webhook_url: str,
            timeout: Optional[httpx.Timeout] = None
    ):
        if timeout is None:
            timeout = httpx.Timeout(timeout=60, connect=10.0, read=60.0)

        ssl_context = ssl.create_default_context()
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            auth=httpx.BasicAuth(username=shop_token, password=sec_key),
            verify=ssl_context,
        )
        self.provider_code = provider_code
        self.webhook_url = webhook_url

    async def create_anonymous_payment(
            self,
            amount: int,
            user_data: str,
            **kwargs: Any
    ) -> Dict[str, Any]:
        payload = {
            "serviceCode": self.provider_code,
            "amount": str(int(amount) * 100),
            "comission": str(0),
            "properties": [{'name': "ЛИЦЕВОЙ_СЧЕТ", "value": user_data}],
            "cbUrl": self.webhook_url
        }
        payload.update(kwargs)

        response = await self.client.post("/do/payment/anonymous", json=payload)
        response.raise_for_status()
        return response.json()['payUrl']

    async def close(self) -> None:
        await self.client.aclose()