
class BatterPlaying:
    def __init__(self, batting_data):
        self.balls_faced = int(batting_data.get("balls_faced") or 0)
        self.batting_position = int(batting_data.get("batting_position") or 0)
        self.fours = int(batting_data.get("fours") or 0)
        self.innings_number = int(batting_data.get("innings_number") or 0)
        self.live_current = int(batting_data.get("live_current") or 0)
        self.is_batting = batting_data.get("live_current_name") == "striker"
        self.minutes = int(batting_data.get("minutes") or 0)
        self.player_id = int(batting_data.get("player_id") or 0)
        self.runs = int(batting_data.get("runs") or 0)
        self.sixes = int(batting_data.get("sixes") or 0)
        self.team_id = int(batting_data.get("team_id") or 0)
        self.strike_rate = batting_data.get("strike_rate") or "0.0"

    def __repr__(self):
        return f"BatterPlaying(Player ID: {self.player_id}, Runs: {self.runs}, Balls Faced: {self.balls_faced})"

class BowlerPlaying:
    def __init__(self, bowling_data):
        self.player_id = int(bowling_data.get("player_id") or 0)
        self.team_id = int(bowling_data.get("team_id") or 0)
        self.innings_number = int(bowling_data.get("innings_number") or 0)
        self.overs = float(bowling_data.get("overs") or 0.0)
        self.maidens = int(bowling_data.get("maidens") or 0)
        self.conceded = int(bowling_data.get("conceded") or 0)
        self.wickets = int(bowling_data.get("wickets") or 0)
        self.economy_rate = float(bowling_data.get("economy_rate") or 0.0)
        self.noballs = int(bowling_data.get("noballs") or 0)
        self.wides = int(bowling_data.get("wides") or 0)
        self.live_current = int(bowling_data.get("live_current") or 0)
        self.is_bowling = bowling_data.get("live_current_name", "") == "current bowler"

    def __repr__(self):
        return f"BowlerPlaying(Player ID: {self.player_id}, Overs: {self.overs}, Wickets: {self.wickets}, Economy: {self.economy_rate})"

class Batsman:
    def __init__(self, data):
        self.balls_faced = int(data.get("balls_faced") or 0)
        self.hand = data.get("hand", "")
        self.image_path = data.get("image_path", "")
        self.name = data.get("known_as", "")
        self.notout = int(data.get("notout") or 0)
        self.player_id = int(data.get("player_id") or 0)
        self.popular_name = data.get("popular_name", "")
        self.position = int(data.get("position") or 0)
        self.position_group = data.get("position_group", "")
        self.runs = int(data.get("runs") or 0)

    def __str__(self):
        return (f"Batsman {self.known_as} (ID: {self.player_id}): "
                f"Runs: {self.runs}, Balls Faced: {self.balls_faced}, "
                f"Position: {self.position} ({self.position_group}), "
                f"Not Out: {'Yes' if self.notout else 'No'}")

class Bowler:
    def __init__(self, data):
        self.conceded = int(data.get("conceded") or 0)
        self.hand = data.get("hand", "")
        self.image_path = data.get("image_path", "")
        self.name = data.get("known_as", "")
        self.maidens = int(data.get("maidens") or 0)
        self.overs = float(data.get("overs") or 0.0)
        self.pacespin = data.get("pacespin", "")
        self.player_id = int(data.get("player_id") or 0)
        self.popular_name = data.get("popular_name", "")
        self.position = int(data.get("position") or 0)
        self.wickets = int(data.get("wickets") or 0)
        self.is_bowling = data.get("live_current_name", "") == "current bowler"
        self.is_previous = data.get("live_current_name", "") == "previous bowler"

    def __str__(self):
        return (f"Bowler {self.known_as} (ID: {self.player_id}): "
                f"Wickets: {self.wickets}, Overs: {self.overs}, Runs Conceded: {self.conceded}, "
                f"Maidens: {self.maidens}, Bowling Style: {self.pacespin}, "
                f"Hand: {self.hand}, Position: {self.position}, "
                f"Current Status: {self.live_current_name}")

class Inning:
    def __init__(self, data):
        self.ball_limit = int(data.get("ball_limit") or 0)
        self.balls = int(data.get("balls") or 0)
        self.batted = int(data.get("batted") or 0)
        self.batting_team_id = int(data.get("batting_team_id") or 0)
        self.bowling_team_id = int(data.get("bowling_team_id") or 0)
        self.bpo = int(data.get("bpo") or 6)
        self.byes = int(data.get("byes") or 0)
        self.event = int(data.get("event") or 0)
        self.event_name = data.get("event_name", "")
        self.extras = int(data.get("extras") or 0)
        self.number = int(data.get("innings_number") or 0)
        self.numth = data.get("innings_numth", "")
        self.lead = int(data.get("lead") or 0)
        self.legbyes = int(data.get("legbyes") or 0)
        self.live_current = int(data.get("live_current") or 0)
        self.live_current_name = data.get("live_current_name", "")
        self.minutes = data.get("minutes")
        self.noballs = int(data.get("noballs") or 0)
        self.old_penalty_or_bonus = int(data.get("old_penalty_or_bonus") or 0)
        self.over_limit = float(data.get("over_limit") or 0.0)
        self.over_limit_run_rate = float(data.get("over_limit_run_rate") or 0.0)
        self.over_split_limit = float(data.get("over_split_limit") or 0.0)
        self.overs = float(data.get("overs") or 0.0)
        self.overs_docked = int(data.get("overs_docked") or 0)
        self.penalties = int(data.get("penalties") or 0)
        self.penalties_field_end = int(data.get("penalties_field_end") or 0)
        self.penalties_field_start = int(data.get("penalties_field_start") or 0)
        self.run_rate = float(data.get("run_rate") or 0.0)
        self.runs = int(data.get("runs") or 0)
        self.target = int(data.get("target") or 0)
        self.wickets = int(data.get("wickets") or 0)
        self.wides = int(data.get("wides") or 0)

    def __str__(self):
        return (f"Innings {self.innings_number} ({self.innings_numth}): "
                f"{self.batting_team_id} vs {self.bowling_team_id}, "
                f"Runs: {self.runs}, Wickets: {self.wickets}, Overs: {self.overs}, "
                f"Run Rate: {self.run_rate}, Event: {self.event_name}")

