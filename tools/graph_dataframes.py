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
    if line.split(",")[0] != "":
        stat = float(line.strip().split(",")[1])
        type = line.strip().split(",")[0].split("==")[1].replace('_',' ')

        values[type] = stat

# graph the data
plt.bar(values.keys(), values.values())
plt.title(filename.split("-politeness")[0] + " Politeness Scores")
plt.xlabel("Score")
plt.ylabel("Frequency")
plt.xticks(rotation=45)

for key in values:
    print(f"({key},{round(values[key] * 100, 2)})", end="")

plt.show()