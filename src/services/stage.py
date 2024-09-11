from sqlalchemy import distinct
from sqlalchemy.orm import Session

from models import Match, Season
from models.stage import Stage


def get_stages(db: Session):
    stage_list = db.query(Stage).all()
    return stage_list


# def get_distinct_stages_with_groups(db: Session, season_id: int):
#     distinct_stage = (
#         db.query(distinct(Stage.id))
#         .join(Match, Match.stage_id == Stage.id)
#         .filter(Match.season_id == season_id, Match.group_id.is_not(None))
#     ).all()
#     return distinct_stage


def get_distinct_stages_with_groups(
    db: Session, season_id: int = None, season_slug: str = None
):
    """Отримує унікальні stage_id з групами для певного сезону"""

    distinct_stage = (
        db.query(Stage.id)
        .join(Match, Match.stage_id == Stage.id)
        .join(Season, Season.id == Match.season_id)
    )

    if season_id is not None:
        distinct_stage = distinct_stage.filter(Match.season_id == season_id)
    elif season_slug is not None:
        distinct_stage = distinct_stage.filter(Season.slug == season_slug)
    else:
        return None  # або підняти виключення, якщо обидва параметри None

    return distinct_stage.distinct().all()
