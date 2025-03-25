# from sqlalchemy import text
# from database import async_session

# async def test_db():
#     async with async_session() as session:
#         result = await session.execute(text("select 1"))
#         print(result.scalar())

# import asyncio
# asyncio.run(test_db())

# import secrets

# print(secrets.token_urlsafe(32))

from sqlalchemy.orm import Session
from app.database import get_db
from app.users.models import User

def delete_existing_users():
    db: Session = next(get_db())  # Get the database session
    db.query(User).delete()  # Delete all users
    db.commit()  # Commit the changes
    print("All users deleted successfully.")

delete_existing_users()


