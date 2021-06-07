class Player():
    """Player class, containing all relevant information

    Args:
        name (str): Chosen profile name for ingame use.
        username (str): Username of the player's FR24 profile. Required to log
                in and access additional data.
        home (str): Three-letter IATA code of the player's home airport.
        offset (:obj:`timedelta`): Time offset from UTC of the player's **actual
            physical location**. This does not change through ingame actions!

    Attributes:
        cur_flt(:obj:`Flight`): Current flight the player is on.
        total_dist(int): Total distance covered through all flights combined.
        flights(list of :obj:`Flight`): List of all past flights.
        total_time(:obj:`timedelta`): Sum of all flight times.
        cur_airport(str): Three-letter IATA code of the airport the player is
            currently at.
        cur_offset(:obj:`timedelta`): Current time offset from UTC of the
            player's current *virtual* position. This value changes through
            ingame actions.
        is_chk_in(bool): Whether or not the player is currently checked in
        is_inflight(bool): Whether the player is currently on an active flight
        """

    def __init__(self, name, username, home, offset):

        self.name = name
        self.username = username
        self.home = home
        self.cur_flt = None
        self.total_dist = 0
        self.flights = []
        self.total_time = 0
        self.offset = offset
        self.cur_airport = None
        self.cur_offset = None
        self.is_chk_in = False
        self.is_inflight = False
