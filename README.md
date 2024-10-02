# FastAPI-SSE

*A tiny library for sending Server-Sent Events (SSE) in FastAPI*

Server-Sent Events (SSE) provide a way to stream real-time updates from the server to the client over HTTP. This library allows sending Pydantic models as SSE events in FastAPI, formatted as JSON.

```python
from fastapi import FastAPI
from fastapi_sse import sse_response
from pydantic import BaseModel

app = FastAPI()

class MyMessage(BaseModel):
    text: str

async def message_generator():
    yield MyMessage(text="Hello, SSE!")
    yield MyMessage(text="Another message")

@app.get("/stream")
async def stream_messages():
    return sse_response(message_generator())
```

And on the frontend to handle:

```javascript
const eventSource = new EventSource('/stream');
eventSource.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Received message:', message);
};
```

## Installation

Install the library using pip:

```
pip install git+https://github.com/MatthewScholefield/fastapi-sse.git
```

## Typed Events

You can also use `typed_sse_response` to send messages with the event type populated with the model name.

*Note: When emitting typed messages, `EventSource` will no longer trigger the `onmessage` event. Instead, you must attach a handler via `.addEventListener('<eventType>', ...)`.:*

```javascript
const eventSource = new EventSource('/stream');
eventSource.addEventListener('MyMessage', (event) => {
    const message = JSON.parse(event.data);
    console.log('Received message:', message);
});
```

```python

## Development

FastAPI-SSE uses Rye for dependency management and the development workflow. To get started with development, ensure you have [Rye](https://github.com/astral-sh/rye) installed and then clone the repository and set up the environment:

```sh
git clone https://github.com/MatthewScholefield/fastapi-sse.git
cd fastapi-sse
rye sync
rye run pre-commit install

# Run tests
rye test
```
