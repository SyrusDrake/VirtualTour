import tkinter as tk
from tkinter import ttk
from pyflightdata import FlightData
from datetime import datetime, timedelta
from time import gmtime, strftime
import math

f = FlightData()
f.login("flo.fruehwirth@gmail.com", "Stardust_06189")
airport = 'bsl'


class Flight():
    def __init__(self, airline, number, destination, dest_coord, dep_time, arr_time, duration, plane, reg):
        self.airline = airline
        self.number = number
        self.destination = destination
        self.dest_coord = dest_coord
        self.dep_time = dep_time
        self.arr_time = arr_time
        self.duration = duration
        self.plane = plane
        self.reg = reg


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


class Departures(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.details = f.get_airport_details(airport)
        self.coord = (self.details['position']['latitude'], self.details['position']['longitude'])
        self.board = f.get_airport_departures(airport, limit=100)

        self.tree = ttk.Treeview(container, columns=('one', 'two', 'three'))

        self.tree.heading("#0", text="Flight Number", anchor=tk.W)
        self.tree.heading("#1", text="Airline", anchor=tk.W)
        self.tree.heading("#2", text="Destination", anchor=tk.W)
        self.tree.heading("#3", text="Departure", anchor=tk.W)

        self.tree.column('#0', stretch=tk.YES)
        self.tree.column('#1', stretch=tk.YES)
        self.tree.column('#2', stretch=tk.YES)
        self.tree.column('#3', stretch=tk.YES)

        self.tree.bind('<Double-1>', self.select_flight)

        self.create_flights()

        self.ID = 0
        for i in self.flights:
            self.tree.insert("", "end", self.ID, text=i.number, values=(i.airline, i.destination, i.dep_time))
            self.ID += 1

        self.tree.pack()

        self.details = ttk.Frame(container, borderwidth=1)
        self.details.pack()

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
            if (departure - datetime.now() < timedelta(1)):
                departure = departure.strftime("%H:%M")
                airline = flight['airline']['name']
                flight_number = flight['identification']['number']['default']
                iata = flight['airport']['destination']['code']['iata']
                destination = flight['airport']['destination']['position']['region']['city'] + " (" + iata + ")"
                dest_coord = (flight['airport']['destination']['position']['latitude'], flight['airport']['destination']['position']['longitude'])
                arrival = datetime.fromtimestamp(flight['time']['scheduled']['arrival'])
                arrival = arrival.strftime("%H:%M")
                duration = strftime("%H:%M", gmtime(flight['time']['scheduled']['arrival'] - flight['time']['scheduled']['departure']))
                plane = flight['aircraft']['model']['text']
                reg = flight['aircraft']['registration']
                self.flights.append(Flight(airline, flight_number, destination, dest_coord, departure, arrival, duration, plane, reg))
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
        self.eta_entry.insert(0, flight.arr_time)
        self.duration_entry.delete(0, 'end')
        self.duration_entry.insert(0, flight.duration)
        self.dist_entry.delete(0, 'end')
        self.dist_entry.insert(0, calc_distance(self.coord, flight.dest_coord))

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Flight Game")
        self.geometry('800x400')


app = App()
departures = Departures(app)
app.mainloop()
