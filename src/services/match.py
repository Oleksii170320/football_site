from datetime import datetime, timedelta

from sqlalchemy import desc, or_, func, case
from sqlalchemy.orm import Session, aliased
from models import (
    Match,
    MatchProperties,
    PositionRole,
    TeamPerson,
    Person,
    Season,
    Tournament,
    Stadium,
    Team,
    Round,
    Stage,
    PlayerRole,
    MatchEvent,
    RefEvent,
    Group,
)
from validation import match as schemas


def get_all_match(db: Session):
    """Запит на всі матчі (з необхідними параметрами)"""

    # Створюємо аліаси для таблиці Team
    team1_alias = aliased(Team)
    team2_alias = aliased(Team)

    result = (
        db.query(
            Match.id.label("match_id"),
            func.strftime("%d-%m-%Y", func.datetime(Match.event, "unixepoch")).label(
                "event"
            ),
            Match.team1_id.label("team1_id"),
            Match.team2_id.label("team2_id"),
            Season.id.label("season_id"),
            Season.name.label("season_name"),
            Season.year.label("season_year"),
            Tournament.logo.label("tournament_logo"),
            Tournament.name.label("tournament_name"),
            Stadium.name.label("stadium_name"),
            Stadium.city.label("stadium_city"),
            team1_alias.logo.label("team1_logo"),
            team1_alias.name.label("team1_name"),
            team1_alias.city.label("team1_city"),
            Match.team1_goals,
            Match.team2_goals,
            Match.team1_penalty,
            Match.team2_penalty,
            team2_alias.name.label("team2_name"),
            team2_alias.city.label("team2_city"),
            team2_alias.logo.label("team2_logo"),
            Match.status,
            Round.name.label("round_name"),
            Stage.name.label("stage_name"),
            Group.name.label("group_name"),
        )
        .join(Season, Season.id == Match.season_id)
        .join(Tournament, Tournament.id == Season.tournament_id)
        .outerjoin(Stadium, Stadium.id == Match.stadium_id)
        .join(team1_alias, team1_alias.id == Match.team1_id)
        .join(team2_alias, team2_alias.id == Match.team2_id)
        .join(Round, Round.id == Match.round_id)
        .outerjoin(Stage, Stage.id == Match.stage_id)
        .outerjoin(Group, Group.id == Match.group_id)
    )

    return result


def get_match(db: Session, match_id: int):
    """Запит на певний матч по ІД"""

    result = get_all_match(db).filter(Match.id == match_id).first()
    return result


def get_matches_team(db: Session, team_id: int):
    """Всі матчі певної команди"""

    result = (
        get_all_match(db)
        .filter(or_(Match.team1_id == team_id, Match.team2_id == team_id))
        .order_by(desc(Match.event))
        .all()
    )
    return result


def get_match_statistics(db: Session, match_id: int):
    """Запит даних статистики матчу (картки, голи і т.д.)"""

    lineups = (
        db.query(
            PositionRole.player_number,
            PositionRole.player_role_id,
            PlayerRole.name.label("role_name"),
            Person.id.label("player_id"),
            Person.lastname.label("player_lastname"),
            Person.name.label("player_name"),
            MatchProperties.protocol,
            MatchProperties.starting,
            MatchProperties.start_min.label("from_what_minute"),
            MatchProperties.end_min.label("how_many_minutes"),
            MatchProperties.id.label("id_player_in_match"),
            TeamPerson.team_id,
            MatchEvent.player_replacement_id,
            # Для 'replacement'
            func.max(case((RefEvent.id == 10, 1), else_=0)).label("replacement"),
            # Для 'all_goals' (рахуємо всі забиті голи)
            func.sum(case((RefEvent.id.in_([1, 2]), 1), else_=0)).label("all_goals"),
            # Для 'count_penalty' (рахуємо голи з пенальті)
            func.sum(case((RefEvent.id == 2, 1), else_=0)).label("penalty"),
            # Для 'count_own_goal' (рахуємо автоголи)
            func.sum(case((RefEvent.id == 4, 1), else_=0)).label("own_goal"),
            # Для 'yellow_card'
            func.max(case((RefEvent.id == 5, 1), else_=0)).label("yellow_card"),
            # Для 'second_yellow_card'
            func.max(case((RefEvent.id == 6, 1), else_=0)).label("second_yellow_card"),
            # Для 'red_card'
            func.max(case((RefEvent.id == 7, 1), else_=0)).label("red_card"),
        )
        .join(TeamPerson, TeamPerson.id == MatchProperties.player_id)
        .join(PositionRole, PositionRole.team_person_id == TeamPerson.id)
        .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
        .join(Person, Person.id == TeamPerson.person_id)
        .outerjoin(MatchEvent, MatchEvent.player_match_id == MatchProperties.id)
        .outerjoin(RefEvent, RefEvent.id == MatchEvent.event_id)
        .filter(MatchProperties.match_id == match_id)
        .group_by(
            Person.id,
            Person.lastname,
            Person.name,
            MatchProperties.protocol,
            MatchProperties.starting,
            MatchProperties.start_min,
            MatchProperties.end_min,
            MatchProperties.id,
        )
        .all()
    )
    return lineups


