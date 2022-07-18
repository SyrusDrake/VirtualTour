from itertools import filterfalse
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from time import gmtime, strftime, sleep
import time
import tkinter
from Player import Player
from Flight import Flight
from login import f
import threading
import logging
import sched
import pytz

# Sets up logger to record all bad flights.
formatter = logging.Formatter("%(asctime)s_%(name)s\n%(message)s\n")

bad_flight = logging.getLogger('Bad Flight')
bad_flight.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('diagnostics.log')
file_handler.setFormatter(formatter)
bad_flight.addHandler(file_handler)


player = Player('Syrus', 'flo.fruehwirth@gmail.com', 'BSL')
player.update_airport('HND')
print(f.is_authenticated())


def start_thread(function, delay, *args):
    """Threading is required to wait for event (eg. departure) while still
    allowing the app to be used.
    Args:
        function: Function to be executed in the thread.
        delay (int): Frequency with which the function should be executed.
        *args: Arguments passed to the function.
    """
    threading.Timer(delay, function, args).start()


def check_dep(number, limit=30):
    """Checks if flight has departed.
    When a flight departs, its status bool is set to True. This function checks
    for this change. If the flight has not gone live, the function will
    restart itself in a background thread and check again in one minute.
    Args:
        number (str): The flight number of the flight to be checked.
        limit (int): Defaults to 30. The length of the flight history list. This
            is necessary because the current flight is not always the first
            flight in the list. Future flights may be above. Most flights will
            require limits well below 30.
    """
    flight = f.get_history_by_flight_number(number, limit=limit)
    now = datetime.now()
    print(f'ping at: {now}')
    for index, item in enumerate(flight):
        if item['status']['live'] is True:
            print(item)
            print('is live')
            player.is_inflight = True
            player.cur_flt.index = index
            return

    start_thread(check_dep, 60, number)
    return


class App(tk.Tk):

    """The main class that starts the app and keeps it running.
    In this class, the frames are created, as well as the functions to switch
    between them.
    """

    def __init__(self):
        tk.Tk.__init__(self)

        self.utc = None
        self.home = None
        self.cur = None

        self.time()

        frames = [
            Start,
            Info,
            Departures
        ]

        # Creates a container for all the pages (should never be visible)
        time_frame = tk.Frame(self, bg='yellow')
        frame_container = tk.Frame(self, bg='red')
        time_frame.pack(side='top', fill='both')
        time_frame.grid_columnconfigure(0, weight=1)
        time_frame.grid_columnconfigure(1, weight=1)
        time_frame.grid_columnconfigure(2, weight=1)
        frame_container.pack(side='top', fill='both', expand=True)
        frame_container.grid_rowconfigure(0, weight=1)
        frame_container.grid_columnconfigure(0, weight=1)

        self.utc_time = tk.Label(time_frame)
        self.local_time = tk.Label(time_frame, bg='red')
        self.virt_time = tk.Label(time_frame)
        self.utc_time.grid(row=0, column=0, sticky='nsew')
        self.local_time.grid(row=0, column=1, sticky='nsew')
        self.virt_time.grid(row=0, column=2, sticky='nsew')
        self.print_time()

        # Initiates a dictionary of frames
        self.framedict = {}

        # Fills the dictionary. Keys=names defined above; values=instances of the classes below
        for frame in (frames):
            name = frame.__name__  # The name of the class currently being called
            new_frame = frame(container=frame_container, controller=self)
            self.framedict[name] = new_frame
            new_frame.grid(row=0, column=0, sticky='nsew')
            # new_frame.pack()

        # Starts the app with the start page
        self.show_frame('Start')

        # Function that calls up any frame in the dictionary
    def show_frame(self, page_name):
        frame = self.framedict[page_name]
        frame.tkraise()

    def time(self):
        """Updates time
        Updates time and sets UTC, real time, and virtual time
        """
        self.utc = pytz.utc.localize(datetime.utcnow())
        self.home = self.utc.astimezone(pytz.timezone(player.tz))
        self.cur = self.utc.astimezone(pytz.timezone(player.cur_tz))

    def print_time(self):
        """Prints all three times at the top of the window
        """
        self.time()
        utc = self.utc.strftime('%H:%M:%S %Z')
        local = self.home.strftime('%H:%M:%S %Z')
        vrt = self.cur.strftime('%H:%M:%S %Z')
        self.utc_time.config(text=f'UTC: {utc}')
        self.local_time.config(text=f'LCL: {local}')
        self.virt_time.config(text=f'VRT: {vrt}')
        self.after(1000, self.print_time)


