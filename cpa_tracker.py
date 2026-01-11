"""
TCPA Data tracker class
"""
import dataclasses
import typing
import pyais
from pyais.tracker import AISTrack, AISTrackEvent, AISUpdateBroker, now
from pyais.messages import AISSentence, ANY_MESSAGE


@dataclasses.dataclass(eq=True, order=True)
class CPATrack():
    """Each track holds some consolidated information about a vessel.
    Each vessel is uniquely identified by its MMSI. Tracks typically hold
    information from multiple messages that were received."""
    mmsi: int = dataclasses.field(compare=True)
    turn: typing.Optional[float] = dataclasses.field(compare=False, default=None)
    speed: typing.Optional[float] = dataclasses.field(compare=False, default=None)
    lon: typing.Optional[float] = dataclasses.field(compare=False, default=None)
    lat: typing.Optional[float] = dataclasses.field(compare=False, default=None)
    course: typing.Optional[float] = dataclasses.field(compare=False, default=None)
    heading: typing.Optional[int] = dataclasses.field(compare=False, default=None)
    imo: typing.Optional[int] = dataclasses.field(compare=False, default=None)
    callsign: typing.Optional[str] = dataclasses.field(compare=False, default=None)
    shipname: typing.Optional[str] = dataclasses.field(compare=False, default=None)
    ship_type: typing.Optional[int] = dataclasses.field(compare=False, default=None)
    to_bow: typing.Optional[int] = dataclasses.field(compare=False, default=None)
    to_stern: typing.Optional[int] = dataclasses.field(compare=False, default=None)
    to_port: typing.Optional[int] = dataclasses.field(compare=False, default=None)
    to_starboard: typing.Optional[int] = dataclasses.field(compare=False, default=None)
    destination: typing.Optional[str] = dataclasses.field(compare=False, default=None)
    last_updated: float = dataclasses.field(compare=False, default_factory=now)
    name: typing.Optional[str] = dataclasses.field(compare=False, default=None)
    ais_version: typing.Optional[int] = dataclasses.field(compare=False, default=None)
    ais_type: typing.Optional[str] = dataclasses.field(compare=False, default=None)
    status: typing.Optional[str] = dataclasses.field(compare=False, default=None)

    tcpa : float = dataclasses.field(default=None, compare=False)
    cpa : float = dataclasses.field(default=None, compare=False)
    distance : float = dataclasses.field(default=None, compare=False)
    bearing : float = dataclasses.field(default=None, compare=False)

# compute a set of all fields only once
FIELDS = dataclasses.fields(CPATrack)
#print(FIELDS)

def cpa_to_track(msg: ANY_MESSAGE,cpa,ts_epoch_ms: typing.Optional[float] = None) -> CPATrack:
    """Convert a AIS message into a AISTrack.
    Only fields known to class CPATrack are considered.
    Depending on the type of the message, the implementation varies.
    ts_epoch_ms can be used as a timestamp for when the message was initially received.
    :param msg:         any decoded AIS message of type AISMessage.
    :param ts_epoch_ms: optional timestamp for the message. If None (default) current time is used."""
    if ts_epoch_ms is None:
        track = CPATrack(mmsi=msg.mmsi)
    else:
        track = CPATrack(mmsi=msg.mmsi, last_updated=ts_epoch_ms)

    for field in FIELDS:
        if not hasattr(msg, field.name):
            continue
        val = getattr(msg, field.name)
        if val is not None:
            setattr(track, field.name, val)
    # print(cpa)
    if cpa is not None:
        setattr(track, 'cpa', cpa['cpa'])
        setattr(track, 'tcpa', cpa['tcpa'])
        setattr(track, 'distance', cpa['distance'])
        setattr(track, 'bearing', cpa['bearing'])
    #print(track)
    return track

def update_track(old: CPATrack, new: CPATrack) -> CPATrack:
    """Updates all fields of old with the values of new.
    :param old: the old AISTrack to update.
    :param new: the new AISTrack to update old with."""
    for field in FIELDS:
        new_val = getattr(new, field.name)
        if new_val is not None:
            setattr(old, field.name, new_val)
    return old

def poplast(dictionary: typing.Dict[typing.Any, typing.Any]) -> typing.Any:
    """Get the last item of a dict non-destructively (in terms of insertion order)."""
    # On Python3.8+ reversed(dict.items()) would do the job.
    # But by doing so, support for Python3.7 would have to be dropped.
    # The fastest and most memory efficient solution for that, is this little hack.
    key, latest = dictionary.popitem()
    dictionary[key] = latest
    return latest

