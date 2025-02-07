import asyncio
import aiofiles
import json

_file_locks = {}
_file_locks_lock = asyncio.Lock()


async def _get_lock(file_path: str) -> asyncio.Lock:
    async with _file_locks_lock:
        if file_path not in _file_locks:
            _file_locks[file_path] = asyncio.Lock()
        return _file_locks[file_path]


class AsyncJsonHandler:
    @staticmethod
    async def read(file_path: str) -> dict:
        lock = await _get_lock(file_path)
        async with lock:
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)

    @staticmethod
    async def write(src_path: str, dst_path: str):
        if src_path == dst_path:
            lock = await _get_lock(src_path)
            async with lock:
                async with aiofiles.open(src_path, mode='r', encoding='utf-8') as src_file:
                    content = await src_file.read()
                data = json.loads(content)
                formatted_content = json.dumps(data, ensure_ascii=False, indent=4)
                async with aiofiles.open(dst_path, mode='w', encoding='utf-8') as dst_file:
                    await dst_file.write(formatted_content)
        else:
            if src_path < dst_path:
                first_lock = await _get_lock(src_path)
                second_lock = await _get_lock(dst_path)
            else:
                first_lock = await _get_lock(dst_path)
                second_lock = await _get_lock(src_path)
            async with first_lock:
                async with second_lock:
                    async with aiofiles.open(src_path, mode='r', encoding='utf-8') as src_file:
                        content = await src_file.read()
                    data = json.loads(content)
                    formatted_content = json.dumps(data, ensure_ascii=False, indent=4)
                    async with aiofiles.open(dst_path, mode='w', encoding='utf-8') as dst_file:
                        await dst_file.write(formatted_content)

    @staticmethod
    async def validate(file_path: str) -> bool:
        lock = await _get_lock(file_path)
        async with lock:
            try:
                async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                    content = await f.read()
                if not content.strip():
                    return False
                json.loads(content)
                return True
            except Exception:
                return False


def get_plan_by_name(json_, plan_name):
    for plan in json_:
        if plan['uid'] == plan_name:
            return plan
    return None