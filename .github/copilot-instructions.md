# AI Coding Agent Instructions for AIS Navigation System

## Project Overview
This is a maritime **AIS (Automatic Identification System) tracking and collision warning system** for monitoring vessel positions and calculating collision risks. The system receives NMEA 0183 AIS messages from SignalK (TCP port 10110), tracks vessel positions, computes Closest Point of Approach (CPA) and Time to CPA (TCPA), and provides audio alerts using text-to-speech.

## Architecture Overview

### Core Data Flow
1. **AIS Stream Input** → **Message Decoding** → **Position Tracking** → **Collision Detection** → **Audio Alerts**
   - `ais_stream.py`: Connects to SignalK TCP server, receives raw AIS messages
   - `multi_process_ais.py`: Main orchestrator using multiprocessing (3 processes)
   - `warn.py`: Processes tracked vessels and generates voice warnings
   - `speech.py`: Text-to-speech using gTTS, outputs to `call.mp2`

### Multiprocessing Architecture
The system uses **3 separate processes** managed in [multi_process_ais.py](multi_process_ais.py#L43-L59):
- **Process 1** (`do_track`): TCP listener collecting AIS messages into shared queue
- **Process 2** (`Decoder.do_decode`): Consumes raw messages, decodes, filters by geographic range, pushes relevant messages to warning queue
- **Process 3** (`do_warn`): Updates AISTracker with messages and triggers callbacks (CREATED, UPDATED, DELETED events)

### Geographic Filter
Reference location: **Jemgum, Germany** (53.26379°N, 7.39738°E) with **7 nautical mile radius** [multi_process_ais.py](multi_process_ais.py#L18-L20). Only vessels within this radius trigger warnings.

## Key Components & Patterns

### 1. Vessel Tracking with pyais
- Uses `pyais.AISTracker` for tracking state (see [warn.py](warn.py#L46-L58))
- Message types filtered: **1, 2, 3, 18** (position reports), **19, 24** (extended ship info)
- Tracker callbacks via `register_callback()` for lifecycle events (CREATED, UPDATED, DELETED)
- Track objects contain: `mmsi`, `lat`, `lon`, `course`, `speed`, `shipname`

### 2. Collision Detection (CPA/TCPA)
Located in [cpa_tcpa.py](cpa_tcpa.py):
- **CPA** = Closest Point of Approach (minimum distance in nautical miles)
- **TCPA** = Time to CPA (in minutes)
- Vectorial calculation between two vessels using course & speed
- Negative TCPA = collision already passed; positive = future collision
- Used in both [cpa_tcpa_class.py](cpa_tcpa_class.py) (class-based) and thread-based implementations

### 3. Virtual Ship Simulation
[ships.py](ships.py) implements a simulated vessel:
- **Threading-based** (inherits from `threading.Thread`) for continuous position updates
- Updates position every 60 seconds using trigonometry (nm/min velocity)
- Stores coordinates in nautical miles internally; converts degrees for output
- Used with MMSI `244030153` (the reference vessel "Johanna")

### 4. Text-to-Speech Alerts
[speech.py](speech.py) generates Dutch-language warnings:
- `speak(pre_text, direction, number, post_text)` constructs voice alerts
- Uses gTTS library, outputs audio to `call.mp2` file
- **Dutch number formatting** with custom logic for 0-9999 range (words like "twintig", "honderd")
- Phonetic alphabet for spelling (Alpha, Bravo, Charlie, etc.)

## Developer Workflows

### Running the Main System
```bash
# Terminal 1: Start SignalK server (provides AIS stream on port 10110)
# (Assumed external dependency - not in repo)

# Terminal 2: Run the multiprocess AIS tracker
python multi_process_ais.py
```

### Testing CPA/TCPA Calculations
```bash
python cpa_tcpa.py
```

### Testing Virtual Ship Simulation
```bash
python ships.py
```

### Testing Speech Synthesis
```bash
python speech.py
```

## Critical Patterns & Conventions

### Message Filtering
Use `pyais.filter` classes:
- `NoneFilter('lon', 'lat', 'mmsi')` - reject messages missing these fields
- `MessageTypeFilter(1, 2, 3, 18, 19, 24)` - whitelist specific AIS message types
- Filter chains can be composed (see [ais_stream.py](ais_stream.py#L10-L13))

### Position Calculations
- **Internal storage**: All distances in nautical miles
- **Bearing calculation**: Uses `math.atan2()` with radians, returns 0-360 degrees (see [warn.py](warn.py#L18-L35))
- **Distance calculation**: Uses `haversine()` from pyais for great-circle distance

### Thread Safety
- [ais-stream_threads.py](ais-stream_threads.py) uses `threading.Lock()` (named `baton`) for shared dictionary access (line 13-14)
- Acquire lock before updating `ships` dict in multithreaded contexts

### Ship Type Classification
[shipstype.py](shipstype.py) provides `shiptype(int)` lookup table mapping AIS ship type codes (0-99) to descriptions (e.g., 30="Fishing", 52="Tug")

## Integration Points

### External Dependencies
- **pyais**: AIS message decoding, tracking, filtering, haversine distance
- **gTTS**: Google Text-to-Speech for Dutch language synthesis
- **playsound3**: Audio playback of generated MP3/MP2 files
- **SignalK**: Assumed external AIS stream server on `localhost:10110`

### Data Interchange
- **Queue objects**: FIFO message passing between processes
- **Raw messages** → decoded via `msg.decode()`
- **Message dictionaries** via `msg.asdict()` for dict key access

## Known Issues & Considerations
- [cpa_tcpa_class.py](cpa_tcpa_class.py#L24-26) has incomplete/incorrect implementation of `cpa_update()` - use [cpa_tcpa.py](cpa_tcpa.py) instead
- Speech synthesis requires internet (gTTS calls Google API)
- File-based queue warning: use `False, 0` timeout parameters to avoid blocking ([multi_process_ais.py](multi_process_ais.py#L39))
