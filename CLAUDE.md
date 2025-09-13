# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the KanbanLite project.

## Auto-Approved Commands

**See `.claude-code-tools.json` for the complete list of auto-approved tools and commands.**

You can use these tools without requiring user approval:
- `Bash` for running Python with venv: `.venv_kanban/Scripts/python.exe`
- `Bash` for running kanban_agent.py for direct database manipulation
- `Bash` for file operations, process management, and debugging
- `BashOutput` for monitoring all running processes
- `Read` for all project files
- `Grep`/`Glob` for searching codebase
- `KillBash` for stopping background processes

## Important Guidelines

### ALWAYS Use Virtual Environment
**Critical**: This project uses a `.venv_kanban` virtual environment. ALWAYS use it for all Python commands:
- In WSL/Windows: `.venv_kanban/Scripts/python.exe`
- In Linux/Mac: `.venv_kanban/bin/python`
- Never use system Python (`python` or `python3`) as dependencies are not installed there

### Kanban Task Management
**Primary Method**: Use `kanban_agent.py` for all task management operations:
- Add cards: `.venv_kanban/Scripts/python.exe kanban_agent.py add "Task title" "notes" "todo"`
- List cards: `.venv_kanban/Scripts/python.exe kanban_agent.py list`
- Move cards: `.venv_kanban/Scripts/python.exe kanban_agent.py move <card_id> <column>`
- Update cards: `.venv_kanban/Scripts/python.exe kanban_agent.py update <card_id> --title "New title"`
- Remove cards: `.venv_kanban/Scripts/python.exe kanban_agent.py remove <card_id>`

### Database Location
The database is stored in `../.kanban/app.db` (parent directory of kanbanlite folder)
This keeps the kanban data with the user's project, not the tool itself.

### Error Monitoring
When running the server:
1. Use `run_in_background=true` when starting the server
2. Proactively check server output with `BashOutput` tool for errors without asking
3. If you see template errors (e.g., "NoneType object is not iterable"), fix them immediately
4. Watch for SQLAlchemy relationship errors - fix these in models.py right away

### Proactive Actions
Take these actions WITHOUT asking for permission:
- Use kanban_agent.py to add/manage tasks
- Check server logs when errors are mentioned
- Fix obvious errors in templates or models
- Restart the server after fixing errors
- Monitor background processes with BashOutput

## Commands

### Initial Setup (One-time)
```bash
# Cross-platform setup
python setup.py

# Or platform-specific:
# Windows: setup.bat
# Linux/Mac: ./setup.sh
```

### Running the Application
```bash
# Cross-platform start
python start.py

# Or platform-specific:
# Windows: start_kanban.bat
# Linux/Mac: ./start.sh

# Direct method (WSL/Windows)
.venv_kanban/Scripts/python.exe app.py

# Direct method (Linux/Mac)
.venv_kanban/bin/python app.py
```

### Task Management via CLI
```bash
# Add a task
.venv_kanban/Scripts/python.exe kanban_agent.py add "Fix bug in login" "Check authentication flow" "todo"

# List all tasks
.venv_kanban/Scripts/python.exe kanban_agent.py list

# Move task to doing
.venv_kanban/Scripts/python.exe kanban_agent.py move 1 doing

# Add checklist item
.venv_kanban/Scripts/python.exe kanban_agent.py checklist 1 "Write unit tests"

# Get board status
.venv_kanban/Scripts/python.exe kanban_agent.py status
```

### Development Setup
Use the provided setup scripts instead of manual setup:
```bash
# Automated setup
python setup.py
```

### Database Management
```bash
# Database is automatically stored in ../.kanban/app.db
# This keeps kanban data with the user's project
# To override location:
export KANBAN_DB_PATH="/path/to/custom/location/app.db"
```

## Architecture

### Core Components

**Three-Tier Architecture:**
1. **Web Layer** (`app.py`): FastAPI server with HTMX-driven UI
   - Serves HTML templates with real-time updates via HTMX
   - RESTful endpoints return HTML fragments for UI updates
   - Fixed three-column Kanban board (Todo/Doing/Done)

2. **Data Layer** (`models.py`, `db.py`): SQLAlchemy ORM with SQLite
   - Four main entities: Board, ColumnModel, Card, ChecklistItem
   - Hierarchical card structure (cards can have sub-cards)
   - Position-based ordering within columns
   - Database stored in `../.kanban/app.db` for portability

