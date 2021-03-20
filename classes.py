class Player():

    def __init__(self, name, username, home, offset):

        self.name = name        # profile name
        self.username = username    # FR24 username
        self.home = home        # home airport
        self.cur_flt = None     # the current flight the player is on
        self.total_dist = 0     # total distance covered
        self.flights = []       # list of all past flights
        self.total_time = 0     # total time of flights
        self.offset = offset

class Flight():
    def __init__(self, airline, number, ori_offset, destination, dest_offset, dest_coord, dep_time, arr_time, duration, plane, reg):
        self.airline = airline
        self.number = number
        self.plane = plane
        self.reg = reg
        self.destination = destination
        self.dest_coord = dest_coord
        self.ori_offset = ori_offset
        self.dest_offset = dest_offset
        self.dep_time = dep_time
        self.arr_time = arr_time
        self.duration = duration
