from .ref_event import RefEvent
from .region import Region
from .association import Association
from .organization import Organization
from .tournament import Tournament
from .season import Season
from .team import Team
from .season_team_assotiation import TeamSeason
from .stadium import Stadium
from .news import News
from .match import Match
from .person import Person
from .position import Position
from .position_role import PositionRole
from .team_person_assotiation import TeamPerson
from .group import Group
from .stage import Stage
from .round import Round
from .match_properties import MatchProperties
from .match_event import MatchEvent
from .player_role import PlayerRole
from .contacts import Contact
from .users import User
from .district import District
from .football_type import FootbalType

MODELS = [
    Region,
    Association,
    Organization,
    News,
    Tournament,
    Season,
    Team,
    TeamSeason,
    Stadium,
    Match,
    Person,
    Position,
    PositionRole,
    TeamPerson,
    Group,
    Stage,
    Round,
    MatchProperties,
    PlayerRole,
    RefEvent,
    MatchEvent,
    Contact,
    User,
    District,
    FootbalType,
]
