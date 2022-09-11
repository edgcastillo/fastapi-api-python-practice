from enum import auto
from sqlite3 import dbapi2
from fastapi import Depends, FastAPI, status, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, List
from passlib.context import CryptContext
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db

# telling bcrypt what is the hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)  # create the tables

app = FastAPI()

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


@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM posts """)
    # all_posts = cursor.fetchall()
    all_posts = db.query(models.Post).all()
    return all_posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s %s %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()  # save new/changes post in database
    new_post = models.Post(
        **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # retreive this newly created post from our database
    return new_post


@app.get("/posts/{id}", response_model=schemas.Post)
def find_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """ SELECT title, content, published, created_at FROM posts WHERE id = %s """, (str(id)))
    # found_post = cursor.fetchone()
    found_post = db.query(models.Post).filter(models.Post.id == id).first()
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return found_post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """ DELETE * FROM posts WHERE id = %s RETURNING * """, (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    post.delete(synchronize_session=False)
    db.commit()
    Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()


@app.get("/users", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db)):
    all_users = db.query(models.User).all()
    return all_users


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users/{id}", response_model=schemas.User)
def get_user(id: int, db: Session = Depends(get_db)):
    found_user = db.query(models.User).filter(models.User.id == id).first()
    if not found_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with {id} does not exist")
    return found_user
