from datetime import datetime, timedelta
import math


class Flight():
    """Flight class

    A class representing a flight the player can take ingame.

    Todo:
        * Define format of "plane" argument (full string or ICAO code)

    Args:
        airline (str): The full name of the flight's airline
        number (str): The flightnumber, usually formated as XX000, although
            this may vary.
        plane (str): The type of plane operating the flight. Exact format yet
                to be decided.
        reg (str): Registration of the plane. Most commonly formated as
            X[X]-XXX[X] or NXXX00, although significant deviation from this
            pattern are possible.
        ori (str): Three-letter IATA code of the departure airport.
        ori_cit (str): City the departure airport is located in.
        ori_offset (int): Time offset from UTC of the city of origin in **seconds**.
        ori_coord (:obj:`tuple` of float): Coordinates of the city of origin.
        dest (str): Three-letter IATA code of the destination airport.
        dest_cit (str): City the destination airport is located in.
        dest_offset(int): Time offset from UTC of the destination in **seconds**.
        dest_coord (:obj:`tuple` of float): Coordinates of the destination.
        dep_time (int): Departure time as a Unix time stamp.
        arr_time (int): Arrival time as a Unix time stamp.

    Attributes:
        ori_offset (:obj:`timedelta`): Time offset from UTC of the city of
            origin as a timedelta object, calculated from the input in seconds.
        dest_offset (:obj:`timedelta`): Time offset from UTC of the destination
            as a timedelta object, calculated from the input in seconds.
        distance (float): Great-circle distance between origin and destination
            based on their respective coordinates.
        dep_time (:obj:`datetime`): Departure time as a UTC datetime object
                calculated from the Unix time stamp.
        arr_time (:obj:`datetime`): Arrival time as a UTC datetime object
                calculated from the Unix time stamp.
        duration (:obj:`timedelta`): Total flight time calculated from departure
            and arrival time.
        """
    def __init__(
            self, airline, number, plane, reg,
            ori, ori_city, ori_offset, ori_coord,
            dest, dest_city, dest_coord, dest_offset,
            dep_time, arr_time):

        self.airline = airline              # Flight airline
        self.number = number                # Flightnumber
        self.plane = plane                  # Full type string
        self.reg = reg                      # Registration
        self.ori = ori                      # Origin IATA
        self.ori_cit = ori_city             # City of origin
        self.ori_offset = timedelta(seconds=ori_offset)    # Timezone offset as timedelta
        self.ori_coord = ori_coord          # Origin coordinates as tuple
        self.dest = dest                    # Destination IATA code
        self.dest_city = dest_city          # Destination city
        self.dest_coord = dest_coord        # Coordinates as tuple
        self.dest_offset = timedelta(seconds=dest_offset)  # Timezone offset as timedelta
        self.distance = self.calc_distance(self.ori_coord, self.dest_coord)  # Distance calculated from coordinates
        self.dep_time = datetime.fromtimestamp(dep_time)    # Departure time as datetime object UTC
        self.arr_time = datetime.fromtimestamp(arr_time)    # Arrival time as datetime object UTC
        self.duration = self.arr_time - self.dep_time       # Flight time in timedelta
        # Use x = strftime(strftime('%H:%M'), gmtime(diff.seconds)) to get timestring from delta

    def calc_distance(self, orig, dest):
        """Distance calculation

        Calculates the great-circle distance between two points on Earth based
        on their coordinates.

        Args:
            orig (:obj:`tuple` of float): Coordinates of the first point
            dest (:obj:`tuple` of float): Coordinates of the second point

        Returns:
            int: Distance in km
        """
        R = 6373

        lat1 = math.radians(orig[0])
        lon1 = math.radians(orig[1])

        lat2 = math.radians(dest[0])
        lon2 = math.radians(dest[1])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        dist = R * c

        return int(dist)
