-- Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

-- TEXT statt varchar(n):
-- "There is no performance difference among these three types, apart from a few extra CPU cycles
-- to check the length when storing into a length-constrained column"
-- ggf. CHECK(char_length(nachname) <= 255)

-- https://www.postgresql.org/docs/current/manage-ag-tablespaces.html
SET default_tablespace = pizzeriaspace;

-- https://www.postgresql.org/docs/current/sql-createtable.html
-- https://www.postgresql.org/docs/current/datatype.html
-- https://www.postgresql.org/docs/current/sql-createtype.html
-- https://www.postgresql.org/docs/current/datatype-enum.html
-- https://www.postgresql.org/docs/current/sql-createtable.html

CREATE TABLE IF NOT EXISTS pizzeria (
    id              INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    name            TEXT NOT NULL,
    telefon         TEXT,
    email           TEXT UNIQUE
);


CREATE TABLE IF NOT EXISTS adresse (
    id              INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    strasse         TEXT NOT NULL,
    hausnummer      TEXT NOT NULL,
    plz             TEXT NOT NULL CHECK (plz ~ '^[0-9]{5}$'),
    ort             TEXT NOT NULL,
    -- UNIQUE: 1:1-Beziehung
    pizzeria_id     INTEGER NOT NULL UNIQUE REFERENCES pizzeria ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS pizza (
    id              INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    name            TEXT NOT NULL,
    beschreibung    TEXT,
    -- https://www.postgresql.org/docs/current/datatype-numeric.html
    preis           NUMERIC(10,2) NOT NULL CHECK (preis > 0),
    vegetarisch     BOOLEAN NOT NULL DEFAULT FALSE,
    -- 1:N-Beziehung
    pizzeria_id     INTEGER NOT NULL REFERENCES pizzeria ON DELETE CASCADE
);


-- default: btree
CREATE INDEX IF NOT EXISTS pizza_pizzeria_id_idx ON pizza(pizzeria_id);