from espncricinfo.match import Match
from espncricinfo.player import Player
from espncricinfo.series import Series
from espncricinfo.summary import Summary

class TestObjects:
    def test_match(self):
        match = Match('1490425')
        assert match.home_team == "IND-W"

    def test_player(self):    
        player = Player('883405')
        assert player.name == "Jemimah Rodrigues"

    def test_series(self):
        series = Series('1478193')
        assert series.short_name == "ICC Women's World Cup"

    def test_summary(self):
        summary = Summary()
        assert "1490429" in summary.match_ids
