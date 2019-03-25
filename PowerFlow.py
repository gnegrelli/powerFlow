import numpy as np


# Class of system buses
class Bus:
    def __init__(self, ID, name, bustype, V, theta, P , Q):
        self.ID = ID
        self.name = name
        self.bustype = bustype
        self.V = V
        self.theta = theta
        self.P = P
        self.Q = Q


# Class of system lines
class Line:
    def __init__(self, origin, destiny, R, X, B):
        self.origin = origin
        self.destiny = destiny
        self.R = R
        self.X = X
        self.B = B

