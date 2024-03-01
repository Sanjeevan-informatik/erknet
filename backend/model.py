import hashlib
import mysql.connector
import uuid
import time
import warnings
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Define database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'erknet',
    'database': 'erknet'
}

# Establish a connection to MariaDB
connection = mysql.connector.connect(**db_config)

# Define Pydantic model for Company
class Company(BaseModel):
    name: str

# Define Pydantic model for User
class FEUser(BaseModel):
    uid: str = Field(alias='uid', default_factory=lambda: str(uuid.uuid4()))
    UserType: int = Field(alias='UserType', default=2)
    tstamp: int = Field(alias='tstamp', default=int(datetime.now().timestamp()))
    ts_lastentry: str = Field(alias='ts_lastentry', default=None)
    password: str = Field(alias='password', max_length=100)
    disable: int = Field(alias='disable', default=0)
    first_name: str = Field(alias='first_name', max_length=50, default=None)
    lastName: str = Field(alias='lastName', max_length=50)
    username: str = Field(alias='username', default_factory=lambda: '')

    # Validators
    @validator('UserType')
    def validate_UserType(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError("UserType must be 1 (institute), 2 (admin), or 3 (user)")
        return v

    @validator('tstamp')
    def validate_tstamp(cls, v):
        if v < 0:
            raise ValueError("tstamp must be a positive integer representing Unix Timestamp")
        return v

    @validator('ts_lastentry', pre=True, always=True)
    def validate_ts_lastentry(cls, v):
        if v is None:
            return str(datetime.now())
        elif isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return v

    @validator('password')
    def hash_password(cls, v):
        return hashlib.md5(v.encode()).hexdigest()

    @validator('disable')
    def validate_disable(cls, v):
        if v not in [0, 1]:
            raise ValueError("disable must be either 0 (False) or 1 (True)")
        return v

    @validator('username', pre=True, always=True)
    def generate_username(cls, v, values):
        if not v:
            return values.get('first_name', '') + " " + values.get('lastName', '')
        return v

# Function to create the database tables
def create_tables():
    try:
        cursor = connection.cursor()

        # Define SQL queries to create tables
        users_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                uid VARCHAR(36) PRIMARY KEY,
                UserType INT NOT NULL DEFAULT 2,
                tstamp INT NOT NULL,
                ts_lastentry DATETIME,
                password VARCHAR(100) NOT NULL,
                disable INT NOT NULL DEFAULT 0,
                first_name VARCHAR(50) NOT NULL,
                lastName VARCHAR(50) NOT NULL,
                username VARCHAR(50) NOT NULL
            )
        """
        user_company_table_query = """
            CREATE TABLE IF NOT EXISTS user_company (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(36),
                company_name VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(uid)
            )
        """

        # Execute the SQL queries
        cursor.execute(users_table_query)
        cursor.execute(user_company_table_query)

        # Commit the transaction
        connection.commit()
        print("Tables created successfully.")

    except Exception as e:
        # Rollback the transaction if an error occurs
        connection.rollback()
        print("Error:", e)

    finally:
        # Close the cursor
        cursor.close()

# Function to insert a new user into the database
def create_user(user: FEUser, companies: List[Company]):
    cursor = connection.cursor()

    try:
        user_query = "INSERT INTO users (uid, UserType, tstamp, ts_lastentry, password, disable, first_name, lastName, username) " \
                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(user_query, (user.uid, user.UserType, user.tstamp, user.ts_lastentry, user.password, user.disable,
                                    user.first_name, user.lastName, user.username))

        user_company_query = "INSERT INTO user_company (user_id, company_name) VALUES (%s, %s)"
        for company in companies:
            cursor.execute(user_company_query, (user.uid, company.name))

        connection.commit()
        print("User inserted successfully.")

    except Exception as e:
        # Rollback the transaction if an error occurs
        connection.rollback()
        print("Error:", e)

    finally:
        # Close the cursor
        cursor.close()

def get_all_users() -> List[dict]:
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch all users
        user_query = "SELECT * FROM users"
        cursor.execute(user_query)
        users_results = cursor.fetchall()

        # Fetch all companies associated with users
        company_query = "SELECT uc.user_id, GROUP_CONCAT(uc.company_name) as companies " \
                        "FROM user_company uc " \
                        "GROUP BY uc.user_id"
        cursor.execute(company_query)
        company_results = cursor.fetchall()

        # Create a dictionary to store companies associated with each user
        user_companies = {result['user_id']: result['companies'].split(',') for result in company_results}

        users_data = []
        for user_result in users_results:
            user_info = {
                'uid': user_result['uid'],
                'UserType': user_result['UserType'],
                'tstamp': user_result['tstamp'],
                'ts_lastentry': user_result['ts_lastentry'],
                'password': user_result['password'],
                'disable': user_result['disable'],
                'first_name': user_result['first_name'],
                'lastName': user_result['lastName'],
                'username': user_result['username'],
                'companies': user_companies.get(user_result['uid'], [])  # Get associated companies for user
            }
            users_data.append(user_info)

        return users_data

    finally:
        cursor.close()

def get_user_and_company_by_id(user_id: str) -> Optional[dict]:
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT u.*, GROUP_CONCAT(c.company_name) as company_names
            FROM users u
            LEFT JOIN user_company c ON u.uid = c.user_id
            WHERE u.uid = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if result:
            result['company_names'] = result['company_names'].split(',') if result['company_names'] else []
            return result

        return None

    finally:
        cursor.close()

def get_user_by_id(user_id: str) -> Optional[FEUser]:
    cursor = connection.cursor(dictionary=True)

    try:
        query = "SELECT * FROM users WHERE uid = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return FEUser(**result)
        return None

    finally:
        # Close the cursor
        cursor.close()

def update_user_by_id(user_id: str, user_data: dict) -> Optional[FEUser]:
    cursor = connection.cursor(dictionary=True)

    try:
        user_update_query = """
            UPDATE users
            SET UserType = %(UserType)s, 
                tstamp = %(tstamp)s, 
                ts_lastentry = %(ts_lastentry)s, 
                password = %(password)s, 
                disable = %(disable)s, 
                first_name = %(first_name)s, 
                lastName = %(lastName)s, 
                username = %(username)s
            WHERE uid = %(uid)s
        """
        user_data['uid'] = user_id
        cursor.execute(user_update_query, user_data)

        connection.commit()

        updated_user = get_user_by_id(user_id)
        return updated_user

    except Exception as e:
        connection.rollback()
        print("Error:", e)

    finally:
        cursor.close()


# Define a function to drop all tables
def drop_all_tables():
    try:
        cursor = connection.cursor()

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE {table_name}")

        print("All tables dropped successfully.")

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":


    create_tables()

    users_data = [
        {"first_name": "admin", "lastName": "demo", "password": "admin_demo", "username": "admin_demo", "companies_data": ["001", "002"]},
        {"UserType": 1, "first_name": "", "lastName": "", "password": "user4","username": "001", "companies_data": ["001", "002"]},
        {"UserType": 3, "first_name": "John", "lastName": "Doe", "password": "user1", "username": "user1", "companies_data": ["001", "002"]},
        {"UserType": 3, "first_name": "Jane", "lastName": "Smith", "password": "user2", "username": "user2", "companies_data": ["001"]},
        {"UserType": 3, "first_name": "Mike", "lastName": "Johnson", "password": "user3", "username": "user3","companies_data": ["001"]},
        {"UserType": 1, "first_name": "", "lastName": "", "password": "user4", "username": "002","companies_data": ["001"]},
        {"UserType": 1, "first_name": "", "lastName": "", "password": "user4", "username": "003","companies_data": ["001"]},
        {"UserType": 3, "first_name": "Emily", "lastName": "Davis", "password": "user4", "username": "user4","companies_data": ["001"]},
        {"UserType": 3, "first_name": "Chris", "lastName": "Miller", "password": "user5", "username": "user5","companies_data": ["001"]},
        {"UserType": 3, "first_name": "Amanda", "lastName": "White", "password": "user6", "username": "user6","companies_data": ["001"]},
        {"UserType": 3, "first_name": "Tom", "lastName": "Brown", "password": "user7", "username": "user7","companies_data": ["001"]},
        {"UserType": 3, "first_name": "Sophie", "lastName": "Wilson", "password": "user8", "username": "user8","companies_data": ["001"]},
        {"UserType": 3, "first_name": "David", "lastName": "Taylor", "password": "user9", "username": "user9","companies_data": ["001"]},
        {"UserType": 3, "first_name": "Rachel", "lastName": "Harris", "password": "user10", "username": "user10","companies_data": ["001"]},
        {"UserType": 3, "first_name": "Mike", "lastName": "Johnson", "password": "user3", "username": "user3","companies_data": ["001"]}
    ]

    users = []
    companies_data = set()  # Store company names in a set to avoid duplicates
    for data in users_data:
        companies_data.update(data.get("companies_data", []))  # Collect all company names
        user_companies = [Company(name=name) for name in data.get("companies_data", [])]
        del data["companies_data"]  # Remove companies_data from user data
        user = FEUser(**data)
        users.append((user, user_companies))

    companies = [Company(name=name) for name in companies_data]

    for user, user_companies in users:
        create_user(user, user_companies)

    all_users = get_all_users()
    for user in all_users:
        print("User:", user)





    