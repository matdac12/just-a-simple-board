#!/usr/bin/env python3
"""
Kanban Agent - Direct database manipulation for task management
Can be used by Claude Code or as a CLI tool for automation
"""
import sys
import os
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, func

# Add current directory to path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_db, Base, engine
from models import Board, ColumnModel, Card, ChecklistItem

def ensure_setup() -> Board:
    """Ensure database and initial setup exists"""
    Base.metadata.create_all(bind=engine)

    with next(get_db()) as db:
        board = db.scalar(select(Board).where(Board.name=="My Board"))
        if board:
            return board

        # Create initial board with fixed columns
        board = Board(name="My Board")
        todo = ColumnModel(name="Todo", position=0)
        doing = ColumnModel(name="Doing", position=1)
        done = ColumnModel(name="Done", position=2)
        board.columns = [todo, doing, done]
        db.add(board)
        db.commit()
        db.refresh(board)
        return board

def get_column_id(column_name: str) -> Optional[int]:
    """Get column ID by name (case insensitive)"""
    column_map = {"todo": 1, "doing": 2, "done": 3}
    return column_map.get(column_name.lower())

def add_card(title: str, notes: str = "", column: str = "todo", due_date: str = None) -> Dict:
    """Add a new card to the specified column"""
    ensure_setup()

    column_id = get_column_id(column)
    if not column_id:
        return {"success": False, "error": f"Invalid column: {column}. Use 'todo', 'doing', or 'done'"}

    with next(get_db()) as db:
        # Get next position in column
        pos = db.scalar(select(func.coalesce(func.max(Card.position), -1)).where(
            Card.column_id == column_id, Card.parent_id == None)) + 1

        card = Card(
            column_id=column_id,
            title=title,
            notes=notes,
            position=pos
        )

        if due_date:
            try:
                card.due_at = datetime.fromisoformat(due_date)
            except ValueError:
                return {"success": False, "error": f"Invalid date format: {due_date}. Use YYYY-MM-DD format"}

        db.add(card)
        db.commit()
        db.refresh(card)

        return {
            "success": True,
            "card_id": card.id,
            "title": card.title,
            "column": column,
            "position": card.position
        }

def list_cards(column: Optional[str] = None) -> Dict:
    """List all cards or cards in a specific column"""
    ensure_setup()

    with next(get_db()) as db:
        query = select(Card).where(Card.parent_id == None).order_by(Card.column_id, Card.position)

        if column:
            column_id = get_column_id(column)
            if not column_id:
                return {"success": False, "error": f"Invalid column: {column}"}
            query = query.where(Card.column_id == column_id)

        cards = db.scalars(query).all()

        card_list = []
        for card in cards:
            column_name = ["", "todo", "doing", "done"][card.column_id]
            card_data = {
                "id": card.id,
                "title": card.title,
                "notes": card.notes,
                "column": column_name,
                "position": card.position,
                "due_at": card.due_at.isoformat() if card.due_at else None,
                "checklist_count": len(card.checklist) if card.checklist else 0
            }
            card_list.append(card_data)

        return {"success": True, "cards": card_list, "count": len(card_list)}

def move_card(card_id: int, column: str) -> Dict:
    """Move a card to a different column"""
    ensure_setup()

    column_id = get_column_id(column)
    if not column_id:
        return {"success": False, "error": f"Invalid column: {column}"}

    with next(get_db()) as db:
        card = db.get(Card, card_id)
        if not card:
            return {"success": False, "error": f"Card {card_id} not found"}

        old_column = ["", "todo", "doing", "done"][card.column_id]

        # Get next position in new column
        pos = db.scalar(select(func.coalesce(func.max(Card.position), -1)).where(
            Card.column_id == column_id, Card.parent_id == None)) + 1

        card.column_id = column_id
        card.position = pos
        db.commit()

        return {
            "success": True,
            "card_id": card_id,
            "title": card.title,
            "moved_from": old_column,
            "moved_to": column,
            "new_position": pos
        }

def update_card(card_id: int, title: Optional[str] = None, notes: Optional[str] = None, due_date: Optional[str] = None) -> Dict:
    """Update card details"""
    ensure_setup()

    with next(get_db()) as db:
        card = db.get(Card, card_id)
        if not card:
            return {"success": False, "error": f"Card {card_id} not found"}

        if title is not None:
            card.title = title
        if notes is not None:
            card.notes = notes
        if due_date is not None:
            if due_date == "":
                card.due_at = None
            else:
                try:
                    card.due_at = datetime.fromisoformat(due_date)
                except ValueError:
                    return {"success": False, "error": f"Invalid date format: {due_date}"}

        db.commit()
        column_name = ["", "todo", "doing", "done"][card.column_id]

        return {
            "success": True,
            "card_id": card_id,
            "title": card.title,
            "notes": card.notes,
            "column": column_name,
            "due_at": card.due_at.isoformat() if card.due_at else None
        }

