# Entry point: creates the FastAPI app, trains the decision tree on startup, and registers routes.

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from backend.api.routes import router, HTTP_BAD_REQUEST
from backend.repository.dataset_repository import load_dataset
from backend.repository.tree_repository import save_tree
from backend.services.tree_builder import build_tree

load_dotenv()

DEFAULT_PORT = 5001

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # train once at startup and stash it so routes don't need to rebuild it
    rows = load_dataset()
    tree = build_tree(rows)
    save_tree(tree)
    app.state.trained_tree = tree
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://lotus-task.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    messages = []
    for error in exc.errors():
        # strip "body" so the path reads "sleep: ..." instead of "body.sleep: ..."
        loc_parts = [str(part) for part in error["loc"] if part != "body"]
        field = ".".join(loc_parts)
        msg = error["msg"]
        messages.append("{}: {}".format(field, msg) if field else msg)
    return JSONResponse(status_code=HTTP_BAD_REQUEST, content={"error": "; ".join(messages)})


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=True)