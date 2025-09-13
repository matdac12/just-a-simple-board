import os
from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
from db import Base, engine, get_db
from models import Board, ColumnModel, Card, ChecklistItem
import uvicorn
from typing import Optional

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

Base.metadata.create_all(bind=engine)

def ensure_seed(db: Session) -> Board:
    board = db.scalar(select(Board).where(Board.name=="My Board"))
    if board: return board
    board = Board(name="My Board")
    # Fixed columns: Todo/Doing/Done
    todo = ColumnModel(name="Todo", position=0)
    doing = ColumnModel(name="Doing", position=1)
    done = ColumnModel(name="Done", position=2)
    board.columns = [todo, doing, done]
    db.add(board); db.commit(); db.refresh(board)
    return board

@app.get("/test")
def test():
    return {"status": "ok", "message": "Server is running"}

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    try:
        from datetime import date
        board = ensure_seed(db)

        # Eagerly load all relationships to avoid N+1 queries
        for c in board.columns:
            _ = c.cards  # Load cards
            for card in c.cards:
                _ = card.checklist  # Load checklist items
                _ = card.children   # Load child cards

        return templates.TemplateResponse("board.html", {
            "request": request,
            "board": board,
            "title": "Kanban",
            "today": date.today()
        })
    except Exception as e:
        import traceback
        return HTMLResponse(content=f"<pre>Error: {str(e)}\n\n{traceback.format_exc()}</pre>", status_code=500)


@app.post("/cards", response_class=HTMLResponse)
def create_card(
    request: Request,
    column_id: int = Form(...),
    parent_id: Optional[int] = Form(None),
    title: str = Form(...),
    notes: str = Form(""),
    due_at: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    pos = db.scalar(select(func.coalesce(func.max(Card.position), -1)).where(Card.column_id==column_id, Card.parent_id==parent_id)) + 1
    card = Card(column_id=column_id, parent_id=parent_id, title=title, notes=notes, position=pos)
    if due_at: card.due_at = datetime.fromisoformat(due_at)
    db.add(card); db.commit(); db.refresh(card)
    # Access relationships to ensure they're loaded (lazy loading)
    _ = card.children  
    _ = card.checklist
    return templates.TemplateResponse("_card.html", {"request": request, "card": card})

@app.put("/cards/{card_id}", response_class=HTMLResponse)
async def update_card(card_id: int, request: Request, db: Session = Depends(get_db), **form):
    card = db.get(Card, card_id)
    if not card: return HTMLResponse(status_code=404, content="Not found")
    title = form.get("title"); notes = form.get("notes"); due_at = form.get("due_at")
    if title is not None: card.title = title
    if notes is not None: card.notes = notes
    if due_at == "": card.due_at = None
    elif due_at is not None: card.due_at = datetime.fromisoformat(due_at)
    db.commit(); db.refresh(card)
    return templates.TemplateResponse("_card.html", {"request": request, "card": card})

@app.delete("/cards/{card_id}", response_class=HTMLResponse)
def delete_card(card_id: int, db: Session = Depends(get_db)):
    card = db.get(Card, card_id)
    if not card: return HTMLResponse(status_code=404, content="")
    db.delete(card); db.commit()
    return HTMLResponse("")

@app.post("/move/{card_id}")
def move_card(card_id: int, payload: dict, db: Session = Depends(get_db)):
    card = db.get(Card, card_id)
    if not card: return {"ok": False}
    new_col = int(payload.get("column_id", card.column_id))
    new_pos = int(payload.get("position", 0))
    card.column_id = new_col
    siblings = db.scalars(select(Card).where(Card.column_id==new_col, Card.parent_id==None).order_by(Card.position)).all()
    siblings = [c for c in siblings if c.id != card.id]
    siblings.insert(min(new_pos, len(siblings)), card)
    for i, c in enumerate(siblings): c.position = i
    db.commit()
    return {"ok": True}

@app.post("/checklist/{card_id}", response_class=HTMLResponse)
def add_checklist_item(card_id: int, request: Request, text: str = Form(...), db: Session = Depends(get_db)):
    pos = db.scalar(select(func.coalesce(func.max(ChecklistItem.position), -1)).where(ChecklistItem.card_id==card_id)) + 1
    item = ChecklistItem(card_id=card_id, text=text, position=pos)
    db.add(item); db.commit(); db.refresh(item)
    return HTMLResponse(f'''
      <li data-item-id="{item.id}">
        <button type="button" class="check-btn" onclick="toggleChecklistItem({item.id}, this)">☐</button>
        <span class="checklist-text">{item.text}</span>
        <button type="button" class="delete-item-btn" onclick="deleteChecklistItem({item.id}, this)" title="Delete item">×</button>
      </li>''')

@app.post("/toggle/{item_id}", response_class=HTMLResponse)
def toggle_item(item_id: int, db: Session = Depends(get_db)):
    it = db.get(ChecklistItem, item_id)
    if not it: return HTMLResponse(status_code=404, content="")
    it.done = not it.done; db.commit()
    box = "☑" if it.done else "☐"
    return HTMLResponse(f'''
      <li class="{'checked' if it.done else ''}" data-item-id="{it.id}">
        <button type="button" class="check-btn" onclick="toggleChecklistItem({it.id}, this)">{box}</button>
        <span class="checklist-text {'done' if it.done else ''}">{it.text}</span>
        <button type="button" class="delete-item-btn" onclick="deleteChecklistItem({it.id}, this)" title="Delete item">×</button>
      </li>''')

@app.delete("/checklist-item/{item_id}", response_class=HTMLResponse)
def delete_checklist_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ChecklistItem, item_id)
    if not item: return HTMLResponse(status_code=404, content="")
    db.delete(item); db.commit()
    return HTMLResponse("")

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True, log_level="debug")
