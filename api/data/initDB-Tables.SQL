CREATE TABLE IF NOT EXISTS users (
id        INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
name      TEXT     NOT NULL,
mail      TEXT     NOT NULL,
hash      TEXT     NOT NULL,                   /* BCRYPT hashed */
d_name    TEXT     NULL,                       /* Discord username foobar#1234 */
d_monkeys TEXT     CHARACTER SET utf8mb4 NULL, /* Discord validation string */
d_ack     BOOLEAN  NOT NULL DEFAULT FALSE,     /* Discord validation ack */
created   DATETIME NOT NULL,
active    BOOLEAN,
date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS mps (
id        INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
src_id    INT      NOT NULL,
src       TEXT     NOT NULL,
dst_id    INT      NOT NULL,
dst       TEXT     NOT NULL,
subject   TEXT     NOT NULL,
body      TEXT     NOT NULL,
date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS squads (
id        INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
name      TEXT     NOT NULL, /* Squad name */
leader    INT      NOT NULL, /* Squad leader */
created   DATETIME NOT NULL, /* Squad creation date */
date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS maps (
id         INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
type       TEXT     NOT NULL,  /* Map type ('Instance', 'Worldmap', 'Encounter') */
size       TEXT     NOT NULL,  /* Map size ('24x24', '24x32', '...') */
data       TEXT     NOT NULL,  /* Map JSON */
date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);
