'''

A class for manipulating the database of energy readings

@author: Agusti Pellicer (Aalto University)

'''

import sqlite3
from datetime import datetime

class EnergyDB():
	def __init__(self,dbName):
		self.connection = sqlite3.connect(dbName)
	def insertReading(self,circle,reading,timestamp,comment):
		cursor = self.connection.cursor()
		query =  ''' INSERT INTO energy_readings VALUES (?, ?, datetime(?), ?)'''
		cursor.execute(query, [circle, reading, timestamp, comment])
		self.connection.commit()
	def getReadings(self):
		cursor = self.connection.cursor()
		query = ''' SELECT * FROM energy_readings '''
		readingList = cursor.execute(query).fetchall()
		self.connection.commit()
		return readingList
	def closeDB(self):
		""" Close the connection """
		self.connection.close()

if __name__ == '__main__':
	""" Try the functionality """
	db = EnergyDB('energy.db')
	db.insertReading("000D6F0000729887", 38.1244, datetime.now().isoformat(), "Gado Robot")
	print db.getReadings()
	db.closeDB()