from fastapi import WebSocket


class ConnectionManager:
    """Manage active WebSocket connections and broadcast data to clients."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection and add it to the active list."""
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from the active list."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_data(self, data: dict) -> None:
        """Broadcast data to all active WebSocket clients."""
        disconnected: list[WebSocket] = []

        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)

        for connection in disconnected:
            await self.disconnect(connection)


manager = ConnectionManager()
