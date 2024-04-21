# graphing
import matplotlib.pyplot as plt
import sys

values = {}

# take in csv from args
if len(sys.argv) != 2:
    print("Usage: python3 graph.py <csv file>")
    sys.exit(1)

filename = sys.argv[1]

for line in open(filename):
    stat = float(line.strip().split(",")[1])

    # from 0 load each count into a dictionary grouped by increments of 0.02
    # i.e. 0.23 would fit into range "0.22 - 0.24"
    # stat = -.03 would fit into range "-0.04 - -0.02"
    # they key will simply be the lower bound of the range
    # so the key for 0.23 would be "0.22" and the key for -.03 would be "-0.04"
    # if the key doesn't exist, create it and set the value to 1
    # if the key does exist, increment the value by 1
    key = str(int(stat * 50) / 50)
    if key not in values:
        values[key] = 1
    else:
        values[key] += 1

# sort the dictionary by key numerically
values = dict(sorted(values.items(), key=lambda x: float(x[0])))

values_percent = {}
# calculate the percentage of each score
for key in values:
    values_percent[key] = values[key] / sum(values.values())

# print the data
for key in values_percent:
    print(f"({key},{round(values_percent[key] * 100, 2)})", end="")

# plot the data
plt.bar(values_percent.keys(), values_percent.values())
plt.title(filename.split("-politeness")[0] + " Politeness Scores")
plt.xlabel("Score")
plt.ylabel("Frequency")
plt.xticks(rotation=45)





plt.show()