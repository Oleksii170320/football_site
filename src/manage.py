import time
import json
from datetime import date, datetime

import click


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

    from sqlalchemy.orm import Session
    from core.database import Base, engine, SessionLocal
    from models import MODELS

    def json_serial(obj):
        if isinstance(obj, (datetime, date)):
            return int(time.mktime(obj.timetuple()))

    data = {}
    db = SessionLocal()
    for Model in MODELS:
        data[Model.__tablename__] = [r.to_dict() for r in db.query(Model).all()]
    with open("../data.json", "w", encoding="utf8") as fh:
        json.dump(data, fh, default=json_serial, indent=2, ensure_ascii=False)
    print("Done.")


@db.command()
def reset():
    """Reset database"""
    from core.database import Base, engine
    from models import MODELS

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("DB Reset is done.")


@db.command()
def seed():
    """Restore database from file"""
    from core.database import SessionLocal
    from models import MODELS

    db = SessionLocal()
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
    db.commit()
    print("DB commit done.")


if __name__ == "__main__":
    Manager()
