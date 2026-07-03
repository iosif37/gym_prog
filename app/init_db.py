from app.database import engine, Base
from app import models  # noqa: F401  (import so SQLAlchemy sees the table classes)

Base.metadata.create_all(bind=engine)
print("Database initialized.")