def get_match_event(db: Session, match_id: int):
    """Запит даних події матчу"""

    lineups = (
        db.query(
            Person.id.label("person_id"),
            Person.name.label("person_name"),
            Person.lastname.label("person_lastname"),
            RefEvent.name.label("event_name"),
            RefEvent.image.label("event_image"),
            MatchEvent.minute.label("minute"),
            MatchEvent.event_id.label("event_id"),
            MatchEvent.player_replacement_id,
            TeamPerson.team_id.label("team_id"),
        )
        .join(TeamPerson, TeamPerson.person_id == Person.id)
        .join(MatchProperties, MatchProperties.player_id == TeamPerson.id)
        .join(MatchEvent, MatchEvent.player_match_id == MatchProperties.id)
        .join(RefEvent, RefEvent.id == MatchEvent.event_id)
        .filter(MatchProperties.match_id == match_id)
        .all()
    )
    return lineups


def get_match_replacement(db: Session, match_id: int):
    """Запит всіх зроблених замін в матчі"""

    # Гравці, якіх замінили
    subquery = (
        db.query(MatchEvent.player_replacement_id)
        .join(MatchProperties, MatchProperties.id == MatchEvent.player_match_id)
        .filter(
            MatchProperties.match_id == match_id,
            MatchEvent.player_replacement_id.isnot(None),
        )
        .subquery()
    )

    # Основний запит, що використовує підзапит
    lineups = (
        db.query(
            Person.id.label("person_id"),
            Person.name.label("person_name"),
            Person.lastname.label("person_lastname"),
            MatchProperties.player_id.label("player_id"),
            MatchProperties.id.label("player_match_id"),
        )
        .join(TeamPerson, TeamPerson.id == MatchProperties.player_id)
        .join(Person, Person.id == TeamPerson.person_id)
        .filter(MatchProperties.id.in_(subquery))
        .all()
    )

    return lineups


def get_replacement(db: Session, match_id: int):
    """Запит гравців, які на заміні"""

    result = (
        db.query(MatchEvent.player_replacement_id)
        .join(MatchProperties, MatchProperties.id == MatchEvent.player_match_id)
        .filter(
            MatchProperties.match_id == match_id,
            MatchEvent.player_replacement_id.isnot(None),
        )
        .all()
    )
    return result


def get_matches(db: Session):
    """Запит вміх матсів"""

    return db.query(Match).order_by(desc(Match.event))


def get_matches_season(db: Session, season_id: int):
    """Запит вміх матсів данного розіграшу"""

    return (
        db.query(Match).filter(Match.season_id == season_id).order_by(desc(Match.event))
    )


def sdc(db: Session, season_id: int):
    """Запит вміх матсів данного розіграшу"""

    matches = (db.query(Match).filter(Match.season_id == season_id)).order_by(
        desc(Match.event)
    )

    return matches


def get_matches_season(db: Session, season_id: int):
    db_match = db.query(Match).filter(Match.season_id == season_id).all()
    return db_match


