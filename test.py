# Insert data
from datetime import date

from sqlalchemy.orm import Session, joinedload

from src.database import engine, Base
from src.models import (
    Season,
    Team,
    Region,
    Organization,
    Tournament,
)


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

with Session(bind=engine) as session:

    region_Sumy = Region(name="Sumy", emblem="-*-")

    asotiation_AFS = Organization(
        name="AFS",
        full_name="-*-",
        description="-*-",
        logo="-*-",
        website="-*-",
        region_id=1,
    )

    tournament_champ = Tournament(
        name="Champ",
        full_name="-*-",
        logo="-*-",
        description="-*-",
        football_type="5646",
        website="-*-",
        organization_id=1,
    )
    tournament_cup = Tournament(
        name="Cup",
        full_name="-*-",
        logo="-*-",
        description="-*-",
        football_type="5646",
        website="-*-",
        organization_id=1,
    )

    season_23 = Season(
        name="Chemp 2023",
        start_date=date.today(),
        end_date=date.today(),
        year="2023",
        tournament_id=1,
    )
    season_24 = Season(
        name="Chemp 2024",
        start_date=date.today(),
        end_date=date.today(),
        year="2023",
        tournament_id=1,
    )

    team_1 = Team(
        name="team_1",
        full_name="5",
        city="7",
        foundation_year="2000",
        logo="-*-",
        description="-*-",
        stadium_id=0,
        region_id=1,
    )
    team_2 = Team(
        name="team_2",
        full_name="5",
        city="7",
        foundation_year="2001",
        logo="-*-",
        description="-*-",
        stadium_id=0,
        region_id=1,
    )
    team_3 = Team(
        name="team_3",
        full_name="5",
        city="7",
        foundation_year="2002",
        logo="-*-",
        description="-*-",
        stadium_id=0,
        region_id=1,
    )
    team_4 = Team(
        name="team_4",
        full_name="5",
        city="7",
        foundation_year="2002",
        logo="-*-",
        description="-*-",
        stadium_id=0,
        region_id=1,
    )

    season_23.teams_associations = [team_1, team_4]
    season_24.teams_associations = [team_1, team_2, team_3, team_4]

    session.add_all(
        [
            region_Sumy,
            asotiation_AFS,
            tournament_champ,
            tournament_cup,
            season_23,
            season_24,
            team_1,
            team_2,
            team_3,
            team_4,
        ]
    )

    session.commit()


# with Session(bind=engine) as session:
#     b1 = session.query(Season).where(Season.id == 1).one()
#     b2 = session.query(Season).where(Season.id == 2).one()
#     print("Region is: ", b1.name)
#     print("Region is: ", b2.name)


# with Session(bind=engine) as session:
#     b1 = (
#         session.query(Season)
#         .options(joinedload(Season.teams_associations))
#         .where(Season.id == 2)
#         .one()
#     )
#     for a in b1.teams_associations:
#         print(b1.name, " - ", a.name)

# with Session(bind=engine) as session:
#     season = session.query(Season).filter(Season.id == 1).first()
#     print(season.name)
#     team = session.query(Team).filter(Team.id == 1).first()
#     print(team)
#     season.teams_associations.append(team)
#     season.commit()

# with Session(bind=engine) as session:
#     season = session.query(Season).filter(Season.id == 1).first()
#     print(season.name, " - ", season.teams_associations)
