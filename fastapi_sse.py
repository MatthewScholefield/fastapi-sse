from functools import wraps
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator, Awaitable, Callable, ParamSpec


P = ParamSpec('P')
EventGeneratorFunc = Callable[P, AsyncGenerator[BaseModel, None]]
StreamingResponseFunc = Callable[P, Awaitable[StreamingResponse]]


def sse_handler(
    *, emit_type: bool = False
) -> Callable[[EventGeneratorFunc], StreamingResponseFunc]:
    """
    Converts an async generator that yields Pydantic models into a streaming
    response handler that formats each model as a Server-Sent Event.

    Args:
        argument: An async generator that yields Pydantic models. If None, the
            function will return a decorator that can be used to decorate an
            async generator.
        emit_type: If True, the event type will be emitted as a field in the
            event data. Note: When using the EventSource API, messages
            will be ONLY handled via .addEventListener('<eventType>', ...)
            and NOT via .onmessage.
    """
    if not isinstance(emit_type, bool):
        raise TypeError(
            "The 'emit_type' argument must be a boolean. Did you forget to "
            'include the parentheses when using the @sse_handler() decorator?'
        )

    def decorator(generator_func: EventGeneratorFunc) -> StreamingResponseFunc:
        @wraps(generator_func)
        async def streaming_handler(
            *args: P.args, **kwargs: P.kwargs
        ) -> StreamingResponse:
            generator_iterator = aiter(generator_func(*args, **kwargs))
            try:
                first_event = await anext(generator_iterator)
            except StopAsyncIteration:

                async def empty_generator():
                    return
                    yield

                return StreamingResponse(
                    empty_generator(), media_type='text/event-stream'
                )

            async def rewrapped_generator():
                yield first_event
                async for event in generator_iterator:
                    yield event

            return sse_response(rewrapped_generator(), emit_type)

        return streaming_handler

    return decorator


def typed_sse_handler() -> Callable[[EventGeneratorFunc], StreamingResponseFunc]:
    """Same as sse_handler, but with emit_type set to True."""
    return sse_handler(emit_type=True)


def sse_response(
    generator: AsyncGenerator[BaseModel, None], emit_type: bool = False
) -> StreamingResponse:
    """
    Creates a StreamingResponse that formats each Pydantic model emitted by the
    generator as a Server-Sent Event. The event type is optionally set to the
    name of the Pydantic model class.

    Args:
        generator: An async generator that yields Pydantic models.
        emit_type: If True, the event type will be emitted as a field in the
            event data. Note: When using the EventSource API, messages
            will be ONLY handled via .addEventListener('<eventType>', ...)
            and NOT via .onmessage
    """

    async def event_source_wrapper():
        async for event in generator:
            message = ''
            if emit_type:
                message += f'event: {event.__class__.__name__}\r\n'
            message += f'data: {event.model_dump_json(exclude_none=True)}\r\n'
            message += '\r\n'
            yield message.encode('utf-8')

    return StreamingResponse(
        event_source_wrapper(),
        media_type='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'},
    )


def typed_sse_response(generator: AsyncGenerator[BaseModel, None]) -> StreamingResponse:
    """Same as sse_response, but with emit_type set to True."""
    return sse_response(generator, emit_type=True)
