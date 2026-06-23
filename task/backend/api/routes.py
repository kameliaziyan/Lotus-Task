# API routes: defines the /predict and /tree endpoints.

from typing import Any, Literal, Optional
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from backend.models.data_row import DataRow
from backend.models.tree_node import node_to_dict
from backend.repository.tree_repository import load_tree
from backend.services.tree_builder import predict

router = APIRouter()

HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500
_ERROR_KEY = "error"


class PredictRequest(BaseModel):
    sleep: float = Field(ge=0, le=24)
    meetings: int = Field(ge=0, le=100)
    weekends: Literal["Yes", "No"]
    stress: float = Field(ge=1, le=10)


def _get_tree(request: Request) -> Optional[Any]:
    tree = getattr(request.app.state, "trained_tree", None)
    if tree is not None:
        return tree
    tree = load_tree()
    # cache in app state so we don't hit disk on every request
    if tree is not None:
        request.app.state.trained_tree = tree
    return tree


async def _predict_handler(body: PredictRequest, request: Request) -> Any:
    tree = _get_tree(request)
    if tree is None:
        return JSONResponse(
            {_ERROR_KEY: "No trained model found. Restart the server to retrain."},
            status_code=HTTP_NOT_FOUND,
        )
    # outcome is required by DataRow but irrelevant for prediction
    row = DataRow(
        sleep=body.sleep,
        meetings=body.meetings,
        weekends=body.weekends,
        stress=body.stress,
        outcome="Healthy",
    )
    outcome, path = predict(tree, row)
    return {"outcome": outcome, "path": path}


@router.post("/predict")
async def predict_endpoint(body: PredictRequest, request: Request) -> Any:
    try:
        return await _predict_handler(body, request)
    except Exception as exc:
        return JSONResponse({_ERROR_KEY: str(exc)}, status_code=HTTP_SERVER_ERROR)
    

@router.get("/tree")
async def get_tree(request: Request) -> Any:
    try:
        tree = _get_tree(request)
        if tree is None:
            return JSONResponse(
                {_ERROR_KEY:"No trained tree found. Restart the server to retrain."},
                status_code=HTTP_NOT_FOUND,
            )
        return node_to_dict(tree)
    except Exception as exc:
        return JSONResponse({_ERROR_KEY: str(exc)}, status_code=HTTP_SERVER_ERROR)


