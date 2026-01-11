"""
geo calculations module
"""
from math import atan, atan2, cos, acos, radians, sin, sqrt, tan, degrees

Rkm = 6371.0  # Radius of earth in kilometers
Rnm = 3440.065  # Radius of earth in nautical miles

JEMGUM_LAT= 53.2644
JEMGUM_LON = 7.3973
JEMGUM = (JEMGUM_LAT,JEMGUM_LON)

NORTH_BORDER = (53.27338,7.3967)
SOUTH_BORDER = (53.25540,7.3949)


def cpa_tcpa(lat1, lon1, course1, speed1,  lat2, lon2, course2, speed2) :
    """Function calculating cpa and tcpa between two moving points."""
    try:
        lat1, lon1 = radians(lat1), radians(lon1)
        lat2, lon2 = radians(lat2), radians(lon2)
        course1 = radians(course1)
        course2 = radians(course2)

        dvx = speed1*sin(course1) - speed2*sin(course2)
        dvy = speed1*cos(course1) - speed2*cos(course2)
        v_rel = sqrt(dvx**2 + dvy**2)  # Relative speed

        d_lon = lon1 - lon2
        d_lat = lat1 - lat2
        
        bear = atan2(d_lat, d_lon) if d_lat != 0 else 0
        bearing =  (degrees(bear) + 360) % 360

        a = sin(d_lat/2)**2 + cos(lat1)*cos(lat2)*sin(d_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = Rnm * c  # in nautical miles
        print(f"Initial distance: {distance:.2f} nM, Relative speed: {v_rel:.2f} kn")
        d_lon = Rnm * c * sin(atan2(d_lon, d_lat)) # in nautical miles
        d_lat = Rnm * c * cos(atan2(d_lon, d_lat)) # in nautical miles
        d = sqrt(d_lon**2 + d_lat**2)
        print(f"Computed distance: {d:.2f} nM and distance from haversine: {distance:.2f} nM")

        tcpa = -(d_lat*dvy + d_lon*dvx) / (dvy**2 + dvx**2)
        cpa = abs(d_lon*dvy - d_lat*dvx) / sqrt(dvy**2 + dvx**2)


        return { "cpa": cpa, "tcpa" : tcpa, 'distance': distance, 'bearing': bearing }
    except ZeroDivisionError as ex:
        print(ex)
        return { "cpa": None, "tcpa" : None, 'distance': 0.0, 'bearing': 0.0 }


# True Bearing = Magnetic Bearing + Magnetic Declination
def bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing between two points on the Earth.

    Parameters:
    lat1, lon1 : float : Latitude and Longitude of point 1 in decimal degrees
    lat2, lon2 : float : Latitude and Longitude of point 2 in decimal degrees

    Returns:
    float : Bearing in degrees from point 1 to point 2
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(dlon))
    initial_bearing = atan2(x, y)

    # Convert from radians to degrees and normalize to 0-360
    initial_bearing = degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on the Earth specified in decimal degrees using the Haversine formula.

    Parameters:
    lat1, lon1 : float : Latitude and Longitude of point 1 in decimal degrees
    lat2, lon2 : float : Latitude and Longitude of point 2 in decimal degrees

    Returns:
    float : Distance between the two points in kilometers
    """
     # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    r = Rnm # Radius of Earth in nautical miles
    distance = r * c

    return distance

def distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on the surface of a sphere
    using the spherical law of cosines.

    Parameters:
    lat1, lon1 : float : Latitude and Longitude of point 1 in decimal degrees
    lat2, lon2 : float : Latitude and Longitude of point 2 in decimal degrees

    Returns:
    float : Distance between the two points in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    distance = acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(dlon)) * Rnm

    return distance

if __name__ == "__main__":
    # Example usage
    lat1, lon1 = 52.2296756, 21.0122287  # Warsaw
    lat2, lon2 = 41.8919300, 12.5113300  # Rome
    lat3, lon3 = 48.8566, 2.3522    # Paris
    lat4, lon4 = 53.5074, 7.0   # London

    print(f"Distance: {haversine(lat1, lon1, lat2, lon2):.2f} nm")
    print(f"Bearing: {bearing(lat1, lon1, lat2, lon2):.2f} degrees")

    lat1, lon1 = 38.9, -77.0 # Washington
    lat2 ,lon2 = 40.7, -74.0 # New York City
    print(f"Distance: {distance(lat1, lon1, lat2, lon2):.2f} nm")
    print(f"Bearing: {bearing(lat1, lon1, lat2, lon2):.2f} degrees")

    d = distance(48.8566, 2.3522, 40.7128, -74.0060)
    print(f"{d:.0f} nm")
    print(cpa_tcpa(48.8566, 2.3522, 90, 20, 40.7128, -74.0060, 270, 15))
    print(cpa_tcpa(53.26379, 7.39738, 180, 15.0, 53.281733, 7.3981, 0, 5.0))
    print(cpa_tcpa(53.281733, 7.39738, 180, 15.0, 53.26379, 7.3981, 0, 5.0))