class Player:
    def __init__(self, player_data):
        self.age_days = int(player_data.get("age_days") or 0)
        self.age_years = int(player_data.get("age_years") or 0)
        self.alpha_name = player_data.get("alpha_name")
        self.batting_hand = player_data.get("batting_hand")
        self.batting_style = player_data.get("batting_style")
        self.batting_style_long = player_data.get("batting_style_long")
        self.bowling_hand = player_data.get("bowling_hand")
        self.bowling_pacespin = player_data.get("bowling_pacespin")
        self.bowling_style = player_data.get("bowling_style")
        self.bowling_style_long = player_data.get("bowling_style_long")
        self.captain = int(player_data.get("captain") or 0)
        self.card_long = player_data.get("card_long")
        self.card_qualifier = player_data.get("card_qualifier")
        self.card_short = player_data.get("card_short")
        self.dob = player_data.get("dob")
        self.image_id = int(player_data.get("image_id") or 0)
        self.keeper = int(player_data.get("keeper") or 0)
        self.name = player_data.get("known_as")
        self.match_player_id = int(player_data.get("match_player_id") or 0)
        self.mobile_name = player_data.get("mobile_name")
        self.object_id = int(player_data.get("object_id") or 0)
        self.id = int(player_data.get("player_id") or 0)
        self.name_id = player_data.get("player_name_id", "0")
        self.primary_role = player_data.get("player_primary_role")
        self.style_id = int(player_data.get("player_style_id") or 0)
        self.p_type = int(player_data.get("player_type") or 0)
        self.type_name = player_data.get("player_type_name")
        self.popular_name = player_data.get("popular_name")
        self.portrait_alt_id = player_data.get("portrait_alt_id")
        self.portrait_object_id = int(player_data.get("portrait_object_id") or 0)
        self.status_id = int(player_data.get("status_id") or 0)
    
    def __repr__(self):
        return f"Player({self.known_as}, {self.batting_hand}, {self.bowling_style_long})"

class Team:
    def __init__(self, team_data):
        self.batsmen_in_side = int(team_data.get("batsmen_in_side") or 0)
        self.content_id = int(team_data.get("content_id") or 0)
        self.country_id = int(team_data.get("country_id") or 0)
        self.fielders_in_side = int(team_data.get("fielders_in_side") or 0)
        self.image_id = int(team_data.get("image_id") or 0)
        self.logo_alt_id = team_data.get("logo_alt_id")
        self.logo_espncdn = team_data.get("logo_espncdn")
        self.logo_height = int(team_data.get("logo_height") or 0)
        self.logo_image_height = int(team_data.get("logo_image_height") or 0)
        self.logo_image_path = team_data.get("logo_image_path")
        self.logo_image_width = int(team_data.get("logo_image_width") or 0)
        self.logo_object_id = int(team_data.get("logo_object_id") or 0)
        self.logo_path = team_data.get("logo_path")
        self.logo_width = int(team_data.get("logo_width") or 0)
        self.object_id = int(team_data.get("object_id") or 0)
        self.players = [Player(p) for p in team_data.get("player", [])]
        self.players_in_side = int(team_data.get("players_in_side") or 0)
        self.site_id = int(team_data.get("site_id") or 0)
        self.abbreviation = team_data.get("team_abbreviation")
        self.filename = team_data.get("team_filename")
        self.general_name = team_data.get("team_general_name")
        self.id = int(team_data.get("team_id") or 0)
        self.name = team_data.get("team_name")
        self.short_name = team_data.get("team_short_name")
        self.url_component = team_data.get("url_component")
    
    def __repr__(self):
        return f"Team({self.team_name}, Players: {len(self.players)})"

class Live:
    def __init__(self, json_data):
        self.batting = [ BatterPlaying(data) for data in json_data['batting'] ]
        self.bowling = [ BowlerPlaying(data) for data in json_data['bowling'] ]
        self.status = json_data['status']
        self.is_finished = True if (json_data['event_name']=='complete') else False
        self.ball_limit = int(json_data.get('innings', {}).get('ball_limit') or 0)
        self.balls = int(json_data.get('innings', {}).get('balls') or 0)
        self.current_inning = int(json_data.get('innings', {}).get('innings_number') or 0)
        self.batting_team_id = int(json_data.get('innings', {}).get('batting_team_id') or 0)
        self.bowling_team_id = int(json_data.get('innings', {}).get('bowling_team_id') or 0)
        self.overs = float(json_data.get('innings', {}).get('overs') or 0.0)
        self.remaining_balls = int(json_data.get('innings', {}).get('remaining_balls') or 0)
        self.rrr = float(json_data.get('innings', {}).get('required_run_rate') or 0.0)
        self.crr = float(json_data.get('innings', {}).get('run_rate') or 0.0)
        self.runs = int(json_data.get('innings', {}).get('runs') or 0)
        self.target = int(json_data.get('innings', {}).get('target') or 0)
        self.team_id = int(json_data.get('innings', {}).get('team_id') or 0)
        self.wickets = int(json_data.get('innings', {}).get('wickets') or 0)