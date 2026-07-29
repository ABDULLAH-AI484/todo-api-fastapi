# Task API — Python/FastAPI CRUD

A small in-memory CRUD API for managing a to-do list, built with [FastAPI](https://fastapi.tiangolo.com/).

> **Note:** Data lives only in memory. When the server restarts, all tasks reset to the original 3 examples (unless you added new ones in code). This is intentional — it illustrates why databases exist.

---

## Install & Run

1. **Clone the repo**
   ```bash
   git clone <your-repo-url>
   cd todo-api-fastapi
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate it**
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

   The API is now running at `http://localhost:8000`

---

## API Endpoints

| Method | Endpoint | Description | Status codes |
|--------|----------|-------------|--------------|
| GET | `/` | API info | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/tasks` | List all tasks (optional `?done=` and `?search=` filters) | 200 |
| GET | `/tasks/{id}` | Get a single task | 200, 404 |
| POST | `/tasks` | Create a new task | 201, 400 |
| PUT | `/tasks/{id}` | Update a task | 200, 400, 404 |
| DELETE | `/tasks/{id}` | Delete a task | 204, 404 |
| GET | `/stats` | Task statistics | 200 |
| POST | `/reset` | Reset task list to defaults | 200 |

---

## Swagger UI

FastAPI auto-generates interactive documentation.

Open your browser to: **`http://localhost:8000/docs`**

You can explore every endpoint and click **"Try it out"** to send real requests without leaving the browser.

<img width="945" height="911" alt="image" src="https://github.com/user-attachments/assets/7751d7d4-5295-4eac-aa24-a189fb82ce77" />


---

## Example `curl` Session

```bash
# 1. Check health
curl -i http://localhost:8000/health
```

**Response:**
```http
HTTP/1.1 200 OK
content-type: application/json

{"status":"ok"}
```

```bash
# 2. List tasks
curl -i http://localhost:8000/tasks
```

**Response:**
```http
HTTP/1.1 200 OK
content-type: application/json

[
  {"id":1,"title":"Buy groceries","done":false},
  {"id":2,"title":"Walk the dog","done":true},
  {"id":3,"title":"Read a book","done":false}
]
```

```bash
# 3. Create a task
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

**Response:**
```http
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

```bash
# 4. Update the task
curl -i -X PUT http://localhost:8000/tasks/4 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'
```

**Response:**
```http
HTTP/1.1 200 OK
content-type: application/json

{"id":4,"title":"Buy milk","done":true}
```

```bash
# 5. Delete the task
curl -i -X DELETE http://localhost:8000/tasks/4
```

**Response:**
```http
HTTP/1.1 204 No Content
```

```bash
# 6. Try a missing task → 404
curl -i http://localhost:8000/tasks/99
```

**Response:**
```http
HTTP/1.1 404 Not Found
content-type: application/json

{"detail":"Task 99 not found"}
```

```bash
# 7. Try invalid input → 400
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```http
HTTP/1.1 422 Unprocessable Entity
content-type: application/json

{"detail":[{"type":"missing","loc":["body","title"],"msg":"Field required"}]}
```

---

## The Mortality Experiment

Create a few tasks via Swagger UI or curl, then stop the server (`Ctrl+C`) and start it again. Now `GET /tasks`.

**What happened?** All tasks you created are gone. Only the original 3 seeded tasks remain.

**Why?** The server stores tasks in a Python variable (`tasks = [...]`). Variables live in RAM, and RAM is wiped when the process ends. Databases exist to save data to disk so it survives restarts. This is the entire reason Week 3 of the program exists.

---

## Extra Features

- **Filtering:** `GET /tasks?done=true` returns only finished tasks.
- **Search:** `GET /tasks?search=milk` returns tasks with "milk" in the title.
- **Stats:** `GET /stats` returns `{"total": N, "done": N, "open": N}`.
- **Reset:** `POST /reset` restores the original 3 tasks.

---

## AI vs Me (Stage 7)

### Prompt Used

> Build a Python FastAPI CRUD API for an in-memory to-do list with endpoints: GET /, GET /health, GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id}. Use an in-memory list. Validate that title is present on create. Return proper status codes: 200 for reads, 201 for create, 204 for delete, 404 when a task is not found. Do not use a database.

### Differences Found

1. **What the AI did better — but do I understand it?**
   The AI version used `max(t["id"] for t in tasks) + 1` to compute the next ID dynamically instead of keeping a global counter. That's clever and avoids a global variable, though slightly less efficient (O(n) each time). I understand the logic and may adopt it as a hybrid.

2. **What did it get wrong or quietly ignore?**
   - The AI returned JSON error bodies with status **200 OK** for 404 cases instead of raising proper HTTP exceptions. FastAPI did not send 404 status codes; it sent 200 with an error dict.
   - The AI did not enforce the missing/empty title validation on its own class definition; it relied on FastAPI defaults which give 422 instead of the prompt's implicit 400 expectation.
   - No query parameters or extra endpoints were included.

3. **What did the prompt forget to specify — and what did the AI silently decide?**
   - The prompt did not mention **query parameters** (`?done=`, `?search=`), so the AI omitted them entirely.
   - The prompt did not mention ** Swagger/OpenAPI descriptions**, so the AI left endpoints undocumented in the UI.
   - The AI silently chose to make `done` optional in the creation model and set it to `False` by default, which happens to match the business rule but was an assumption.

### One Rematch

Improved prompt: *"...Return **404 Not Found** with a proper HTTP exception (not a 200 JSON error) when a task ID does not exist. On create, if title is missing or empty, return **400 Bad Request**. Add GET /tasks?done=true query filtering and a GET /stats endpoint. Add short docstrings so Swagger UI shows descriptions."*

**Result:** The regenerated AI code raised `HTTPException(status_code=404)` correctly and added the stats endpoint, confirming the output is only as good as the specification.

---

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic

---

