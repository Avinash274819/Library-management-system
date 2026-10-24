
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management API")


# ========== BOOK APIs ==========

# 1. Get all books
@app.get("/books", response_model=list[schemas.BookOut], tags=["Books"])
def get_books(db: Session = Depends(get_db)):
    return db.scalars(
        select(models.Book).order_by(models.Book.id)
    ).all()


# 2. Get one book
@app.get("/books/{book_id}", response_model=schemas.BookOut, tags=["Books"])
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


# 3. Add a book
@app.post(
    "/books",
    response_model=schemas.BookOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Books"]
)
def add_book(payload: schemas.BookCreate, db: Session = Depends(get_db)):
    book = models.Book(**payload.model_dump())

    db.add(book)
    db.commit()
    db.refresh(book)

    return book


# 4. Update a book
@app.put("/books/{book_id}", response_model=schemas.BookOut, tags=["Books"])
def update_book(
    book_id: int,
    payload: schemas.BookUpdate,
    db: Session = Depends(get_db)
):
    book = db.get(models.Book, book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    changes = payload.model_dump(exclude_unset=True)

    new_total = changes.get("total_copies", book.total_copies)
    new_available = changes.get(
        "available_copies", book.available_copies
    )

    if new_available is None or new_available > new_total:
        raise HTTPException(
            status_code=400,
            detail="Available copies cannot exceed total copies"
        )

    borrowed_copies = book.total_copies - book.available_copies

    if new_total < borrowed_copies:
        raise HTTPException(
            status_code=400,
            detail="Total copies cannot be less than borrowed copies"
        )

    for key, value in changes.items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)

    return book


# 5. Delete a book
@app.delete("/books/{book_id}", tags=["Books"])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    existing_record = db.scalar(
        select(models.BorrowRecord.id)
        .where(models.BorrowRecord.book_id == book_id)
        .limit(1)
    )

    if existing_record is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a book with borrow records"
        )

    db.delete(book)
    db.commit()

    return {"message": "Book deleted successfully"}


# ========== MEMBER APIs ==========

# 6. Get all members
@app.get(
    "/members",
    response_model=list[schemas.MemberOut],
    tags=["Members"]
)
def get_members(db: Session = Depends(get_db)):
    return db.scalars(
        select(models.Member).order_by(models.Member.id)
    ).all()


# 7. Get one member
@app.get(
    "/members/{member_id}",
    response_model=schemas.MemberOut,
    tags=["Members"]
)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.get(models.Member, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    return member


# 8. Register a member
@app.post(
    "/members",
    response_model=schemas.MemberOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Members"]
)
def add_member(
    payload: schemas.MemberCreate,
    db: Session = Depends(get_db)
):
    member = models.Member(
        name=payload.name,
        email=str(payload.email)
    )

    db.add(member)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="A member with this email already exists"
        )

    db.refresh(member)
    return member


# ========== BORROW AND RETURN APIs ==========

# 9. Borrow a book
@app.post(
    "/borrow",
    response_model=schemas.BorrowRecordOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Borrowing"]
)
def borrow_book(
    payload: schemas.BorrowRequest,
    db: Session = Depends(get_db)
):
    book = db.get(models.Book, payload.book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    member = db.get(models.Member, payload.member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if book.available_copies <= 0:
        raise HTTPException(
            status_code=400,
            detail="No copies of this book are currently available"
        )

    book.available_copies -= 1

    record = models.BorrowRecord(
        book_id=book.id,
        member_id=member.id,
        status="borrowed"
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


# 10. Return a book
@app.post(
    "/return/{record_id}",
    response_model=schemas.BorrowRecordOut,
    tags=["Borrowing"]
)
def return_book(record_id: int, db: Session = Depends(get_db)):
    record = db.get(models.BorrowRecord, record_id)

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Borrow record not found"
        )

    if record.status == "returned":
        raise HTTPException(
            status_code=400,
            detail="This book has already been returned"
        )

    book = db.get(models.Book, record.book_id)

    record.status = "returned"
    record.returned_at = datetime.utcnow()
    book.available_copies += 1

    db.commit()
    db.refresh(record)

    return record


# 11. Get all borrow records
@app.get(
    "/borrow-records",
    response_model=list[schemas.BorrowRecordOut],
    tags=["Borrowing"]
)
def get_borrow_records(db: Session = Depends(get_db)):
    return db.scalars(
        select(models.BorrowRecord).order_by(models.BorrowRecord.id)
    ).all()