class Start(tk.Frame):

    """Start page w/ navigation to other pages
    Args:
        container (:obj:`tk.Frame`): "Master"-Frame into which the frame is
            loaded.
        controller (:obj:`class`): Controller-class in which the frame-switching
            function is defined.
    """

    def __init__(self, container, controller):
        tk.Frame.__init__(self, container, bg='blue')

        self.label = ttk.Label(self, text='hello')
        self.label.pack()

        self.b_Info = ttk.Button(
            self, text='Info', command=lambda: controller.show_frame('Info'))
        self.b_Departures = ttk.Button(
            self, text='Departures', command=lambda: controller.show_frame('Departures'))
        self.b_Info.pack()
        self.b_Departures.pack()


class Info(tk.Frame):

    """General Info Page
    Args:
        container (:obj:`tk.Frame`): "Master"-Frame into which the frame is
            loaded.
        controller (:obj:`class`): Controller-class in which the frame-switching
            function is defined.
    """

    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)

        self.player_frame = tk.Frame(self, bg='yellow')
        self.flight_frame = tk.Frame(self, bg='blue')
        self.b_cancel = ttk.Button(
            self, text='Check out', command=player.check_out)
        self.b_back = ttk.Button(
            self, text='Back', command=lambda: controller.show_frame('Start'))
        self.b_test = ttk.Button(
            self, text='Test', command=self.update_info)

        self.player_frame.grid(row=0, column=0, sticky='nsew')
        self.flight_frame.grid(row=0, column=1, sticky='nsew')
        self.b_back.grid(row=1, column=0, sticky='n')
        self.b_cancel.grid(row=1, column=1, sticky='n')
        self.b_test.grid(row=1, column=2, sticky='n')

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.p_header = ttk.Label(self.player_frame, text='Player Info')
        self.p_name_label = ttk.Label(
            self.player_frame, text="Name: ", width=20)
        self.p_name_entry = ttk.Label(
            self.player_frame, width=20, background='white', relief='ridge')
        self.p_home_label = ttk.Label(self.player_frame, text="Home: ")
        self.p_home_entry = ttk.Label(
            self.player_frame, width=20, background='white', relief='ridge')
        self.p_dist_label = ttk.Label(self.player_frame, text="Distance: ")
        self.p_dist_entry = ttk.Label(
            self.player_frame, width=20, background='white', relief='ridge')
        self.p_time_label = ttk.Label(
            self.player_frame, text="Total Flight Time: ")
        self.p_time_entry = ttk.Label(
            self.player_frame, width=20, background='white', relief='ridge')
        self.p_curap_label = ttk.Label(
            self.player_frame, text="Current Airport: ")
        self.p_curap_entry = ttk.Label(
            self.player_frame, width=20, background='white', relief='ridge')

        self.p_header.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.p_name_label.grid(row=1, column=0)
        self.p_name_entry.grid(row=1, column=1)
        self.p_home_label.grid(row=2, column=0)
        self.p_home_entry.grid(row=2, column=1)
        self.p_dist_label.grid(row=3, column=0)
        self.p_dist_entry.grid(row=3, column=1)
        self.p_time_label.grid(row=4, column=0)
        self.p_time_entry.grid(row=4, column=1)
        self.p_curap_label.grid(row=5, column=0)
        self.p_curap_entry.grid(row=5, column=1)

        self.flight_header = ttk.Label(
            self.flight_frame, text='Current Flight Info')
        self.f_curflight_label = ttk.Label(
            self.flight_frame, text="Flight Number: ", width=20)
        self.f_curflight_entry = ttk.Label(
            self.flight_frame, width=20, background='white', relief='ridge')
        self.f_reg_label = ttk.Label(
            self.flight_frame, text="Registration: ", width=20)
        self.f_reg_entry = ttk.Label(
            self.flight_frame, width=20, background='white', relief='ridge')
        self.f_ori_label = ttk.Label(
            self.flight_frame, text="Origin: ", width=20)
        self.f_ori_entry = ttk.Label(
            self.flight_frame, width=20, background='white', relief='ridge')
        self.f_dest_label = ttk.Label(
            self.flight_frame, text="Destination: ", width=20)
        self.f_dest_entry = ttk.Label(
            self.flight_frame, width=20, background='white', relief='ridge')
        self.f_eta_label = ttk.Label(
            self.flight_frame, text="ETA: ", width=20)
        self.f_eta_entry = ttk.Label(
            self.flight_frame, width=20, background='white', relief='ridge')
        self.f_remaining_label = ttk.Label(
            self.flight_frame, text="Time left (approx.): ", width=20)
        self.f_remaining_entry = ttk.Label(
            self.flight_frame, width=20, background='white', relief='ridge')
        self.f_index_label = ttk.Label(
            self.flight_frame, text="Current index: ", width=20)
        self.f_index_entry = ttk.Label(
            self.flight_frame, width=20, background='white', relief='ridge')
        self.f_state_label = ttk.Label(
            self.flight_frame, text="Current state: ", width=20)
        self.f_state_entry = ttk.Label(
            self.flight_frame, width=20, background='white', relief='ridge')

        self.flight_header.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.f_curflight_label.grid(row=1, column=0)
        self.f_curflight_entry.grid(row=1, column=1)
        self.f_reg_label.grid(row=2, column=0)
        self.f_reg_entry.grid(row=2, column=1)
        self.f_ori_label.grid(row=3, column=0)
        self.f_ori_entry.grid(row=3, column=1)
        self.f_dest_label.grid(row=4, column=0)
        self.f_dest_entry.grid(row=4, column=1)
        self.f_eta_label.grid(row=5, column=0)
        self.f_eta_entry.grid(row=5, column=1)
        self.f_remaining_label.grid(row=6, column=0)
        self.f_remaining_entry.grid(row=6, column=1)
        self.f_index_label.grid(row=7, column=0)
        self.f_index_entry.grid(row=7, column=1)
        self.f_state_label.grid(row=8, column=0)
        self.f_state_entry.grid(row=8, column=1)

        # self.update_info()

    def update_info(self):

        self.flight = player.cur_flt

        self.p_name_entry.config(text=player.name)
        self.p_home_entry.config(text=player.home)
        self.p_dist_entry.config(text=player.total_dist)
        self.p_time_entry.config(text=player.total_time)
        self.p_curap_entry.config(text=player.cur_airport)

        # try:
        # self.flight.refresh_index()
        self.f_curflight_entry.config(
            text=self.flight.short_name + ' ' + self.flight.number)
        self.f_reg_entry.config(text=self.flight.reg)
        self.f_ori_entry.config(
            text=self.flight.ori_city + ' (' + self.flight.ori + ')')
        self.f_dest_entry.config(
            text=self.flight.dest_city + ' (' + self.flight.dest + ')')
        self.f_index_entry.config(text=self.flight.index)
        self.f_state_entry.config(text=self.flight.refresh_index())

        # except Exception:
        #     print('exc')
        #     self.f_curflight_entry.config(text='NIL')
        #     self.f_reg_entry.config(text='')
        #     self.f_ori_entry.config(text='')
        #     self.f_dest_entry.config(text='')
        #     self.f_index_entry.config(text='')
        #     self.f_state_entry.config(text='')

        self.after(1000, self.update_info)


