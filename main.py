from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A simple in-memory CRUD API for managing tasks."
)

# In-memory task storage
# Data lives only while the server is running — this is by design.
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Read a book", "done": False},
]

next_id = 4  # Used to auto-increment task IDs


# Pydantic models for request/response validation
class Task(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        json_schema_extra = {
            "example": {"id": 1, "title": "Buy groceries", "done": False}
        }


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="The title of the task")

    class Config:
        json_schema_extra = {
            "example": {"title": "Buy milk"}
        }


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="The new title")
    done: Optional[bool] = Field(None, description="Whether the task is completed")

    class Config:
        json_schema_extra = {
            "example": {"title": "Buy almond milk", "done": True}
        }


# --- Stage 1: Root and Health ---
@app.get("/", summary="API Info", tags=["Meta"])
def read_root():
    """Returns basic information about the API."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Health Check", tags=["Meta"])
def health_check():
    """Returns the health status of the server."""
    return {"status": "ok"}


# --- Stage 2: Read ---
@app.get("/tasks", response_model=List[Task], summary="List all tasks", tags=["Tasks"])
def list_tasks(
    done: Optional[bool] = Query(None, description="Filter by completion status"),
    search: Optional[str] = Query(None, description="Search in task titles")
):
    """
    Returns the in-memory task list.
    
    Optional query parameters:
    - **done**: filter by true/false
    - **search**: case-insensitive search in titles
    """
    result = tasks.copy()

    if done is not None:
        result = [t for t in result if t["done"] == done]

    if search:
        result = [t for t in result if search.lower() in t["title"].lower()]

    return result


@app.get("/tasks/{task_id}", response_model=Task, summary="Get a single task", tags=["Tasks"])
def get_task(task_id: int):
    """Returns a single task by its ID."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# --- Stage 3: Create ---
@app.post("/tasks", response_model=Task, status_code=201, summary="Create a new task", tags=["Tasks"])
def create_task(payload: TaskCreate):
    """
    Creates a new task with the given title.
    
    - **title** is required and must not be empty.
    - The server assigns the next available ID and sets **done** to false.
    """
    global next_id
    new_task = {
        "id": next_id,
        "title": payload.title.strip(),
        "done": False
    }
    tasks.append(new_task)
    next_id += 1
    return new_task


# --- Stage 4: Update & Delete ---
@app.put("/tasks/{task_id}", response_model=Task, summary="Update a task", tags=["Tasks"])
def update_task(task_id: int, payload: TaskUpdate):
    """
    Updates an existing task's title and/or done status.
    
    - Returns 404 if the task ID does not exist.
    - At least one valid field must be provided.
    """
    for task in tasks:
        if task["id"] == task_id:
            if payload.title is not None:
                task["title"] = payload.title.strip()
            if payload.done is not None:
                task["done"] = payload.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task", tags=["Tasks"])
def delete_task(task_id: int):
    """
    Deletes a task by ID.
    
    - Returns 204 No Content on success.
    - Returns 404 if the task ID does not exist.
    """
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# --- Extras ---
@app.get("/stats", summary="Task statistics", tags=["Extras"])
def get_stats():
    """Returns a summary of task counts."""
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    return {
        "total": total,
        "done": done_count,
        "open": total - done_count
    }


@app.post("/reset", summary="Reset tasks", tags=["Extras"])
def reset_tasks():
    """
    Resets the in-memory task list back to the original 3 example tasks.
    Handy for demos and testing.
    """
    global next_id
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Buy groceries", "done": False},
        {"id": 2, "title": "Walk the dog", "done": True},
        {"id": 3, "title": "Read a book", "done": False},
    ])
    next_id = 4
    return {"message": "Tasks reset to defaults"}


# Entry point for running directly
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
