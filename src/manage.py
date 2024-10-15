import asyncio
import json
import time
from datetime import date, datetime

import click
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import Base, engine, AsyncSessionLocal
from models import MODELS


@click.group()
def Manager():
    pass


@Manager.group()
def db():
    """Database context"""


@Manager.command()
@click.option("-h", "--host", default="127.0.0.1")
@click.option("-p", "--port", default=8000, type=int)
def runserver(host, port):
    """Run server"""
    import uvicorn

    uvicorn.run("main:app", host=host, port=port, reload=True)


@db.command()
def dump():
    """Dump database to file"""

    async def async_dump():
        def json_serial(obj):
            if isinstance(obj, (datetime, date)):
                return int(time.mktime(obj.timetuple()))

        data = {}
        async with AsyncSessionLocal() as db:  # Асинхронний контекст для сесії
            async with db.begin():  # Асинхронний контекст для транзакції
                for Model in MODELS:
                    stmt = select(Model)
                    result = await db.execute(stmt)
                    data[Model.__tablename__] = [
                        r[0].to_dict() for r in result.fetchall()
                    ]  # Отримуємо всі результати

        with open("../data.json", "w", encoding="utf8") as fh:
            json.dump(data, fh, default=json_serial, indent=2, ensure_ascii=False)
        print("Done.")

    asyncio.run(async_dump())


@db.command()
def reset():
    """Reset database"""

    async def async_reset():
        from core.database import Base, engine
        from models import MODELS

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("DB Reset is done.")

    asyncio.run(async_reset())


@db.command()
def seed():
    """Restore database from file"""

    async def async_seed():
        from core.database import AsyncSessionLocal
        from models import MODELS

        async with AsyncSessionLocal() as db:
            async with db.begin():
                data = json.load(open("../data.json", "r", encoding="utf8"))
                for Model in MODELS:
                    try:
                        rows = data[Model.__tablename__]
                    except KeyError:
                        print(f"Cannot find data for table: {Model.__tablename__}")
                        raise
                    for row in rows:
                        model = Model(**row)
                        db.add(model)
            await db.commit()
        print("DB commit done.")

    asyncio.run(async_seed())


if __name__ == "__main__":
    Manager()
