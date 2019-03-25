import numpy as np


# Class of system buses
class Bus:
    def __init__(self, databus):

        bustypes = {'0': 'PQ', '1': 'PV', '2': 'Vθ'}

        self.ID = int(databus[0:4])
        self.name = databus[8:22]
        self.bustype = bustypes[databus[4:8].strip()]

        self.V = float(databus[22:26])/1000
        if databus[26:30].strip():
            self.theta = float(databus[26:30])
        else:
            self.theta = 0

        P = []
        Q = []
        for item in [databus[30:35], databus[56:60]]:
            if not item.strip():
                P.append(0)
            else:
                P.append(float(item))

        for item in [databus[35:40], databus[60:65]]:
            if not item.strip():
                Q.append(0)
            else:
                Q.append(float(item))

        self.P = P[0] - P[1]
        self.Q = Q[0] - Q[1]


# Class of system lines
class Line:
    def __init__(self, origin, destiny, R, X, B):
        self.origin = origin
        self.destiny = destiny
        self.R = R
        self.X = X
        self.B = B


rawData = open("Monticelli_ex5_2.txt", "r").read()
datasets = rawData.split("9999\n")

# Create bus objects
buses = dict()
bus_set = datasets[0].split('\n')

for row in bus_set:
    if row.strip():
        buses[str(int(row[0:4]))] = Bus(row)
