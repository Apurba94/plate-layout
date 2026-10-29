# plate-layout

**Design 6- to 384-well plate layouts in seconds: replicates, fixed controls and blanks,
optional edge-well exclusion, seeded randomization, and CSV/ASCII maps for the plate reader and notebook.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Plate maps are drawn by hand in spreadsheets, re-drawn for every experiment, and the mapping between
wells and samples is where analysis errors start. Systematic placement (all replicates of a condition
in one row) confounds treatment with position effects such as edge evaporation and temperature
gradients; randomized layouts avoid that, but only if they are recorded and reproducible.

## Features

- 6, 12, 24, 48, 96 and 384-well formats; well names like `A1` ... `P24`
- Fixed controls (`--control pos=H11,H12`) and blanks, then samples with N replicates
- Fill by row or by column, grouped replicates, or **randomized with a seed**
- Exclude edge wells to avoid evaporation artefacts
- Collision and capacity checks; CSV export (well, row, column, sample, type, replicate) and an ASCII map

## Usage

```bash
pip install .
plate-layout --samples s1,s2,s3,s4 -r 3 --control neg=A1,A2 --control pos=H11,H12 -o layout.csv
plate-layout --samples @samples.txt -r 2 --randomize --seed 2026 --exclude-edges -o random_layout.csv
plate-layout -s 384 --samples @compounds.txt -r 4 --by column
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
