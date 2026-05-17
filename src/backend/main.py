import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Support running this file directly from the IDE or shell, e.g.
# `python src/backend/main.py`. In that mode Python only adds
# `src/backend` to sys.path, so absolute imports starting with `src` fail.
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.backend.api.data import generate_mock_data
from src.backend.api.data import router as data_router
from src.backend.core.connection import manager


async def broadcast_mock_device_data() -> None:
    """Generate mock device data every second and broadcast it via WebSocket."""
    while True:
        data = generate_mock_data("plc_01").model_dump(mode="json")
        await manager.broadcast_data(data)
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    broadcast_task = asyncio.create_task(broadcast_mock_device_data())
    try:
        yield
    finally:
        broadcast_task.cancel()
        try:
            await broadcast_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Industrial Platform Demo API",
    description="Industrial platform demo backend service",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow frontend cross-origin requests. Use explicit origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Industrial Platform Demo API is running"}


@app.websocket("/ws/data")
async def websocket_data_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive and allow clients to send heartbeat messages.
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
