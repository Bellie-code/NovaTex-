from app.db.base import Base
from app.db.session import engine

# Import all models so SQLAlchemy knows them
from app.models.user import User
from app.models.attendance import Attendance
from app.models.face_embedding import FaceEmbedding


def init_db():
    Base.metadata.create_all(bind=engine)
