"""
Calculate closest point of approach and time to closest point of approach
"""

from math import cos, sin, sqrt, atan, atan2, radians, degrees

JEMGUM_LAT= 53.2644
JEMGUM_LON = 7.3973
JEMGUM = (JEMGUM_LAT,JEMGUM_LON)
NORTH_BORDER = (53.27338,7.3967)
SOUTH_BORDER = (53.25540,7.3949)
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
        #lat1, lon1 = radians(lat1), radians(lon1)
        #lat2, lon2 = radians(lat2), radians(lon2)
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
        if dv < 1e-10:
            return {"cpa": 0.0, "tcpa": float('inf'), "mmsi": mmsi2, "distance": 0.0, "bearing": 0.0, "approaching_speed": 0.0}
        
        #a = sin(d_lat/2)**2 + cos(lat1)*cos(lat2)*sin(d_lon/2)**2
        #c = 2 * atan2(sqrt(a), sqrt(1 - a))
        #distance = R * c  # in nautical miles
        #d_lon = R * c * sin(atan2(d_lon, d_lat)) # in nautical miles
        #d_lat = R * c * cos(atan2(d_lon, d_lat)) # in nautical miles

        d_lat = (lat1 - lat2) * 60  # in nautical miles
        d_lon = (lon1 - lon2) * 60 * cos( (lat1+lat2)/2 )  # in nautical miles
        distance = sqrt(d_lon**2 + d_lat**2)
   
        tcpa = -(d_lat*dvy+ d_lon*dvx)/dv**2  # in minutes
        if tcpa < 0:
            # CPA has already occurred
            cpa = sqrt( (d_lon + dvx*tcpa)**2 + (d_lat + dvy*tcpa)**2 )
        else:
            # CPA will occur in future
            cpa = sqrt( (d_lon - dvx*tcpa)**2 + (d_lat - dvy*tcpa)**2 )
            #print(distance)

        bear = atan2(d_lat,d_lon) if d_lon  != 0 else 0
        bearing = degrees(bear) % 360

        #print(f"Delta lon {d_lon:.4}, delta Vx {dvx:.4}, Delta lat {d_lat:.4}, delta Vy {dvy:.4}")

        return { "cpa": cpa, "tcpa" : tcpa, "mmsi" : mmsi2, "distance": distance, "bearing": bearing, "approaching_speed": dv }
    except ZeroDivisionError as ex:
        print(ex, mmsi1 )
        return { "cpa": None, "tcpa" : None, "mmsi" : mmsi2, "distance": 0.0, "bearing": 0.0, "approaching_speed" : 0.0 }

def print_cpa(k,v):
    """function pretty print cpa tcpa"""
    if v['distance']< 3:
        if v["tcpa"] < 0.0:
            print(f"The closest point of boat {k}  to {v["mmsi"]} is passed, distance {v["distance"]:.2f} nM, bearing {v["bearing"]:.2f} deg.")
        else:
            print(f"The closest point of boat {k}  to {v["mmsi"]} is : {v["cpa"]:.2f} nM in {v["tcpa"]*60:.2f} min., distance {v["distance"]:.2f} nM, bearing {v["bearing"]:.2f} deg.")

def show_cpas(cpas):
    """function pretty print dict cpa tcpa"""
    for k,v in cpas.items():
       print_cpa(k,v)

def test_tcpa(speed1, speed2, course1, course2):
    """test function for cpa tcpa"""
    course1 = radians(course1)
    course2 = radians(course2)
    dvx = abs(speed1*sin(course1) - speed2*sin(course2))
    dvy = abs(speed1*cos(course1) - speed2*cos(course2))
    print(f"Delta Vx {dvx:.2f}, Delta Vy {dvy:.2f}")

if __name__ == "__main__":
    test_tcpa(5.0, 5.0, 0.0, 180.0)
    test_tcpa(5.0, 5.0,270, 90.0)
    test_tcpa(5.0, 5.0, 0.0, 180.0)
    test_tcpa(5.0, 5.0, 180, 0.0)
    test_tcpa(5.0, 5.0, 90.0, 0.0)
    cpas = dict()
    cpas["211040155"]= cpa_tcpa( 211040155, 53.281733, 7.3981, 180,  2.5,  244030153,  JEMGUM_LAT, JEMGUM_LON, 0, 5.0)
    cpas["211040156"]= cpa_tcpa( 211040156, 53.23472,  7.3947, 180,  3.0,  244030153,  JEMGUM_LAT, JEMGUM_LON, 0, 5.0)
    cpas["211040154"]= cpa_tcpa( 211040154, 53.281733, 7.3981,   0,  5.0,  244030153,  JEMGUM_LAT, JEMGUM_LON, 0, 0.0)
    cpas["211040153"]= cpa_tcpa( 211040153, 53.23540,  7.3949,   0,  10.0,  244030153,  JEMGUM_LAT, JEMGUM_LON, 0, 0.0)
    show_cpas(cpas)
