import asyncio
from mongoengine import Document
from functools import partial
from contextlib import asynccontextmanager


class BaseDocument(Document):
    meta = {
        "abstract": True,
        "allow_inheritance": True,
    }

    async def async_save(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        func = partial(self.save, *args, **kwargs)
        return await loop.run_in_executor(None, func)

    @classmethod
    async def async_find_one(cls, *args, **kwargs):
        loop = asyncio.get_event_loop()
        func = partial(cls.objects, *args, **kwargs)
        users = await loop.run_in_executor(None, func)
        return users.first()

    @classmethod
    async def async_find(cls, *args, **kwargs):
        loop = asyncio.get_event_loop()
        func = partial(cls.objects, *args, **kwargs)
        return await loop.run_in_executor(None, func)

    @asynccontextmanager
    async def auto_async_save(self, *args, **kwargs):
        try:
            yield
        finally:
            await self.async_save(*args, **kwargs)
