'''

Creating the database with sqlite3

@author: Agusti Pellicer (Aalto University)

'''

import sqlite3


conn = sqlite3.connect('gado.db')

c = conn.cursor()

c.execute(''' CREATE TABLE artifact (path VARCHAR(255), thumbnail VARCHAR(255), run DATETIME)  ''')
c.execute(''' CREATE TABLE tag (name VARCHAR(100) UNIQUE) ''')
c.execute(''' CREATE TABLE artifact_tag(
  artifact_id INTEGER,
  tag_id INTEGER,
  FOREIGN KEY(artifact_id) REFERENCES artifact(ROWID),
  FOREIGN KEY(tag_id) REFERENCES tag(ROWID),
  PRIMARY KEY (artifact_id, tag_id)
)''')
#c.execute(''' CREATE TABLE artifacttag (FOREIGN KEY(artifactid) REFERENCES artifact(ROWID), FOREIGN KEY(tagid) REFERENCES tag(ROWID)) ''')
conn.commit()
conn.close()