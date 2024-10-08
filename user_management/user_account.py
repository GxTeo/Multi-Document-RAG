import gradio as gr
from pymongo import MongoClient

# Authentication
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now you can import from backend
from backend.utils import *
from backend.classes import *
from backend.hashing import Hash


# Connect to MongoDB
MONGO_CLIENT = MongoClient('localhost', 27017)
USER_DB = MONGO_CLIENT['Users']
USER_COLLECTION = USER_DB['users']

# Create a new user
def create_user(username, password):
    if len(username) < 4 or len(username) > 20 or not username.isalnum():
        return "Invalid username."

    if len(password) < 8 or not any(char in "!@#$%^&*()-_+=~`[]{}|;:,.<>?/" for char in password):
        return "Invalid password."

    if USER_COLLECTION.find_one({"username": username}):
        return "User already exists."

    hashed_pass = Hash.bcrypt(password)
    user_object = User(username=username, password=hashed_pass)
    USER_COLLECTION.insert_one(user_object.dict())  
    return "User created successfully."

# Read user information
def read_user(search_term=None):
    try:
        if search_term:
            users = USER_COLLECTION.find({"username": search_term})
        else:
            users = USER_COLLECTION.find()
        
        user_list = []
        for user in users:
            user_list.append({
                "Username": user.get("username"),
                "Password": "*********"  # Hide the actual password
                # Add other fields as necessary
            })
        
        if not user_list:
            return "No users found."
        
        return user_list
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
# Update user information
def update_user(username, old_password, new_password):

    user = USER_COLLECTION.find_one({"username": username})
    if not user:
        return "User not found."

    if not Hash.verify(user["password"], old_password):
        return "Please enter the correct username and password."    
    
    hashed_pass = Hash.bcrypt(new_password)
    USER_COLLECTION.update_one({"username": username}, {"$set": {"password": hashed_pass}})
    return "User updated successfully."

# Delete user
def delete_user(username, password):

    user = USER_COLLECTION.find_one({"username": username})
    if not user:
        return "User not found."
    
    if not Hash.verify(user["password"], password):
        return "Please enter the correct username and password."
    
    result = USER_COLLECTION.delete_one({"username": username, "password": password})   

    # Delete the corresponding user data from other collections
     
    return "User deleted successfully."

# Create Gradio interfaces
create_interface = gr.Interface(
    fn=create_user,
    inputs=[
        gr.Textbox(label="Username"),
        gr.Textbox(label="Password", type="password")
    ],
    outputs=gr.Textbox(label="Result"),
    title="Create User",
    description="Create a new user account"
)

read_interface = gr.Interface(
    fn=read_user,
    inputs=[gr.Textbox(label="Search (optional)")],
    outputs=gr.JSON(label="User Data"),
    title="Read Users",
    description="View all users or search for specific users"
)


update_interface = gr.Interface(
    fn=update_user,
    inputs=[
        gr.Textbox(label="Username"),
        gr.Textbox(label="Old Password", type="password"),
        gr.Textbox(label="New Password (optional)", type="password")
    ],
    outputs=gr.Textbox(label="Result"),
    title="Update User",
    description="Update user account information"
)

delete_interface = gr.Interface(
    fn=delete_user,
    inputs=[gr.Textbox(label="Username"), gr.Textbox(label="Password", type="password")],
    outputs=gr.Textbox(label="Result"),
    title="Delete User",
    description="Delete a user account"
)

# Combine interfaces
demo = gr.TabbedInterface([create_interface, read_interface, update_interface, delete_interface], 
                          ["Create", "Read", "Update", "Delete"])

# Launch the app
if __name__ == "__main__":
    demo.launch(server_port=8080) 