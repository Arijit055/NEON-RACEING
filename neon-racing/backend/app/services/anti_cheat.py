# These constants must mirror the actual game balance in index.html.
# If you tune movement speed / spawn rates in the game, update these too.
BASE_MAX_SPEED = 220              # save.engineLevel = 1 baseline (units/sec)
SPEED_PER_ENGINE_LEVEL = 30
MAX_COIN_SPAWN_RATE = 1.5         # generous upper bound: coins collectible per second
NEAR_MISS_BONUS_MAX = 3           # matches coinScore += 3 in index.html
MILESTONE_COIN_BONUS = 15         # matches coinScore += 15 per 1000m in index.html


def max_plausible_distance(duration_seconds, engine_level):
    max_speed = BASE_MAX_SPEED + (engine_level * SPEED_PER_ENGINE_LEVEL)
    # 10% buffer for acceleration ramp-up / rounding — not big enough to be a loophole
    return max_speed * duration_seconds * 1.1


def max_plausible_coins(duration_seconds, distance):
    pickup_coins = MAX_COIN_SPAWN_RATE * duration_seconds
    milestone_coins = (distance // 1000) * MILESTONE_COIN_BONUS
    near_miss_buffer = NEAR_MISS_BONUS_MAX * ((duration_seconds // 5) + 1)
    return int(pickup_coins + milestone_coins + near_miss_buffer)


def validate_run(claimed_distance, claimed_coins, duration_seconds, engine_level):
    """Returns clamped, trustworthy values for a completed run — never
    trusts the client's numbers directly. `flagged` marks runs that
    exceeded plausible limits, for logging/review rather than an
    automatic ban."""
    max_dist = max_plausible_distance(duration_seconds, engine_level)
    max_coins = max_plausible_coins(duration_seconds, claimed_distance)

    flagged = claimed_distance > max_dist or claimed_coins > max_coins

    return {
        "distance": min(claimed_distance, max_dist),
        "coins": min(claimed_coins, max_coins),
        "flagged": flagged,
    }
