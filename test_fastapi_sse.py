import asyncio
from typing import AsyncGenerator, Any, List

from fastapi.exceptions import HTTPException
import pytest
from fastapi import FastAPI
from fastapi_sse import sse_handler, typed_sse_handler
from pydantic import BaseModel
from async_asgi_testclient import TestClient

app = FastAPI()


class MyEvent(BaseModel):
    message: str


class MyEventWithOptionals(BaseModel):
    message: str
    metadata: str | None


async def emit_my_events() -> AsyncGenerator[MyEvent, Any]:
    for i in range(3):
        yield MyEvent(message=f'Test message {i}')
        await asyncio.sleep(0.1)


@app.get('/test-stream')
@sse_handler()
async def my_events_handler():
    for i in range(3):
        await asyncio.sleep(0.1)
        yield MyEvent(message=f'Test message {i}')


@app.get('/test-stream-containing-optionals')
@sse_handler()
async def my_events_with_optionals_handler():
    for i in range(3):
        await asyncio.sleep(0.1)
        yield MyEventWithOptionals(
            message=f'Test message {i}', metadata='sometimes' if i == 0 else None
        )


@app.get('/test-stream-sequence')
@sse_handler()
async def my_events_handler_sequence():
    for i in range(3):
        await asyncio.sleep(0.1)
        yield [MyEvent(message=f'Test message {i}-{j}') for j in range(3)]


@app.get('/test-stream-typed-sequence')
@typed_sse_handler()
async def my_events_handler_typed_sequence():
    for i in range(3):
        await asyncio.sleep(0.1)
        yield [MyEvent(message=f'Test message {i}-{j}') for j in range(3)]


@app.get('/test-stream-typed')
@typed_sse_handler()
async def my_events_handler_typed():
    for i in range(3):
        await asyncio.sleep(0.1)
        yield MyEvent(message=f'Test message {i}')


@app.get('/test-stream-erroring')
@sse_handler()
async def my_events_handler_erroring():
    raise HTTPException(status_code=404, detail='Example stream not found error')

    for i in range(3):
        await asyncio.sleep(0.1)
        yield MyEvent(message=f'Test message {i}')


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
async def test_sse_sequence_response():
    async with TestClient(app) as client:
        response = await client.get('/test-stream-sequence', stream=True)
        events = await collect_events_data(response)

        assert response.status_code == 200
        assert events[0] == dict(data='[{"message":"Test message 0-0"},{"message":"Test message 0-1"},{"message":"Test message 0-2"}]')
        assert events[1] == dict(data='[{"message":"Test message 1-0"},{"message":"Test message 1-1"},{"message":"Test message 1-2"}]')
        assert events[2] == dict(data='[{"message":"Test message 2-0"},{"message":"Test message 2-1"},{"message":"Test message 2-2"}]')


@pytest.mark.asyncio
async def test_sse_response_containing_optionals():
    async with TestClient(app) as client:
        response = await client.get('/test-stream-containing-optionals', stream=True)
        events = await collect_events_data(response)

        assert response.status_code == 200
        assert events[0] == dict(data='{"message":"Test message 0","metadata":"sometimes"}')
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


@pytest.mark.asyncio
async def test_typed_sequence_sse_response():
    async with TestClient(app) as client:
        response = await client.get('/test-stream-typed-sequence', stream=True)
        events = await collect_events_data(response)

        assert response.status_code == 200
        assert events[0]["event"] == "MyEvent"


@pytest.mark.asyncio
async def test_sse_response_erroring():
    async with TestClient(app) as client:
        response = await client.get('/test-stream-erroring')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Example stream not found error'}


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
