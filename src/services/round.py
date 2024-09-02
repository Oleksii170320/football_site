from datetime import date

from sqlalchemy import desc
from sqlalchemy.orm import Session
from models import round as models, Round, Match
from validation import round as schemas


def get_rounds_list(db: Session):
    """Список всіх турів/раундів"""
    return db.query(models.Round).all()


def get_round(db: Session, round_slug: str):
    return db.query(models.Round).filter(models.Round.slug == round_slug).first()
