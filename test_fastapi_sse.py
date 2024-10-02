import asyncio
from typing import AsyncGenerator, Any, List

import pytest
from fastapi import FastAPI
from fastapi_sse import sse_response, typed_sse_response
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


@app.get('/test-stream-typed')
async def my_events_handler_typed():
    return typed_sse_response(emit_my_events())


@pytest.mark.asyncio
async def test_sse_response():
    async with TestClient(app) as client:
        response = await client.get('/test-stream', stream=True)
        events = await collect_events_data(response)

        assert response.status_code == 200
        assert events[0] == dict(data='{"message":"Test message 0"}')
        assert events[1] == dict(data='{"message":"Test message 1"}')
        assert events[2] == dict(data='{"message":"Test message 2"}')


@pytest.mark.asyncio
async def test_typed_sse_response():
    async with TestClient(app) as client:
        response = await client.get('/test-stream-typed', stream=True)
        events = await collect_events_data(response)

        assert response.status_code == 200
        assert events[0] == dict(data='{"message":"Test message 0"}', event='MyEvent')
        assert events[1] == dict(data='{"message":"Test message 1"}', event='MyEvent')
        assert events[2] == dict(data='{"message":"Test message 2"}', event='MyEvent')


async def collect_events_data(response) -> List[dict]:
    events = []
    async for event in response.iter_content(None):
        message_content: str = event.strip().decode()
        event_data = {
            key: value
            for line in message_content.splitlines()
            for key, value in [line.split(': ', 1)]
        }
        events.append(event_data)
    return events
