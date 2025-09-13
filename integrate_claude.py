#!/usr/bin/env python3
"""
Integrate KanbanLite with Claude Code in parent project

This script helps set up Claude Code integration by copying
the CLAUDE.md template to the parent project directory.
"""
import os
import shutil
import sys

def get_paths():
    """Get the relevant paths for integration"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    template_path = os.path.join(script_dir, 'CLAUDE_PARENT_TEMPLATE.md')
    parent_claude = os.path.join(parent_dir, 'CLAUDE.md')

    return script_dir, parent_dir, template_path, parent_claude

def check_location():
    """Check if we're in the right location"""
    script_dir, parent_dir, template_path, parent_claude = get_paths()

    # Check if we have the required files (this indicates we're in a KanbanLite folder)
    required_files = ['kanban_agent.py', 'app.py', 'CLAUDE_PARENT_TEMPLATE.md']
    missing_files = []

    for file in required_files:
        if not os.path.exists(os.path.join(script_dir, file)):
            missing_files.append(file)

    if missing_files:
        print("⚠️  Error: This doesn't appear to be a KanbanLite folder")
        print(f"Current location: {script_dir}")
        print(f"Missing required files: {', '.join(missing_files)}")
        return False

    if not os.path.exists(template_path):
        print("❌ Error: CLAUDE_PARENT_TEMPLATE.md not found")
        print(f"Expected at: {template_path}")
        return False

    return True

def append_to_existing_claude(parent_claude, template_path):
    """Append KanbanLite instructions to existing CLAUDE.md"""
    print(f"📝 Found existing CLAUDE.md at: {parent_claude}")

    # Check if KanbanLite integration already exists
    try:
        with open(parent_claude, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'KanbanLite Integration' in content:
                print("✅ KanbanLite integration already exists in CLAUDE.md")
                return True
    except Exception as e:
        print(f"❌ Error reading existing CLAUDE.md: {e}")
        return False

    response = input("Append KanbanLite instructions to existing CLAUDE.md? (y/n): ").lower()
    if response not in ['y', 'yes']:
        print("❌ Integration cancelled by user")
        return False

    try:
        with open(parent_claude, 'a', encoding='utf-8') as f:
            f.write("\n\n")
            with open(template_path, 'r', encoding='utf-8') as t:
                f.write(t.read())
        print("✅ KanbanLite instructions appended to existing CLAUDE.md")
        return True
    except Exception as e:
        print(f"❌ Error appending to CLAUDE.md: {e}")
        return False

def create_new_claude(parent_claude, template_path):
    """Create new CLAUDE.md from template"""
    try:
        shutil.copy(template_path, parent_claude)
        print(f"✅ Created CLAUDE.md in parent directory")
        return True
    except Exception as e:
        print(f"❌ Error creating CLAUDE.md: {e}")
        return False

def integrate():
    """Main integration function"""
    print("🤖 KanbanLite Claude Code Integration")
    print("====================================")

    # Check if we're in the right location
    if not check_location():
        return False

    script_dir, parent_dir, template_path, parent_claude = get_paths()

    print(f"📁 KanbanLite location: {script_dir}")
    print(f"📁 Parent project: {parent_dir}")
    print()

    # Check if CLAUDE.md already exists in parent
    if os.path.exists(parent_claude):
        success = append_to_existing_claude(parent_claude, template_path)
    else:
        success = create_new_claude(parent_claude, template_path)

    if success:
        print()
        print("✅ Claude Code integration complete!")
        print()
        print("🎯 What you can do now:")
        print("• Ask Claude: 'Add a task to review the documentation'")
        print("• Ask Claude: 'Show me my current kanban board status'")
        print("• Ask Claude: 'Start the kanban server'")
        print()
        print("🤖 Optional: Create a specialized KanbanLite Manager agent:")
        print("• Run: /agent create kanbanlite-manager \"Expert Kanban manager for task organization and workflow optimization\"")
        print("• Then ask the agent to organize your tasks and optimize your workflow!")
        print()
        print("📖 For more commands, see: kanbanlite/README.md")
        return True

    return False

def main():
    """Main entry point"""
    try:
        success = integrate()
        if not success:
            print()
            print("❌ Integration failed")
            print()
            print("💡 Alternative options:")
            print("1. Manually copy CLAUDE_PARENT_TEMPLATE.md to your project root as CLAUDE.md")
            print("2. Tell Claude directly: 'Use kanban tools in kanbanlite folder'")
            print("3. See kanbanlite/README.md for detailed instructions")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Integration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()