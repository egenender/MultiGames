--DROP TABLE IF EXISTS users;
--DROP TABLE IF EXISTS games;


/*CREATE TABLE IF NOT EXISTS users (
    id bigint PRIMARY KEY,
    name text NOT NULL
);
*/
/*CREATE TABLE IF NOT EXISTS games_xapi_bot (
    id bigint PRIMARY KEY,
    groupName TEXT NOT NULL,
    data text NOT NULL
);*/
/*DROP TABLE IF EXISTS games_xapi_bot;*/

CREATE TABLE IF NOT EXISTS games (
    id bigint PRIMARY KEY,
    groupName TEXT NOT NULL,
    tipojuego TEXT NOT NULL,
    data TEXT NOT NULL
);
