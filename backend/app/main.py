from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.middleware.request_logger import RequestLoggerMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware

# Models (important so SQLAlchemy registers tables)
from app.models.user import User
from app.models.attendance import Attendance

# Services
from app.services.recognition_cache_service import load_embeddings_to_cache

# Security
from app.core.security import hash_password

# Routers
from app.routers.analytics import router as analytics_router
from app.routers.spoof import router as spoof_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.attendance import router as attendance_router
from app.routers.admin_users import router as admin_users_router
from app.routers.admin_face import router as admin_face_router

app = FastAPI(
    title="Privacy-Aware Face Recognition Attendance System",
    version="1.0.0",
)


# =====================================================
# DATABASE INITIALIZATION
# =====================================================

Base.metadata.create_all(bind=engine)


# =====================================================
# MIDDLEWARE
# =====================================================

app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# ROUTERS
# =====================================================

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(attendance_router)
app.include_router(spoof_router)
app.include_router(analytics_router)
app.include_router(admin_users_router)
app.include_router(admin_face_router)
# =====================================================
# BASIC ROUTES
# =====================================================

@app.get("/")
def root():
    return {"status": "Backend running successfully"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# =====================================================
# CREATE DEFAULT ADMIN (BOOTSTRAP)
# =====================================================

def create_default_admin():

    db = SessionLocal()

    try:
        admin = db.query(User).filter(
            User.employee_id == "ADMIN001"
        ).first()

        if not admin:
            admin_user = User(
                employee_id="ADMIN001",
                name="System Admin",
                password_hash=hash_password("admin123"),
                role="admin"
            )

            db.add(admin_user)
            db.commit()

            print("✅ Default admin created (ADMIN001 / admin123)")

        else:
            print("ℹ️ Admin already exists")

    except Exception as e:
        print("❌ Failed to create admin:", str(e))

    finally:
        db.close()


# =====================================================
# STARTUP EVENT
# =====================================================

@app.on_event("startup")
def startup_event():

    db = SessionLocal()

    try:
        print("🔄 Loading embeddings into Redis cache...")
        load_embeddings_to_cache(db)
        print("✅ Embedding cache initialized")

        # Create first admin if not exists
        create_default_admin()

    except Exception as e:
        print("❌ Startup error:", str(e))

    finally:
        db.close()