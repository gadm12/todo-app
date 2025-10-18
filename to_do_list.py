import json
import os
from datetime import datetime

file_name = "to_do_list.json"
INVALID = "invalid entry!"



def add_task():
    """Prompt the user for new tasks and return them as a list of dictionaries."""

    tasks_to_add = []

    while True:
        new_task = input("\nEnter a task: ").strip()
        if not new_task:
            print("\nYou can't enter a blank task.")
            continue
        due_date = input("when is this task due? 'YYYY-MM-DD': ")
        try:
            dt = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print(INVALID)
            continue

        tasks_to_add.append(
            {"task": new_task, "completed": False, "due_date": due_date}
        )

        add_more = (
            input("\nAdd another task? ('y' for yes, anything else for no): ")
            .lower()
            .strip()
        )

        if add_more == "y":
            continue  # If they say 'y', continue to the next loop iteration
        else:
            break  # For ANY other input, break the loop

    return tasks_to_add


def view_tasks(all_tasks):
    """Display all tasks in a numbered list."""
    
    TODAY = datetime.now()
    
    if not all_tasks:
        print("No tasks yet.")
        return

    for i, task in enumerate(all_tasks, start=1):
        if isinstance(task, dict):
            name = task.get("task", "<no task>")
            completed = task.get("completed", False)
            due = task.get("due_date")
        else:
            name = str(task)
            completed = False
            due = None

        status = "[\u2713]" if completed else "[ ]"
        display_text = f"{i}. {status} {name}"
        if due:
            due_date_obj = datetime.strptime(due, "%Y-%m-%d")
            if due_date_obj.date() < TODAY.date():
                display_text += f" due: {due} ⚠ OVERDUE!"
            elif due_date_obj.date() == TODAY.date():
                display_text += f" due: {due} due Today"
            else:
                display_text += f" due: {due}"

        print(display_text)


def get_task_selection(prompt, all_tasks):
    """Get a valid task index from user input."""

    if not all_tasks:
        return None

    while True:
        user_input = input(prompt).strip().lower()

        if user_input in ("exit", "e", "cancel", "c"):
            return None

        try:
            idx = int(user_input)
        except ValueError:
            print(INVALID)
            continue

        if 1 <= idx <= len(all_tasks):
            return idx - 1
        else:
            print(f"\nPlease enter a number between 1 and {len(all_tasks)}")

def edit_task(all_tasks):
    """Edit an already existing task."""
    view_tasks(all_tasks)
    
    if not all_tasks:
        return
    
    prompt="\nwhich task do you want to edit?: "
    
    idx_edit=get_task_selection(prompt,all_tasks)
    
    if idx_edit is not None:
        task_to_edit=all_tasks[idx_edit]
        print(f"\nEditing task: {task_to_edit["task"]}")
        print(f"current due date: {task_to_edit.get("due_date","N/A")}")
        
        choice=input("what do you want to edit? (1) description, (2) Due date: ").strip()
        
        if choice == "1":
            new_text=input("enter your update: ")
            if not new_text:
                print("\nYou can't enter a blank task.")
                return
            task_to_edit["task"]=new_text
            print(f"\nTask description updated successfully!")
            
        elif choice == "2":
            new_date=input("when is this task due? 'YYYY-MM-DD': ")
            try:
                dt=datetime.strptime(new_date,"%Y-%m-%d")
                
                task_to_edit['due_date']=new_date
                print(f"\nTask due date updated successfully!")
                
            except ValueError:
                print(INVALID)
        else:
            print(INVALID)
                
                
        
    
    

def mark_complete(all_tasks):
    """Mark a selected task as complete."""

    view_tasks(all_tasks)

    if not all_tasks:
        return

    prompt = "Which task did you complete? (number or 'exit'): "
    marking = get_task_selection(prompt, all_tasks)

    if marking is not None:
        all_tasks[marking]["completed"] = True
        print(f"{all_tasks[marking]['task']} marked complete\n")


def delete_task(all_tasks):
    """Delete a selected task from the list."""

    view_tasks(all_tasks)

    if not all_tasks:
        return

    prompt = "\nWhich task would you like to delete? (number or 'exit'): "
    removing = get_task_selection(prompt, all_tasks)

    if removing is not None:
        removed_task = all_tasks.pop(removing)
        print(f"{removed_task['task']} removed\n")


def search_tasks(all_tasks):
    """Search for a task by keyword."""

    query = input("\nwhat are you looking for: ").lower().strip()
    results = []
    for task in all_tasks:
        description = task.get("task", "<not found>")
        if query in description.lower():
            results.append(task)

    return results


def save_tasks(all_tasks):
    """Save all tasks to a JSON file."""

    try:
        with open(file_name, "w") as f:
            json.dump({"to_do_list": all_tasks}, f, indent=4)
    except Exception as e:
        print("Failed to save tasks:", e)


def load_tasks():
    """Load tasks from the JSON file if it exists."""

    if not os.path.exists(file_name):
        return []

    try:
        with open(file_name, "r") as f:
            data = json.load(f)
            return data.get("to_do_list", [])
    except (json.JSONDecodeError, IOError) as e:
        print("Warning: could not load saved tasks (starting fresh).", e)
        return []


def main_loop():
    """Main program loop."""

    all_tasks = load_tasks()
    print("")
    print("=" * 33)
    print(" Welcome to the To Do List App!!")
    print("=" * 33)
    count=len(all_tasks)
    print(f"\nLoaded {len(all_tasks)} saved task{'s' if count > 1 else ''}.\n")

    try:
        while True:
            command = input(
                "\nEnter 'add', 'view', 'edit','mark', 'delete', 'search' or 'q' to quit: "
            ).lower()

            if command in ("add", "1", "a"):
                new_tasks = add_task()
                if new_tasks:
                    all_tasks.extend(new_tasks)
                    count = len(new_tasks)
                    save_tasks(all_tasks)
                    print(
                        f"\n{count} task{'s' if count > 1 else ''} added successfully!"
                    )

            elif command in ("view", "2", "v"):
                view_tasks(all_tasks)

            elif command in ("mark", "3", "m"):
                mark_complete(all_tasks)
                save_tasks(all_tasks)

            elif command in ("delete", "4", "d"):
                delete_task(all_tasks)
                save_tasks(all_tasks)
                
            elif command in ("edit","e"):
                edit_task(all_tasks)
                save_tasks(all_tasks)

            elif command in ("search", "6", "s"):
                found_tasks = search_tasks(all_tasks)
                count=len(found_tasks)
                print(f"\nFound {len(found_tasks)} matching task{'s' if count > 1 else ''}:")
                view_tasks(found_tasks)
            elif command in ("quit", "5", "q"):
                save_tasks(all_tasks)
                break

            else:
                print(INVALID)

    except KeyboardInterrupt:
        print("\nYou quit the program with Ctrl+C, saving...")
        save_tasks(all_tasks)


if __name__ == "__main__":
    main_loop()
