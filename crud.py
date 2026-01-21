from fastapi import FastAPI, HTTPException, status, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List


app = FastAPI(title='Api messages', description = "API work with messages",  version = "0.1.0")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


class MessageCreate(BaseModel):
    content: str


class Message(BaseModel):
    id: int
    content: str


messages_db: list[Message] = [
    Message(id=0, content="First post in FastAPI"),
    Message(id=1, content="Second post in FastAPI")
    ]


@app.get("/messages", response_model=list[Message])
async def read_messages() -> list[Message]:
    return messages_db


@app.get("/messages/{message_id}", response_model=Message)
async def read_message(message_id: int) -> Message:
    for message in messages_db:
        if message.id == message_id:
            return message
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.post("/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
async def create_message(message_create: MessageCreate) -> Message:
    next_id = max((msg.id for msg in messages_db), default=-1) + 1
    new_message = Message(id=next_id, content=message_create.content)
    messages_db.append(new_message)
    return new_message


@app.put("/messages/{message_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def update_message(message_id: int, message_create: MessageCreate) -> Message:
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            updated_message = Message(id=message_id, content=message_create.content)
            messages_db[i] = updated_message
            return updated_message
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.delete("/messages/{message_id}", status_code=status.HTTP_200_OK)
async def delete_message(message_id: int) -> dict:
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            messages_db.pop(i)
            return {"detail": f"Message ID={message_id} deleted!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.delete("/messages", status_code=status.HTTP_200_OK)
async def delete_messages() -> dict:
    messages_db.clear()
    return {"detail": "All messages deleted!"}


@app.get("/web/messages/create", response_class=HTMLResponse)
async def get_create_message_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.get("/web/messages", response_class=HTMLResponse)
async def get_messages_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "messages": messages_db})


@app.post("/web/messages", response_class=HTMLResponse)
async def create_message_form(request: Request, content: str = Form(...)):
    next_id = max((msg.id for msg in messages_db), default=-1) + 1
    new_message = Message(id=next_id, content=content)
    messages_db.append(new_message)
    return templates.TemplateResponse("index.html", {"request": request, "messages": messages_db})


@app.get("/web/messages/{message_id}", response_class=HTMLResponse)
async def get_message_detail_page(request: Request, message_id: int):
    for message in messages_db:
        if message.id == message_id:
            return templates.TemplateResponse("detail.html", {"request": request, "message": message})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.get("/web/messages/{message_id}/edit", response_class=HTMLResponse)
async def get_edit_message_page(request: Request, message_id: int):
    for message in messages_db:
        if message.id == message_id:
            return templates.TemplateResponse(
                "edit.html",
                {"request": request, "message": message}
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.post("/web/messages/{message_id}/edit", response_class=HTMLResponse)
async def update_message_form(
    request: Request,
    message_id: int,
    content: str = Form(...)
):
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            updated_message = Message(id=message_id, content=content)
            messages_db[i] = updated_message
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "messages": messages_db}
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.post("/web/messages/{message_id}/delete")
async def delete_message_form(message_id: int):
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            messages_db.pop(i)
            return RedirectResponse(url="/web/messages", status_code=status.HTTP_303_SEE_OTHER)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.post("/web/messages/{message_id}/delete", response_class=HTMLResponse)
async def delete_message_web(request: Request, message_id: int):
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            messages_db.pop(i)
            return RedirectResponse(
                url=app.url_path_for("get_messages_page"),
                status_code=status.HTTP_303_SEE_OTHER,
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")