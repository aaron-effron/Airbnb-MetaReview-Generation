import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Extracted from various runs of grammarBasedRL
# nplus   n       best score
# 9       8       0.59170059157                   
# 8       7       0.59170059157                  
# 7       6       0.59170059157    
# 6       5       0.59170059157         
# 5       4       0.59170059157            
# 4       3       0.484504963259         
# 3       2       0.425557483188 
# 2       1       0.231475216501

# Plot n vs the best score seen
x = range(1,10)
y = [0.231475216501, 0.425557483188, 0.484504963259, 0.59170059157, 0.59170059157, 0.59170059157, 0.59170059157, 0.59170059157, 0.59170059157]
plt.figure()
plt.plot(x, y,'r')
plt.title("n-gram Size Vs. Best Correlation Score")
plt.xlabel("n-gram Size")
plt.ylabel("Best Correlation Score")
plt.xticks(x)
plt.savefig('ngramVSscore.png')