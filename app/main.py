from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

from app.database import get_db
from app.models import Exercise, Set


app = FastAPI()


# ---- Pydantic schemas (define the shape of request/response data) ----

class ExerciseCreate(BaseModel):
    name: str


class ExerciseOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class SetCreate(BaseModel):
    exercise_id: int
    weight: float
    reps: int
    set_number: int
    timestamp: datetime | None = None  # optional, will default to now if not provided


class SetOut(BaseModel):
    id: int
    exercise_id: int
    weight: float
    reps: int
    set_number: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ---- Exercise endpoints ----

@app.post("/exercises", response_model=ExerciseOut)
def create_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
    existing = db.query(Exercise).filter(Exercise.name == exercise.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Exercise already exists")
    new_exercise = Exercise(name=exercise.name)
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise


@app.get("/exercises", response_model=list[ExerciseOut])
def list_exercises(db: Session = Depends(get_db)):
    return db.query(Exercise).order_by(Exercise.name).all()


# ---- Set endpoints ----

@app.post("/sets", response_model=SetOut)
def create_set(set_data: SetCreate, db: Session = Depends(get_db)):
    exercise = db.query(Exercise).filter(Exercise.id == set_data.exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    new_set = Set(
        exercise_id=set_data.exercise_id,
        weight=set_data.weight,
        reps=set_data.reps,
        set_number=set_data.set_number,
        timestamp=set_data.timestamp or datetime.utcnow(),
    )
    db.add(new_set)
    db.commit()
    db.refresh(new_set)
    return new_set


@app.get("/sets", response_model=list[SetOut])
def list_sets(exercise_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Set)
    if exercise_id is not None:
        query = query.filter(Set.exercise_id == exercise_id)
    return query.order_by(Set.timestamp).all()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})