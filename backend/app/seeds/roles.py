from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.role import Role

DEFAULT_ROLES = [
    {
        "name": "Manager",
        "description": "Manages projects, staff, clients, and organization resources.",
    },
    {
        "name": "Staff",
        "description": "Works on assigned projects and tasks.",
    },
    {
        "name": "Client",
        "description": "Reviews project progress and provides feedback.",
    },
]


def seed_roles():
    db = SessionLocal()
    
    try:
        for role_data in DEFAULT_ROLES:
            existing_role = db.scalar(
                select(Role).where(Role.name == role_data["name"])
            )
            
            if existing_role:
                continue
            
            db.add(Role(**role_data))
            
        db.commit()
    
    finally:
        db.close()
        

if __name__ == "__main__":
    seed_roles()
        