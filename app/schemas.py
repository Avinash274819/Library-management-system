
from datetime import datetime
from pydantic import (
    BaseModel, ConfigDict, EmailStr, Field, model_validator
)


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=150)
    total_copies: int = Field(ge=1)
    available_copies: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_copies(self):
        if self.available_copies is None:
            self.available_copies = self.total_copies

        if self.available_copies > self.total_copies:
            raise ValueError(
                "Available copies cannot exceed total copies"
            )
        return self


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=150)
    total_copies: int | None = Field(default=None, ge=1)
    available_copies: int | None = Field(default=None, ge=0)


class BookOut(BaseModel):
    id: int
    title: str
    author: str
    total_copies: int
    available_copies: int

    model_config = ConfigDict(from_attributes=True)


class MemberCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class MemberOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class BorrowRequest(BaseModel):
    book_id: int = Field(gt=0)
    member_id: int = Field(gt=0)


class BorrowRecordOut(BaseModel):
    id: int
    book_id: int
    member_id: int
    status: str
    borrowed_at: datetime
    returned_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
