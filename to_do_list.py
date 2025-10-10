import json
import os

file_name= "to_do_list.json"

def add_task():
    
    """Prompt the user for a new task and return it as a dictionary."""
    
    new_task=input("enter a task: ").strip()
    
    if not new_task:
        print("you can't enter a blank task")
        return None
    
    return {"task":new_task,"completed":False}


def view_tasks(all_tasks):
    
    if not all_tasks:
        print("no tasks yet")
        return
    
    for i,task in enumerate(all_tasks,start=1):
        if isinstance(task,dict):
            name=task.get("task","<no task>")
            completed=task.get("completed",False)
        else:
            name=str(task)
            completed=False
        
        status= "[\u2713]" if completed else "[ ]"
        print(f"{i}.{status} {name}") 

def get_task_selection(prompt,all_tasks):
    
    if not all_tasks:
        return None
    
    while True:
        
        user_input=input(prompt).strip().lower()
        
        if user_input in ("exit", "e", "cancel", "c"):
            return None
        
        try:
            idx=int(user_input)
        except ValueError:
            print("Invalid entry")
            continue
        
        if 1<= idx <= len(all_tasks):
            return idx-1
        else:
            print(f"please enter a number between 1 and {len(all_tasks)}")
            
def mark_complete(all_tasks):
    
    view_tasks(all_tasks)
    
    if not all_tasks:
        return
    
    prompt="Which task did you complete? (number or 'exit'): "
    
    marking=get_task_selection(prompt,all_tasks)
    
    if marking is not None:
        
        all_tasks[marking]["completed"]=True
        print(f"{all_tasks[marking]['task']} marked complete\n")
        
def delete_task(all_tasks):
    
    view_tasks(all_tasks)
    
    if not all_tasks:
        return
    
    prompt="Which task would you like to delete? (number or 'exit'): "
    
    removing=get_task_selection(prompt,all_tasks)
    
    if removing is not None:
        
        removed_task=all_tasks.pop(removing)
        
        print(f"{removed_task['task']} removed\n")
        return
    
def save_task(all_tasks):
    
    try:
        with open(file_name, "w") as f:
            json.dump({"to_do_list":all_tasks},f, indent=4)
    except Exception as e:
        print("Failed to save tasks:", e)

def load_tasks():
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
    all_tasks=load_tasks()
    print("")
    print("="*33)
    print(" Welcome to the To Do List App!!")
    print("="*33)
    print("")


    try:
        while True:
            
            command=input("\nEnter 'add', 'view', 'mark', 'delete', or 'q' to quit: ").lower()
            
            if command in ("add","1","a"):
                dict_task=add_task()
                if dict_task:
                    all_tasks.append(dict_task)
                    save_task(all_tasks)
                    print("\nTask added successfully!")
                    
            elif command in ("view","2","v"):
                view_tasks(all_tasks)
                
            elif command in ("mark","3","m"):
                mark_complete(all_tasks)
                save_task(all_tasks)
                
            elif command in ("delete","4","d"):
                delete_task(all_tasks)
                save_task(all_tasks)
                
            elif command in ("quit","5",'q'):
                save_task(all_tasks)
                break
            
            else:
                print("Invalid entry!")

    except KeyboardInterrupt:
        
        print("\nyou quit the program with ctrl+c, saving...")
        save_task(all_tasks)
        
if __name__ == "__main__":
    main_loop()