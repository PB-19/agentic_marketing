import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f"mysql+aiomysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"
)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                hashed_password VARCHAR(255) NOT NULL
            )
        """))
    print("Table `users` ensured.")

    async with session_factory() as session:
        result = await session.execute(
            text("SELECT COUNT(*) FROM users WHERE username = :u"), {"u": "newuser"}
        )
        if result.scalar() == 0:
            hashed = pwd_ctx.hash("newuser")
            await session.execute(
                text("INSERT INTO users (username, hashed_password) VALUES (:u, :p)"),
                {"u": "newuser", "p": hashed},
            )
            await session.commit()
            print("Seeded: newuser / newuser")
        else:
            print("Already exists: newuser — skipped.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
