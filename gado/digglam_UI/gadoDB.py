'''

A class for manipulating the database of scanned artifacts

@author: Agusti Pellicer (Aalto University)

'''

import sqlite3
from datetime import datetime

class GadoDB():
	def __init__(self,dbName):

		self.connection = sqlite3.connect(dbName)


	def insertTagsOfArtifact(self,artifact,tags):
		""" Set tags of a given artifact """
		tagsIDs = []
		someTags = self.getTags()
		cursor = self.connection.cursor()
		for id_tag, tag in someTags:
			if tag in tags:
				tagsIDs.append(id_tag)
		query = ''' INSERT INTO artifact_tag VALUES (?, ?)'''
		for id_tag in tagsIDs:
			cursor.execute(query,[artifact, id_tag])
		self.connection.commit()

	def insertArtifact(self,nameFile,run,tags):
		""" Inserts an artifact in the database """
		cursor = self.connection.cursor()
		query = ''' INSERT INTO artifact VALUES(?,?,datetime(?)) '''
		cursor.execute(query, [nameFile + '.tiff', nameFile + '-t.png', run])
		rowid = cursor.lastrowid
		self.connection.commit()
		self.insertTagsOfArtifact(rowid,tags)

	def insertTags(self,tags):
		""" Insert the tags in the database """
		cursor = self.connection.cursor()
		query = ''' INSERT INTO tag VALUES(?) '''
		for tag in tags:
			try:
				cursor.execute(query, [tag])
			except sqlite3.IntegrityError:
				pass
		self.connection.commit()
	def getTags(self):
		""" Just getting the tags """
		cursor = self.connection.cursor()
		query = ''' SELECT ROWID, name FROM tag '''
		tagList = cursor.execute(query).fetchall()
		self.connection.commit()
		return tagList
	def getArtifactsByRun(self, run):
		""" Getting the artifacts of a certain run """
		cursor = self.connection.cursor()
		query = ''' SELECT ROWID,path,thumbnail FROM artifact WHERE run = datetime(?)'''
		artifacts = cursor.execute(query,[run]).fetchall()
		self.connection.commit()
		return artifacts
	def getRuns(self):
		""" Get all the runs in the DB """
		cursor = self.connection.cursor()
		query = ''' SELECT DISTINCT run FROM artifact '''
		runs = cursor.execute(query).fetchall()
		self.connection.commit()
		return runs
	def getArtifacts(self):
		""" Getting the artifacts """
		cursor = self.connection.cursor()
		query = ''' SELECT ROWID, path, thumbnail FROM artifact '''
		artifactList = cursor.execute(query).fetchall()
		self.connection.commit()
		return artifactList
	def getArtifactsByTag(self,tag):
		pass
	def getTagsByArtifact(self,artifact):
		""" Get the tags of an artifact given a certain ID """
		cursor = self.connection.cursor()
		query = ''' SELECT tag_id FROM artifact_tag WHERE artifact_id = ? '''
		#Now we have the ids of the tags
		tag_ids = cursor.execute(query,[artifact]).fetchall()
		self.connection.commit()
		#print tag_ids
		tags = []
		for t_id in tag_ids:
			query = ''' SELECT name FROM tag WHERE ROWID = ? '''
			tag = cursor.execute(query, t_id).fetchall()
			tags.append(tag[0][0])
		self.connection.commit()
		return tags
	def deleteTagsOfArtifact(self,artifact):
		""" Deletes the tags of a certain artifact """
		cursor = self.connection.cursor()
		query = ''' DELETE FROM artifact_tag WHERE artifact_id= ? '''
		cursor.execute(query,[artifact])
		self.connection.commit()

	def getArtifactById(self,artifact):
		""" Given an ID we get the infor of the artifact """
		cursor = self.connection.cursor()
		query = ''' SELECT ROWID, path, thumbnail FROM artifact WHERE ROWID = ? '''
		artifact = cursor.execute(query,[artifact]).fetchall()
		self.connection.commit()
		return artifact

	def setTagsOfArtifact(self,artifact,tags):
		self.deleteTagsOfArtifact(artifact)
		self.insertTags(tags)
		self.insertTagsOfArtifact(artifact,tags)

	def closeDB(self):
		""" Close the connection """
		self.connection.close()

if __name__ == '__main__':
	""" Try the functionality """
	db = GadoDB('prova.db')
	db.insertTags(['bw', 'pictures','day in the park', 'atag','anewtag'])
	db.insertArtifact('anotherpath',datetime.now().isoformat(),['bw', 'day in the park'])
	db.getTagsByArtifact(9)
	#print db.getArtifacts()
	runs = db.getRuns()
	print db.getArtifactsByRun(runs[0][0])
	db.closeDB()