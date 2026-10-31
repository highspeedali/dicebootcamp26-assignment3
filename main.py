import os

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

APP_VERSION = os.getenv("APP_VERSION", "0.1.0") or os.getenv(
    "GITHUB_REF_NAME",
    "0.1.0",
)

app = FastAPI(title="CI/CD Lab", version=APP_VERSION)


class Item(BaseModel):
    name: str
    price: float


items: dict[int, Item] = {}


@app.get("/")
def read_root():
    return {
        "message": "Hello from CI/CD lab!",
        "version": APP_VERSION,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/items/{item_id}", status_code=status.HTTP_201_CREATED)
def create_item(item_id: int, item: Item):
    if item_id in items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exists"
        )
    items[item_id] = item
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Item created successfully"},
    )


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return items[item_id]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
