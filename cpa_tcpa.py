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

def cpa_tcpa(mmsi1, lat1, lon1, course1, speed1,  mmsi2, lat2, lon2, course2, speed2):
    """Function calulating cpa and tcpa."""
    try:
        lat1, lon1 = radians(lat1), radians(lon1)
        lat2, lon2 = radians(lat2), radians(lon2)
        course1 = radians(course1)
        course2 = radians(course2)

        dvx = abs(speed1*sin(course1) - speed2*sin(course2))
        dvy = abs(speed1*cos(course1) - speed2*cos(course2))

        dv = sqrt(dvx**2 + dvy**2)  # relative speed
        if VERBOSE:
            print(f"Relative speed {dv:.4} kn")

        d_lon = lon1 - lon2
        d_lat = lat1 - lat2

        a = sin(d_lat/2)**2 + cos(lat1)*cos(lat2)*sin(d_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c  # in nautical miles

        if VERBOSE:
            print(f"Initial distance {distance:.4} nM")
            print(int(distance/dv * 60) if dv !=0 else "inf", " minutes to CPA at relative speed")

        d_lon = R * c * sin(atan2(d_lon, d_lat)) # in nautical miles
        d_lat = R * c * cos(atan2(d_lon, d_lat)) # in nautical miles

        tcpa = -(d_lat*dvy+ d_lon*dvx)/(dvy**2 + dvx**2)*60
        cpa = abs(d_lon*dvy - d_lat*dvx) / pow(dvy**2 + dvx**2, 0.5)

        #distance = sqrt(d_lon**2 + d_lat**2)
        #print(distance)

        bear = atan2(d_lat,d_lon) if d_lon  != 0 else 0
        bearing = degrees(bear) % 360

        #print(f"Delta lon {d_lon:.4}, delta Vx {dvx:.4}, Delta lat {d_lat:.4}, delta Vy {dvy:.4}")

        return { "cpa": cpa, "tcpa" : tcpa, "mmsi" : mmsi2, "distance": distance, "bearing": bearing }
    except ZeroDivisionError as ex:
        print(ex, mmsi1 )
        return { "cpa": None, "tcpa" : None, "mmsi" : mmsi2, "distance": 0.0, "bearing": 0.0 }

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
    test_tcpa(5.0, 5.0,270,90.0)
    test_tcpa(5.0, 5.0, 0.0, 180.0)
    test_tcpa(5.0, 5.0, 180, 0.0)
    test_tcpa(5.0, 5.0, 90.0, 0.0)
    cpas = dict()
    cpas["211040155"]= cpa_tcpa( 211040155, 53.281733, 7.3981, 180,  2.5,  244030153,  JEMGUM_LAT, JEMGUM_LON, 0, 5.0)
    cpas["211040156"]= cpa_tcpa( 211040156, 53.23472,  7.3947, 180,  3.0,  244030153,  JEMGUM_LAT, JEMGUM_LON, 0, 5.0)
    cpas["211040154"]= cpa_tcpa( 211040154, 53.281733, 7.3981,   0,  5.0,  244030153,  JEMGUM_LAT, JEMGUM_LON, 0, 0.0)
    cpas["211040153"]= cpa_tcpa( 211040153, 53.23540,  7.3949,   0,  10.0,  244030153,  JEMGUM_LAT, JEMGUM_LON, 0, 0.0)
    show_cpas(cpas)
