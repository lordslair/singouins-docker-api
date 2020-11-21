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

CREATE TABLE IF NOT EXISTS metaWeapons (
id         INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
name       TEXT     NOT NULL,
mastery    INT      NULL,      /* If a special skill  needed to use it */
onehanded  BOOLEAN,            /* if it is a 1-hand or 2-hands weapon */
ranged     BOOLEAN,            /* if it is a ranged weapon or not */
rng        INT      NULL,      /* range of the weapon */
pas_use    INT      NOT NULL,  /* PA needed to use it */
pas_reload INT      NULL,      /* PA needed to reload it */
moddable   BOOLEAN,            /* if it is a moddable weapon or not */
caliber    TEXT     NULL,      /* ('.32', '.45', '7.62', ...) */
rounds     INT      NULL,      /* ('single', 'double', 'triple', 'burst') */
burst_acc  INT      NULL,      /* Acuracy modifier for burst mode */
size       TEXT     NOT NULL,  /* for inventory purposes ('1x2', '2x3', ...)*/
dmg_base   INT      NOT NULL,  /* base damages of the weapon (without any mods) */
dmg_sneaky INT      NOT NULL,  /* sneaky damages modifier (base %) */
parry      INT      NOT NULL,  /* parry modifier (base %) */
arpen      INT      NOT NULL,  /* armor penetration (base %) */
defcan     INT      NOT NULL,  /* defense cancelation (base %) */
min_m      INT      NOT NULL,  /* minimal M carac to use the item */
min_r      INT      NOT NULL,  /* minimal R carac to use the item */
min_g      INT      NOT NULL,  /* minimal G carac to use the item */
min_v      INT      NOT NULL,  /* minimal V carac to use the item */
min_p      INT      NOT NULL,  /* minimal P carac to use the item */
min_b      INT      NOT NULL); /* minimal B carac to use the item */

CREATE TABLE IF NOT EXISTS metaArmors (
id         INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
name       TEXT     NOT NULL,
tier       INT      NOT NULL,  /* Gear tiering (none, light, medium, heavy) */
mastery    INT      NULL,      /* If a special skill  needed to use it */
moddable   BOOLEAN,            /* if it is a moddable gear or not */
size       TEXT     NOT NULL,  /* for inventory purposes ('1x2', '2x3', ...)*/
arm_p      INT      NOT NULL,  /* Physical Armor */
arm_b      INT      NOT NULL,  /* Ballistic Armor */
min_m      INT      NOT NULL,  /* minimal M carac to use the item */
min_r      INT      NOT NULL,  /* minimal R carac to use the item */
min_g      INT      NOT NULL,  /* minimal G carac to use the item */
min_v      INT      NOT NULL,  /* minimal V carac to use the item */
min_p      INT      NOT NULL,  /* minimal P carac to use the item */
min_b      INT      NOT NULL); /* minimal B carac to use the item */

CREATE TABLE IF NOT EXISTS maps (
id         INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
type       TEXT     NOT NULL,  /* Map type ('Instance', 'Worldmap', 'Encounter') */
size       TEXT     NOT NULL,  /* Map size ('24x24', '24x32', '...') */
data       TEXT     NOT NULL,  /* Map JSON */
date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS items (
id         INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
metatype   ENUM('armor','weapon'),                   /* meta type */
metaid     INT      NOT NULL,                        /* ID from Meta`metatype table */
bearer     INT      NULL,                            /* ID of the PC who possesses the item */
bound      BOOLEAN,                                  /* if the item is already bound to this PC */
bound_type ENUM('BoE','BoP','BoA','BoU','BtA'),      /* bound type */
modded     BOOLEAN,                                  /* if it is modded yet */
mods       TEXT     NULL,                            /* list of linked mods */
state      INT      NOT NULL,                        /* 0-100 scale. 100 = new, 0 = unusable */
rarity     ENUM('Legendary','Epic','Rare','Common','Uncommon','Broken'),
offsetx    INT      NULL,                            /* X pos in the inventory */
offsety    INT      NULL,                            /* Y pos in the inventory */
date       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);
