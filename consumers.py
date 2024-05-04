import json
from fastapi import (
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from datetime import datetime
from fastapi.responses import JSONResponse
from models import User, Message
from sqlalchemy.orm import Session
from database import get_db


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, message: dict[str, str]) -> None:
        # Make a copy of the list to prevent modification during iteration
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except (
                Exception
            ) as e:  # This exception is likely if the socket is no longer connected
                print(f"Error sending message: {e}")
                await self.disconnect(connection)


manager = ConnectionManager()


async def websocket_endpoint(
    websocket: WebSocket, client_id: int, db: Session = Depends(get_db)
) -> None:
    await manager.connect(websocket)
    user = db.query(User).filter(User.id == client_id).first()

    if not user:
        await websocket.close(code=4000)

        return  # Closing the WebSocket if the user is not found

    try:
        user.online = True
        db.commit()

        while True:
            data: str = await websocket.receive_text()
            if not data:
                continue

            message: dict[str, str] = {
                "time": datetime.now().strftime("%H:%M"),
                "clientId": client_id,
                "message": data,
            }
            await manager.broadcast(json.dumps(message))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        user.online = False
        db.commit()
        message = {
            "time": datetime.now(),
            "clientId": client_id,
            "message": "Offline",
            "type_offline": True,
        }
        await manager.broadcast(json.dumps(message))


async def send_message(message: str, client_id: int, db: Session) -> dict[str, str]:
    user = db.query(User).filter(User.id == client_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create the message
    db_message = Message(sender_id=client_id, content=message)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return JSONResponse(
        status_code=201,
        content={
            "message": "Message inserted successfully",
            "new_message": db_message.content,
        },
    )