class Departures(tk.Frame):
    """Departure screen
    Shows a list of all the upcoming departures from the current airport.
    Args:
        container (:obj:`tk.Frame`): "Master"-Frame into which the frame is
            loaded.
        controller (:obj:`class`): Controller-class in which the frame-switching
            function is defined.
    """

    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)

        airport = player.cur_airport
        self.details = f.get_airport_details(airport)
        self.iata = self.details['code']['iata']
        self.city = self.details['position']['region']['city']
        self.coord = (self.details['position']['latitude'],
                      self.details['position']['longitude'])
        self.offset = self.details['timezone']['offset']
        self.board = f.get_airport_departures(airport, limit=100)

        self.tree = ttk.Treeview(self, columns=('one', 'two', 'three'))

        self.tree.heading("#0", text="Flight Number", anchor=tk.W)
        self.tree.heading("#1", text="Airline", anchor=tk.W)
        self.tree.heading("#2", text="Destination", anchor=tk.W)
        self.tree.heading("#3", text="Departure", anchor=tk.W)

        self.tree.column('#0', stretch=tk.YES)
        self.tree.column('#1', stretch=tk.YES)
        self.tree.column('#2', stretch=tk.YES)
        self.tree.column('#3', stretch=tk.YES)

        self.tree.bind('<ButtonRelease-1>', self.select_flight)

        self.create_flights()

        self.ID = 0
        for i in self.flights:
            self.tree.insert("", "end", self.ID, text=i.number, values=(
                i.airline, i.dest_city + '(' + i.dest + ')', (i.dep_time + timedelta(seconds=self.offset)).strftime('%H:%M')))
            self.ID += 1

        self.tree.grid(row=0, column=0)

        self.details = ttk.Frame(self, borderwidth=1)
        self.details.grid(row=1, column=0)

        self.b_checkin = ttk.Button(self, text='Check In', command=lambda: self.check_in(
            self.flights[int(self.tree.focus())]))
        self.b_checkin.grid(row=2, column=0)

        self.b_back = ttk.Button(
            self, text='Back', command=lambda: controller.show_frame('Start'))
        self.b_back.grid(row=3, column=0)

        self.airline_label = ttk.Label(self.details, text="Airline: ")
        self.airline_entry = ttk.Entry(self.details, width=20)

        self.number_label = ttk.Label(self.details, text="Flight Number: ")
        self.number_entry = ttk.Entry(self.details, width=20)

        self.dest_label = ttk.Label(self.details, text="Destination: ")
        self.dest_entry = ttk.Entry(self.details, width=20)

        self.dep_label = ttk.Label(self.details, text="Departure: ")
        self.dep_entry = ttk.Entry(self.details, width=20)

        self.plane_label = ttk.Label(self.details, text="Plane: ")
        self.plane_entry = ttk.Entry(self.details, width=20)

        self.reg_label = ttk.Label(self.details, text="Registration: ")
        self.reg_entry = ttk.Entry(self.details, width=20)

        self.eta_label = ttk.Label(self.details, text="ETA: ")
        self.eta_entry = ttk.Entry(self.details, width=20)

        self.duration_label = ttk.Label(self.details, text="Duration: ")
        self.duration_entry = ttk.Entry(self.details, width=20)

        self.dist_label = ttk.Label(self.details, text="Distance (km): ")
        self.dist_entry = ttk.Entry(self.details, width=20)

        self.airline_label.grid(row=0, column=0)
        self.airline_entry.grid(row=0, column=1)
        self.number_label.grid(row=0, column=2)
        self.number_entry.grid(row=0, column=3)
        self.dest_label.grid(row=0, column=4)
        self.dest_entry.grid(row=0, column=5)
        self.dep_label.grid(row=1, column=0)
        self.dep_entry.grid(row=1, column=1)
        self.eta_label.grid(row=1, column=2)
        self.eta_entry.grid(row=1, column=3)
        self.duration_label.grid(row=1, column=4)
        self.duration_entry.grid(row=1, column=5)
        self.plane_label.grid(row=2, column=0)
        self.plane_entry.grid(row=2, column=1)
        self.reg_label.grid(row=2, column=2)
        self.reg_entry.grid(row=2, column=3)
        self.dist_label.grid(row=2, column=4)
        self.dist_entry.grid(row=2, column=5)

    def create_flights(self):
        self.flights = []
        for i in self.board:
            flight = i['flight']
            departure = datetime.fromtimestamp(
                flight['time']['scheduled']['departure'])
            canceled = False
            if flight['status']['generic']['status']['text'] == 'canceled':
                canceled = True
            if (departure - datetime.now() < timedelta(1)):
                if (canceled is False):
                    try:
                        departure = (flight['time']['scheduled']
                                     ['departure'])
                        dest_offset = flight['airport']['destination']['timezone']['offset']
                        airline = flight['airline']['name']
                        short = flight['airline']['short']
                        flight_number = flight['identification']['number']['default']
                        dest = flight['airport']['destination']['code']['iata']
                        dest_city = flight['airport']['destination']['position']['region']['city']
                        dest_coord = (flight['airport']['destination']['position']['latitude'],
                                      flight['airport']['destination']['position']['longitude'])
                        arrival = (flight['time']['scheduled']
                                   ['arrival'])
                        plane = flight['aircraft']['model']['text']
                        reg = flight['aircraft']['registration']
                        self.flights.append(Flight(airline, short, flight_number, plane, reg, self.iata, self.city,
                                            self.offset, self.coord, dest, dest_city, dest_coord, dest_offset, departure, arrival))
                    except Exception:
                        bad_flight.debug(flight)

            else:
                break

    def select_flight(self, event):
        flight = self.flights[int(self.tree.focus())]

        self.airline_entry.delete(0, 'end')
        self.airline_entry.insert(0, flight.airline)
        self.number_entry.delete(0, 'end')
        self.number_entry.insert(0, flight.number)
        self.dest_entry.delete(0, 'end')
        self.dest_entry.insert(0, flight.dest_city + ' (' + flight.dest + ')')
        self.dep_entry.delete(0, 'end')
        self.dep_entry.insert(
            0, ((flight.dep_time + flight.ori_offset).strftime('%H:%M')))
        self.plane_entry.delete(0, 'end')
        self.plane_entry.insert(0, flight.plane)
        self.reg_entry.delete(0, 'end')
        self.reg_entry.insert(0, flight.reg)
        self.eta_entry.delete(0, 'end')
        self.eta_entry.insert(
            0, ((flight.arr_time + flight.dest_offset).strftime('%H:%M')))
        self.duration_entry.delete(0, 'end')
        self.duration_entry.insert(0, strftime(
            '%H:%M', gmtime(flight.duration.seconds)))
        self.dist_entry.delete(0, 'end')
        self.dist_entry.insert(0, flight.distance)

    def check_in(self, flight):
        """Sets the active flight for the player and waits for departure.
        `player_cur_flt` will be set to the selected flight (object).
        A scheduler will be set that waits until the *scheduled* departure of
        the flight. Once that time is reached, the program will check every
        60 seconds if the flight has gone live.
        If the player is already checked in to a flight, an error will be displayed.
        Args:
            flight (:obj:`Flight`): The flight selected
        """
        # pass selected flight to Player
        if player.is_chk_in is True:
            tk.messagebox.showerror(
                title='Already checked in', message=f'You area already checked into flight {player.cur_flt.number}. Please check out first if you want to change your flight.')
            pass
        else:
            player.cur_flt = flight
            player.is_chk_in = True
            player.standby = True
            # start countdown and wait for departure
            print(
                f'Checking in to flight {flight.number}, departing at {flight.dep_time.time()} UTC')
            self.standby_thread = threading.Thread(
                target=self.stand_by, args=(flight.dep_time, flight.number))
            self.standby_thread.start()

    def stand_by(self, evt_time, number):
        """Waiting for scheduled time
        Starts a separate thread that will regularly check if a specific time is reached. Once that time is reached, the program will regularly check if the state of the flight has changed as expected.
        Todo:
            * Storing schedule times in the `Flight` class as a Unix timestamp
              might be more convenient.
        Args:
            evt_time (:obj:`datetime`): The scheduled time of the status change.
                Schedulers need Unix timestamps, so this has to be converted
                inside the function.
            number (str): Flight number of the flight that should be observed.
                This function itself does not need it but it has to be passed on
                as an argument.
        """

        # Changes the even time from UTC to player time actual
        target_time = evt_time.astimezone(pytz.timezone(player.tz))
        current_time = pytz.utc.localize(
            datetime.utcnow()).astimezone(pytz.timezone(player.tz))

        if current_time < target_time and player.standby is True:
            time.sleep(1)
            print('still waiting...')
            self.standby_thread = threading.Thread(
                target=self.stand_by, args=(evt_time, number))
            self.standby_thread.start()
        elif player.standby is False:
            print('Timer has been stopped')
        else:
            player.standby = False
            print('Flight should be departing any minute.')
            check_dep(number)


if __name__ == '__main__':
    app = App()
    app.geometry('750x500+1400+400')
    app.mainloop()
