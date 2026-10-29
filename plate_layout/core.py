"""Plate model, automatic layout of samples (sequential or randomized) and exports."""
import csv
import io
import random
import re
import string

FORMATS = {6: (2, 3), 12: (3, 4), 24: (4, 6), 48: (6, 8), 96: (8, 12), 384: (16, 24)}


def well_name(row, col):
    return "%s%d" % (string.ascii_uppercase[row], col + 1)


def parse_well(name):
    m = re.fullmatch(r"([A-Pa-p])(\d{1,2})", name.strip())
    if not m:
        raise ValueError("bad well name %r" % name)
    return string.ascii_uppercase.index(m.group(1).upper()), int(m.group(2)) - 1


class Plate:
    def __init__(self, size=96, exclude_edges=False):
        if size not in FORMATS:
            raise ValueError("plate size must be one of %s" % sorted(FORMATS))
        self.size = size
        self.rows, self.cols = FORMATS[size]
        self.wells = {}            # (r, c) -> dict(sample, type, replicate)
        self.blocked = set()
        if exclude_edges:
            for r in range(self.rows):
                for c in range(self.cols):
                    if r in (0, self.rows - 1) or c in (0, self.cols - 1):
                        self.blocked.add((r, c))

    def _check(self, rc):
        r, c = rc
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise ValueError("well %s is outside a %d-well plate" % (well_name(r, c), self.size))

    def place(self, well, sample, kind="sample", replicate=1):
        rc = parse_well(well) if isinstance(well, str) else well
        self._check(rc)
        if rc in self.wells:
            raise ValueError("well %s already holds %s" % (well_name(*rc), self.wells[rc]["sample"]))
        self.wells[rc] = {"sample": sample, "type": kind, "replicate": replicate}

    def free_wells(self, by="row"):
        cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        if by == "column":
            cells.sort(key=lambda rc: (rc[1], rc[0]))
        return [rc for rc in cells if rc not in self.wells and rc not in self.blocked]

    def fill(self, samples, replicates=1, by="row", randomize=False, seed=None, kind="sample", group_replicates=True):
        """Place every sample `replicates` times in free wells. Randomization shuffles positions (seeded)."""
        items = [(s, i + 1) for s in samples for i in range(replicates)] if group_replicates else \
            [(s, i + 1) for i in range(replicates) for s in samples]
        free = self.free_wells(by)
        if len(items) > len(free):
            raise ValueError("need %d wells but only %d are free" % (len(items), len(free)))
        targets = free[:len(items)]
        if randomize:
            rng = random.Random(seed)
            targets = rng.sample(free, len(items))
        for (s, rep), rc in zip(items, targets):
            self.place(rc, s, kind, rep)
        return len(items)

    def table(self):
        out = []
        for r in range(self.rows):
            for c in range(self.cols):
                w = self.wells.get((r, c))
                status = "blocked" if (r, c) in self.blocked and not w else ("used" if w else "empty")
                out.append({"well": well_name(r, c), "row": string.ascii_uppercase[r], "column": c + 1,
                            "sample": w["sample"] if w else "", "type": w["type"] if w else status,
                            "replicate": w["replicate"] if w else ""})
        return out

    def to_csv(self):
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=["well", "row", "column", "sample", "type", "replicate"], lineterminator="\n")
        w.writeheader()
        w.writerows(self.table())
        return buf.getvalue()

    def ascii_map(self, width=6):
        head = "    " + "".join(str(c + 1).center(width) for c in range(self.cols))
        lines = [head]
        for r in range(self.rows):
            cells = []
            for c in range(self.cols):
                w = self.wells.get((r, c))
                label = "xx" if (r, c) in self.blocked and not w else (w["sample"][:width - 1] if w else ".")
                cells.append(label.center(width))
            lines.append(" %s  %s" % (string.ascii_uppercase[r], "".join(cells)))
        return "\n".join(lines)

    def summary(self):
        counts = {}
        for w in self.wells.values():
            counts[w["type"]] = counts.get(w["type"], 0) + 1
        return {"size": self.size, "used": len(self.wells), "blocked": len(self.blocked),
                "free": len(self.free_wells()), "by_type": counts}
