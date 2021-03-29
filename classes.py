from datetime import datetime, timedelta
import math


class Player():

    def __init__(self, name, username, home, offset):

        self.name = name        # profile name
        self.username = username    # FR24 username
        self.home = home        # home airport
        self.cur_flt = None     # the current flight the player is on
        self.total_dist = 0     # total distance covered
        self.flights = []       # list of all past flights
        self.total_time = 0     # total time of flights
        self.offset = offset    # time offset of the player's pyhsical location as timedelta
        self.cur_airport = None     # The airport the player is currently at
        self.cur_offset = None  # Current virtual offset


class Flight():
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
