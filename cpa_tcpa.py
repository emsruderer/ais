"""
Calculate closest point of approach and time to closest point of approach
"""

from math import cos, sin, sqrt, atan, atan2, radians, degrees

JEMGUM_LAT= 53.2644
JEMGUM_LON = 7.3973
JEMGUM = (JEMGUM_LAT,JEMGUM_LON)
NORTH_POSITION = (53.27338,7.3973)
SOUTH_POSITION = (53.25540,7.3973)
R = 3440.065  # Radius of earth in nautical miles

VERBOSE = False

def cpa_tcpa(mmsi1, lat1, lon1, cog1, sog1,  mmsi2, lat2, lon2, cog2, sog2):
    """
        Calculate CPA and TCPA between two moving vessels.

        Args:
            lat1, lon1: Own ship position (degrees)
            sog1: Speed Over Ground (knots)
            cog1: Course Over Ground (degrees True)
            lat2, lon2: Target ship position (degrees)
            sog2, sog2: Target speed and course
            R: Earth radius in nautical miles

        Returns:
            (CPA in nautical miles, TCPA in minutes)
            If TCPA < 0, CPA has already occurred |TCPA| minutes ago
            (CPA in nautical miles, TCPA in minutes, distance in nautical miles,
            bearing in degrees, approaching speed in knots)
    """
    try:
        cog1 = radians(cog1)
        cog2 = radians(cog2)

        v1 = sog1 / 60  # Own ship speed (nm/min)
        v2 = sog2 / 60  # Target ship speed (nm/min)

        v1x = v1 * sin(cog1)  # East component
        v1y = v1 * cos(cog1)  # North component

        v2x = v2 * sin(cog2)  # East component
        v2y = v2 * cos(cog2)  # North component

        dvx = v2x - v1x  # relative speed in x (nm/min)
        dvy = v2y - v1y  # relative speed in y (nm/min)
        dv = sqrt(dvx**2 + dvy**2)  # relative speed

        d_lat = (lat1 - lat2) * 60  # in nautical miles
        d_lon = (lon1 - lon2) * 60 * cos( (lat1+lat2)/2 )  # in nautical miles
        distance = sqrt(d_lon**2 + d_lat**2)

        if dv < 1e-10:
            bear = atan2(d_lat,d_lon) if d_lon  != 0 else 0
            bearing = degrees(bear) % 360
            return {"cpa": distance, "tcpa": float('inf'), "mmsi": mmsi2, "distance": distance, "bearing": bearing, "approaching_speed": 0.0}

        tcpa = (d_lat*dvy+ d_lon*dvx)/dv**2  # in minutes
        if tcpa < 0:
            # CPA has already occurred
            cpa = sqrt( (d_lon + dvx*tcpa)**2 + (d_lat + dvy*tcpa)**2 )
            dv = -dv  # now receding
        else:
            # CPA will occur in future
            cpa = sqrt( (d_lon - dvx*tcpa)**2 + (d_lat - dvy*tcpa)**2 )
            #print(distance)

        bear = atan2(d_lon,d_lat) if d_lon  != 0 else 0
        bearing = degrees(bear) % 360

        return { "cpa": cpa, "tcpa" : tcpa, "mmsi" : mmsi2, "distance": distance, "bearing": bearing, "approaching_speed": dv }
    except ZeroDivisionError as ex:
        print(ex, mmsi1 )
        return { "cpa": None, "tcpa" : None, "mmsi" : mmsi2, "distance": 0.0, "bearing": 0.0, "approaching_speed" : 0.0 }

def print_cpa(k,v):
    """function pretty print cpa tcpa"""
    if v['distance']< 3:
        if v["tcpa"] < 0.0:
            print(f"The closest point of boat {k} to {v["mmsi"]} is passed, distance {v["distance"]:.2f} nM, bearing {v["bearing"]:.2f} deg. Approaching speed {v["approaching_speed"]*60:.2f} kn.")
        else:
            print(f"The closest point of boat {k} to {v["mmsi"]} is : {v["cpa"]:.2f} nM in {v["tcpa"]:.2f} min., distance {v["distance"]:.2f} nM, bearing {v["bearing"]:.2f} deg. Approaching speed {v["approaching_speed"]*60:.2f} kn.")

def show_cpas(cpas):
    """function pretty print dict cpa tcpa"""
    for k,v in cpas.items():
       print_cpa(k,v)

def calc_speed(speed1, speed2, course1, course2):
    """test function for cpa tcpa"""
    course1 = radians(course1)
    course2 = radians(course2)
    dvx = abs(speed1*sin(course1) - speed2*sin(course2))
    dvy = abs(speed1*cos(course1) - speed2*cos(course2))
    dv = sqrt(dvx**2 + dvy**2)
    return f"Delta Vx {dvx:.2f}, Delta Vy {dvy:.2f} => Delta V {dv:.2f} kn."

if __name__ == "__main__":
    " Test speed calculations and cpa tcpa calculations """
    print(calc_speed(5.0, 5.0, 0, 180))
    print("CPA and TCPA calculations test")
    cpas = dict()
    cpas["211040154"]= cpa_tcpa( 211040154, SOUTH_POSITION[0], SOUTH_POSITION[1],   0,  5.0,  244030153,  NORTH_POSITION[0], NORTH_POSITION[1], 180, 5.0)
    cpas["211040155"]= cpa_tcpa( 211040155, SOUTH_POSITION[0], SOUTH_POSITION[1],   0,  3.0,  244030153,  NORTH_POSITION[0], NORTH_POSITION[1],180, 3.0)
    cpas["211040156"]= cpa_tcpa( 211040156  , SOUTH_POSITION[0], SOUTH_POSITION[1],  180,  3.0,  244030153,  NORTH_POSITION[0], NORTH_POSITION[1],180, 10.0)
    cpas["211040157"]= cpa_tcpa( 211040157  , SOUTH_POSITION[0], SOUTH_POSITION[1],  180,  0.0,  244030153,  NORTH_POSITION[0], NORTH_POSITION[1],358, 0.0)
    cpas["211040158"]= cpa_tcpa( 211040158  , SOUTH_POSITION[0], SOUTH_POSITION[1],  180,  0.1,  244030153,  SOUTH_POSITION[0], SOUTH_POSITION[1],358, 0.0)
    show_cpas(cpas)
