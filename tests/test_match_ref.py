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


class TestMatchRefSerialization(unittest.TestCase):

    def setUp(self):
        self.ref = MatchRef(series_id=1478874, match_id=1478914)

    # --- to_dict ---

    def test_to_dict_returns_dict(self):
        self.assertIsInstance(self.ref.to_dict(), dict)

    def test_to_dict_keys(self):
        d = self.ref.to_dict()
        self.assertIn("series_id", d)
        self.assertIn("match_id", d)

    def test_to_dict_values_are_int(self):
        d = self.ref.to_dict()
        self.assertEqual(d["series_id"], 1478874)
        self.assertEqual(d["match_id"], 1478914)
        self.assertIsInstance(d["series_id"], int)
        self.assertIsInstance(d["match_id"], int)

    # --- from_dict ---

    def test_from_dict_round_trips(self):
        d = self.ref.to_dict()
        restored = MatchRef.from_dict(d)
        self.assertEqual(restored.series_id, self.ref.series_id)
        self.assertEqual(restored.match_id, self.ref.match_id)

    def test_from_dict_accepts_string_values(self):
        ref = MatchRef.from_dict({"series_id": "1478874", "match_id": "1478914"})
        self.assertEqual(ref.series_id, 1478874)
        self.assertEqual(ref.match_id, 1478914)

    # --- to_csv_row ---

    def test_to_csv_row_returns_list(self):
        self.assertIsInstance(self.ref.to_csv_row(), list)

    def test_to_csv_row_values_are_strings(self):
        row = self.ref.to_csv_row()
        self.assertEqual(row, ["1478874", "1478914"])
        for v in row:
            self.assertIsInstance(v, str)

    def test_to_csv_row_order_is_series_then_match(self):
        row = self.ref.to_csv_row()
        self.assertEqual(row[0], "1478874")   # series_id first
        self.assertEqual(row[1], "1478914")   # match_id second

    # --- from_csv_row ---

    def test_from_csv_row_round_trips(self):
        row = self.ref.to_csv_row()
        restored = MatchRef.from_csv_row(row)
        self.assertEqual(restored.series_id, self.ref.series_id)
        self.assertEqual(restored.match_id, self.ref.match_id)

    def test_from_csv_row_accepts_tuple(self):
        ref = MatchRef.from_csv_row(("1478874", "1478914"))
        self.assertEqual(ref.series_id, 1478874)
        self.assertEqual(ref.match_id, 1478914)
