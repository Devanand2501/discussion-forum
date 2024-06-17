# Discussion and User Management API

This project provides a FastAPI-based REST API for managing users, discussions, comments, and replies. Users can follow/unfollow other users, like comments, and reply to comments. The API interacts with a MongoDB database to store data.

## Features

- User Management:
  - Create a user
  - Update a user
  - Delete a user
  - Get a list of all users
  - Search users by name
  - Follow/unfollow other users
  - Get followers and followed users

- Discussion Management:
  - Create a discussion
  - Update a discussion
  - Delete a discussion
  - Get discussions based on tags
  - Get discussions based on text search
  - View count of a discussion

- Comment Management:
  - Add a comment to a discussion
  - Update a comment
  - Delete a comment
  - Like a comment
  - Reply to a comment

## Endpoints

The detailed API documentation, including request and response examples for each endpoint, is available in the Postman collection:

[Postman Documentation](https://documenter.getpostman.com/view/33074643/2sA3XSA1Lp)

## Installation

1. Clone the repository:

    ```bash
    https://github.com/Devanand2501/discussion-forum.git
    cd your-repo
    ```

2. Create a virtual environment and activate it:

    ```bash
    python3 -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your environment variables. Create a `.env` file in the root directory and add the following:

    ```plaintext
    ATLAS_URL=your_mongo_atlas_url
    DB_NAME=your_database_name
    DISCUSSION_COLLECTION=your_discussion_collection_name
    USER_COLLECTION=your_user_collection_name
    ```

## Running the Application

1. Start the FastAPI server:

    ```bash
    uvicorn main:app --reload
    ```

2. The API will be available at `http://127.0.0.1:8000`.

## Usage

You can use the API endpoints as described in the [Postman Documentation](https://documenter.getpostman.com/view/33074643/2sA3XSA1Lp).

## Example Requests

### Create a User

**Request**:

```http
POST /create_user/
Content-Type: application/json

{
    "name": "John Doe",
    "mobile": "1234567890",
    "email": "john@example.com"
}
```

**Response**:

```json
{
    "message": "User created successfully",
    "user_id": "60c72b2f9b1d8c1e4a7b9f2a"
}
```

### Create a Discussion

**Request**:

```http
POST /create_discussion/
Content-Type: application/json

{
    "text": "This is a discussion",
    "image": "http://example.com/image.png",
    "hashtags": ["#example", "#discussion"]
}
```

**Response**:

```json
{
    "message": "Discussion created successfully",
    "discussion_id": "60c72b2f9b1d8c1e4a7b9f2b"
}
```

### Reply to a Comment

**Request**:

```http
POST /discussion/{discussion_id}/comments/{comment_index}/reply
Content-Type: application/json

{
    "text": "This is a reply",
    "author": "Jane Doe"
}
```

**Response**:

```json
{
    "message": "Reply added successfully"
}
```

## System Architecture

### Diagram
![System Architecture Diagram](![System Architecture Diagram](https://github.com/Devanand2501/discussion-forum/blob/main/Architecture.svg?raw=true)
System Architecture.png)

The system architecture consists of:

- **FastAPI Server**: Handles API requests and responses.
- **MongoDB**: Database for storing user, discussion, and comment data.
- **Client**: Can be a web or mobile application making requests to the FastAPI server.

### Flow

1. **Client** sends HTTP requests to the **FastAPI server**.
2. **FastAPI server** processes the requests and interacts with the **MongoDB** database.
3. The **MongoDB** database stores and retrieves data as needed.
4. The **FastAPI server** returns responses to the **Client**.

## Database Schema

### Collections and Relationships

#### Users Collection

```json
{
    "_id": "ObjectId",
    "name": "string",
    "mobile": "string",
    "email": "string",
    "followers": ["ObjectId"],
    "followed_users": ["ObjectId"]
}
```

- `followers`: List of user IDs who follow this user.
- `followed_users`: List of user IDs whom this user follows.

#### Discussions Collection

```json
{
    "_id": "ObjectId",
    "text": "string",
    "image": "string",
    "hashtags": ["string"],
    "created_on": "datetime",
    "view_count": "int",
    "comments": [
        {
            "text": "string",
            "author": "string",
            "likes": "int",
            "replies": [
                {
                    "text": "string",
                    "author": "string",
                    "likes": "int",
                    "created_on": "datetime"
                }
            ],
            "created_on": "datetime"
        }
    ]
}
```

- `view_count`: Number of times the discussion has been viewed.
- `comments`: List of comments on the discussion.
- `replies`: List of replies to a comment.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