class CPATracker(pyais.tracker.AISTracker):
    """AISTracker subclass for CPA data"""
    track_class = CPATrack  # Use CPATrack for tracks
    def __init__(self,  ttl_in_seconds: typing.Optional[int] = 600, stream_is_ordered: bool = False):
        super().__init__(ttl_in_seconds, stream_is_ordered)
        self._tracks: typing.Dict[int, CPATrack] = {}  # { mmsi: CPATrack(), ...}
        self.ttl_in_seconds: typing.Optional[int] = ttl_in_seconds  # in seconds or None
        self.stream_is_ordered: bool = stream_is_ordered
        self.oldest_timestamp: typing.Optional[float] = None
        self._broker = AISUpdateBroker()

    def __set_oldest_timestamp(self, ts: float) -> None:
        if self.oldest_timestamp is None:
            self.oldest_timestamp = ts
        else:
            self.oldest_timestamp = min(self.oldest_timestamp, ts)

    @property
    def tracks(self) -> typing.List[AISTrack]:
        """Returns a list of all known tracks."""
        return list(self._tracks.values())

    def get_track(self, mmsi: typing.Union[str, int]) -> typing.Optional[CPATrack]:
        """Get a track by mmsi. Returns None if the track does not exist."""
        try:
            return self._tracks[int(mmsi)]
        except KeyError:
            return None

    def register_callback(
        self, event: AISTrackEvent, callback: typing.Callable[[CPATrack], typing.Any]
    ) -> None:
        """Register a callback that is called every time a specific event happens.
        The callback should be function that takes an AISTrack as a single argument."""
        self._broker.attach(event, callback)

    def remove_callback(
        self, event: AISTrackEvent, callback: typing.Callable[[CPATrack], typing.Any]
    ) -> None:
        """Remove a callback. Every callback is identified by its event and callback-function."""
        self._broker.detach(event, callback)

    def insert_or_update(self, mmsi: int, track: CPATrack) -> None:
        """Insert or update a track."""
        # Does the track already exist?
        if mmsi in self._tracks:
            self.update_track(mmsi, track)
        else:
            self.insert_track(mmsi, track)
        self.__set_oldest_timestamp(track.last_updated)

    def insert_track(self, mmsi: int, new: CPATrack) -> None:
        """Creates a new track records in memory"""
        self._tracks[mmsi] = new
        self._broker.propagate(new, AISTrackEvent.CREATED)

    def update_track(self, mmsi: int, new: CPATrack) -> None:
        """Updates an existing track in memory"""
        old = self._tracks[mmsi]
        if new.last_updated < old.last_updated:
            raise ValueError('cannot update track with older message')

        updated = update_track(old, new)
        # Neat little trick to keep tracks ordered after timestamp
        del self._tracks[mmsi]
        self._tracks[mmsi] = updated
        self._broker.propagate(updated, AISTrackEvent.UPDATED)

    def update(self, msg: AISSentence, cpa, ts_epoch_ms: typing.Optional[float] = None) -> None:
        """Update the tracker with a new AIS message.
        If the track for the MMSI of the message does not exist, it is created.
        :param msg:         any decoded AIS message of type AISMessage.
        :param ts_epoch_ms: optional timestamp for the message. If None (default) current time is used."""
        mmsi = int(msg.mmsi)
        track = cpa_to_track(msg, cpa, ts_epoch_ms)
        super().ensure_timestamp_constraints(track.last_updated)
        self.insert_or_update(mmsi, track)
        self.cleanup()

        mmsi = track.mmsi
        if mmsi in self._tracks:
            old_track = self._tracks[mmsi]
            updated_track = update_track(old_track, track)
            self._tracks[mmsi] = updated_track

    def n_latest_tracks(self, n: int) -> typing.List[CPATrack]:
        """Return the latest N tracks. These are the tracks with the youngest timestamps.
        E.g. the tracks that were updated most recently."""
        n_latest = []
        n = min(n, len(self._tracks))

        tracks = self._tracks_ordered_after_insertion()

        for i, track in enumerate(tracks):
            if n <= i:
                break
            n_latest.append(track)

        return n_latest

    def cleanup(self) -> None:
        """Delete all records whose last update is older than ttl."""
        if self.ttl_in_seconds is None or self.oldest_timestamp is None:
            return

        t = now()
        # the oldest track is still younger than the ttl
        if (t - self.ttl_in_seconds) < self.oldest_timestamp:
            return

        to_be_deleted = set()
        tracks = self._tracks_ordered_after_insertion()

        for track in tracks:
            if (t - track.last_updated) < self.ttl_in_seconds:
                self.oldest_timestamp = track.last_updated
                break
            # ttl is over. delete it.
            to_be_deleted.add(track.mmsi)

        for mmsi in to_be_deleted:
            self.pop_track(mmsi)

