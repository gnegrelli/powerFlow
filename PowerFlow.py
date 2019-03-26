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

        p = []
        q = []
        for item in [databus[30:35], databus[56:60]]:
            if not item.strip():
                p.append(0)
            else:
                p.append(float(item))

        for item in [databus[35:40], databus[60:65]]:
            if not item.strip():
                q.append(0)
            else:
                q.append(float(item))

        self.P = (p[0] - p[1])/Sb
        self.Q = (q[0] - q[1])/Sb

    # Function to refresh values of voltage and angle on buses
    def refresh(self, ang, v):
        print("I'm here!")
        if self.bustype == 'PQ':
            self.theta += ang
            self.V += v
        elif self.bustype == 'PV':
            self.theta += ang


# Class of system lines
class Line:

    def __init__(self, dataline):

        self.origin = int(dataline[0:4].strip())
        self.destiny = int(dataline[4:12].strip())

        if dataline[16:23].strip():
            self.R = float(dataline[16:23])/100
        else:
            self.R = 0

        if dataline[23:29].strip():
            self.X = float(dataline[23:29])/100
        else:
            self.X = 0

        if dataline[29:35].strip():
            self.B = float(dataline[29:35])/100
        else:
            self.B = 0


# Base Power
Sb = 100

# rawData = open("Monticelli_ex5_2.txt", "r").read()
rawData = open("example.txt", "r").read()
datasets = rawData.split("9999\n")

# Create bus objects
buses = dict()
bus_set = datasets[0].split('\n')

for row in bus_set:
    if row.strip():
        buses[str(int(row[0:4]))] = Bus(row)

# Create line objects
lines = dict()
line_set = datasets[1].split("\n")

for row in line_set:
    if row.strip():
        lines[row[0:4].strip() + "-" + row[4:12].strip()] = Line(row)

# Nodal Admittance Matrix
Ybus = np.zeros((len(buses), len(buses)), dtype=complex)

# Shunt Elements Vector
Bshunt = np.zeros(len(buses), dtype=complex)

for key in lines.keys():
    Ybus[lines[key].origin - 1][lines[key].destiny - 1] = -1/(lines[key].R + 1j*lines[key].X)
    Bshunt[lines[key].origin - 1] += 1j*lines[key].B/2
    Bshunt[lines[key].destiny - 1] += 1j*lines[key].B/2

Ybus += Ybus.T

np.fill_diagonal(Ybus, Bshunt - np.sum(Ybus, axis=1))

# Flat Start
for key in buses.keys():
    if buses[key].bustype == 'PQ':
        buses[key].V = 1
        buses[key].theta = 0
    elif buses[key].bustype == 'PV':
        buses[key].theta = 0

#
P = np.zeros(len(buses))
Q = np.zeros(len(buses))

# Mismatches
misP = np.zeros(len(buses))
misQ = np.zeros(len(buses))

for bus in range(len(buses)):
    for otherbus in range(len(buses)):

        # Calculate angle difference
        theta_km = buses[str(bus + 1)].theta - buses[str(otherbus + 1)].theta

        # Calculate active and reactive power reaching bus
        P[bus] += buses[str(bus+1)].V*buses[str(otherbus+1)].V*(np.real(Ybus[bus, otherbus])*np.cos(theta_km) + np.imag(Ybus[bus, otherbus]*np.sin(theta_km)))
        Q[bus] += buses[str(bus+1)].V*buses[str(otherbus+1)].V*(np.real(Ybus[bus, otherbus])*np.sin(theta_km) - np.imag(Ybus[bus, otherbus]*np.cos(theta_km)))

    if buses[str(bus+1)].bustype == 'PQ':
        misP[bus] = buses[str(bus+1)].P - P[bus]
        misQ[bus] = buses[str(bus+1)].Q - Q[bus]
    elif buses[str(bus+1)].bustype == 'PV':
        misP[bus] = buses[str(bus+1)].P - P[bus]

# Mismatch vector
mis = np.vstack((np.array([misP]).T, np.array([misQ]).T,))

# Create Jacobian Submatrices
H = np.zeros((len(buses), len(buses)))
N = np.zeros((len(buses), len(buses)))
M = np.zeros((len(buses), len(buses)))
L = np.zeros((len(buses), len(buses)))

# Calculate Jacobian Submatrices
for bus in range(len(buses)):
    for otherbus in range(len(buses)):

        # Calculate angle difference
        theta_km = buses[str(bus + 1)].theta - buses[str(otherbus + 1)].theta

        if bus is not otherbus:
            H[bus, otherbus] = buses[str(bus+1)].V*buses[str(otherbus+1)].V*(np.real(Ybus[bus, otherbus])*np.sin(theta_km) - np.imag(Ybus[bus, otherbus]*np.cos(theta_km)))
            N[bus, otherbus] = buses[str(bus+1)].V*(np.real(Ybus[bus, otherbus])*np.cos(theta_km) + np.imag(Ybus[bus, otherbus]*np.sin(theta_km)))
            M[bus, otherbus] = -buses[str(bus+1)].V*buses[str(otherbus+1)].V*(np.real(Ybus[bus, otherbus])*np.cos(theta_km) + np.imag(Ybus[bus, otherbus]*np.sin(theta_km)))
            L[bus, otherbus] = buses[str(bus+1)].V*(np.real(Ybus[bus, otherbus])*np.sin(theta_km) - np.imag(Ybus[bus, otherbus]*np.cos(theta_km)))
        else:
            if buses[str(bus+1)].bustype == 'Vθ':
                H[bus, otherbus] = 10**99
            else:
                H[bus, otherbus] = -Q[bus] - (buses[str(bus+1)].V**2)*np.imag(Ybus[bus, bus])
            N[bus, otherbus] = (P[bus] + (buses[str(bus+1)].V**2)*np.real(Ybus[bus, bus]))/buses[str(bus+1)].V
            M[bus, otherbus] = P[bus] - (buses[str(bus+1)].V**2)*np.real(Ybus[bus, bus])
            if buses[str(bus+1)].bustype == 'PQ':
                L[bus, otherbus] = (Q[bus] - (buses[str(bus+1)].V**2)*np.imag(Ybus[bus, bus]))/buses[str(bus+1)].V
            else:
                L[bus, otherbus] = 10**99

J = np.vstack((np.hstack((H, N)), np.hstack((M, L))))

correction = np.linalg.solve(J, mis)

print(correction, correction[3], len(correction)/2)

# for index in range(len(correction)/2):
buses['2'].refresh(10, 2)

print(buses['2'].V, buses['2'].theta)
