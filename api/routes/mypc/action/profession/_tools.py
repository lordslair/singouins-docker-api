# -*- coding: utf8 -*-

import datetime
import math

from random import choices, random

from mongo.models.Profession import ProfessionDocument


def profession_gain(creatureuuid, profession, profession_score=None):
    """Calculate the Profession score gained (0 or 1)."""
    # If we didn't get profession_score, we fetch it
    if profession_score is None:
        Profession = ProfessionDocument.objects(_id=creatureuuid).get()
        profession_score = getattr(Profession, profession)

    # Define thresholds and corresponding weights
    THRESHOLDS = [
        (100, None),      # No action needed
        (75, (70, 30)),   # 75-99 → 70% 0, 30% 1
        (50, (60, 40)),   # 50-74 → 60% 0, 40% 1
        (25, (50, 50)),   # 25-49 → 50% 0, 50% 1
        (0, None)         # 0-24 → Always 1
    ]
    # Profession  → Probability to gain 1 point
    #  75 - 99    | [██████..............] 30%
    #  50 - 74    | [████████............] 40%
    #  25 - 49    | [██████████..........] 50%
    #   0 - 24    | [████████████████████] 100%

    # We calculate the amount of Profession points acquired
    gain = 0
    for THRESHOLD, weights in THRESHOLDS:
        if profession_score >= THRESHOLD:
            if weights is None:
                gain = 1 if THRESHOLD == 0 else 0  # Force 1 only for the lowest threshold
            else:
                gain = choices([0, 1], weights=weights)[0]

            if gain == 1:
                # We INCR the Profession accordingly
                profession_update_query = {
                    f'inc__{profession}': gain,
                    "set__updated": datetime.datetime.utcnow(),
                    }
                ProfessionDocument.objects(_id=creatureuuid).update(**profession_update_query)


def profession_scaled(profession_score):
    """Return a number (1 to 4) based on Profession score."""
    # Profession  → Probability to gain shards
    #  00 - 25    | [....................] 0
    #  26 - 50    | [█████...............] 1
    #  51 - 75    | [██████████..........] 2
    #  76 - 99    | [███████████████.....] 3
    #      100    | [████████████████████] 4
    return math.floor(profession_score/25)


def scaled_stat(stat):
    """Compute the scaled value as probability."""
    return 1 - math.pow(math.exp(-(stat - 100) / 50), 1.5)


def probabilistic_binary(stat):
    """Return 1 with probability scaled_stat(stat), else return 0."""
    # Stats.b   → Probability to gain 1 additional shard
    # 100 - 119 | [██...................] 11%
    # 120 - 139 | [████.................] 22%
    # 140 - 159 | [███████..............] 35%
    # 160 - 179 | [███████████..........] 53%
    # 180 - 199 | [██████████████.......] 69%
    # 200 - 219 | [████████████████.....] 81%
    # 220 - 239 | [██████████████████...] 89%
    # 240 - 259 | [███████████████████..] 94%
    # 260 - 279 | [████████████████████.] 97%
    # 280 - 299 | [████████████████████.] 98%
    # 300+      | [████████████████████.] 99%
    return 1 if random() < scaled_stat(stat) else 0
