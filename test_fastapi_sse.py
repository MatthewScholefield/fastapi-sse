import asyncio
from typing import AsyncGenerator, Any

import pytest
from fastapi import FastAPI
from fastapi_sse import sse_response
from pydantic import BaseModel
from async_asgi_testclient import TestClient

app = FastAPI()


class MyEvent(BaseModel):
    message: str


async def emit_my_events() -> AsyncGenerator[MyEvent, Any]:
    for i in range(3):
        yield MyEvent(message=f'Test message {i}')
        await asyncio.sleep(0.1)


@app.get('/test-stream')
async def my_events_handler():
    return sse_response(emit_my_events())


@pytest.mark.asyncio
async def test_sse_response():
    """
    Tests that the SSE response correctly streams events with the Pydantic model name as the event type.
    """
    async with TestClient(app) as client:
        response = await client.get('/test-stream', stream=True)
        events = []
        async for event in response.iter_content(None):
            events.append(event)

        assert response.status_code == 200
        assert events[0] == b'event: MyEvent\ndata: {"message":"Test message 0"}\n\n'
        assert events[1] == b'event: MyEvent\ndata: {"message":"Test message 1"}\n\n'
        assert events[2] == b'event: MyEvent\ndata: {"message":"Test message 2"}\n\n'
