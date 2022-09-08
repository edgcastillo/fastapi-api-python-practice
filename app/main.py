from fastapi import FastAPI, status, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


while True:
    try:
        conn = psycopg2.connect(
            host='localhost', database='fastapi', user='postgres', password='', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)


@app.get("/")
def root():
    return {"message": "Work in Progress"}


@app.get("/posts")
def get_posts():
    cursor.execute(""" SELECT * FROM posts """)
    all_posts = cursor.fetchall()
    return {"data": all_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s %s %s) RETURNING * """,
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()  # save new/changes post in database
    return {"data": new_post}


@app.get("/posts/{id}")
def find_post(id: int):
    cursor.execute(
        """ SELECT title, content, published, created_at FROM posts WHERE id = %s """, (str(id)))
    found_post = cursor.fetchone()
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return {"data": found_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(
        """ DELETE * FROM posts WHERE id = %s RETURNING * """, (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return {'data': updated_post}
