from sqlalchemy import desc, or_, func
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
)
from validation import match as schemas


# def get_match(db: Session, match_id: int):
#     # Створюємо аліаси для таблиці Team
#     team1_alias = aliased(Team)
#     team2_alias = aliased(Team)
#
#     result = (
#         db.query(
#             Match.id.label("match_id"),
#             Tournament.logo.label("tournament_logo"),
#             Season.name.label("season_name"),
#             Season.year.label("season_year"),
#             Stage.name.label("stage_name"),
#             Round.name.label("round_name"),
#             func.strftime("%d-%m-%Y", func.datetime(Match.event, "unixepoch")).label(
#                 "event"
#             ),
#             Stadium.name.label("stadium_name"),
#             Stadium.city.label("stadium_city"),
#             Match.team1_id.label("team1_id"),
#             team1_alias.logo.label("team1_logo"),
#             team1_alias.name.label("team1_name"),
#             team1_alias.city.label("team1_city"),
#             Match.team1_goals,
#             Match.team2_goals,
#             Match.team1_penalty,
#             Match.team2_penalty,
#             Match.team2_id.label("team2_id"),
#             team2_alias.name.label("team2_name"),
#             team2_alias.city.label("team2_city"),
#             team2_alias.logo.label("team2_logo"),
#         )
#         .join(Season, Season.id == Match.season_id)
#         .join(Tournament, Tournament.id == Season.tournament_id)
#         .join(Stadium, Stadium.id == Match.stadium_id)
#         .join(team1_alias, team1_alias.id == Match.team1_id)
#         .join(team2_alias, team2_alias.id == Match.team2_id)
#         .join(Round, Round.id == Match.round_id)
#         .join(Stage, Stage.id == Match.stage_id)
#         .filter(Match.id == match_id)
#         .first()
#     )
#
#     return result


def get_match(db: Session, match_id: int):
    # Створюємо аліаси для таблиці Team
    team1_alias = aliased(Team)
    team2_alias = aliased(Team)

    result = (
        db.query(
            Match.id.label("match_id"),
            Match.team1_id.label("team1_id"),
            Match.team2_id.label("team2_id"),
            func.strftime("%d-%m-%Y", func.datetime(Match.event, "unixepoch")).label(
                "event"
            ),
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
        )
        .join(Season, Season.id == Match.season_id)
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Stadium, Stadium.id == Match.stadium_id)
        .join(team1_alias, team1_alias.id == Match.team1_id)
        .join(team2_alias, team2_alias.id == Match.team2_id)
        .filter(Match.id == match_id)
        .first()
    )

    return result


def get_match_info(db: Session, match_id: int):
    match_info = (
        db.query(
            PositionRole.player_number,
            PositionRole.type_role,
            Person.id,
            Person.name,
            Person.surname,
            Person.lastname,
            MatchProperties.protocol,
            MatchProperties.starting,
            MatchProperties.replacement,
            MatchProperties.minutes,
            MatchProperties.goals,
            MatchProperties.goals_penalty,
            MatchProperties.own_goal,
            MatchProperties.yellow_card,
            MatchProperties.second_yellow_card,
            MatchProperties.red_card,
            TeamPerson.team_id,
            MatchProperties.match_id,
        )
        .join(TeamPerson, TeamPerson.id == MatchProperties.player_id)
        .join(Person, Person.id == TeamPerson.person_id)
        .join(PositionRole, PositionRole.team_person_id == TeamPerson.id)
        .filter(
            MatchProperties.match_id == match_id,
            PositionRole.position_id.in_([9, 10]),
            PositionRole.active == True,  # Використовуємо True для булевих значень
        )
        .all()
    )
    return match_info


def get_matches(db: Session):
    return db.query(Match).order_by(desc(Match.event))


def get_matches_season(db: Session, season_id: int):
    return (
        db.query(Match).filter(Match.season_id == season_id).order_by(desc(Match.event))
    )


def season_matches(db: Session, season_id: int):
    matches = (db.query(Match).filter(Match.season_id == season_id)).order_by(
        desc(Match.event)
    )

    return matches


def get_matches_season(db: Session, season_id: int):
    db_match = db.query(Match).filter(Match.season_id == season_id).all()
    return db_match


def get_matches_team(db: Session, team_id: int):
    """Всі матчі певної команди"""
    db_match = (
        db.query(Match)
        .filter(or_(Match.team1_id == team_id, Match.team2_id == team_id))
        .order_by(desc(Match.event))
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
