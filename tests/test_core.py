import csv
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from plate_layout.cli import main
from plate_layout.core import Plate, parse_well, well_name


class WellTests(unittest.TestCase):
    def test_names(self):
        self.assertEqual(well_name(0, 0), "A1")
        self.assertEqual(well_name(7, 11), "H12")
        self.assertEqual(parse_well("p24"), (15, 23))
        with self.assertRaises(ValueError):
            parse_well("Z99")


class PlateTests(unittest.TestCase):
    def test_sequential_fill_by_row_and_column(self):
        p = Plate(96)
        p.fill(["S1", "S2"], replicates=3)
        self.assertEqual([r["sample"] for r in p.table()[:7]], ["S1", "S1", "S1", "S2", "S2", "S2", ""])
        q = Plate(96)
        q.fill(["S1"], 2, by="column")
        self.assertEqual(q.wells[(1, 0)]["sample"], "S1")

    def test_controls_and_collisions(self):
        p = Plate(96)
        p.place("A1", "neg", "control")
        with self.assertRaises(ValueError):
            p.place("a1", "x")
        with self.assertRaises(ValueError):
            p.place("I1", "x")                      # row I does not exist on a 96-well plate
        p.fill(["S1"], 2)
        self.assertEqual(p.wells[(0, 1)]["sample"], "S1")

    def test_edge_exclusion_and_capacity(self):
        p = Plate(96, exclude_edges=True)
        self.assertEqual(len(p.free_wells()), 60)
        p.fill(["S"], 60)
        self.assertNotIn((0, 0), p.wells)
        with self.assertRaises(ValueError):
            Plate(96).fill(["S"], 97)
        with self.assertRaises(ValueError):
            Plate(100)

    def test_randomization_reproducible(self):
        a, b = Plate(96), Plate(96)
        a.fill(list("ABCD"), 3, randomize=True, seed=7)
        b.fill(list("ABCD"), 3, randomize=True, seed=7)
        self.assertEqual(a.wells, b.wells)
        self.assertNotEqual(sorted(a.wells)[:12], [(0, c) for c in range(12)])

    def test_exports(self):
        p = Plate(24)
        p.fill(["X"], 2)
        rows = list(csv.DictReader(io.StringIO(p.to_csv())))
        self.assertEqual(len(rows), 24)
        self.assertEqual(rows[0]["sample"], "X")
        self.assertIn(" A    X     X  ", p.ascii_map())
        self.assertEqual(p.summary()["by_type"], {"sample": 2})

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "layout.csv")
            with redirect_stdout(io.StringIO()) as buf:
                code = main(["--samples", "s1,s2,s3", "-r", "2", "--control", "pos=H11,H12", "--blank", "H1",
                             "--randomize", "--seed", "1", "-o", out])
            self.assertEqual(code, 0)
            self.assertIn('"used": 9', buf.getvalue())
            with open(out, encoding="utf-8") as fh:
                self.assertIn("H12,H,12,pos,control,2", fh.read())


if __name__ == "__main__":
    unittest.main()
