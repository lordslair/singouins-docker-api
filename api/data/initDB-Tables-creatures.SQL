CREATE TABLE IF NOT EXISTS creatures (
id          INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
race        INT      NOT NULL,                 /* races.id */
name        TEXT     NOT NULL,                 /* Creature Name */
account     INT      NULL,                     /* users.id */
rarity      ENUM('Small','Normal','Big','Unique','Boss','God') NOT NULL DEFAULT 'Normal',
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
avatar      TEXT     NULL,                     /* Creature Avatar */
sprite      TEXT     NULL,                     /* Creature Sprite */
date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS creaturesLog (
id          INT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
src         INT      NOT NULL,  /* creatures.id */
dst         INT      NULL,      /* creatures.id or NULL */
action      TEXT     NOT NULL,  /* description of the action */
date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS creaturesStats (
id          INT      NOT NULL PRIMARY KEY,     /* creatures.id */
m_race      INT      NOT NULL,                 /* Creature M carac (racial bonus) */
m_class     INT      NOT NULL,                 /* Creature M carac (class bonus) */
m_skill     INT      NOT NULL,                 /* Creature M carac (skill bonus) */
m_point     INT      NOT NULL,                 /* Creature M carac (points invested) */
r_race      INT      NOT NULL,                 /* Creature R carac (racial bonus) */
r_class     INT      NOT NULL,                 /* Creature R carac (class bonus) */
r_skill     INT      NOT NULL,                 /* Creature R carac (skill bonus) */
r_point     INT      NOT NULL,                 /* Creature R carac (points invested) */
g_race      INT      NOT NULL,                 /* Creature G carac (racial bonus) */
g_class     INT      NOT NULL,                 /* Creature G carac (class bonus) */
g_skill     INT      NOT NULL,                 /* Creature G carac (skill bonus) */
g_point     INT      NOT NULL,                 /* Creature G carac (points invested) */
v_race      INT      NOT NULL,                 /* Creature V carac (racial bonus) */
v_class     INT      NOT NULL,                 /* Creature V carac (class bonus) */
v_skill     INT      NOT NULL,                 /* Creature V carac (skill bonus) */
v_point     INT      NOT NULL,                 /* Creature V carac (points invested) */
p_race      INT      NOT NULL,                 /* Creature P carac (racial bonus) */
p_class     INT      NOT NULL,                 /* Creature P carac (class bonus) */
p_skill     INT      NOT NULL,                 /* Creature P carac (skill bonus) */
p_point     INT      NOT NULL,                 /* Creature P carac (points invested) */
b_race      INT      NOT NULL,                 /* Creature B carac (racial bonus) */
b_class     INT      NOT NULL,                 /* Creature B carac (class bonus) */
b_skill     INT      NOT NULL,                 /* Creature B carac (skill bonus) */
b_point     INT      NOT NULL,                 /* Creature B carac (points invested) */
points      INT      NOT NULL,                 /* Creature points not yet invested */
date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS creaturesSlots (
id          INT      NOT NULL PRIMARY KEY,     /* creatures.id */
lefthand    INT      NULL,                     /* weapons.id */
righthand   INT      NULL,                     /* weapons.id */
holster     INT      NULL,                     /* weapons.id */
head        INT      NULL,                     /* gear.id */
shoulders   INT      NULL,                     /* gear.id */
torso       INT      NULL,                     /* gear.id */
hands       INT      NULL,                     /* gear.id */
legs        INT      NULL,                     /* gear.id */
feet        INT      NULL,                     /* gear.id */
ammo        INT      NULL,                     /* gear.id */
wallet      INT      NOT NULL DEFAULT '0',     /* Amount of currency */
date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);
