# KanbanLite 🚀

A lightweight, portable Kanban board that you can drop into any project for local task management. Perfect for personal productivity and project organization, with full privacy and offline functionality.

## ✨ Features

- **📱 Modern Web Interface**: Clean, responsive HTMX-powered UI
- **🔄 Drag & Drop**: Move tasks between Todo/Doing/Done columns
- **✅ Checklists**: Add subtasks with checkable items
- **📅 Due Dates**: Set and track task deadlines
- **🤖 AI Integration**: Built-in support for Claude Code automation
- **📁 Portable**: Single folder you can copy to any project
- **🔒 Private**: All data stays local on your machine
- **🌐 Cross-Platform**: Works on Windows, Mac, and Linux

## 🚀 Quick Start

### 1. Setup (One-time)

Choose your preferred method:

**Cross-platform (Recommended):**
```bash
python setup.py
```

**Platform-specific:**
```bash
# Windows
setup.bat

# Linux/Mac
./setup.sh
```

### 2. Start the Server

**Cross-platform:**
```bash
python start.py
```

**Platform-specific:**
```bash
# Windows
start_kanban.bat
# or double-click start_kanban.bat

# Linux/Mac
./start.sh
```

### 3. Open Your Dashboard

Navigate to: **http://127.0.0.1:8000**

That's it! Start managing your tasks! 🎉

## 📋 Usage

### Web Interface

- **Add Tasks**: Click the "+" button in any column
- **Edit Tasks**: Click on a task to edit title, notes, or due date
- **Move Tasks**: Drag and drop between columns or use dropdown
- **Delete Tasks**: Click the "×" button on any task
- **Add Checklists**: Use the checklist button to add subtasks
- **Toggle Checklist Items**: Click the checkboxes to mark complete

### Command Line Interface (CLI)

For automation or quick task management:

```bash
# Add a new task
python kanban_agent.py add "Fix login bug" "Check authentication flow" "todo" "2024-01-15"

# List all tasks
python kanban_agent.py list

# List tasks in specific column
python kanban_agent.py list todo

# Move a task
python kanban_agent.py move 5 doing

# Update task details
python kanban_agent.py update 3 --title "Updated title" --notes "New notes"

# Add checklist item
python kanban_agent.py checklist 3 "Write unit tests"

# Toggle checklist completion
python kanban_agent.py toggle 1

# Get board status
python kanban_agent.py status

# Remove a task
python kanban_agent.py remove 5
```

## 🤖 Claude Code Integration

KanbanLite comes with full Claude Code support for AI-powered task management:

### Auto-Approved Commands

Claude can automatically:
- Add, update, and manage tasks via `kanban_agent.py`
- Monitor the server and fix issues
- Run setup and start scripts

### Example Interactions

Just ask Claude:
- *"Add a task to review the API documentation"*
- *"Show me all tasks in the doing column"*
- *"Move task 5 to done"*
- *"Add a checklist item to task 3 for writing tests"*
- *"What's the current status of my board?"*

Claude will use the `kanban_agent.py` script to manage your tasks directly!

## 📁 Project Structure

```
kanbanlite/
├── 🚀 Setup & Start
│   ├── setup.py          # Cross-platform setup
│   ├── setup.bat         # Windows setup
│   ├── setup.sh          # Linux/Mac setup
│   ├── start.py          # Cross-platform launcher
│   ├── start.sh          # Linux/Mac starter
│   └── start_kanban.bat  # Windows starter
│
├── 🧠 Core Application
│   ├── app.py            # FastAPI web server
│   ├── models.py         # Database models
│   ├── db.py             # Database configuration
│   └── schemas.py        # Data schemas
│
├── 🤖 Automation
│   ├── kanban_agent.py   # CLI & Claude integration
│   ├── CLAUDE.md         # Claude Code instructions
│   └── .claude-code-tools.json  # Auto-approved commands
│
├── 🎨 Frontend
│   ├── templates/        # HTML templates
│   │   ├── base.html
│   │   ├── board.html
│   │   └── _card.html
│   └── static/
│       └── dnd.js        # Drag-and-drop functionality
│
└── 📋 Documentation
    ├── README.md         # This file
    ├── requirements.txt  # Python dependencies
    └── .gitignore       # Git ignore rules
```

## 🗃️ Database

- **Location**: `../.kanban/app.db` (in your project's parent directory)
- **Type**: SQLite (no external database needed)
- **Portable**: Automatically created and managed
- **Privacy**: All data stays on your local machine

The database is stored outside the `kanbanlite` folder so your kanban data stays with your project, not the tool.

## 🔧 Configuration

### Environment Variables

```bash
# Custom database location (optional)
export KANBAN_DB_PATH="/path/to/your/database.db"
```

### Default Columns

The board has three fixed columns:
- **Todo** (📝): New tasks and backlog
- **Doing** (🏃): Tasks currently in progress
- **Done** (✅): Completed tasks

## 🛠️ Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if virtual environment exists
ls .venv_kanban/

# Re-run setup if missing
python setup.py
```

**Port already in use:**
```bash
# Kill any existing processes on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /F /PID <process_id>

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

**Permission errors (Linux/Mac):**
```bash
# Make scripts executable
chmod +x setup.sh start.sh
```

### Getting Help

1. Check the [CLAUDE.md](./CLAUDE.md) file for detailed technical documentation
2. Look at the `kanban_agent.py --help` output for CLI usage
3. Ensure Python 3.7+ is installed and accessible

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

KanbanLite is designed to be simple and focused. If you have ideas for improvements:

1. Keep it lightweight and portable
2. Maintain cross-platform compatibility
3. Preserve the single-folder deployment model
4. Focus on core task management features

## 🎯 Use Cases

- **Personal Projects**: Track your own tasks and todos
- **Small Teams**: Simple shared task management
- **Development**: Manage feature development and bug fixes
- **Learning**: Practice with Kanban methodology
- **Offline Work**: Full functionality without internet
- **Privacy**: Keep your tasks completely private

---

**Happy Task Management!** 🎉

Start organizing your work with KanbanLite today!