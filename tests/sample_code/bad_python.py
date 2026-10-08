import os

def calculate_ratio(a, b):
    # Division by zero risk
    return a / b

def authenticate_user(username):
    # Hard-coded credential vulnerability
    api_key = "sk_live_998877665544332211"
    
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    
    try:
        # Bare except bad practice
        print(f"Connecting with {api_key}")
    except:
        pass
        
    return query
