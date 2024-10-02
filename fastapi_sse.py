from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator, Any


def sse_response(
    generator: AsyncGenerator[BaseModel, Any], emit_type: bool = False
) -> StreamingResponse:
    """
    Creates a StreamingResponse that formats each Pydantic model emitted by the
    generator as a Server-Sent Event. The event type is set to the name of the
    Pydantic model class.

    Args:
        generator: An async generator that yields Pydantic models.
        emit_type: If True, the event type will be emitted as a field in the
            event data. Note: When using the EventSource API, messages
            will be ONLY handled via .addEventListener('<eventType>', ...)
            and NOT via .onmessage.
    """

    async def event_source_wrapper():
        async for event in generator:
            message = ''
            if emit_type:
                message += f'event: {event.__class__.__name__}\r\n'
            message += f'data: {event.model_dump_json()}\r\n'
            message += '\r\n'
            yield message.encode('utf-8')

    return StreamingResponse(
        event_source_wrapper(),
        media_type='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'},
    )


def typed_sse_response(generator: AsyncGenerator[BaseModel, Any]) -> StreamingResponse:
    """
    Creates a StreamingResponse that formats each Pydantic model emitted by the
    generator as a Server-Sent Event. The event type is set to the name of the
    Pydantic model class.

    Args:
        generator: An async generator that yields Pydantic models.
    """
    return sse_response(generator, emit_type=True)
