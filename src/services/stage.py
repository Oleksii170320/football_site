from sqlalchemy import distinct
from sqlalchemy.orm import Session

from models import Match
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


def get_distinct_stages_with_groups(db: Session, season_id: int):
    # Отримуємо унікальні stage_id за допомогою SQLAlchemy
    distinct_stage = (
        db.query(Stage.id)
        .join(Match, Match.stage_id == Stage.id)
        .filter(Match.season_id == season_id, Match.group_id.is_not(None))
        .distinct()
        .all()
    )

    return distinct_stage
