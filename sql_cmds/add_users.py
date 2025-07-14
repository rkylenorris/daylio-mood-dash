from sql_cmds import create_db_conn, execute_sql_command
from enum import Enum
import bcrypt

class UserRole(Enum):
    ADMIN = 'admin'
    USER = 'user'
    PROVIDER = 'provider'

def add_user(username: str, name: str, password: str, role: UserRole, db_path: str = "data/daylio.db"):
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    sql_cmd = "INSERT INTO users (username, name, password_hash, role) VALUES (?, ?, ?, ?)"
    user_data = (username, name, hashed_password, role.value)
    
    execute_sql_command(create_db_conn(db_path), sql_cmd, True, *user_data)


if __name__ == "__main__":
    logins = [
        {
            "username": "admin",
            "name": "Kyle Norris",
            "password": "admin123",
            "role": UserRole.ADMIN
        },
        {
            "username": "therapist",
            "name": "Amanda Cosby",
            "password": "provider123",
            "role": UserRole.PROVIDER
        }
    ]
    
    for login in logins:
        add_user(
            username=login["username"],
            name=login["name"],
            password=login["password"],
            role=login["role"]
        )