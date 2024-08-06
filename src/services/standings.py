from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Match, Group, Team


def get_calculate_standings(db: Session, season_id: int, group_id: int = None):
    standings = {}

    # Фільтруємо матчі за season_id, статусом і standing
    matches_query = db.query(Match).filter(
        Match.season_id == season_id,
        Match.standing.is_(True),
        or_(Match.status == "played", Match.status == "technical_defeat"),
    )

    # Якщо group_id не None, то додатково фільтруємо за group_id
    if group_id is not None:
        matches_query = matches_query.filter(Match.group_id == group_id)

    matches = matches_query.all()

    for match in matches:
        # Перевіряємо наявність команди 1 в standings
        if match.team1_id not in standings:
            standings[match.team1_id] = {
                "team_name": match.team_1.name,
                "team_city": match.team_1.city,
                "logo": match.team_1.logo,
                "played": 0,
                "won": 0,
                "drawn": 0,
                "lost": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,
                "points": 0,
                "group_id": match.group_id,  # Додаємо group_id
            }
        # Перевіряємо наявність команди 2 в standings
        if match.team2_id not in standings:
            standings[match.team2_id] = {
                "team_name": match.team_2.name,
                "team_city": match.team_2.city,
                "logo": match.team_2.logo,
                "played": 0,
                "won": 0,
                "drawn": 0,
                "lost": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,
                "points": 0,
                "group_id": match.group_id,  # Додаємо group_id
            }

        # Оновлюємо статистику команд
        standings[match.team1_id]["played"] += 1
        standings[match.team2_id]["played"] += 1

        standings[match.team1_id]["goals_for"] += int(match.team1_goals)
        standings[match.team1_id]["goals_against"] += int(match.team2_goals)
        standings[match.team2_id]["goals_for"] += int(match.team2_goals)
        standings[match.team2_id]["goals_against"] += int(match.team1_goals)

        standings[match.team1_id]["goal_difference"] = (
            standings[match.team1_id]["goals_for"]
            - standings[match.team1_id]["goals_against"]
        )
        standings[match.team2_id]["goal_difference"] = (
            standings[match.team2_id]["goals_for"]
            - standings[match.team2_id]["goals_against"]
        )

        if match.team1_goals > match.team2_goals:
            standings[match.team1_id]["won"] += 1
            standings[match.team2_id]["lost"] += 1
            standings[match.team1_id]["points"] += 3
        elif match.team1_goals < match.team2_goals:
            standings[match.team2_id]["won"] += 1
            standings[match.team1_id]["lost"] += 1
            standings[match.team2_id]["points"] += 3
        else:
            standings[match.team1_id]["drawn"] += 1
            standings[match.team2_id]["drawn"] += 1
            standings[match.team1_id]["points"] += 1
            standings[match.team2_id]["points"] += 1

    standings_list = [
        {
            "team_id": team_id,
            "team_name": stats["team_name"],
            "team_city": stats["team_city"],
            "logo": stats["logo"],
            "played": stats["played"],
            "won": stats["won"],
            "drawn": stats["drawn"],
            "lost": stats["lost"],
            "goals_for": stats["goals_for"],
            "goals_against": stats["goals_against"],
            "goal_difference": stats["goal_difference"],
            "points": stats["points"],
            "group_id": stats["group_id"],  # Додаємо group_id до списку
        }
        for team_id, stats in standings.items()
    ]

    standings_list.sort(
        key=lambda x: (-x["points"], -x["goal_difference"], -x["goals_for"])
    )

    return standings_list
