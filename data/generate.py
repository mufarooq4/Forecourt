#!/usr/bin/env python3
"""
Forecourt data generator
========================

Fills the Forecourt database (see schema.sql) with 90 days of realistic,
made-up data for a network of 55 petrol stations.

    python data/generate.py
    python data/generate.py --stations 10 --days 30 --out data/small.db

The same seed and arguments always give exactly the same database. That
matters later: the agent's test questions need answers that never move.

Four tanks hide a problem (two leaks, one theft, one faulty meter). They are
listed in a separate answers file, never in the database, so they can only be
found the honest way: by reconciling dips, deliveries and sales.

Prices, margins and salaries are placeholders, not official figures.
Standard library only; no installs needed.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sqlite3
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ----------------------------------------------------------------- settings

GRADES = {  # code: (full name, average litres per fill)
    "SUPER": ("Super (RON 92)", 9.0),         # lots of motorbikes
    "HI_OCTANE": ("Hi-Octane (RON 97)", 22.0),
    "DIESEL": ("Diesel (HSD)", 60.0),         # trucks, buses, tractors
}
START_PRICE = {"SUPER": 262.0, "HI_OCTANE": 305.0, "DIESEL": 270.0}  # PKR per litre
DEALER_MARGIN = {"SUPER": 8.6, "HI_OCTANE": 12.0, "DIESEL": 8.6}     # PKR per litre

# Typical litres per day for each grade (low, high), by station kind
BASE_DEMAND = {
    "city":    {"SUPER": (6000, 14000), "HI_OCTANE": (400, 1500), "DIESEL": (2000, 6000)},
    "highway": {"SUPER": (3000, 8000),  "HI_OCTANE": (200, 800),  "DIESEL": (8000, 20000)},
}
# Monday to Sunday. Highways go quiet on Sunday: fewer trucks on the road.
WEEKDAY_FACTOR = {
    "city":    [1.00, 1.00, 1.00, 1.02, 1.05, 1.08, 0.88],
    "highway": [1.00, 1.02, 1.02, 1.00, 0.95, 0.97, 0.82],
}
PAYDAY_BUMP = 1.06                 # petrol sells more in the first 5 days of a month

SHIFTS = ["morning", "evening", "night"]   # 06-14, 14-22, 22-06
SHIFT_SPLIT = {"city": [0.46, 0.40, 0.14], "highway": [0.36, 0.34, 0.30]}

TANK_SIZES = [15000, 20000, 25000, 30000, 35000, 40000]   # litres
DEAD_STOCK_L = 300                 # a pump can't draw the last few hundred litres
REORDER_FRACTION = 0.30            # order a tanker when below 30% of capacity...
REORDER_DAYS = 2.0                 # ...or below 2 days of stock
FILL_TO = 0.92                     # never fill brim-full: fuel expands in the heat
LATE_TANKER_P = 0.03               # about 1 order in 33 arrives a day late

SITES = {  # city: [(area, kind)]
    "Islamabad": [("Blue Area", "city"), ("F-10 Markaz", "city"), ("G-11 Markaz", "city"),
                  ("I-8 Markaz", "city"), ("E-11", "city"), ("Srinagar Highway", "highway"),
                  ("Kashmir Highway", "highway")],
    "Rawalpindi": [("Saddar", "city"), ("Murree Road", "city"), ("Chaklala", "city"),
                   ("Adiala Road", "city"), ("Peshawar Road", "city"), ("GT Road Rawat", "highway")],
    "Lahore": [("Mall Road", "city"), ("Gulberg", "city"), ("Johar Town", "city"),
               ("DHA Phase 5", "city"), ("Model Town", "city"), ("Wapda Town", "city"),
               ("Ferozepur Road", "city"), ("Raiwind Road", "city"), ("Thokar Niaz Baig", "highway"),
               ("Ravi Road", "highway")],
    "Karachi": [("Shahrah-e-Faisal", "city"), ("Clifton", "city"), ("Gulshan-e-Iqbal", "city"),
                ("Korangi", "city"), ("Nazimabad", "city"), ("Tariq Road", "city"),
                ("Bahadurabad", "city"), ("North Karachi", "city"), ("Super Highway", "highway"),
                ("Northern Bypass", "highway"), ("National Highway Landhi", "highway")],
    "Peshawar": [("Hayatabad", "city"), ("University Road", "city"), ("Saddar Peshawar", "city"),
                 ("Ring Road", "highway"), ("GT Road Peshawar", "highway")],
    "Multan": [("Bosan Road", "city"), ("Vehari Road", "city"), ("Nawan Shehar", "city"),
               ("Multan Bypass", "highway"), ("Khanewal Road", "highway")],
    "Faisalabad": [("Canal Road", "city"), ("D Ground", "city"), ("Susan Road", "city"),
                   ("Satiana Road", "city"), ("Sargodha Road", "highway"), ("Jhang Road", "highway")],
    "Quetta": [("Sariab Road", "city"), ("Airport Road", "city"), ("Jinnah Road", "city"),
               ("Spinny Road", "city"), ("Quetta Bypass", "highway")],
}
NAME_ENDINGS = ["Filling Station", "Petroleum", "Service Station", "Fuels"]
SUPPLIER = {
    "Islamabad": "Northern depot", "Rawalpindi": "Northern depot",
    "Lahore": "Central depot", "Faisalabad": "Central depot",
    "Multan": "South Punjab depot", "Karachi": "Karachi port depot",
    "Peshawar": "Khyber depot", "Quetta": "Balochistan depot",
}
FIRST_NAMES = ["Ali", "Ahmed", "Usman", "Bilal", "Hamza", "Imran", "Kashif", "Naveed", "Asif",
               "Tariq", "Zahid", "Faisal", "Shahid", "Waqas", "Adnan", "Rizwan", "Sajid",
               "Javed", "Kamran", "Nadeem", "Irfan", "Arshad", "Saeed", "Yasir", "Junaid",
               "Sohail", "Khalid", "Rashid", "Aamir", "Fahad"]
LAST_NAMES = ["Khan", "Ahmed", "Hussain", "Malik", "Butt", "Qureshi", "Sheikh", "Raza",
              "Iqbal", "Chaudhry", "Abbasi", "Awan", "Mirza", "Siddiqui", "Baloch"]
MAINTENANCE_NOTES = ["Dispenser repair", "Canopy lights", "Generator service",
                     "Forecourt cleaning", "Meter calibration check", "Air compressor repair"]


# -------------------------------------------------------------------- model

@dataclass
class Nozzle:
    id: int
    meter: float                   # running total of litres, like a car's odometer


@dataclass
class Tank:
    id: int
    station: dict
    grade: str
    capacity: float
    base_demand: float             # typical litres per day, before weekday effects and noise
    level: float                   # the TRUE litres in the tank; a dip only estimates this
    nozzles: list = field(default_factory=list)
    pending: float = 0.0           # tanker ordered yesterday, arriving this morning
    problem: dict | None = None    # hidden leak, theft or meter fault


def daily_demand(t: Tank, d: date, rng: random.Random) -> float:
    kind = t.station["kind"]
    factor = WEEKDAY_FACTOR[kind][d.weekday()]
    if d.day <= 5 and t.grade != "DIESEL":
        factor *= PAYDAY_BUMP
    return t.base_demand * factor * rng.lognormvariate(0, 0.08)


def price_change_dates(start: date, end: date):
    """Fuel prices are revised twice a month, on the 1st and the 16th."""
    d = start.replace(day=16) if start.day >= 16 else start.replace(day=1)
    while d <= end:
        yield d
        d = d.replace(day=16) if d.day == 1 else (d.replace(day=1) + timedelta(days=32)).replace(day=1)


def round_to(x: float, step: int) -> int:
    return int(round(x / step) * step)


# -------------------------------------------------------------------- build

def build(args) -> None:
    rng = random.Random(args.seed)
    end = date.fromisoformat(args.end)
    start = end - timedelta(days=args.days - 1)
    days = [start + timedelta(days=i) for i in range(args.days)]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    db = sqlite3.connect(out)
    db.execute("PRAGMA foreign_keys = ON")      # without this, REFERENCES isn't checked
    db.executescript((HERE / "schema.sql").read_text(encoding="utf-8"))

    # fuel types
    grade_id = {}
    for i, (code, (name, _)) in enumerate(GRADES.items(), start=1):
        db.execute("INSERT INTO fuel_types (id, code, name) VALUES (?, ?, ?)", (i, code, name))
        grade_id[code] = i

    # stations, tanks, nozzles, staff
    sites = [(city, area, kind) for city, areas in SITES.items() for area, kind in areas]
    if args.stations < len(sites):
        sites = sorted(rng.sample(sites, args.stations), key=sites.index)

    tanks: list[Tank] = []
    attendants: dict[int, list[int]] = {}
    staff_rows = []
    tank_id = nozzle_id = staff_id = 0

    for sid, (city, area, kind) in enumerate(sites, start=1):
        st = {"id": sid, "name": f"{area} {rng.choice(NAME_ENDINGS)}", "city": city, "kind": kind}
        db.execute("INSERT INTO stations (id, name, city, kind) VALUES (?, ?, ?, ?)",
                   (sid, st["name"], city, kind))

        # which grades this station sells, and how much of each
        grades = ["SUPER", "DIESEL"] + (["HI_OCTANE"] if rng.random() < 0.65 else [])
        demand = {g: rng.uniform(*BASE_DEMAND[kind][g]) for g in grades}
        busiest = max(demand, key=demand.get)
        tanks_per_grade = {g: 2 if demand[g] > 14000 or (g == busiest and rng.random() < 0.3) else 1
                           for g in grades}

        tank_no = nozzle_no = 0
        for g in grades:
            for _ in range(tanks_per_grade[g]):
                base = demand[g] / tanks_per_grade[g]
                cap = next((s for s in TANK_SIZES if s >= 2.5 * base), TANK_SIZES[-1])
                if rng.random() < 0.3:
                    cap = min(cap + 5000, TANK_SIZES[-1])
                tank_id += 1
                tank_no += 1
                t = Tank(tank_id, st, g, cap, min(base, cap / 2.5), level=rng.uniform(0.45, 0.85) * cap)
                db.execute("INSERT INTO tanks (id, station_id, fuel_type_id, label, capacity_l) "
                           "VALUES (?, ?, ?, ?, ?)", (tank_id, sid, grade_id[g], f"Tank {tank_no}", cap))
                for _ in range(rng.randint(1, 2) if g == "HI_OCTANE" else rng.randint(2, 3)):
                    nozzle_id += 1
                    nozzle_no += 1
                    t.nozzles.append(Nozzle(nozzle_id, round(rng.uniform(1e5, 3e6), 2)))
                    db.execute("INSERT INTO nozzles (id, station_id, tank_id, label) VALUES (?, ?, ?, ?)",
                               (nozzle_id, sid, tank_id, f"N{nozzle_no}"))
                tanks.append(t)

        def hire(role, low, high):
            nonlocal staff_id
            staff_id += 1
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            staff_rows.append((staff_id, sid, name, role, round_to(rng.uniform(low, high), 500)))
            return staff_id

        hire("manager", 90000, 140000)
        for _ in range(rng.randint(1, 2)):
            hire("cashier", 45000, 55000)
        attendants[sid] = [hire("attendant", 37000, 42000) for _ in range(min(12, max(6, nozzle_no + 2)))]

    db.executemany("INSERT INTO staff (id, station_id, name, role, monthly_salary_pkr) "
                   "VALUES (?, ?, ?, ?, ?)", staff_rows)

    # hidden problems: four busy tanks, each at a different station
    busy_by_station: dict[int, list[Tank]] = {}
    for t in tanks:
        if t.base_demand >= 3000:
            busy_by_station.setdefault(t.station["id"], []).append(t)
    chosen = [rng.choice(busy_by_station[sid]) for sid in rng.sample(sorted(busy_by_station), 4)]
    answers = []
    for t, kind in zip(chosen, ["leak", "leak", "theft", "meter_fault"]):
        starts_on = rng.randint(args.days // 4, args.days // 2)
        rate = round(rng.uniform(0.008, 0.014), 4) if kind == "leak" else 0.008 if kind == "meter_fault" else None
        t.problem = {"type": kind, "starts_on": starts_on, "rate": rate}
        if kind == "leak":
            detail = f"loses {rate:.1%} of the litres sold, every day"
        elif kind == "theft":
            detail = "150-300 L goes missing on roughly 1 night in 5"
        else:
            detail = f"meters over-record by {rate:.1%}, so sales look higher than they were"
        answers.append({"tank_id": t.id, "station_id": t.station["id"], "station": t.station["name"],
                        "city": t.station["city"], "grade": t.grade, "problem": kind,
                        "starts": days[starts_on].isoformat(), "detail": detail})

    # prices
    price = dict(START_PRICE)
    price_by_date: dict[date, dict] = {}
    price_rows = []
    for i, change_day in enumerate(price_change_dates(start, end)):
        if i:
            price = {g: round(p + rng.uniform(-7, 7), 2) for g, p in price.items()}
        price_by_date[change_day] = price
        price_rows += [(grade_id[g], p, change_day.isoformat()) for g, p in price.items()]
    db.executemany("INSERT INTO price_history (fuel_type_id, price_pkr_per_l, effective_from) "
                   "VALUES (?, ?, ?)", price_rows)
    change_days = sorted(price_by_date)

    def price_on(d: date) -> dict:
        return price_by_date[max(c for c in change_days if c <= d)]

    # simulate one business day at a time
    sales, deliveries, expenses = [], [], []
    dips = [(t.id, (start - timedelta(days=1)).isoformat(), round(t.level, 1)) for t in tanks]  # opening stock
    short_days = 0

    for day_no, d in enumerate(days):
        today = price_on(d)
        for t in tanks:
            st, p = t.station, t.problem
            active = p is not None and day_no >= p["starts_on"]

            # 1. the tanker ordered yesterday arrives in the morning
            if t.pending:
                t.level += t.pending
                cost = round(today[t.grade] - DEALER_MARGIN[t.grade], 2)
                when = f"{d.isoformat()} {rng.randint(5, 9):02d}:{rng.choice([0, 15, 30, 45]):02d}:00"
                deliveries.append((t.id, when, t.pending, cost, round(t.pending * cost, 2), SUPPLIER[st["city"]]))
                t.pending = 0.0

            # 2. sales, read off each nozzle's meter at every shift change
            wanted = daily_demand(t, d, rng)
            dispensed = max(0.0, min(wanted, t.level - DEAD_STOCK_L))
            if dispensed < 0.98 * wanted:
                short_days += 1
            meter_error = 1 + p["rate"] if active and p["type"] == "meter_fault" else 1.0
            staff_here = attendants[st["id"]]
            for shift_no, (shift, share) in enumerate(zip(SHIFTS, SHIFT_SPLIT[st["kind"]])):
                weights = [rng.uniform(0.7, 1.3) for _ in t.nozzles]
                for n_no, (noz, w) in enumerate(zip(t.nozzles, weights)):
                    litres = round(dispensed * share * w / sum(weights) * meter_error, 2)
                    opening = noz.meter
                    noz.meter = round(opening + litres, 2)
                    fills = max(1, round(litres / GRADES[t.grade][1] * rng.uniform(0.85, 1.15))) if litres else 0
                    attendant = staff_here[(day_no * 3 + shift_no * 2 + n_no) % len(staff_here)]
                    sales.append((noz.id, grade_id[t.grade], attendant, d.isoformat(), shift,
                                  opening, noz.meter, litres, today[t.grade],
                                  round(litres * today[t.grade], 2), fills))
            t.level -= dispensed

            # 3. losses nobody writes down
            loss = 0.0
            if active and p["type"] == "leak":
                loss = dispensed * p["rate"]
            elif active and p["type"] == "theft" and rng.random() < 0.2:
                loss = rng.uniform(150, 300)
            t.level = max(0.0, t.level - loss)

            # 4. closing dip: a measurement, so it carries a small error
            error = rng.gauss(0, 0.15 + 0.0007 * dispensed)
            dips.append((t.id, d.isoformat(), round(max(0.0, t.level + error), 1)))

            # 5. running low? order a tanker for tomorrow morning
            if t.level < max(REORDER_FRACTION * t.capacity, REORDER_DAYS * t.base_demand):
                qty = math.floor((FILL_TO * t.capacity - t.level) / 1000) * 1000
                if qty >= 5000 and rng.random() > LATE_TANKER_P:
                    t.pending = float(qty)

        # money going out, per station
        for sid in attendants:
            expenses.append((sid, d.isoformat(), "misc", round_to(rng.uniform(1500, 6000), 50), "Daily running costs"))
            if d.day == 1:
                payroll = sum(r[4] for r in staff_rows if r[1] == sid)
                expenses.append((sid, d.isoformat(), "salaries", payroll, "Monthly payroll"))
            if d.day == 10:
                load = sum(t.base_demand for t in tanks if t.station["id"] == sid)
                expenses.append((sid, d.isoformat(), "electricity",
                                 round_to((90000 + 10 * load) * rng.uniform(0.9, 1.1), 100), "Monthly bill"))
            if rng.random() < 0.05:
                expenses.append((sid, d.isoformat(), "maintenance",
                                 round_to(rng.uniform(15000, 120000), 500), rng.choice(MAINTENANCE_NOTES)))

    db.executemany("INSERT INTO sales (nozzle_id, fuel_type_id, staff_id, business_date, shift, "
                   "opening_meter_l, closing_meter_l, litres, unit_price_pkr, amount_pkr, transactions) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sales)
    db.executemany("INSERT INTO deliveries (tank_id, delivered_at, litres, cost_pkr_per_l, amount_pkr, supplier) "
                   "VALUES (?, ?, ?, ?, ?, ?)", deliveries)
    db.executemany("INSERT INTO tank_dips (tank_id, business_date, measured_l) VALUES (?, ?, ?)", dips)
    db.executemany("INSERT INTO expenses (station_id, expense_date, category, amount_pkr, note) "
                   "VALUES (?, ?, ?, ?, ?)", expenses)
    db.commit()

    answer_file = out.with_name(out.stem + "_answers.json")
    answer_file.write_text(json.dumps(answers, indent=2), encoding="utf-8")

    print(f"Built {out}")
    print(f"  {start} to {end}, seed {args.seed}")
    for table in ["stations", "fuel_types", "tanks", "nozzles", "staff", "price_history",
                  "sales", "deliveries", "tank_dips", "expenses"]:
        count = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<15}{count:>9,}")
    print(f"  tank-days that ran short of fuel: {short_days}")
    print(f"Answer key, don't open it until stage 03: {answer_file}")
    db.close()


def main() -> None:
    p = argparse.ArgumentParser(description="Generate the Forecourt demo database.")
    p.add_argument("--stations", type=int, default=55, help="number of stations (max 55)")
    p.add_argument("--days", type=int, default=90, help="days of history")
    p.add_argument("--end", default="2026-11-08", help="last business day, YYYY-MM-DD")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default=str(HERE / "forecourt.db"))
    build(p.parse_args())


if __name__ == "__main__":
    main()
