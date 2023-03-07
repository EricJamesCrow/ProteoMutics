import BedtoolsCommands
import Statistics
import General
import Tools
from pathlib import Path
import multiprocessing as mp
import pandas as pd
from plotnine import *
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

###################################################33 plotnine graph code ##################################33

df = pd.read_csv('/home/cam/Documents/repos/Nucleomutics/src/models/test.txt', sep = '\t', index_col=0, header=0)
# df = df[(np.abs(stats.zscore(df)) < 4).all(axis=1)]
indexes = df.index.tolist()
graph_values = []
for item in indexes:
    graph_values.append(sum(df.loc[item]))

x = np.array(indexes)
y = np.array(graph_values)

smoothed_x, smoothed_y = Tools.smooth_data(x,y)
# print(smoothed_data)

# Create the scatter plot with smaller dots
fig, ax = plt.subplots()
ax.scatter(x, y, s=5)
ax.plot(smoothed_x, smoothed_y, 'r-', lw = 2)

# Set the x-axis and y-axis labels
ax.set_xlabel('X values')
ax.set_ylabel('Y values')

# Set the title of the plot
ax.set_title('Scatter Plot')

# Disable scientific notation on the x-axis
ax.ticklabel_format(axis='x', style='plain')

# Format y-axis tick labels as whole numbers
formatter = plt.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x))
ax.yaxis.set_major_formatter(formatter)

# Set the number of ticks on the y-axis
ax.yaxis.set_major_locator(plt.MaxNLocator(5))

# Display the plot
# plt.savefig('/home/cam/Documents/repos/Nucleomutics/Mutations_nucleosome.png', dpi = 300)
plt.show()