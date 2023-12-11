CREATE TABLE collections (
    name TEXT,
    object_type TEXT,
    uuid TEXT,
    PRIMARY KEY (uuid)
);

CREATE TABLE players (
    name TEXT,
    sex TEXT,
    birthday TEXT,
    country TEXT,
    title TEXT,
    rating INTEGER,
    uuid TEXT,
    uuid_associate TEXT,
    FOREIGN KEY (uuid_associate) REFERENCES collections(uuid) ON DELETE CASCADE,
    PRIMARY KEY (uuid, uuid_associate)
);

CREATE TABLE tournaments (
    mode TEXT,
    name TEXT,
    participants INTEGER,
    parameters TEXT,
    variables TEXT,
    participant_order TEXT,
    uuid TEXT,
    uuid_associate TEXT,
    FOREIGN KEY (uuid_associate) REFERENCES collections(uuid) ON DELETE CASCADE,
    PRIMARY KEY (uuid)
);

CREATE TABLE teams (
    name TEXT,
    members INTEGER,
    uuid TEXT,
    uuid_associate TEXT,
    FOREIGN KEY (uuid_associate) REFERENCES collections(uuid) ON DELETE CASCADE,
    PRIMARY KEY (uuid, uuid_associate)
);

CREATE TABLE ms_tournaments (
    name TEXT,
    participants INTEGER,
    stages_advance_lists TEXT,
    draw_lots INTEGER,
    stage INTEGER,
    tournament_order TEXT,
    uuid TEXT,
    uuid_associate TEXT,
    FOREIGN KEY (uuid_associate) REFERENCES collections(uuid) ON DELETE CASCADE,
    PRIMARY KEY (uuid)
);

CREATE TABLE players_to_teams (
    uuid_player TEXT,
    uuid_associate_player TEXT,
    uuid_team TEXT,
    uuid_associate_team TEXT,
    member_order INTEGER,
    FOREIGN KEY (uuid_player, uuid_associate_player) REFERENCES players(uuid, uuid_associate) ON DELETE CASCADE,
    FOREIGN KEY (uuid_team, uuid_associate_team) REFERENCES teams(uuid, uuid_associate) ON DELETE CASCADE,
    PRIMARY KEY (uuid_player, uuid_team)
);

CREATE TABLE tournaments_players (
    name TEXT,
    sex TEXT,
    birthday TEXT,
    country TEXT,
    title TEXT,
    rating INTEGER,
    uuid TEXT,
    uuid_associate TEXT,
    FOREIGN KEY (uuid_associate) REFERENCES tournaments(uuid) ON DELETE CASCADE,
    PRIMARY KEY (uuid, uuid_associate)
);

CREATE TABLE tournaments_teams (
    name TEXT,
    members INTEGER,
    uuid TEXT,
    uuid_associate TEXT,
    FOREIGN KEY (uuid_associate) REFERENCES tournaments(uuid) ON DELETE CASCADE,
    PRIMARY KEY (uuid, uuid_associate)
);

CREATE TABLE tournaments_players_to_teams (
    uuid_player TEXT,
    uuid_associate_player TEXT,
    uuid_team TEXT,
    uuid_associate_team TEXT,
    member_order INTEGER,
    FOREIGN KEY (uuid_player, uuid_associate_player) REFERENCES tournaments_players(uuid, uuid_associate) ON DELETE CASCADE,
    FOREIGN KEY (uuid_team, uuid_associate_team) REFERENCES tournaments_teams(uuid, uuid_associate) ON DELETE CASCADE,
    PRIMARY KEY (uuid_player, uuid_associate_player, uuid_team, uuid_associate_team)
);

CREATE TABLE ms_tournaments_tournaments (
    mode TEXT,
    name TEXT,
    participants INTEGER,
    parameters TEXT,
    variables TEXT,
    participant_order TEXT,
    uuid TEXT,
    uuid_associate TEXT,
    FOREIGN KEY (uuid_associate) REFERENCES ms_tournaments(uuid) ON DELETE CASCADE,
    PRIMARY KEY (uuid, uuid_associate)
);

CREATE TABLE ms_tournaments_players (
    name TEXT,
    sex TEXT,
    birthday TEXT,
    country TEXT,
    title TEXT,
    rating INTEGER,
    uuid TEXT,
    uuid_associate TEXT,
    FOREIGN KEY (uuid_associate) REFERENCES ms_tournaments(uuid) ON DELETE CASCADE,
    PRIMARY KEY (uuid, uuid_associate)
);

CREATE TABLE ms_tournaments_teams (
    name TEXT,
    members INTEGER,
    uuid TEXT,
    uuid_associate TEXT,
    FOREIGN KEY (uuid_associate) REFERENCES ms_tournaments(uuid) ON DELETE CASCADE,
    PRIMARY KEY (uuid, uuid_associate)
);

CREATE TABLE ms_tournaments_players_to_teams (
    uuid_player TEXT,
    uuid_associate_player TEXT,
    uuid_team TEXT,
    uuid_associate_team TEXT,
    member_order INTEGER,
    FOREIGN KEY (uuid_player, uuid_associate_player) REFERENCES ms_tournaments_players(uuid, uuid_associate) ON DELETE CASCADE,
    FOREIGN KEY (uuid_team, uuid_associate_team) REFERENCES ms_tournaments_teams(uuid, uuid_associate) ON DELETE CASCADE,
    PRIMARY KEY (uuid_player, uuid_associate_player, uuid_team, uuid_associate_team)
);
