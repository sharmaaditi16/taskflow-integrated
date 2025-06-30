import mysql.connector
from flask import Flask,request

"""
AppConfig class to manage application configuration and database connection.
This class initializes the Flask application and sets up the database connection.
"""
class AppConfig:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",    
            user="root",         
            password="",  
            database="task_manager"
        )
        self.app = None  # Placeholder for Flask app instance
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = '3o374eoxq0qiou4'  # Secret key for session management
        self.app.config['JWT_SECRET_KEY'] = '3o374eoxq0qiou4'  # Secret key for JWT
        self.app.config['JWT_TOKEN_LOCATION'] = ['headers']


