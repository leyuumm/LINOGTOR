# LINOGTOR - Real-Time Earthquake Detector for Bogo City, Cebu, Philippines

**Copyright © 2025 Lliam Khenzo P. Monleon. All Rights Reserved.**

🌐 **Live Demo**: [https://web-production-dc7b.up.railway.app](https://web-production-dc7b.up.railway.app)

📱 **iOS App Available**: Install as PWA on iPhone/iPad - [See Instructions](IOS_INSTALL.md)

A real-time earthquake monitoring system specifically designed to track seismic activity in the Philippines, with a special focus on Cebu Province and Bogo City.

## ✨ Features

### Core Functionality
- **Real-time earthquake data** from USGS + PHIVOLCS
- **Focused on Bogo City** (50km radius monitoring)
- **Interactive map** showing earthquake epicenters
- **Distance calculations** from Bogo City for each earthquake
- **Auto-refresh** every 30 seconds to get the latest data
- **7-day historical data** display
- **Sound & Visual Alerts** for new earthquakes

### PWA Features (NEW! 📱)
- **📲 Install on iOS** - Works like a native app
- **📴 Offline Mode** - Access cached data without internet
- **🔔 Push Notifications** - Get alerts even when app is closed
- **🎨 Custom App Icon** - Beautiful home screen presence
- **⚡ Fast Loading** - Cached resources for instant access
- **🔄 Auto-Updates** - Always get the latest version
- **🖼️ Full Screen** - Immersive experience without browser UI

### Data Visualization
- **Color-coded magnitude** indicators:
  - Green: Minor (< 3.0)
  - Orange: Light (3.0 - 4.9)
  - Red: Moderate (5.0 - 6.9)
  - Dark Red: Strong (7.0+)
- **Statistics dashboard** showing:
  - Total earthquakes in Philippines (last 7 days)
  - Earthquakes in Cebu Province
  - Earthquakes within 50km of Bogo City
  - Earthquakes in the last 24 hours

## Geographic Focus

- **Primary Focus**: Bogo City, Cebu (11.0333°N, 124.0167°E)
- **Secondary Focus**: Cebu Province
- **Coverage Area**: Entire Philippines

## Installation

1. Make sure you have Python 3.7+ installed on your system

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. The application will automatically:
   - Load earthquake data from the USGS API
   - Display earthquakes on an interactive map
   - Show detailed information for each earthquake
   - Calculate distances from Bogo City
   - Refresh every 60 seconds

## API Endpoints

- `GET /` - Main web interface
- `GET /api/earthquakes` - JSON data of all earthquakes
- `GET /api/stats` - JSON statistics summary

## Data Source

This application uses the USGS Earthquake API:
- API Documentation: https://earthquake.usgs.gov/fdsnws/event/1/
- Data is updated in real-time by USGS
- Covers earthquakes worldwide with magnitude 1.0+

## Location Details

### Bogo City, Cebu
- Coordinates: 11.0333°N, 124.0167°E
- Province: Cebu
- Region: Central Visayas (Region VII)

### Cebu Province Boundaries
- Latitude: 9.5°N to 11.5°N
- Longitude: 123.0°E to 124.5°E

## Safety Information

**Important Notes:**
- This is a monitoring tool, not an early warning system
- Always follow official guidelines from PHIVOLCS (Philippine Institute of Volcanology and Seismology)
- In case of emergency, follow local authority instructions
- For official Philippine earthquake information, visit: https://www.phivolcs.dost.gov.ph/

## Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Mapping**: Leaflet.js
- **Data Source**: USGS Earthquake API

## License

**Copyright © 2025 Lliam Khenzo P. Monleon. All Rights Reserved.**

This software and associated documentation files are the proprietary property of Lliam Khenzo P. Monleon. Unauthorized copying, distribution, modification, or use of this software is strictly prohibited without explicit written permission from the copyright holder.

## Author

**Lliam Khenzo P. Monleon**

## Contributing

Feel free to submit issues or pull requests to improve the earthquake detector!

## Disclaimer

This application is for informational purposes only. Always refer to official sources like PHIVOLCS for authoritative earthquake information and safety guidelines.
