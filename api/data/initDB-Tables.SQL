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

CREATE TABLE IF NOT EXISTS weaponsMeta (
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

CREATE TABLE IF NOT EXISTS weapons (
id         INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
type       INT      NOT NULL,  /* ID from weaponsMeta = ('Revolver', 'Pistol', 'Axe', ...) */
bearer     INT      NULL,      /* ID of the PC who possesses the weapon */
bound      BOOLEAN,            /* if the weapon is already bound to this PC */
bound_type TEXT     NOT NULL,  /* ('BoE', 'BoP', 'BoA', 'BoU', 'BtA') */
modded     BOOLEAN,            /* if it is modded yet */
mods       TEXT     NULL,      /* list of linked mods */
state      INT      NOT NULL,  /* 0-100 scale. 100 = new, 0 = unusable */
rarity     INT      NOT NULL,  /* ('Legendary', 'Epic', 'Rare', ...) */
date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS gearMeta (
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

CREATE TABLE IF NOT EXISTS gear (
id         INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
type       INT      NOT NULL,  /* ID from gearMeta */
bearer     INT      NULL,      /* ID of the PC who possesses the weapon */
bound      BOOLEAN,            /* if the weapon is already bound to this PC */
bound_type TEXT     NOT NULL,  /* ('BoE', 'BoP', 'BoA', 'BoU', 'BtA') */
modded     BOOLEAN,            /* if it is modded yet */
mods       TEXT     NULL,      /* list of linked mods */
state      INT      NOT NULL,  /* 0-100 scale. 100 = new, 0 = unusable */
rarity     INT      NOT NULL,  /* ('Legendary', 'Epic', 'Rare', ...) */
date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS maps (
id         INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
type       TEXT     NOT NULL,  /* Map type ('Instance', 'Worldmap', 'Encounter') */
size       TEXT     NOT NULL,  /* Map size ('24x24', '24x32', '...') */
data       TEXT     NOT NULL,  /* Map JSON */
date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS races (
id          INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
name        TEXT     NOT NULL,
loots       BOOLEAN,                                  /* If the monster loots treasures */
rarity      ENUM('Legendary','Epic','Rare','Common'), /* rarity level */
min_level   INT      NOT NULL,                        /* minimum level */
max_level   INT      NOT NULL,                        /* maximum level */
min_hp      INT      NOT NULL,                        /* minimum HP */
max_hp      INT      NOT NULL,                        /* maximum HP */
min_arm_p   INT      NOT NULL,                        /* minimum Physical Armor */
max_arm_p   INT      NOT NULL,                        /* maximum Physical Armor */
min_arm_b   INT      NOT NULL,                        /* minimum Ballistic Armor */
max_arm_b   INT      NOT NULL,                        /* maximum Ballistic Armor */
min_m       INT      NOT NULL,                        /* minimum M */
max_m       INT      NOT NULL,                        /* maximum M */
min_r       INT      NOT NULL,                        /* minimum R */
max_r       INT      NOT NULL,                        /* maximum R */
min_g       INT      NOT NULL,                        /* minimum G */
max_g       INT      NOT NULL,                        /* maximum G */
min_v       INT      NOT NULL,                        /* minimum V */
max_v       INT      NOT NULL,                        /* maximum V */
min_p       INT      NOT NULL,                        /* minimum P */
max_p       INT      NOT NULL,                        /* maximum P */
min_b       INT      NOT NULL,                        /* minimum B */
max_b       INT      NOT NULL);                       /* maximum B */

CREATE TABLE IF NOT EXISTS creatures (
id          INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
race        INT      NOT NULL,                 /* races.id */
name        TEXT     NOT NULL,                 /* Creature Name */
account     INT      NULL,                     /* users.id */
targeted    BOOLEAN,                           /* If the creature is targeted */
targeted_by INT      NULL,                     /* creatures.id */
x           INT      NOT NULL,                 /* Creature X pos */
y           INT      NOT NULL,                 /* Creature Y pos */
level       INT      NOT NULL,                 /* Creature level */
hp_max      INT      NOT NULL,                 /* Creature HP (max) */
hp          INT      NOT NULL,                 /* Creature HP (now) */
arm_p       INT      NOT NULL,                 /* Creature Physical Armor */
arm_b       INT      NOT NULL,                 /* Creature Ballistic Armor */
m           INT      NOT NULL,                 /* Creature M carac */
r           INT      NOT NULL,                 /* Creature R carac */
g           INT      NOT NULL,                 /* Creature G carac */
v           INT      NOT NULL,                 /* Creature V carac */
p           INT      NOT NULL,                 /* Creature P carac */
b           INT      NOT NULL,                 /* Creature B carac */
instance    INT      NULL,                     /* instance.id */
squad       INT      NULL,                     /* squads.id */
squad_rank  ENUM('Leader','Member','Pending'), /* Creature rank in squad */
xp          INT      NULL,                     /* Creature total XP */
date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);
