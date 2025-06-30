import bcrypt
from flask import jsonify
from appconf import AppConfig
from validations import Validations

"""
User class to manage user-related operations.
This class provides methods to create a new user and retrieve user information by ID.
"""
class User:
    """
    Initialize the User class with database connection.
    Uses the AppConfig class to get the database connection.
    """
    def __init__(self):
        self.conn = AppConfig().conn
        self.validations = Validations()
    
    """
    create_user method to add a new user to the database.
    It hashes the password using bcrypt and stores the username, email, and hashed password.
    If the user is added successfully, it returns a success message.
    If an error occurs, it returns an error message with a 500 status code.
    """
    def create_user(self, request=None):
        try:
            data=request.json
            username = data.get("username")
            email = data.get("email")
            password = data.get("password") 
            mySalt = bcrypt.gensalt()
            bytePwd = password.encode('utf-8')
            hash_pass = bcrypt.hashpw(bytePwd, mySalt)

            cursor = self.conn.cursor()

            sql= "insert into users (username, email, password) values(%s, %s, %s)"
            values = (username, email, hash_pass)
            cursor.execute(sql, values)
            self.conn.commit()
            return jsonify({"message": "User added successfully!"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500 
   
    """
    get_user_by_id method retrieves a user by their ID from the database.
    It queries the database for the user with the specified ID and returns their information in JSON format.
    If the user is found, it returns the user information.
    """
    def get_user_by_id(self, user_id=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                return jsonify({"user": user[0]})
            else:
                return jsonify({"message": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500 

