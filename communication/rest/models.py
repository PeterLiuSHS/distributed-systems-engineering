import uuid

class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    def to_dict(self):
        # Convert user to dict for JSON serialization.
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }

    @staticmethod
    def from_dict(data):
        # Create User from dict (not used in this basic CRUD, but handy for extensions).
        return User(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email')
        )

# In-memory storage - acts like a tiny DB.
USERS = {
    "1": User("1", "TestUser_Alice", "alice@testusr.com"),
    "2": User("2", "TestUser_Bob", "bob@testusr.com")
}

def get_all():
    # Fetch all users as list of dicts.
    return [user.to_dict() for user in USERS.values()]

def get_by_id(user_id):
    # Get one user by ID, or None if not found.
    user = USERS.get(user_id)
    return user.to_dict() if user else None

def create(name, email):
    # Create new user with UUID ID, basic validation.
    if not name or not email:
        return None  # Invalid input
    new_id = str(uuid.uuid4())[:8]  # Short UUID for simplicity in demo
    user = User(new_id, name, email)
    USERS[new_id] = user
    return user.to_dict()

def update(user_id, name, email):
    # Update user fields if exists and input valid.
    if user_id not in USERS:
        return None
    if not name or not email:
        return None  # Invalid input
    user = USERS[user_id]
    user.name = name
    user.email = email
    return user.to_dict()

def delete(user_id):
    # Delete user if exists, return success flag.
    if user_id in USERS:
        del USERS[user_id]
        return True
    return False