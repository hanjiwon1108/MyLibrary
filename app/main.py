from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import time

from . import models, schemas, crud
from .database import engine, Base, SessionLocal

# 데이터베이스 연결 재시도 로직
for retry in range(5):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except Exception as e:
        if retry < 4:  # 마지막 시도 전까지는 대기
            print(f"데이터베이스 연결 시도 {retry+1}/5 실패. 5초 후 재시도...")
            time.sleep(5)
        else:
            print(f"데이터베이스 연결 실패: {e}")
            raise

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_books(request: Request, db: Session = Depends(get_db)):
    books = crud.get_books(db)
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

@app.get("/books/new")
def new_book_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "action": "create"})

@app.post("/books/create")
def create_book(
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    is_read: bool = Form(False),
    db: Session = Depends(get_db),
):
    crud.create_book(db, schemas.BookCreate(title=title, author=author, year=year, is_read=is_read))
    return RedirectResponse("/", status_code=303)

@app.get("/books/{book_id}")
def book_detail(book_id: int, request: Request, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    return templates.TemplateResponse("detail.html", {"request": request, "book": book})

@app.post("/books/{book_id}/delete")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    crud.delete_book(db, book_id)
    return RedirectResponse("/", status_code=303)

@app.get("/books/{book_id}/edit")
def edit_book_form(book_id: int, request: Request, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    return templates.TemplateResponse("form.html", {"request": request, "book": book, "action": "update"})

@app.post("/books/{book_id}/update")
def update_book(
    book_id: int,
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    is_read: bool = Form(False),
    db: Session = Depends(get_db),
):
    book_data = schemas.BookUpdate(title=title, author=author, year=year, is_read=is_read)
    crud.update_book(db, book_id, book_data)
    return RedirectResponse(f"/books/{book_id}", status_code=303)