def get_matches_round(db: Session, season_id: int):
    db_match = (
        db.query(Round.id, Round.name)
        .join(Round, Round.id == Match.round_id)
        .filter(Match.season_id == season_id)
        .group_by(Round.id)  # Використовуємо distinct без аргументів
        .all()
    )
    return db_match


def get_matches_results_season(db: Session, season_id: int):
    db_match = (
        db.query(Match)
        .filter(
            Match.season_id == season_id,
            Match.status.in_(["played", "technical_defeat"]),
        )
        .order_by(desc(Match.event))
        .all()
    )
    return db_match


def get_season_matches(db: Session, season_id: int):
    """Перелік всіх матчів поточного розіграшу"""
    Team1 = aliased(Team)
    Team2 = aliased(Team)

    db_match = (
        db.query(
            Match.id.label("match_id"),
            func.strftime("%d-%m-%Y", func.datetime(Match.event, "unixepoch")).label(
                "event"
            ),
            Match.round_id,
            Round.name.label("round_name"),
            Match.stage_id,
            Stage.name.label("stage_name"),
            Match.group_id,
            Group.name.label("group_name"),
            Team1.id.label("team1_id"),
            Team1.slug.label("team1_slug"),
            Team1.logo.label("team1_logo"),
            Team1.name.label("team1_name"),
            Team1.city.label("team1_city"),
            Match.team1_penalty,
            Match.team1_goals,
            Match.team2_penalty,
            Match.team2_goals,
            Team2.id.label("team2_id"),
            Team2.slug.label("team2_slug"),
            Team2.logo.label("team2_logo"),
            Team2.name.label("team2_name"),
            Team2.city.label("team2_city"),
            Match.status,
        )
        .join(Round, Round.id == Match.round_id)
        .outerjoin(Stage, Stage.id == Match.stage_id)
        .outerjoin(Group, Group.id == Match.group_id)
        .join(Team1, Team1.id == Match.team1_id)
        .join(Team2, Team2.id == Match.team2_id)
        .filter(Match.season_id == season_id)
    )
    return db_match


def get_season_matches_weeks(db: Session, season_id: int):
    """Перелік матчів поточного розіграшу в межах -7 до +7 днів від поточної дати"""

    # Обчислення дати -7 та +7 днів від поточної дати
    current_date = datetime.now()
    start_date = current_date - timedelta(days=7)
    end_date = current_date + timedelta(days=7)

    matches_results = (
        get_season_matches(db, season_id=season_id)
        .filter(
            func.date(Match.event, "unixepoch").between(
                start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
            )
        )
        .all()
    )

    return matches_results


def get_season_matches_results(db: Session, season_id: int):
    """Перелік зіграних матчів поточного розіграшу"""
    matches_results = (
        get_season_matches(db, season_id=season_id)
        .filter(Match.status.in_(["played", "technical_defeat"]))
        .order_by(desc(Match.event))
        .all()
    )
    return matches_results


def get_season_matches_upcoming(db: Session, season_id: int):
    """Перелік не зіграних матчів поточного розіграшу"""
    matches_upcoming = (
        get_season_matches(db, season_id=season_id)
        .filter(Match.status.in_(["not_played", "postponed", "canceled"]))
        .order_by(Round.id)  # Сортування в зворотному порядку
        .all()
    )
    return matches_upcoming


def get_matches_upcoming_season(db: Session, season_id: int):
    db_match = (
        db.query(Match)
        .filter(
            Match.season_id == season_id,
            Match.status.in_(["not_played", "postponed", "canceled"]),
        )
        .order_by(Match.event)
        .all()
    )
    return db_match


def create_match(db: Session, match: schemas.MatchCreateSchemas):
    db_match = Match(**match.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


def update_match(db: Session, match_id: int, match: schemas.MatchUpdateSchemas):
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if db_match is None:
        return None
    for key, value in match.dict().items():
        setattr(db_match, key, value)
    db.commit()
    db.refresh(db_match)
    return db_match


def delete_match(db: Session, match_id: int):
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if db_match is None:
        return None
    db.delete(db_match)
    db.commit()
    return db_match
