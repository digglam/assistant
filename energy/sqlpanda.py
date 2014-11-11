'''

@author: Agusti Pellicer (Aalto University)

'''

import matplotlib.pyplot as plt
from pandasql import *
import pandas as pd
 
pysqldf = lambda q: sqldf(q, globals())
 
q  = """
SELECT
  m.date
  , m.beef
  , b.births
FROM
  meat m
LEFT JOIN
  births b
    ON m.date = b.date
WHERE
    m.date > '1974-12-31';
"""
 
meat = load_meat()
births = load_births()
 
df = pysqldf(q)
df.births = df.births.fillna(method='backfill')
 
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(pd.rolling_mean(df['beef'], 12), color='b')
ax1.set_xlabel('months since 1975')
ax1.set_ylabel('cattle slaughtered', color='b')
 
ax2 = ax1.twinx()
ax2.plot(pd.rolling_mean(df['births'], 12), color='r')
ax2.set_ylabel('babies born', color='r')
plt.title("Beef Consumption and the Birth Rate")
plt.show()