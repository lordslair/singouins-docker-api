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
