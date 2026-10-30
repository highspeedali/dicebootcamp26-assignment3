# Assignment 3 - GitHub Actions Assignment

A simple FastAPI application with two endpoints:
- `/` - Returns a "Hello, World!" message
- `/ping` - Health check endpoint that returns "pong"

#### Requirements

- Python 3.8+
- FastAPI
- Uvicorn

```
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello, World!"}

@app.get("/ping")
def health_check():
    return {"pong"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```
