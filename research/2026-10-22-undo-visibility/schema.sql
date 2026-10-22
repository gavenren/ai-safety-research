CREATE TABLE fields (
    name TEXT PRIMARY KEY CHECK (name IN ('x', 'y')),
    value INTEGER NOT NULL CHECK (value IN (0, 1))
);
CREATE TABLE receipts (
    field TEXT PRIMARY KEY CHECK (field IN ('x', 'y'))
);
CREATE TABLE gate (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    closed INTEGER NOT NULL CHECK (closed IN (0, 1))
);
CREATE TABLE decisions (
    job INTEGER PRIMARY KEY,
    phase TEXT NOT NULL CHECK (phase IN ('primary', 'probe')),
    predicate INTEGER NOT NULL CHECK (predicate BETWEEN 0 AND 15),
    observed_x INTEGER NOT NULL CHECK (observed_x IN (0, 1)),
    observed_y INTEGER NOT NULL CHECK (observed_y IN (0, 1)),
    decision INTEGER NOT NULL CHECK (decision IN (0, 1))
);
CREATE TABLE actions (job INTEGER PRIMARY KEY REFERENCES decisions(job));
