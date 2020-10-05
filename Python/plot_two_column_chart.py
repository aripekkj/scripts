# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 08:33:55 2020

@author: aripekkj
"""

import pandas as pd
import matplotlib.pyplot as plt


# filepath
fp = r"E:/LocalData/aripekkj/ProtectedAreas/Madagascar/Tourist_data/visitor_some_join_selected_columns.csv"

# read file
df = pd.read_csv(fp)

# sort df by 'NAME'
df = df.sort_values(by='NAME', ascending=True)

# output image filepath
img_out = r'E:/LocalData/aripekkj/ProtectedAreas/Madagascar/Tourist_data/visitor_sums_fig.png'

# plot
fig = plt.figure() # Create matplotlib figure

ax = fig.add_subplot(111) # Create matplotlib axes
ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.

width = 0.4

f = df.plot('NAME', 'flickr_sum', kind='bar', color='red', ax=ax, width=width, fontsize=3, position=1, legend=False, label='Flickr sum')
m = df.plot('NAME', 'mnp_sum', kind='bar', color='blue', ax=ax2, width=width, fontsize=3, position=0, legend=False, label= 'MNP sum')

# legends
ax.legend(bbox_to_anchor=(0, 1), loc='upper left', fontsize='xx-small')
ax2.legend(bbox_to_anchor=(0,0.8), loc='upper left', fontsize='xx-small')

# set y- ticks
ax.set_yticks(list(range(0, max(df.flickr_sum), 10)), minor=True)
ax2.set_yticks(list(range(0, max(df.mnp_sum), 10000)), minor=True)

# set labels
ax.set_ylabel('Flickr sum', fontsize=5)
ax2.set_ylabel('Official visitor sum', fontsize=5)
ax.set_xlabel('Protected area')

# grid
ax.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

# title
ax.set_title('Visitors on Madagascar protected areas')

fig.tight_layout(pad=5)
#plt.show()
plt.savefig(img_out, dpi=600)
