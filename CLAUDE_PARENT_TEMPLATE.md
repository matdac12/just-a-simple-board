# CLAUDE.md

## KanbanLite Integration

This project includes KanbanLite for task management in the `kanbanlite/` folder.

### Available Kanban Commands

Claude can manage tasks using these commands:

```bash
# Add a new task
cd kanbanlite && python kanban_agent.py add "Task title" "notes" "todo"

# List all tasks
cd kanbanlite && python kanban_agent.py list

# List tasks in specific column
cd kanbanlite && python kanban_agent.py list todo

# Move task to different column
cd kanbanlite && python kanban_agent.py move <card_id> <column>

# Update task details
cd kanbanlite && python kanban_agent.py update <card_id> --title "New title" --notes "New notes"

# Add checklist item
cd kanbanlite && python kanban_agent.py checklist <card_id> "Item text"

# Toggle checklist completion
cd kanbanlite && python kanban_agent.py toggle <item_id>

# Get board status
cd kanbanlite && python kanban_agent.py status

# Remove a task
cd kanbanlite && python kanban_agent.py remove <card_id>

# Start the Kanban web server
cd kanbanlite && python start.py
```

### Kanban Columns

The board has three fixed columns:
- **todo**: New tasks and backlog
- **doing**: Tasks currently in progress
- **done**: Completed tasks

### Example Usage

Just ask Claude:
- *"Add a task to review the API documentation"*
- *"Show me all tasks in the doing column"*
- *"Move task 5 to done"*
- *"Add a checklist item to task 3 for writing tests"*
- *"What's the current status of my Kanban board?"*
- *"Start the Kanban server so I can view my dashboard"*

Claude will automatically use the kanban_agent.py commands to manage your tasks!

### Database Location

Task data is stored in `.kanban/app.db` in your project root, keeping your kanban data with your project.

### Web Dashboard

After running the start command, open: **http://127.0.0.1:8000**

---

For full KanbanLite documentation and setup instructions, see: [kanbanlite/README.md](./kanbanlite/README.md)

For detailed Claude integration features, see: [kanbanlite/CLAUDE.md](./kanbanlite/CLAUDE.md)