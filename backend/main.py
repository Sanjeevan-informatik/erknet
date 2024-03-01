from flask import Flask, request, jsonify
from model import FEUser, Company, create_user, get_all_users, update_user_by_id, get_user_by_id, get_user_and_company_by_id
from functools import wraps
from flask_cors import CORS
import hashlib

app = Flask(__name__)
CORS(app)

# Custom decorator for basic authentication
def basic_auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_basic_auth(auth.username, auth.password):
            return jsonify({'error': 'Unauthorized'}), 401
        return func(*args, **kwargs)
    return wrapper

def check_basic_auth(username, password):
    # Fetch all users from the database
    users = get_all_users()
    for user in users:
        if user['username'] == username and hashlib.md5(password.encode()).hexdigest() == user['password'] and user['UserType'] == 2:
            return True
    return False

@app.route('/login', methods=['POST'])
def login():
    auth_data = request.get_json()
    username = auth_data.get('username')
    password = auth_data.get('password')
    if check_basic_auth(username, password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/users', methods=['GET'])
def get_users():
    users = get_all_users()
    return jsonify(users)


@app.route('/user/<string:uid>', methods=['GET'])
def get_user(uid):
    user = get_user_and_company_by_id(uid)
    print(user)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"error": f"User with UID {uid} not found"}), 404

        
@app.route('/userupdate/<string:uid>', methods=['PUT'])
def update_user(uid):
    user_data = request.json
    # Fetch user data from the database
    existing_user_data = get_user_by_id(uid)
    existing_user_data = dict(existing_user_data)
    if existing_user_data:
        # Update the existing user data with the new data
        for key, value in user_data.items():
            existing_user_data[key] = value

        # Update the user in the database
        updated_user = update_user_by_id(uid, existing_user_data)
        if updated_user:
            return jsonify({"message": f"User with UID {uid} updated successfully"}), 200
        else:
            return jsonify({"error": f"Failed to update user with UID {uid}"}), 500
    else:
        return jsonify({"error": f"User with UID {uid} not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)