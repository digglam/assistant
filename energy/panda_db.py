'''

Showing readings from energy db

@author: Agusti Pellicer (Aalto University)

'''

from pandas.io import sql
import sqlite3


connection = sqlite3.connect("energy.db")
query = "SELECT * from energy_readings"
results = sql.read_frame(query,con=connection)
print results.describe()