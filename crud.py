from fastapi import FastAPI, status, Body, HTTPException

app = FastAPI(title='Api messages', description = "API work with messages",  version = "0.0.1")

messages_db = {0: "First post in FastAPI"}

@app.get("/messages")
async def read_messages() -> dict:
    return messages_db

@app.get("/messages/{message_id}")
async def read_message(message_id: int) -> str:
    return messages_db[message_id]

@app.post("/messages", status_code=status.HTTP_201_CREATED)
async def create_message(message: str = Body(...)) -> str:
    current_index = max(messages_db) + 1 if messages_db else 0
    messages_db[current_index] = message
    return "Message created!"

@app.put("/messages/{message_id}", status_code=status.HTTP_200_OK)
async def update_message(message_id: int, message: str = Body(...)) -> str:
    if message_id not in messages_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    messages_db[message_id] = message
    return "Message uptated"

@app.delete("/messages/{message_id}", status_code=status.HTTP_200_OK)
async def delete_message(message_id: int) -> str:
    if message_id not in messages_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    messages_db.pop(message_id)
    return f"Message ID={message_id} was deleted"

@app.delete("/messages", status_code=status.HTTP_200_OK)
async def delete_messages() -> str:
    messages_db.clear()
    return "All message deleted"