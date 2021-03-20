import tkinter as tk
from tkinter import ttk
from pyflightdata import FlightData
from datetime import datetime, timedelta
from time import gmtime, strftime
import math
from classes import Player, Flight
import keyring

utc_time = int(datetime.utcnow().timestamp())
usr_time = int(datetime.now().timestamp())
usr_offset = usr_time - utc_time
player = Player('Syrus', 'flo.fruehwirth@gmail.com', 'akl', usr_offset)
f = FlightData()
f.login(player.username, keyring.get_password('FR24', player.username))
airport = player.home
print(f.is_authenticated())

def calc_distance(orig, dest):
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
            self.tree.insert("", "end", self.ID, text=i.number, values=(i.airline, i.destination, datetime.fromtimestamp(i.dep_time + self.offset).strftime('%H:%M')))
            self.ID += 1

        self.tree.grid(row=0, column=0)

        self.details = ttk.Frame(self, borderwidth=1)
        self.details.grid(row=1, column=0)

        self.b_back = ttk.Button(self, text='Back', command=lambda: controller.show_frame('Start'))
        self.b_back.grid(row=2, column=0)

        self.airline_label = ttk.Label(self.details, text="Airline: ")
        self.airline_entry = ttk.Entry(self.details, width=20)

        self.number_label = ttk.Label(self.details, text="Flight Number: ")
        self.number_entry = ttk.Entry(self.details, width=20)

        self.dest_label = ttk.Label(self.details, text="Destination: ")
        self.dest_entry = ttk.Entry(self.details, width=20)

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
        self.plane_label.grid(row=1, column=0)
        self.plane_entry.grid(row=1, column=1)
        self.reg_label.grid(row=1, column=2)
        self.reg_entry.grid(row=1, column=3)
        self.eta_label.grid(row=2, column=0)
        self.eta_entry.grid(row=2, column=1)
        self.duration_label.grid(row=2, column=2)
        self.duration_entry.grid(row=2, column=3)
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
                    departure = (flight['time']['scheduled']['departure'] - player.offset)
                    dest_offset = flight['airport']['destination']['timezone']['offset']
                    airline = flight['airline']['name']
                    flight_number = flight['identification']['number']['default']
                    iata = flight['airport']['destination']['code']['iata']
                    destination = flight['airport']['destination']['position']['region']['city'] + " (" + iata + ")"
                    dest_coord = (flight['airport']['destination']['position']['latitude'], flight['airport']['destination']['position']['longitude'])
                    arrival = (flight['time']['scheduled']['arrival'] - player.offset)
                    duration = (flight['time']['scheduled']['arrival'] - flight['time']['scheduled']['departure'])
                    plane = flight['aircraft']['model']['text']
                    reg = flight['aircraft']['registration']
                    self.flights.append(Flight(airline, flight_number, self.offset, destination, dest_offset, dest_coord, departure, arrival, duration, plane, reg))
            else:
                break

    # def clicker(self, event):
    #     self.select_flight()

    def select_flight(self, event):
        flight = self.flights[int(self.tree.focus())]
        # plane = flight.plane
        # reg = flight.reg
        # distance = calc_distance(self.coord, flight.dest_coord)
        # duration = flight.duration
        # arrival = flight.arr_time

        self.airline_entry.delete(0, 'end')
        self.airline_entry.insert(0, flight.airline)
        self.number_entry.delete(0, 'end')
        self.number_entry.insert(0, flight.number)
        self.dest_entry.delete(0, 'end')
        self.dest_entry.insert(0, flight.destination)
        self.plane_entry.delete(0, 'end')
        self.plane_entry.insert(0, flight.plane)
        self.reg_entry.delete(0, 'end')
        self.reg_entry.insert(0, flight.reg)
        self.eta_entry.delete(0, 'end')
        self.eta_entry.insert(0, (datetime.fromtimestamp(flight.arr_time + flight.dest_offset).strftime('%H:%M')))
        self.duration_entry.delete(0, 'end')
        self.duration_entry.insert(0, strftime('%H:%M', gmtime(flight.duration)))
        self.dist_entry.delete(0, 'end')
        self.dist_entry.insert(0, calc_distance(self.coord, flight.dest_coord))


app = App()
app.geometry('750x500+1400+400')
app.mainloop()
