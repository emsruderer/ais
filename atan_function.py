from math import radians, cos, sin, sqrt, atan, tan, pi
import matplotlib.pyplot as plt

tuple_list = [[10.0,10.0],[20.0,20.0], [30.0,10.0],[40.0,20.0], [50.0,10.0],[60.0,20.0]]
for i, point in enumerate(tuple_list):
    plt.scatter(point[0], point[1])
plt.axis([0,70, 0, 60])
plt.xlabel('lengte')
plt.ylabel('breedte')
plt.show()