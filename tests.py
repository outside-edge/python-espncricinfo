import unittest
from espncricinfo.match import Match

class TestMatchMethods(unittest.TestCase):

    def setUp(self):
        id=857713
        self.match = Match(id)

    def test_match_description(self):
        self.assertEqual(self.match.description, 'Caribbean Premier League, 6th Match: St Lucia Zouks v Guyana Amazon Warriors at Gros Islet, Jun 26, 2015')

    def test_match_match_class(self):
        self.assertEqual(self.match.match_class, 'Twenty20')

    def test_toss_winner(self):
        self.assertEqual(self.match.toss_winner, '5153')

if __name__ == '__main__':
    unittest.main()
