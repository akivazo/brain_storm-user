
Rest API to create, retrive and delete users.

user model:
   name: name of the user
   email: user's emails
   tags: categorites tags that interesting the user
_________________________

1. Create a New User
Endpoint: POST /user
Description: Creates a new user in the system.
Request Body:

{
  "name": "User's name",
  "email": "user@example.com",
  "tags": ["tag1", "tag2"]
}

Response:
Status 201: User created successfully.

{
  "id": "generated_uuid"
}

Status 400: Bad request (if validation fails).

{
  "error": "Validation error message"
}

_________________________

2. Get a User by ID
Endpoint: GET /user/<id>
Description: Retrieves a user by their unique ID.
Response:
Status 200: User found.

{
  "user": {
    "id": "user_id",
    "name": "User's name",
    "email": "user@example.com",
    "tags": ["tag1", "tag2"]
  }
}
Status 404: User not found.

{
  "error": "User with id 'user_id' was not found"
}

_________________________

3. Delete a User by ID
Endpoint: DELETE /user/<id>
Description: Deletes a user by their unique ID.
Response:
Status 204: User deleted successfully.

"User with id 'user_id' was deleted successfully"
