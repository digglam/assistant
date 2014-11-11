'''

Collecting and plotting energy readings from Plugwise circles

@author: Agusti Pellicer (Aalto University)

'''

from pandas.io import sql
import sqlite3
import matplotlib.pyplot as plt


#J'S CIRCLES
CIRCLE_PLUS_MAC_2 = "000D6F00036BB2F0"
CIRCLE_MAC_2 = "000D6F00029C2AD3"

connection = sqlite3.connect("gado.db")
query = "SELECT * from artifact"
results = sql.read_frame(query,con=connection)

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.set_title("Energy consumption")
ax.set_ylabel("Watts")
ax.plot(results.energy_robot,'r',label="Laptop")
ax.plot(results.energy_computer,'b',label="digGLAM")


box = ax.get_position()
ax.set_position([box.x0,box.y0,box.width*0.8,box.height])
legend = ax.legend(bbox_to_anchor=(1, 0.5), loc="center left",fancybox=True,shadow=True)

#plt.plot(results[results.circle == CIRCLE_PLUS_MAC].time,results[results.circle == CIRCLE_MAC_1].time,results[results.circle == CIRCLE_MAC_3].time,results[results.circle == CIRCLE_MAC_4].time)
plt.show()
