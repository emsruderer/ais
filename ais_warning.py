"""
The following example shows how to decode AIS messages from a TCP socket.
"""
import sys
import pyais
from pyais.tracker import AISTrackEvent
from pyais.filter import haversine

def pretty(message):
    if message.mmsi and message.lat :
        print(f"{message.mmsi}, lat: {message.lat:.6} B, lon: {message.lon:.6} L, course: {message.course} deg, speed: {message.speed:.3} knots")
    else:
        print("corrupted", message)


