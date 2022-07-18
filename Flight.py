from datetime import datetime, timedelta
import math
from login import f
import pytz


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
        index (int): The index of the flight in its history. Will be used to
            request status updates instead of looping through the history.
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
            self, airline, short_name, number, plane, reg,
            ori, ori_city, ori_offset, ori_coord,
            dest, dest_city, dest_coord, dest_offset,
            dep_time, arr_time):

        self.airline = airline              # Flight airline
        self.short_name = short_name
        self.number = number                # Flightnumber
        self.plane = plane                  # Full type string
        self.reg = reg                      # Registration
        self.ori = ori                      # Origin IATA
        self.ori_city = ori_city             # City of origin
        # Timezone offset as timedelta
        self.ori_offset = timedelta(seconds=ori_offset)
        self.ori_coord = ori_coord          # Origin coordinates as tuple
        self.dest = dest                    # Destination IATA code
        self.dest_city = dest_city          # Destination city
        self.dest_coord = dest_coord        # Coordinates as tuple
        self.index = None                  # The list index of the flight in its own history
        # Timezone offset as timedelta
        self.dest_offset = timedelta(seconds=dest_offset)
        # Distance calculated from coordinates
        self.distance = self.calc_distance(self.ori_coord, self.dest_coord)
        self.dep_time = pytz.utc.localize(datetime.utcfromtimestamp(
            dep_time))    # Departure time as datetime object UTC (time-zone aware)
        self.arr_time = pytz.utc.localize(datetime.utcfromtimestamp(
            arr_time))    # Arrival time as datetime object UTC (time-zone aware)
        self.duration = self.arr_time - self.dep_time       # Flight time in timedelta
        # Use x = strftime(strftime('%H:%M'), gmtime(diff.seconds)) to get timestring from delta

    def request_state(self):
        """Returns the current state of the flight.

        Returns:
            str: State of the flight. "In flight" if still ongoing,
            "landed" if on the ground.
        """
        x = f.get_history_by_flight_number(
            self.number, page=1, limit=self.index + 5)
        if x[self.index]['status']['generic']['status']['type'] == "departure":
            self.refresh_index()
            self.request_state()
        elif (x[self.index]['status']['generic']['status']['type'] == "arrival"
              and x[self.index]['status']['generic']['status']['text'] != "landed"):
            return "in flight"
        elif (x[self.index]['status']['generic']['status']['text'] == "landed"):
            return "landed"

    def refresh_index(self):
        """Refreshes the index of the active flight.

        It is possible that future flights get added to the list while the
        flight is still active. If this happens, the index needs to be updated.
        """
        x = f.get_history_by_flight_number(self.number, page=1, limit=20)
        for index, item in enumerate(x):
            if item['status']['generic']['status']['type'] == "arrival":
                break
        self.index = index

    # def update_flight(self):
    #     x = f.get_history_by_flight_number(
    #         self.number, page=1, limit=self.index + 5)
    #     self.reg = x[self.index]['aircraft']['registration']
    #     print('updated')

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

        a = math.sin(dlat / 2)**2 + math.cos(lat1) * \
            math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        dist = R * c

        return int(dist)
