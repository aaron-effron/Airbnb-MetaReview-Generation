import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# nplus   n       best score
# 9       8       0.59170059157                   Perfect if you need to be close to the airport
# 8       7       0.59170059157                   Perfect if you need to be close to the airport
# 7       6       0.59170059157                   Perfect if you need to be close to the airport
# 6       5       0.59170059157                   Perfect if you need to be close to the airport
# 5       4       0.59170059157                   Perfect if you need to be close to the airport
# 4       3       0.484504963259                  There have several problems the host needs to improve
# 3       2       0.231475216501/0.425557483188   Oh and the subway station which has shuttle buses
# 2       1       0.231475216501                  Oh and there the talking to Boston Memorial
x = range(1,10)
y = [0.231475216501, 0.425557483188, 0.484504963259, 0.59170059157, 0.59170059157, 0.59170059157, 0.59170059157, 0.59170059157, 0.59170059157]
plt.figure()
plt.plot(x, y,'r')
plt.title("n-gram Size Vs. Best Correlation Score")
plt.xlabel("n-gram Size")
plt.ylabel("Best Correlation Score")
plt.xticks(x)
plt.savefig('ngramVSscore.png')