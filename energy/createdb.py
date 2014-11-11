'''

Creating the database to store the collected energy readings

@author: Agusti Pellicer (Aalto University)

'''

import sqlite3


conn = sqlite3.connect('energy.db')

c = conn.cursor()

c.execute(''' CREATE TABLE energy_readings (circle VARCHAR(255), time DATETIME, reading REAL, comments VARCHAR(255))  ''')

conn.commit()
conn.close()