from fastapi import FastAPI, status, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


try:
    conn = psycopg2.connect(
        host='localhost', database='fastapi', user='postgres', password='')
    cursor = conn.cursor()
except Exception as error:
    print("Connecting to database failed")
    print("Error: ", error)


all_posts = [
    {"id": 1, "title": "Post One", "content": "This is the first post"},
    {"id": 2, "title": "Post Two", "content": "This is the second post"}
]


def find_single_post(id):
    for post in all_posts:
        if id == post["id"]:
            return post


def find_post_index(id):
    for index, post in all_posts:
        if id == post["id"]:
            return index, post


@app.get("/")
def root():
    return {"message": "Work in Progress"}


@app.get("/posts")
def get_posts():
    return {"data": all_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    new_post = post.dict()
    new_post["id"] = randrange(0, 1000000)
    all_posts.append(new_post)
    return {"data": new_post}


@app.get("/posts/{id}")
def find_post(id: int):
    post = find_single_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return {"data": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index, post = find_post_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    all_posts.pop(index)
    Response(status_code=status.HTTP_204_NO_CONTENT)
