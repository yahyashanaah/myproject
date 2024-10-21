import os
import sys
import django
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add the project root directory to the Python path


# Initialize Django
django.setup()

from myapp.models import Post  # Import the Django model after setting up Django
from django.db import connection

app = FastAPI()

# Pydantic model for Post
class PostSchema(BaseModel):
    title: str
    content: str

# Helper function to execute raw SQL for Django ORM
def get_db_cursor():
    cursor = connection.cursor()
    return cursor

# CREATE a post
@app.post("/posts/", response_model=PostSchema)
async def create_post(post: PostSchema):
    cursor = get_db_cursor()
    cursor.execute(
        "INSERT INTO myapp_post (title, content, created_at) VALUES (%s, %s, NOW()) RETURNING id",
        [post.title, post.content]
    )
    post_id = cursor.fetchone()[0]
    return {**post.dict(), "id": post_id}

# READ all posts
@app.get("/posts/")
async def get_posts():
    cursor = get_db_cursor()
    cursor.execute("SELECT id, title, content FROM myapp_post")
    posts = cursor.fetchall()
    return [{"id": p[0], "title": p[1], "content": p[2]} for p in posts]

# READ a single post by ID
@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    cursor = get_db_cursor()
    cursor.execute("SELECT id, title, content FROM myapp_post WHERE id = %s", [post_id])
    post = cursor.fetchone()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": post[0], "title": post[1], "content": post[2]}

# UPDATE a post
@app.put("/posts/{post_id}")
async def update_post(post_id: int, post: PostSchema):
    cursor = get_db_cursor()
    cursor.execute("UPDATE myapp_post SET title = %s, content = %s WHERE id = %s", 
                   [post.title, post.content, post_id])
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": post_id, **post.dict()}

# DELETE a post
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    cursor = get_db_cursor()
    cursor.execute("DELETE FROM myapp_post WHERE id = %s", [post_id])
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"detail": "Post deleted"}