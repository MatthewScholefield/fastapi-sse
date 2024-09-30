# FastAPI-SSE

*A simple library for sending Server-Sent Events (SSE) in FastAPI*

Server-Sent Events (SSE) provide a way to stream real-time updates from the server to the client over HTTP. This library allows sending Pydantic models as SSE events in FastAPI, formatted as JSON.

```python
from fastapi import FastAPI
from fastapi_sse import sse_response
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    text: str

async def message_generator():
    yield Message(text="Hello, SSE!")
    yield Message(text="Another message")

@app.get("/stream")
async def stream_messages():
    return sse_response(message_generator())
```

## Installation

Install the library using pip:

```
pip install git+https://github.com/MatthewScholefield/fastapi-sse.git
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
