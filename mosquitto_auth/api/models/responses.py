from enum import Enum

class UserMessages(str, Enum):
    USER_CREATED = "User '{username}' created successfully."
    MANY_USERS_CREATED = "Users created successfully."
    USER_EXISTS = "User '{username}' already exists."
    USER_DELETED = "User '{username}' removed successfully."
    USER_NOT_FOUND = "User '{username}' not found"
    PASSWORD_UPDATED = "Password for user '{username}' updated successfully."
    USER_LISTED = "Users listed successfully."
    USER_INVALID = "User '{username}' is invalid."