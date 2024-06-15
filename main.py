from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import time
import sqlite3

app = FastAPI()

conn = sqlite3.connect('movies.db', check_same_thread=False)
c = conn.cursor()

class Movie(BaseModel):
    id: Optional[int]
    title: str = Field(..., max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    director: str = Field(..., max_length=100)
    length: time
    rating: float = Field(..., ge=1, le=10)


@app.get("/api/movies", status_code=200)
def read_movies():
    c.execute("SELECT * FROM movies")
    res = {'list': [] }
    for movie in c.fetchall():
        res['list'].append(createMovie(movie))
    return res

@app.get("/api/movies/{movie_id}", status_code=200)
def read_movie(movie_id: int):
    movie = checkFilm(movie_id)
    return { 'movie': createMovie(movie) }

@app.post("/api/movies", status_code=200) 
def create_movie(movie: Movie):
    c.execute("SELECT * FROM movies WHERE id=?", (movie.id,))
    if c.fetchone() is not None:
        raise HTTPException(status_code=400, detail = 'Film with that id is already exist')
    try:
        c.execute("INSERT INTO movies (title, year, director, length, rating) VALUES (?, ?, ?, ?, ?)",
                (movie.title, movie.year, movie.director, movie.length.isoformat(), movie.rating))
        conn.commit()
    except:
        raise HTTPException(status_code=500, detail = 'Server Expection')
    return {"movie": createMovie(movie)}

@app.patch("/api/movies/{movie_id}", status_code=200)
def update_movie(movie_id: int, movie: Movie):
    try:
        c.execute("UPDATE movies SET title=?, year=?, director=?, length=?, rating=? WHERE id=?",
                (movie.title, movie.year, movie.director, movie.length.isoformat(), movie.rating, movie_id))
        conn.commit()
    except:
        raise HTTPException(status_code=500, detail = 'Server Expection')
    mov = checkFilm(movie_id)
    return {"movie": createMovie(mov)}

@app.delete("/api/movies/{movie_id}", status_code=202)
def delete_movie(movie_id: int):
    checkFilm(movie_id)
    try:
        c.execute("DELETE FROM movies WHERE id=?", (movie_id,))
        conn.commit()
    except:
        raise HTTPException(status_code=500, detail = 'Server Expection')
    return {"detail": "Movie deleted successfully"}


def createMovie(movie: list):
    """Создает обьект фильма в словаре"""
    return {'id': movie[0], 'title': movie[1], 'year': movie[2], 'director': movie[3], 'length': movie[4], 'rating': movie[5] }

def checkFilm(id: int):
    """Проверяет существует ли фильм"""
    c.execute("SELECT * FROM movies WHERE id=?", (id,))
    movie = c.fetchone()
    if movie is None:
        raise HTTPException(status_code=404, detail = 'Not Found')
    return movie
    