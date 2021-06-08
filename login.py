from pyflightdata import FlightData
import keyring

f = FlightData()
f.login("flo.fruehwirth@gmail.com", keyring.get_password('FR24', 'flo.fruehwirth@gmail.com'))