3. **Agent Layer** (`kanban_agent.py`): Direct database manipulation
   - Python-based CLI and programmatic interface
   - Functions for all CRUD operations on cards and checklists
   - Can be called by Claude or used as standalone CLI tool
   - Maintains business logic invariants (fixed columns, position reindexing)

### Key Design Decisions

- **Fixed Columns**: Todo/Doing/Done columns are hardcoded, not configurable
- **No Drag-to-Nest**: Sub-cards created via button, not drag-and-drop
- **Position Management**: Cards maintain contiguous positions [0..n-1] per column
- **HTML-First API**: REST endpoints return HTML fragments for HTMX, not JSON
- **Agent-Based AI**: Claude uses kanban_agent.py for direct database manipulation
- **Portable Database**: Data stored in parent project directory (../.kanban/)

### Database Schema

- `boards`: Single board with name "My Board"
- `columns`: Three fixed columns with positions 0-2
- `cards`: Hierarchical structure with column_id, parent_id, position
- `checklist_items`: Linked to cards with done status and position

### Frontend Architecture

- **Templates**: Jinja2 templates with HTMX attributes
  - `base.html`: Layout and styles
  - `board.html`: Main board view
  - `_card.html`: Recursive card component
- **Interactivity**: HTMX for partial updates, minimal JavaScript for drag-and-drop
- **Styling**: Inline CSS, no build process required

## Agent Integration

The kanban_agent.py provides these functions:
- `add_card(title, notes, column, due_date)`: Create new card
- `list_cards(column)`: List cards (all or filtered by column)
- `move_card(card_id, column)`: Move card to different column
- `update_card(card_id, title, notes, due_date)`: Update card details
- `remove_card(card_id)`: Delete a card
- `add_checklist(card_id, text)`: Add checklist item
- `toggle_checklist(item_id)`: Toggle checklist completion
- `get_status()`: Get board statistics

Columns: "todo", "doing", "done"

## Using Agent from Claude Code

Claude can directly call kanban_agent.py functions to manage tasks:

### Examples:
```bash
# Add a new task
.venv_kanban/Scripts/python.exe kanban_agent.py add "Review API docs" "Check authentication flow" "todo" "2024-01-15"

# List all todo items
.venv_kanban/Scripts/python.exe kanban_agent.py list todo

# Move task to doing column
.venv_kanban/Scripts/python.exe kanban_agent.py move 5 doing

# Update task title
.venv_kanban/Scripts/python.exe kanban_agent.py update 3 --title "Updated task title"

# Add checklist item
.venv_kanban/Scripts/python.exe kanban_agent.py checklist 3 "Write unit tests"

# Get board status
.venv_kanban/Scripts/python.exe kanban_agent.py status
```

### Usage from Any Project
1. Copy kanbanlite folder to your project
2. Run setup once: `python setup.py`
3. Claude can manage tasks via kanban_agent.py
4. View dashboard at http://127.0.0.1:8000

## Troubleshooting

### Common Issues and Fixes

1. **500 Internal Server Error on startup**
   - Check `models.py` - Card.children relationship needs `single_parent=True` for delete-orphan cascade
   - Run: `.venv_kanban/Scripts/python.exe test_home.py` to see detailed error

2. **"NoneType object is not iterable" in templates**
   - In `_card.html`, use `(card.children or [])` instead of `card.children` in loops
   - Same for `card.checklist` - always provide fallback empty list

3. **Card creation fails**
   - Ensure relationships are loaded after creating card (access them to trigger lazy loading)
   - Don't try to assign empty lists directly to SQLAlchemy relationships

4. **Server won't connect from WSL**
   - Windows Python binds to Windows localhost, not WSL localhost
   - Access from browser on Windows at http://127.0.0.1:8000
   - Cannot use curl/wget from WSL to test Windows Python server

5. **ModuleNotFoundError**
   - You're using system Python instead of venv
   - Always use: `.venv_kanban/Scripts/python.exe` in WSL/Windows

### Testing Commands
```bash
# Test kanban agent functions
.venv_kanban/Scripts/python.exe kanban_agent.py status

# Test adding a card
.venv_kanban/Scripts/python.exe kanban_agent.py add "Test card" "Testing the system" "todo"

# Test listing cards
.venv_kanban/Scripts/python.exe kanban_agent.py list
```