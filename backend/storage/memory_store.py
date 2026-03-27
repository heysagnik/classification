import asyncio
from copy import deepcopy
from typing import Any
from uuid import uuid4


class ImageNotFoundError(Exception):
    pass


class StepOrderError(Exception):
    pass


class MemoryStore:
    """In-memory store for user-driven step pipeline state."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def create_entry(self, image_bytes: bytes, step1: dict[str, Any]) -> str:
        image_id = str(uuid4())
        async with self._lock:
            self._store[image_id] = {
                "image_bytes": bytes(image_bytes),
                "step1": deepcopy(step1),
                "step2": None,
            }
        return image_id

    async def get_step1(self, image_id: str) -> dict[str, Any]:
        async with self._lock:
            entry = self._store.get(image_id)
            if not entry:
                raise ImageNotFoundError("Invalid image_id")
            step1 = entry.get("step1")
            if not isinstance(step1, dict):
                raise StepOrderError("Step 1 result is missing for this image_id")
            return deepcopy(step1)

    async def save_step2(self, image_id: str, step2: dict[str, Any]) -> None:
        async with self._lock:
            entry = self._store.get(image_id)
            if not entry:
                raise ImageNotFoundError("Invalid image_id")
            step1 = entry.get("step1")
            if not isinstance(step1, dict):
                raise StepOrderError("Step 1 must be completed before Step 2")
            entry["step2"] = deepcopy(step2)

    async def get_for_generation(self, image_id: str) -> tuple[bytes, list[str]]:
        async with self._lock:
            entry = self._store.get(image_id)
            if not entry:
                raise ImageNotFoundError("Invalid image_id")

            step2 = entry.get("step2")
            if not isinstance(step2, dict):
                raise StepOrderError("Step 2 must be completed before Step 3")

            improvements = step2.get("improvements")
            if not isinstance(improvements, list) or not improvements:
                raise StepOrderError("Step 2 improvements are missing for this image_id")

            image_bytes = entry.get("image_bytes")
            if not isinstance(image_bytes, (bytes, bytearray)):
                raise StepOrderError("Stored image is missing for this image_id")

            return bytes(image_bytes), [str(item) for item in improvements]


memory_store = MemoryStore()
