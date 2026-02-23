import unittest
from espncricinfo.match_ref import MatchRef


class TestMatchRefFields(unittest.TestCase):

    def test_fields_stored_as_int(self):
        ref = MatchRef(series_id=1478874, match_id=1478914)
        self.assertEqual(ref.series_id, 1478874)
        self.assertEqual(ref.match_id, 1478914)
        self.assertIsInstance(ref.series_id, int)
        self.assertIsInstance(ref.match_id, int)

    def test_string_inputs_coerced_to_int(self):
        ref = MatchRef(series_id="1478874", match_id="1478914")
        self.assertIsInstance(ref.series_id, int)
        self.assertIsInstance(ref.match_id, int)

    def test_tuple_unpacking(self):
        ref = MatchRef(series_id=1478874, match_id=1478914)
        series_id, match_id = ref
        self.assertEqual(series_id, 1478874)
        self.assertEqual(match_id, 1478914)

    def test_repr(self):
        ref = MatchRef(series_id=1478874, match_id=1478914)
        self.assertIn("1478874", repr(ref))
        self.assertIn("1478914", repr(ref))
