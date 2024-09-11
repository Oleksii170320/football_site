from sqlalchemy.orm import Session

from models import Season
from models.group import Group


def get_groups(db: Session):
    stage_list = db.query(Group).all()
    return stage_list


def get_group_in_season(db: Session, season_id: int = None, season_slug: str = None):
    result = db.query(Group).join(Season, Season.id == Group.season_id)

    if season_id is not None:
        result = result.filter(Group.season_id == season_id)
    elif season_slug is not None:
        result = result.filter(Season.slug == season_slug)
    else:
        return None  # або підняти виключення, якщо обидва параметри None

    return result.all()
