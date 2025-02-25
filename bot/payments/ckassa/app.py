import base64
import ssl
from typing import Dict, Any, Optional

import httpx

from bot.utils.config import ApiLoginAuthorization, ApiAuthorization, servCode


class CKassa:
    def __init__(
            self,
            base_url: str,
            webhook_url: str,
            timeout: Optional[httpx.Timeout] = None
    ):
        if timeout is None:
            timeout = httpx.Timeout(timeout=60, connect=10.0, read=60.0)

        ssl_context = ssl.create_default_context()
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        auth = httpx.BasicAuth(ApiLoginAuthorization, ApiAuthorization)

        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            auth=auth,
            verify=ssl_context,
        )
        self.webhook_url = webhook_url

    async def create_invoice(
            self,
            amount: int,
            properties: list[str]
    ) -> Dict[str, Any]:
        payload = {
            "serviceCode": servCode,
            "amount": str(int(amount) * 100),
            "comission": str(0),
            "properties": properties,
            "cbUrl": self.webhook_url,
        }
        response = await self.client.post(
            "do/payment/anonymous",
            json=payload
        )
        response.raise_for_status()
        return response.json()['payUrl']

    async def close(self) -> None:
        await self.client.aclose()
