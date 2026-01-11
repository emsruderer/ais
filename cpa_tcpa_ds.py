import math
from typing import Tuple

def calculate_cpa_tcpa(
    lat1: float, lon1: float, sog1: float, cog1: float,  # Own ship: knots, degrees
    lat2: float, lon2: float, sog2: float, cog2: float,  # Target ship: knots, degrees
    earth_radius_nm: float = 3440.065  # Earth radius in nautical miles
) -> Tuple[float, float]:
    """
    Calculate CPA and TCPA between two moving vessels.

    Args:
        lat1, lon1: Own ship position (degrees)
        sog1: Speed Over Ground (knots)
        cog1: Course Over Ground (degrees True)
        lat2, lon2: Target ship position (degrees)
        sog2, sog2: Target speed and course
        earth_radius_nm: Earth radius in nautical miles

    Returns:
        (CPA in nautical miles, TCPA in minutes)
        If TCPA < 0, CPA has already occurred |TCPA| minutes ago
    """

    # Convert degrees to radians
    cog1_rad = math.radians(cog1)
    cog2_rad = math.radians(cog2)

    # 1. Calculate initial relative position in nautical miles
    # Convert lat/lon differences to nautical miles
    # 1 nautical mile = 1 minute of latitude
    delta_lat_nm = (lat2 - lat1) * 60  # Convert degrees to minutes (nautical miles)

    # Longitude conversion depends on latitude (cosine correction)
    mid_lat_rad = math.radians((lat1 + lat2) / 2)
    delta_lon_nm = (lon2 - lon1) * 60 * math.cos(mid_lat_rad)

    # Initial relative position vector (own ship at origin)
    dx0 = delta_lon_nm  # East-West distance (nautical miles)
    dy0 = delta_lat_nm  # North-South distance (nautical miles)

    # Initial range
    D0 = math.sqrt(dx0**2 + dy0**2)

    # 2. Convert speeds from knots to nautical miles per minute
    # 1 knot = 1 nautical mile per hour = 1/60 nautical miles per minute
    V1 = sog1 / 60  # Own ship speed (nm/min)
    V2 = sog2 / 60  # Target ship speed (nm/min)

    # 3. Velocity vectors (in nm/min)
    # Course 0° = North, 90° = East (mathematical convention)
    V1_x = V1 * math.sin(cog1_rad)  # East component
    V1_y = V1 * math.cos(cog1_rad)  # North component

    V2_x = V2 * math.sin(cog2_rad)  # East component
    V2_y = V2 * math.cos(cog2_rad)  # North component

    # 4. Relative velocity vector (target relative to own)
    V_rel_x = V2_x - V1_x
    V_rel_y = V2_y - V1_y

    V_rel_squared = V_rel_x**2 + V_rel_y**2

    # 5. Check for zero relative motion (div by zero protection)
    if V_rel_squared < 1e-10:  # Essentially stationary relative to each other
        return D0, float('inf')  # CPA is current distance, TCPA is infinite

    # 6. Calculate TCPA (Time to Closest Point of Approach)
    # TCPA = - (initial_position • relative_velocity) / |relative_velocity|²
    numerator = dx0 * V_rel_x + dy0 * V_rel_y
    TCPA_minutes = -numerator / V_rel_squared

    # 7. Calculate CPA
    # CPA = √(D0² - (V_rel * TCPA)²)
    # But safer: CPA = distance at time TCPA
    dx_at_tcpa = dx0 + V_rel_x * TCPA_minutes
    dy_at_tcpa = dy0 + V_rel_y * TCPA_minutes
    CPA = math.sqrt(dx_at_tcpa**2 + dy_at_tcpa**2)

    return CPA, TCPA_minutes


def calculate_cpa_tcpa_vector(
    pos1: Tuple[float, float], vel1: Tuple[float, float],
    pos2: Tuple[float, float], vel2: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Vector-based CPA/TCPA calculation (Cartesian coordinates).
    Assumes positions and velocities are in consistent units.

    Args:
        pos1: (x1, y1) - Own ship position
        vel1: (vx1, vy1) - Own ship velocity
        pos2: (x2, y2) - Target position
        vel2: (vx2, vy2) - Target velocity

    Returns:
        (CPA, TCPA) in same units as input
    """
    x1, y1 = pos1
    vx1, vy1 = vel1
    x2, y2 = pos2
    vx2, vy2 = vel2

    # Relative position and velocity
    dx = x2 - x1
    dy = y2 - y1
    dvx = vx2 - vx1
    dvy = vy2 - vy1

    # Initial distance
    D0 = math.sqrt(dx**2 + dy**2)

    # Avoid division by zero
    dv_squared = dvx**2 + dvy**2
    if dv_squared < 1e-10:
        return D0, float('inf')

    # TCPA
    TCPA = -(dx * dvx + dy * dvy) / dv_squared

    # Position at TCPA
    x_cpa = x2 + vx2 * TCPA - (x1 + vx1 * TCPA)
    y_cpa = y2 + vy2 * TCPA - (y1 + vy1 * TCPA)

    CPA = math.sqrt(x_cpa**2 + y_cpa**2)

    return CPA, TCPA
