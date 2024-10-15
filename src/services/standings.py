from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, select
from models import Match, Group, Team, Season


async def get_calculate_standings(
    db: AsyncSession,
    season_id: int = None,
    season_slug: str = None,
    group_id: int = None,
):
    standings = {}

    # Створюємо запит
    stmt = (
        select(Match)
        .join(Season, Season.id == Match.season_id)
        .options(joinedload(Match.team_1), joinedload(Match.team_2))
    )

    if season_id is not None:
        stmt = stmt.filter(
            Match.season_id == season_id,
            Match.standing.is_(True),
            or_(Match.status == "played", Match.status == "technical_defeat"),
        )
    elif season_slug is not None:
        stmt = stmt.filter(
            Season.slug == season_slug,
            Match.standing.is_(True),
            or_(Match.status == "played", Match.status == "technical_defeat"),
        )
    else:
        return None  # або підняти виключення, якщо обидва параметри None

    if group_id is not None:
        stmt = stmt.filter(Match.group_id == group_id)

    # Виконуємо запит
    result = await db.execute(stmt)
    matches = result.scalars().all()

    for match in matches:
        # Перевіряємо наявність команди 1 ("господар матчу") в standings
        if match.stage_id not in standings:
            standings[match.stage_id] = {}

        if match.group_id not in standings[match.stage_id]:
            standings[match.stage_id][match.group_id] = {}

        if match.team1_id not in standings[match.stage_id][match.group_id]:
            standings[match.stage_id][match.group_id][match.team1_id] = {
                "team_slug": match.team_1.slug,
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
            }

        if match.team2_id not in standings[match.stage_id][match.group_id]:
            standings[match.stage_id][match.group_id][match.team2_id] = {
                "team_slug": match.team_2.slug,
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
            }

        # Оновлюємо статистику команд
        standings[match.stage_id][match.group_id][match.team1_id]["played"] += 1
        standings[match.stage_id][match.group_id][match.team2_id]["played"] += 1

        standings[match.stage_id][match.group_id][match.team1_id]["goals_for"] += int(
            match.team1_goals
        )
        standings[match.stage_id][match.group_id][match.team1_id][
            "goals_against"
        ] += int(match.team2_goals)
        standings[match.stage_id][match.group_id][match.team2_id]["goals_for"] += int(
            match.team2_goals
        )
        standings[match.stage_id][match.group_id][match.team2_id][
            "goals_against"
        ] += int(match.team1_goals)

        standings[match.stage_id][match.group_id][match.team1_id]["goal_difference"] = (
            standings[match.stage_id][match.group_id][match.team1_id]["goals_for"]
            - standings[match.stage_id][match.group_id][match.team1_id]["goals_against"]
        )
        standings[match.stage_id][match.group_id][match.team2_id]["goal_difference"] = (
            standings[match.stage_id][match.group_id][match.team2_id]["goals_for"]
            - standings[match.stage_id][match.group_id][match.team2_id]["goals_against"]
        )

        # Якщо матч завершився нічиєю
        if match.team1_goals == match.team2_goals:
            standings[match.stage_id][match.group_id][match.team1_id]["drawn"] += 1
            standings[match.stage_id][match.group_id][match.team2_id]["drawn"] += 1

            # Перевіряємо наявність післяматчевих пенальті
            if match.team1_penalty is not None and match.team2_penalty is not None:
                if match.team1_penalty > match.team2_penalty:
                    standings[match.stage_id][match.group_id][match.team1_id][
                        "points"
                    ] += 2
                    standings[match.stage_id][match.group_id][match.team2_id][
                        "points"
                    ] += 1
                else:
                    standings[match.stage_id][match.group_id][match.team1_id][
                        "points"
                    ] += 1
                    standings[match.stage_id][match.group_id][match.team2_id][
                        "points"
                    ] += 2
            else:
                standings[match.stage_id][match.group_id][match.team1_id]["points"] += 1
                standings[match.stage_id][match.group_id][match.team2_id]["points"] += 1

        elif match.team1_goals > match.team2_goals:
            standings[match.stage_id][match.group_id][match.team1_id]["won"] += 1
            standings[match.stage_id][match.group_id][match.team2_id]["lost"] += 1
            standings[match.stage_id][match.group_id][match.team1_id]["points"] += 3
        else:
            standings[match.stage_id][match.group_id][match.team2_id]["won"] += 1
            standings[match.stage_id][match.group_id][match.team1_id]["lost"] += 1
            standings[match.stage_id][match.group_id][match.team2_id]["points"] += 3

    standings_list = []
    for stage_id, groups in standings.items():
        for group_id, teams in groups.items():
            for team_id, stats in teams.items():
                standings_list.append(
                    {
                        "team_id": team_id,
                        "team_slug": stats["team_slug"],
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
                        "group_id": group_id,
                        "stage_id": stage_id,
                    }
                )

    standings_list.sort(
        key=lambda x: (
            x["stage_id"],
            x["group_id"],
            -x["points"],
            -x["goals_for"],
            -x["goal_difference"],
        )
    )

    return standings_list
