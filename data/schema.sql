-- Forecourt database schema
--
-- Units: litres (L) for fuel, Pakistani rupees (PKR) for money.
-- Dates are text 'YYYY-MM-DD'; timestamps 'YYYY-MM-DD HH:MM:SS' (Pakistan time).
-- A business day runs 06:00 to 06:00. The night shift belongs to the day it started.
--
-- SQLite only enforces REFERENCES when foreign keys are switched on, and the
-- switch is per connection. Any Python code that opens this database must run
--     conn.execute("PRAGMA foreign_keys = ON")
-- right after connecting, or bad references will slip through silently.

PRAGMA foreign_keys = ON;

-- Drop in reverse order so nothing is deleted while another table still points at it.
DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS tank_dips;
DROP TABLE IF EXISTS deliveries;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS price_history;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS nozzles;
DROP TABLE IF EXISTS tanks;
DROP TABLE IF EXISTS fuel_types;
DROP TABLE IF EXISTS stations;


-- =====================================================================
-- REFERENCE TABLES: rarely change
-- =====================================================================

-- One row = one petrol station.
CREATE TABLE stations (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL UNIQUE,                               -- no two stations share a name
    city  TEXT NOT NULL,
    kind  TEXT NOT NULL CHECK (kind IN ('city', 'highway'))   -- highway sites sell mostly diesel
);

-- One row = one grade of fuel.
CREATE TABLE fuel_types (
    id    INTEGER PRIMARY KEY,
    code  TEXT NOT NULL UNIQUE CHECK (code IN ('SUPER', 'HI_OCTANE', 'DIESEL')),
    name  TEXT NOT NULL                                       -- e.g. 'Super (RON 92)'
);

-- One row = one underground tank.
CREATE TABLE tanks (
    id            INTEGER PRIMARY KEY,
    station_id    INTEGER NOT NULL REFERENCES stations(id),
    fuel_type_id  INTEGER NOT NULL REFERENCES fuel_types(id), -- what it holds TODAY
    label         TEXT NOT NULL,                              -- 'Tank 1', 'Tank 2' within a station
    capacity_l    REAL NOT NULL CHECK (capacity_l > 0),
    UNIQUE (station_id, label)                                -- no two 'Tank 1's at one station
);

-- One row = one pump nozzle.
CREATE TABLE nozzles (
    id          INTEGER PRIMARY KEY,
    station_id  INTEGER NOT NULL REFERENCES stations(id),
    tank_id     INTEGER NOT NULL REFERENCES tanks(id),        -- the tank it draws fuel from
    label       TEXT NOT NULL,                                -- 'N1', 'N2' within a station
    UNIQUE (station_id, label)
);

-- One row = one employee.
CREATE TABLE staff (
    id                  INTEGER PRIMARY KEY,
    station_id          INTEGER NOT NULL REFERENCES stations(id),
    name                TEXT NOT NULL,
    role                TEXT NOT NULL CHECK (role IN ('manager', 'cashier', 'attendant')),
    monthly_salary_pkr  REAL NOT NULL CHECK (monthly_salary_pkr > 0)
);

-- One row = one price change for one grade.
-- A price applies from effective_from until the next row for the same grade.
CREATE TABLE price_history (
    id               INTEGER PRIMARY KEY,
    fuel_type_id     INTEGER NOT NULL REFERENCES fuel_types(id),
    price_pkr_per_l  REAL NOT NULL CHECK (price_pkr_per_l > 0),
    effective_from   TEXT NOT NULL,
    UNIQUE (fuel_type_id, effective_from)                     -- one price per grade per start date
);


-- =====================================================================
-- EVENT TABLES: only ever get new rows. Totals are calculated, never stored.
-- =====================================================================

-- One row = one nozzle's meter readings for one shift.
-- (Option b. For option a, one row per fill, you would drop the meter
--  columns and add a timestamp per fill instead.)
CREATE TABLE sales (
    id               INTEGER PRIMARY KEY,
    nozzle_id        INTEGER NOT NULL REFERENCES nozzles(id),
    fuel_type_id     INTEGER NOT NULL REFERENCES fuel_types(id), -- grade sold, frozen at sale time
    staff_id         INTEGER NOT NULL REFERENCES staff(id),      -- attendant on that nozzle
    business_date    TEXT NOT NULL,
    shift            TEXT NOT NULL CHECK (shift IN ('morning', 'evening', 'night')), -- 06-14, 14-22, 22-06
    opening_meter_l  REAL NOT NULL,                              -- meter at shift start
    closing_meter_l  REAL NOT NULL,                              -- meter at shift end
    litres           REAL NOT NULL CHECK (litres >= 0),          -- closing minus opening
    unit_price_pkr   REAL NOT NULL CHECK (unit_price_pkr > 0),   -- price charged, frozen at sale time
    amount_pkr       REAL NOT NULL,                              -- litres x unit price
    transactions     INTEGER NOT NULL CHECK (transactions >= 0), -- number of fills in the shift
    CHECK (closing_meter_l >= opening_meter_l),                  -- a meter never runs backwards
    UNIQUE (nozzle_id, business_date, shift)                     -- one reading per nozzle per shift
);

-- One row = one tanker unloading into one tank. Paid on delivery.
CREATE TABLE deliveries (
    id              INTEGER PRIMARY KEY,
    tank_id         INTEGER NOT NULL REFERENCES tanks(id),
    delivered_at    TEXT NOT NULL,                            -- timestamp
    litres          REAL NOT NULL CHECK (litres > 0),
    cost_pkr_per_l  REAL NOT NULL CHECK (cost_pkr_per_l > 0), -- what the station paid
    amount_pkr      REAL NOT NULL,                            -- invoice total
    supplier        TEXT NOT NULL
);

-- One row = one tank measured at the close of one business day.
-- The row dated the day before the first sale is the opening stock.
CREATE TABLE tank_dips (
    id             INTEGER PRIMARY KEY,
    tank_id        INTEGER NOT NULL REFERENCES tanks(id),
    business_date  TEXT NOT NULL,
    measured_l     REAL NOT NULL CHECK (measured_l >= 0),
    UNIQUE (tank_id, business_date)                           -- one closing reading per tank per day
);

-- One row = one payment out, other than fuel deliveries.
CREATE TABLE expenses (
    id            INTEGER PRIMARY KEY,
    station_id    INTEGER NOT NULL REFERENCES stations(id),
    expense_date  TEXT NOT NULL,
    category      TEXT NOT NULL CHECK (category IN ('salaries', 'electricity', 'maintenance', 'misc')),
    amount_pkr    REAL NOT NULL CHECK (amount_pkr > 0),
    note          TEXT                                        -- optional, e.g. 'Dispenser repair'
);


-- =====================================================================
-- INDEXES: like a book's index, they make common lookups fast
-- =====================================================================
CREATE INDEX idx_sales_date      ON sales (business_date);
CREATE INDEX idx_sales_nozzle    ON sales (nozzle_id);
CREATE INDEX idx_nozzles_tank    ON nozzles (tank_id);
CREATE INDEX idx_deliveries_tank ON deliveries (tank_id, delivered_at);
CREATE INDEX idx_expenses_date   ON expenses (expense_date);
