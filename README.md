# FastAPI-SSE

![PyPI - Downloads](https://img.shields.io/pypi/dd/fastapi-sse)
![PyPI - Version](https://img.shields.io/pypi/v/fastapi-sse)
[![Rye](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/rye/main/artwork/badge.json)](https://rye.astral.sh)

*A tiny library for sending Server-Sent Events (SSE) in FastAPI*

Server-Sent Events (SSE) provide a way to stream real-time updates from the server to the client over HTTP. This library allows sending Pydantic models as SSE events in FastAPI, formatted as JSON.

```python
from fastapi import FastAPI
from fastapi_sse import sse_response
from pydantic import BaseModel

app = FastAPI()

class MyMessage(BaseModel):
    text: str

@app.get("/stream")
@sse_handler()
async def message_generator(some_url_arg: str):
    yield MyMessage(text=f"Hello, {some_url_arg}!")
    yield MyMessage(text="Another message")
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
pip install fastapi-sse
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