def remove_card(card_id: int) -> Dict:
    """Remove a card and all its checklist items"""
    ensure_setup()

    with next(get_db()) as db:
        card = db.get(Card, card_id)
        if not card:
            return {"success": False, "error": f"Card {card_id} not found"}

        title = card.title
        column_name = ["", "todo", "doing", "done"][card.column_id]

        db.delete(card)
        db.commit()

        return {
            "success": True,
            "card_id": card_id,
            "title": title,
            "column": column_name,
            "message": "Card deleted successfully"
        }

def add_checklist(card_id: int, text: str) -> Dict:
    """Add a checklist item to a card"""
    ensure_setup()

    with next(get_db()) as db:
        card = db.get(Card, card_id)
        if not card:
            return {"success": False, "error": f"Card {card_id} not found"}

        # Get next position in checklist
        pos = db.scalar(select(func.coalesce(func.max(ChecklistItem.position), -1)).where(
            ChecklistItem.card_id == card_id)) + 1

        item = ChecklistItem(
            card_id=card_id,
            text=text,
            position=pos
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return {
            "success": True,
            "item_id": item.id,
            "card_id": card_id,
            "text": item.text,
            "done": item.done,
            "position": item.position
        }

def toggle_checklist(item_id: int) -> Dict:
    """Toggle completion status of a checklist item"""
    ensure_setup()

    with next(get_db()) as db:
        item = db.get(ChecklistItem, item_id)
        if not item:
            return {"success": False, "error": f"Checklist item {item_id} not found"}

        item.done = not item.done
        db.commit()

        return {
            "success": True,
            "item_id": item_id,
            "card_id": item.card_id,
            "text": item.text,
            "done": item.done
        }

def get_status() -> Dict:
    """Get overall kanban board status"""
    ensure_setup()

    with next(get_db()) as db:
        todo_count = db.scalar(select(func.count(Card.id)).where(Card.column_id == 1, Card.parent_id == None)) or 0
        doing_count = db.scalar(select(func.count(Card.id)).where(Card.column_id == 2, Card.parent_id == None)) or 0
        done_count = db.scalar(select(func.count(Card.id)).where(Card.column_id == 3, Card.parent_id == None)) or 0

        return {
            "success": True,
            "status": {
                "todo": todo_count,
                "doing": doing_count,
                "done": done_count,
                "total": todo_count + doing_count + done_count
            }
        }

# CLI interface
def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Kanban Agent - Direct database manipulation")
        print("Usage:")
        print("  python kanban_agent.py add 'Task title' [notes] [column] [due_date]")
        print("  python kanban_agent.py list [column]")
        print("  python kanban_agent.py move <card_id> <column>")
        print("  python kanban_agent.py update <card_id> [--title 'New title'] [--notes 'New notes'] [--due 'YYYY-MM-DD']")
        print("  python kanban_agent.py remove <card_id>")
        print("  python kanban_agent.py checklist <card_id> 'Item text'")
        print("  python kanban_agent.py toggle <item_id>")
        print("  python kanban_agent.py status")
        print("\nColumns: todo, doing, done")
        return

    command = sys.argv[1].lower()

    try:
        if command == "add":
            title = sys.argv[2]
            notes = sys.argv[3] if len(sys.argv) > 3 else ""
            column = sys.argv[4] if len(sys.argv) > 4 else "todo"
            due_date = sys.argv[5] if len(sys.argv) > 5 else None
            result = add_card(title, notes, column, due_date)
            print(result)

        elif command == "list":
            column = sys.argv[2] if len(sys.argv) > 2 else None
            result = list_cards(column)
            print(result)

        elif command == "move":
            card_id = int(sys.argv[2])
            column = sys.argv[3]
            result = move_card(card_id, column)
            print(result)

        elif command == "update":
            card_id = int(sys.argv[2])
            # Simple argument parsing for --title, --notes, --due
            kwargs = {}
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--title" and i + 1 < len(sys.argv):
                    kwargs["title"] = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--notes" and i + 1 < len(sys.argv):
                    kwargs["notes"] = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--due" and i + 1 < len(sys.argv):
                    kwargs["due_date"] = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            result = update_card(card_id, **kwargs)
            print(result)

        elif command == "remove":
            card_id = int(sys.argv[2])
            result = remove_card(card_id)
            print(result)

        elif command == "checklist":
            card_id = int(sys.argv[2])
            text = sys.argv[3]
            result = add_checklist(card_id, text)
            print(result)

        elif command == "toggle":
            item_id = int(sys.argv[2])
            result = toggle_checklist(item_id)
            print(result)

        elif command == "status":
            result = get_status()
            print(result)

        else:
            print(f"Unknown command: {command}")

    except (IndexError, ValueError) as e:
        print(f"Error: {e}")
        print("Use 'python kanban_agent.py' for help")

if __name__ == "__main__":
    main()