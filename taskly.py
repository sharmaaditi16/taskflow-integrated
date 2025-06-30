import bcrypt
from flask import jsonify
import jwt
from datetime import datetime, timezone, timedelta
from appconf import AppConfig
from transformers import pipeline
from validations import Validations

"""
Taskly class to manage tasks and user authentication.
This class provides methods to create, read, update, and delete tasks,
as well as user login and AI-assisted task suggestions.
"""
class Taskly:

    """
    Initialize the Taskly class with database connection and AI model.
    Uses the AppConfig class to get the database connection and application configuration.
    Loads a text-to-text generation model from Hugging Face for AI-assisted bot.
    """
    def __init__(self):
        self.conn = AppConfig().conn
        self.config = AppConfig().app.config
        self.generator = pipeline("text2text-generation", model="google/flan-t5-small")
        self.validations = Validations()

    """
    get_tasks method retrieves all tasks created by a specific user.
    It queries the database for tasks associated with the user ID and returns them in JSON format.
    If no tasks are found, it returns a 404 error with a message.
    """
    def get_tasks(self,user_id=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, title, description, status, due_date, created_at, updated_at from tasks where created_by = %s", (user_id,))
            tasks = cursor.fetchall()
            cursor.close()
            self.conn.close()
            if not tasks:
                return jsonify({"message": "No tasks found"}), 404
            response = []
            for task in tasks:
                task_dict = {
                    "id": task[0],
                    "title": task[1],
                    "description": task[2],
                    "status": task[3],
                    "due_date": task[4],
                    "created_at": task[5],
                }
                # Convert datetime objects to ISO format strings
                for key in ["due_date", "created_at"]:
                    if isinstance(task_dict[key], datetime):
                        task_dict[key] = task_dict[key].isoformat()
                response.append(task_dict)
        except Exception as e:
            return jsonify({"error": str(e), "tasks" : []}), 500

        return jsonify({"tasks": response}), 200 

    """
    add_task method adds a new task for a specific user.
    It retrieves the task details from the request and inserts them into the database.
    If the task is added successfully, it returns a 201 status with the task ID.
    """
    def add_task(self, request=None,user_id=None):

        try:
            data=request.json

            title = data.get("title")
            description = data.get("description")
            status = data.get("status", "pending")            
            due_date = data.get("due_date") 

            cursor = self.conn.cursor()
            query = "INSERT INTO tasks (title, description, status, due_date, created_by) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (title, description, status, due_date,user_id))
            self.conn.commit()
            task_id = cursor.lastrowid
            cursor.close()
            self.conn.close()
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify({"message": "Task added successfully", "task_id": task_id}), 201

    """
    update_task method updates an existing task for a specific user.
    It retrieves the task details from the request and updates the corresponding record in the database.
    If the task is updated successfully, it returns a success message.
    """
    def update_task(self,request,user_id=None):

        try:
            data=request.get_json()

            cursor = self.conn.cursor()
            task_id = data['id'] #extract values
            title = data['title']
            description = data['description']
            status= data['status']
            due_date = data['due_date']

            if task_id is None or title is None or description is None or status is None or due_date is None:
                return jsonify({"error": "Missing required fields"}), 400
            cursor.execute("UPDATE tasks SET title = %s,description = %s,status = %s,due_date = %s WHERE id = %s AND created_by = %s", (title, description, status, due_date,task_id,user_id))
            self.conn.commit()
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
        return jsonify({"message": "Task updated successfully"})

    """
    get_task_by_id method retrieves a specific task by its ID for a specific user.
    It queries the database for the task associated with the task ID and user ID.
    If the task is found, it returns the task details in JSON format.
    If the task is not found, it returns a 404 error with a message.
    """
    def get_task_by_id(self,task_id, user_id=None): 
        try:
            cursor = self.conn.cursor()  
            cursor.execute("SELECT * FROM tasks WHERE id = %s and created_by = %s", (task_id,user_id))#single tuple
            task = cursor.fetchone() 
            if task is None:
                return jsonify({"error": "Task not found"}), 404
            task_dict = {
                "id": task[0],
                "title": task[1],
                "description": task[2],
                "status": task[3],
                "due_date": task[4],
                "created_at": task[5],
            }
        except Exception as e:
            return jsonify({"error": str(e), "task" : {}}), 500

        if task:
            return jsonify({"task": task_dict})
        else:  
            return jsonify({"error": "task not found"}), 404

    """
    delete_by_id method deletes a specific task by its ID for a specific user.
    It checks if the task exists in the database and if it does, it deletes the task.
    If the task is deleted successfully, it returns a success message.
    """
    def delete_by_id(self,task_id,user_id=None):
        try:
            cursor = self.conn.cursor()  
            cursor.execute("SELECT * FROM tasks WHERE id = %s and created_by = %s", (task_id,user_id))#single tuple
            task = cursor.fetchone() 
            if task is not None:
                query="DELETE from tasks where id="+ str(task_id) +" and created_by = " + str(user_id)
                cursor.execute(query)
                self.conn.commit()
                return jsonify({"message": "Task with ID " + str(task_id) + " deleted successfully"})
            else:
                return jsonify({"error": "task not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e), "message" : ""}), 500

    """
    login method authenticates a user based on their email and password.
    It checks if the user exists in the database and verifies the password.
    If the login is successful, it generates a JWT token for the user.
    """
    def login(self,request=None):
        token = ""
        pass_check_status = False
        try:
            data=request.json
            email = data.get("email")  
            cursor = self.conn.cursor()  
            query = "SELECT * FROM users WHERE email = '" + str(email) + "'"
            cursor.execute(query)
            user = cursor.fetchone()
            if user is None:
                return jsonify({"login": pass_check_status, "message": "User not found"}), 404
            p = data.get("password")
            p_assword = p.encode('utf-8')
            pass_check_status = bcrypt.checkpw(p_assword,bytes(user[3], 'utf-8'))
            token = jwt.encode({'id': user[0], 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
                            self.config['SECRET_KEY'], algorithm="HS256")

        except Exception as e:
            return jsonify({"error": str(e), "message" : ""}), 500

        return jsonify({"login": pass_check_status, "token": token})
    
    """
    copilot_suggest method generates a suggestion for the user based on the input provided.
    It uses the language model to generate a response to the user's request.
    """
    def copilot_suggest(self, request):
        data = request.json
        input_text = data.get("input", "")
        prompt = f"Help me with: {input_text}"

        try:
            result = self.generator(prompt, max_new_tokens=100)
            response = jsonify({"answer": result[0]["generated_text"]})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    """
    autocomplete_task method generates a task suggestion based on the prefix provided.
    It uses the language model to complete the task description based on the prefix.
    """
    def autocomplete_task(self, request):
        data = request.json
        prefix = data.get("prefix", "")
        prompt = f"Complete this task: {prefix}"

        try:
            result = self.generator(prompt, max_new_tokens=15, num_return_sequences=1)
            suggestion = result[0]["generated_text"]

            # Clean and compare
            suggestion = suggestion.strip()
            if suggestion.lower().startswith(prefix.lower()):
                completion = suggestion[len(prefix):]
            else:
                completion = suggestion

            response = jsonify({"suggestion": prefix + completion.strip()})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        except Exception as e:
            return jsonify({"error": str(e)}), 500
