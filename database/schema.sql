-- 1. Teams Table
CREATE TABLE IF NOT EXISTS Teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Venues Table
CREATE TABLE IF NOT EXISTS Venues (
    venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    capacity INTEGER
);

-- 3. Players Table
CREATE TABLE IF NOT EXISTS Players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(150) NOT NULL,
    team_id INTEGER,
    playing_role VARCHAR(50),
    batting_style VARCHAR(50),
    bowling_style VARCHAR(50),
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);

-- 4. Series Table
CREATE TABLE IF NOT EXISTS Series (
    series_id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name VARCHAR(200) NOT NULL,
    host_country VARCHAR(100),
    match_type VARCHAR(50),
    start_date DATE,
    total_matches INTEGER
);

-- 5. Matches Table
CREATE TABLE IF NOT EXISTS Matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER,
    match_description VARCHAR(200),
    format VARCHAR(20),
    venue_id INTEGER,
    match_date DATE,
    team1_id INTEGER,
    team2_id INTEGER,
    toss_winner_id INTEGER,
    toss_decision VARCHAR(20),
    match_winner_id INTEGER,
    victory_margin INTEGER,
    victory_type VARCHAR(20),
    FOREIGN KEY (series_id) REFERENCES Series(series_id),
    FOREIGN KEY (venue_id) REFERENCES Venues(venue_id),
    FOREIGN KEY (team1_id) REFERENCES Teams(team_id),
    FOREIGN KEY (team2_id) REFERENCES Teams(team_id),
    FOREIGN KEY (toss_winner_id) REFERENCES Teams(team_id),
    FOREIGN KEY (match_winner_id) REFERENCES Teams(team_id)
);

-- 6. Player_Match_Stats Table
CREATE TABLE IF NOT EXISTS Player_Match_Stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    player_id INTEGER,
    batting_position INTEGER,
    runs_scored INTEGER DEFAULT 0,
    balls_faced INTEGER DEFAULT 0,
    overs_bowled REAL DEFAULT 0.0,
    runs_conceded INTEGER DEFAULT 0,
    wickets_taken INTEGER DEFAULT 0,
    catches INTEGER DEFAULT 0,
    stumpings INTEGER DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES Matches(match_id),
    FOREIGN KEY (player_id) REFERENCES Players(player_id)
);