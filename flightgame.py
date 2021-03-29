import tkinter as tk
from tkinter import ttk
from pyflightdata import FlightData
from datetime import datetime, timedelta
from time import gmtime, strftime
import time
from classes import Player, Flight
import keyring
import threading
import logging
import sched

formatter = logging.Formatter("%(asctime)s_%(name)s\n%(message)s\n")

bad_flight = logging.getLogger('Bad Flight')
bad_flight.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('diagnostics.log')
file_handler.setFormatter(formatter)
bad_flight.addHandler(file_handler)


# utc_time = int(datetime.utcnow().timestamp())
# usr_time = int(datetime.now().timestamp())
# usr_offset = usr_time - utc_time
utc_time = datetime.utcnow()
usr_time = datetime.now()
usr_offset = usr_time - utc_time
player = Player('Syrus', 'flo.fruehwirth@gmail.com', 'LAX', usr_offset)
f = FlightData()
f.login(player.username, keyring.get_password('FR24', player.username))
airport = player.home
print(f.is_authenticated())


def start_thread(function, delay, *args):
    threading.Timer(delay, function, args).start()


def check_in(evt_time, number):
    scheduler = sched.scheduler(datetime.now, time.sleep)
    evt_time = evt_time + usr_offset
    # lambda needs to target an event so it can be canceled
    # Also, these functions should probably live inside a class...
    threading.Thread(target=lambda: scheduler.enterabs(evt_time, 2, check_dep, [number])).start()
    scheduler.run()
    print(f'Checking in to flight {number}, departing at {evt_time.time()} UTC')


def check_dep(number, limit=30):
    flight = f.get_history_by_flight_number(number, limit=limit)
    now = datetime.now()
    print(f'ping at: {now}')
    for i in flight:
        if i['status']['live'] is True:
            print(i)
            print('is live')
            return

    start_thread(check_dep, 60, number)
    return


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        frames = [
            Start,
            PlayerInfo,
            Departures,
            CurrentFlight
        ]

        # Creates a container for all the pages (should never be visible)
        frame_container = tk.Frame(self, bg='red')
        frame_container.pack(side='top', fill='both', expand=True)
        frame_container.grid_rowconfigure(0, weight=1)
        frame_container.grid_columnconfigure(0, weight=1)

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


class Start(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container, bg='blue')

        self.label = ttk.Label(self, text='hello')
        self.label.pack()

        self.b_Player = ttk.Button(self, text='Player', command=lambda: controller.show_frame('PlayerInfo'))
        self.b_cur_flt = ttk.Button(self, text='Current Flight', command=lambda: controller.show_frame('CurrentFlight'))
        self.b_Departures = ttk.Button(self, text='Departures', command=lambda: controller.show_frame('Departures'))
        self.b_Player.pack()
        self.b_cur_flt.pack()
        self.b_Departures.pack()


class PlayerInfo(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)

        self.label = ttk.Label(self, text=player.name)
        self.label.pack()

        self.b_back = ttk.Button(self, text='Start', command=lambda: controller.show_frame('Start'))
        self.b_back.pack()


class CurrentFlight(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)

        self.b_back = ttk.Button(self, text='Start')


class Departures(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)

        self.details = f.get_airport_details(airport)
        self.iata = self.details['code']['iata']
        self.city = self.details['position']['region']['city']
        self.coord = (self.details['position']['latitude'], self.details['position']['longitude'])
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
            self.tree.insert("", "end", self.ID, text=i.number, values=(i.airline, i.dest_city + '(' + i.dest + ')', (i.dep_time + timedelta(seconds=self.offset)).strftime('%H:%M')))
            self.ID += 1

        self.tree.grid(row=0, column=0)

        self.details = ttk.Frame(self, borderwidth=1)
        self.details.grid(row=1, column=0)

        self.b_checkin = ttk.Button(self, text='Check In', command=lambda: self.check_in(self.flights[int(self.tree.focus())]))
        self.b_checkin.grid(row=2, column=0)

        self.b_back = ttk.Button(self, text='Back', command=lambda: controller.show_frame('Start'))
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
            departure = datetime.fromtimestamp(flight['time']['scheduled']['departure'])
            canceled = False
            if flight['status']['generic']['status']['text'] == 'canceled':
                canceled = True
            if (departure - datetime.now() < timedelta(1)):
                if (canceled is False):
                    try:
                        departure = (flight['time']['scheduled']['departure'] - player.offset.seconds)
                        dest_offset = flight['airport']['destination']['timezone']['offset']
                        airline = flight['airline']['name']
                        flight_number = flight['identification']['number']['default']
                        dest = flight['airport']['destination']['code']['iata']
                        dest_city = flight['airport']['destination']['position']['region']['city']
                        dest_coord = (flight['airport']['destination']['position']['latitude'], flight['airport']['destination']['position']['longitude'])
                        arrival = (flight['time']['scheduled']['arrival'] - player.offset.seconds)
                        plane = flight['aircraft']['model']['text']
                        reg = flight['aircraft']['registration']
                        self.flights.append(Flight(airline, flight_number, plane, reg, self.iata, self.city, self.offset, self.coord, dest, dest_city, dest_coord, dest_offset, departure, arrival))
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
        self.dest_entry.insert(0, flight.dest_city + '(' + flight.dest + ')')
        self.dep_entry.delete(0, 'end')
        self.dep_entry.insert(0, ((flight.dep_time + flight.ori_offset).strftime('%H:%M')))
        self.plane_entry.delete(0, 'end')
        self.plane_entry.insert(0, flight.plane)
        self.reg_entry.delete(0, 'end')
        self.reg_entry.insert(0, flight.reg)
        self.eta_entry.delete(0, 'end')
        self.eta_entry.insert(0, ((flight.arr_time + flight.dest_offset).strftime('%H:%M')))
        self.duration_entry.delete(0, 'end')
        self.duration_entry.insert(0, strftime('%H:%M', gmtime(flight.duration.seconds)))
        self.dist_entry.delete(0, 'end')
        self.dist_entry.insert(0, flight.distance)

    def check_in(self, flight):
        # pass selected flight to Player
        player.cur_flt = flight

        # start countdown and wait for departure
        check_in(flight.dep_time, flight.number)


app = App()
app.geometry('750x500+1400+400')
app.mainloop()
