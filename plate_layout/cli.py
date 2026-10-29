"""Command-line interface for plate-layout."""
import argparse
import json

from .core import Plate


def main(argv=None):
    ap = argparse.ArgumentParser(prog="plate-layout", description="Design a multi-well plate layout.")
    ap.add_argument("-s", "--size", type=int, default=96)
    ap.add_argument("--samples", help="comma-separated sample names, or @file.txt with one per line")
    ap.add_argument("-r", "--replicates", type=int, default=3)
    ap.add_argument("--control", action="append", default=[], help="NAME=WELL,WELL (fixed control positions)")
    ap.add_argument("--blank", action="append", default=[], help="wells for blanks")
    ap.add_argument("--by", choices=["row", "column"], default="row")
    ap.add_argument("--randomize", action="store_true")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--exclude-edges", action="store_true", help="leave outer wells empty (evaporation edge effect)")
    ap.add_argument("-o", "--output", help="CSV layout file")
    args = ap.parse_args(argv)
    plate = Plate(args.size, args.exclude_edges)
    try:
        for spec in args.control:
            name, _, wells = spec.partition("=")
            for i, w in enumerate(wells.split(","), 1):
                plate.place(w, name, "control", i)
        for w in args.blank:
            plate.place(w, "blank", "blank")
        samples = []
        if args.samples:
            if args.samples.startswith("@"):
                with open(args.samples[1:], encoding="utf-8") as fh:
                    samples = [l.strip() for l in fh if l.strip()]
            else:
                samples = [s.strip() for s in args.samples.split(",") if s.strip()]
        plate.fill(samples, args.replicates, args.by, args.randomize, args.seed)
    except ValueError as exc:
        print("error: %s" % exc)
        return 1
    print(plate.ascii_map())
    print(json.dumps(plate.summary()))
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as fh:
            fh.write(plate.to_csv())
    return 0
