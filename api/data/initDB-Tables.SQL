CREATE TABLE IF NOT EXISTS pjsAuth (
id        INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
name      TEXT     NOT NULL,
mail      TEXT     NOT NULL,
hash      TEXT     NOT NULL, /* BCRYPT hashed */
created   DATETIME NOT NULL,
active    BOOLEAN,
date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS pjsInfos (
id        INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
name      TEXT     NOT NULL,
race      TEXT     NOT NULL,
account   INT      NOT NULL, /* pjsAuth.id */
level     INT      NOT NULL,
x         INT      NOT NULL,
y         INT      NOT NULL,
xp        INT      NOT NULL,
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
