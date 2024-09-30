from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator, Any


def sse_response(
    generator: AsyncGenerator[BaseModel, Any],
) -> StreamingResponse:
    """
    Creates a StreamingResponse that formats each Pydantic model emitted by the generator as a Server-Sent Event.
    The event type is set to the name of the Pydantic model class.
    """

    async def event_source_wrapper():
        async for event in generator:
            event_type = event.__class__.__name__
            data = event.model_dump_json()
            yield f'event: {event_type}\ndata: {data}\n\n'.encode()

    return StreamingResponse(
        event_source_wrapper(),
        media_type='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'},
    )
