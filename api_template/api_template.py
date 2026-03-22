#!/usr/bin/env python3
"""
REST API Template
FastAPI-based API with CRUD operations, validation, and documentation.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="API Template",
    description="REST API with CRUD operations",
    version="1.0.0"
)

# --- Models ---
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    created_at: datetime

# --- In-memory storage (replace with database in production) ---
items_db: List[ItemResponse] = []
next_id = 1

# --- Routes ---
@app.get("/")
def root():
    return {"message": "API Template", "version": "1.0.0"}

@app.get("/items", response_model=List[ItemResponse])
def list_items(skip: int = 0, limit: int = 10):
    return items_db[skip:skip + limit]

@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate):
    global next_id
    new_item = ItemResponse(
        id=next_id,
        name=item.name,
        description=item.description,
        price=item.price,
        created_at=datetime.now()
    )
    items_db.append(new_item)
    next_id += 1
    return new_item

@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate):
    for i, existing in enumerate(items_db):
        if existing.id == item_id:
            updated = ItemResponse(
                id=item_id,
                name=item.name or existing.name,
                description=item.description if item.description is not None else existing.description,
                price=item.price or existing.price,
                created_at=existing.created_at
            )
            items_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(i)
            return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)