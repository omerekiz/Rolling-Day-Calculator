# Turkey-Germany Residence Tracker

An interactive web application for tracking Turkey residency days within the rolling 365-day window compliance rule (max 183 days in Turkey per 365-day period).

## 🚀 Quick Start

### Installation

```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Or install individually:
pip install pandas matplotlib streamlit altair

# Run the web app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

> **Note**: If you get a "module not found" error, make sure to install the requirements first!

### Alternative: Command Line Tool

```bash
# Default mode: Full text output + save visualization
python check_my_trip.py

# Text only mode (no visualization)
python check_my_trip.py --no-viz

# Quiet mode (minimal output)
python check_my_trip.py --quiet

# Show visualization interactively
python check_my_trip.py --show
```

## 📁 Files

- **`app.py`** - Interactive Streamlit web application
- **`check_my_trip.py`** - Command-line tool for scripts/automation
- **`residence_calculator.py`** - Core calculation library
- **`config.py`** - Data loading/saving manager
- **`data/`** - User data directory
  - **`sample/`** - Sample user folder with example data
    - `travel_history.json` - Example travel periods and settings
    - `planned_trips.json` - Example planned trips (empty by default)

## 🎯 Features

### Web Application (`app.py`)

- ✅ **Tab-Based Interface** - Separate tabs for trip planning and travel history
- ✅ **Multi-Trip Planning** - Plan multiple trips simultaneously with add/edit/delete
- ✅ **Auto-Calculate Max Days** - "Use Max Days" button fills end date to buffer limit
- ✅ **Live Validation** - Real-time warnings for buffer violations and limit breaches
- ✅ **Interactive Visualization** - Altair chart with dark mode support and tooltips
- ✅ **Editable Travel History** - Add/edit/delete past periods directly in the UI
- ✅ **Trip Reports** - Generate comprehensive trip planning summaries
- ✅ **Multiple Users** - Switch between different people's data
- ✅ **Persistent Settings** - Buffer days and travel history saved to disk
- ✅ **Color-Coded Status** - Instant visual feedback on compliance

### Command Line Tool (`check_my_trip.py`)

- Multiple output modes (full, quiet, no-viz)
- Beautiful formatted text with box drawing
- Perfect for automation and scripts
- Quick status checks

## Output Modes

### Default Mode
- Beautiful formatted text output with emojis and box drawing
- Full analysis including current status, trip recommendations, alternatives
- Saves visualization to `residence_analysis.png`

### `--no-viz` Mode
- Same text output as default
- Skips visualization generation (faster)

### `--quiet` Mode
- Minimal output (4 lines)
- Perfect for scripts or quick checks
- Still generates visualization

### `--show` Mode
- Same as default
- Opens visualization window interactively

## Example Output (Quiet Mode)

```
Status: 27 days remaining (156/183 used)
Trip: Dec 20, 2025 (42 days away)
Max duration: 28 days (return Jan 16, 2026)
After trip: 12 days buffer remaining
```

## Example Output (Default Mode)

```
╔════════════════════════════════════════════════════════════════════╗
║            TURKEY-GERMANY RESIDENCE TRACKER                        ║
╚════════════════════════════════════════════════════════════════════╝

📋 Person: Omer
📅 Analysis Date: November 08, 2025
📏 Rule: Maximum 183 Turkey days in any rolling 365-day window
🛡️  Safety Buffer: 12 days

┌────────────────────────────────────────────────────────────────────┐
│                      CURRENT STATUS                                │
└────────────────────────────────────────────────────────────────────┘

📍 Current Location: Germany
🇹🇷 Turkey Days Used: 156 / 183
⏳ Days Remaining: 27
✅ Compliance Status: COMPLIANT (Safe)
```

## Visualization

The generated chart shows:
- **Days available** to spend in Turkey (inverted scale - higher is better!)
- **Background coloring** for Turkey (red) vs Germany (blue) periods
- **Labeled key dates** with exact dates and days remaining:
  - Today's status
  - Trip start date
  - Recommended return date
  - End of projection (March 2026)
- **Historical** (solid line) vs **Projected** (dashed line) data
- **Reference lines** for limits and buffer

## 👥 Getting Started

### First Time Setup

1. **Try the sample data**: When you first run the app, select "Sample User" from the person selector to see how it works
2. **Create your own data**: Follow the instructions below to add your own travel history

### Adding New Users

1. Create a new folder in `data/` with the user's ID (e.g., `data/john/`)
2. Add `travel_history.json` - See format below (you can copy from `data/sample/` as a template)
3. The new user will appear in the person selector in the web app

> **Note**: Your personal data (anything in `data/` except `sample/`) is ignored by git and will not be committed to the repository.

### Data Format

**`data/username/travel_history.json`**:
```json
{
  "person_name": "John Doe",
  "buffer_days": 12,
  "travel_history": [
    {
      "country": "Germany",
      "start": "2025-01-01",
      "end": "2025-03-15"
    },
    {
      "country": "Turkey",
      "start": "2025-03-16",
      "end": "2025-04-15"
    }
  ]
}
```

> **Note**: Planned trips are NOT saved to disk. They exist only in the session state for scenario planning.

## 🔧 Requirements

See `requirements.txt`:
```
pandas>=2.0.0
matplotlib>=3.7.0
streamlit>=1.28.0
altair>=5.0.0
```

## ✨ Key Features

- ✅ Rolling 365-day window calculation
- ✅ Configurable safety buffer
- ✅ Trip duration optimization
- ✅ Alternative scenario testing
- ✅ Visual compliance tracking
- ✅ Multi-person support
- ✅ Multiple output modes
- ✅ Data validation
