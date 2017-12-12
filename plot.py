import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# nplus   n       best score
# 6       5       0.59170059157
# 5       4       0.59170059157
# 4       3       0.5
# 3       2       0.231475216501
# 2       1       0.231475216501
x = range(1,6)
y = [0.231475216501, 0.231475216501, 0.5, 0.59170059157, 0.59170059157]
plt.figure()
plt.plot(x, y,'r')
plt.title("n-gram Size Vs. Best Correlation Score")
plt.xlabel("n-gram Size")
plt.ylabel("Best Correlation Score")
plt.xticks(x)
plt.savefig('ngramVSscore.png')