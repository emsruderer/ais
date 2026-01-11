"""
AIS tracker with CPA data
"""

import sys
import pyais
from cpa_tracker import CPATracker

HOST = 'localhostT'
PORT = 10110


def pretty_print(tracks):
    """Pretty print a list of tracks to stdout."""
    headers = ['mmsi', 'callsign', 'shipname', 'lat', 'lon', 'cpa', 'tcpa', 'last_updated']
    rows = [[getattr(t, a) or 'N.A.' for a in headers] for t in tracks]
    row_format = "{:>15}" * (len(headers) + 1)
    sys.stdout.write(row_format.format("", *headers) + '\n')

    for i, row in enumerate(rows, start=1):
        sys.stdout.write(row_format.format(i, *row) + '\n')


def live_print(tracks):
    """Live print a list of tracks to stdout."""
    for _ in range(len(tracks) + 1):
        sys.stdout.write("\x1b[1A\x1b[2K")  # move up cursor and delete whole line
    pretty_print(tracks)


print('\n' * 11)

with CPATracker() as tracker:
    for msg in pyais.TCPConnection('localhost',10110):
        decoded = msg.decode()
        tracker.update(decoded, 10.0, 5.0, 0.0, 0.0)
        latest_tracks = tracker.n_latest_tracks(20)
        live_print(latest_tracks)
