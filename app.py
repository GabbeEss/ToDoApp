from flask import Flask, jsonify, request, abort, render_template
import json

app = Flask(__name__)

# Root route to serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

#Define a function to read tasks from tasks.json

def read_tasks():
    with open("tasks.json", "r") as f:
        return  json.load(f)
    
# Define a function to save tasks to tasks.json

def save_tasks(tasks):
    with open("tasks.json", "w") as f:
        json.dump(tasks, f)

# Decorator to check for a password in the request
def require_auth(func):
    def wrapper(*args, **kwargs):
        data = request.get_json()
        
        # Check if password is correct
        if not data or data.get("password") != "123":
            abort(403, description="Unauthorized: Invalid password.")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper




# Endpoint to get all tasks with status filter

@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = read_tasks()
    completed_param = request.args.get("completed")

    # Filter based on the 'completed' query parameter if provided
    if completed_param is not None:
        completed = completed_param.lower() == "true"
        tasks = [task for task in tasks if task.get("completed", False) == completed]

    return jsonify(tasks), 200

    

    # Endpoint to add a new task 
@app.route("/tasks", methods=["POST"])
def create_task():
    tasks = read_tasks()
    new_task = request.json
    # Check if task has a description and category
    if "description" not in new_task or "category" not in new_task:
        abort(400, description="Task must have a description and category")
    new_task["completed"] = False
    tasks = read_tasks()
    new_task["id"] = max(task["id"] for task in tasks) + 1
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

# ================================================================================================================================================0

# Endpoint to get a specific task by ID
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    tasks = read_tasks()
    # Find the task by ID
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        abort(404, description="Task not found.")
    return jsonify(task)

# Endpoint to delete a specific task by ID (requires password)
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@require_auth
def delete_task(task_id):
    tasks = read_tasks()
    # Find the task by ID
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        abort(404, description="Task not found.")
    tasks.remove(task)
    save_tasks(tasks)
    return jsonify({"message": "Task deleted"}), 200

# Endpoint to update a specific task by ID
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = read_tasks()
    # Find the task by ID
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        abort(404, description="Task not found.")
    updates = request.json  # Get updates from the request
    task.update(updates)  # Update the task with the new data
    save_tasks(tasks)
    return jsonify(task)

# Endpoint to mark a task as completed
@app.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    tasks = read_tasks()
    # Find the task by ID
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        abort(404, description="Task not found.")
    task["completed"] = True # Mark the task as completed
    save_tasks(tasks)
    return jsonify(task)

# Endpoint to get all unique categories from the tasks
@app.route('/tasks/categories', methods=['GET'])
def get_categories():
    tasks = read_tasks()
    categories = list(set(task.get("category", "Uncategorized") for task in tasks))
    return jsonify(categories)

# Endpoint to get tasks by category
@app.route('/tasks/categories/<string:category_name>', methods=['GET'])
def get_tasks_by_category(category_name):
    tasks = read_tasks()
    category_tasks = [task for task in tasks if task.get("category") == category_name]
    return jsonify(category_tasks)

if __name__ == "__main__":
    app.run(debug=True)