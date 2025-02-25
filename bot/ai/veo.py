import asyncio
import logging

import httpx
from typing import Optional, Dict, Any

from bot.utils.config import GEN_VIDEO_DURATION, GEN_VIDEO_ASPECT_RATIO


class VeoAPI:
    BASE_URL = "https://veo2api.com/api/index.php"
    # BASE_URL = "http://127.0.0.1:5000/api/index.php"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_video(
            self,
            prompt: str,
            duration: Optional[str] = GEN_VIDEO_DURATION,
            aspect_ratio: Optional[str] = None
    ) -> str:
        data: Dict[str, Any] = {"prompt": prompt}

        if duration is not None:
            data["duration"] = str(duration)
        if aspect_ratio is not None:
            data["aspect_ratio"] = aspect_ratio

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.BASE_URL,
                headers=self.headers,
                json=data
            )
            logging.info(response.text)
            response.raise_for_status()
            result = response.json()
        if "request_id" not in result:
            raise ValueError("Ошибка: No 'request_id' in response. Response: {}".format(result))

        return result["request_id"]

    async def check_status(self, request_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/status"
        params = {"request_id": request_id}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            logging.info(response.text)
            response.raise_for_status()
            return response.json()

    async def get_result(self, request_id: str) -> Dict[str, Any]:
        params = {"request_id": request_id}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, headers=self.headers, params=params)
            logging.info(response.text)
            response.raise_for_status()
            return response.json()
    async def run(
        self,
        prompt: str,
        duration: Optional[str] = GEN_VIDEO_DURATION,
        aspect_ratio: Optional[str] = GEN_VIDEO_ASPECT_RATIO,
        poll_interval: int = 30,
        max_iterations: int = 900
    ) -> str:
        request_id = await self.generate_video(prompt, duration, aspect_ratio)
        for _ in range(max_iterations):
            status_response = await self.check_status(request_id)
            status = status_response.get("status", "").lower()

            if status == "completed":
                result = await self.get_result(request_id)
                return result["video"]["url"]
            elif status == "error":
                raise Exception(f"Ошибка: {status_response}")
            await asyncio.sleep(poll_interval)
        raise TimeoutError(
            f"Видео не было сгенерировано за  {poll_interval * max_iterations} секунд"
        )