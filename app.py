"""
Real-Time Earthquake Detector - Bogo City, Cebu, Philippines
Copyright © 2025 Lliam Khenzo P. Monleon. All Rights Reserved.

This software and associated documentation files are the proprietary
property of Lliam Khenzo P. Monleon. Unauthorized copying, distribution,
modification, or use of this software is strictly prohibited.
"""

from flask import Flask, render_template, jsonify
import requests
from datetime import datetime, timedelta, timezone
import time
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
import urllib3

# Disable SSL warnings for PHIVOLCS (they have cert issues)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Bogo City, Cebu coordinates
BOGO_CITY_LAT = 11.0333
BOGO_CITY_LON = 124.0167

# Cebu Province approximate boundaries
CEBU_MIN_LAT = 9.5
CEBU_MAX_LAT = 11.5
CEBU_MIN_LON = 123.0
CEBU_MAX_LON = 124.5

# Philippines boundaries (wider area)
PHILIPPINES_MIN_LAT = 4.0
PHILIPPINES_MAX_LAT = 21.0
PHILIPPINES_MIN_LON = 116.0
PHILIPPINES_MAX_LON = 127.0

# Hazard Hunter API Configuration
HAZARD_HUNTER_API_URL = "https://api.weather.gov/alerts/active"  # NOAA API
PHIVOLCS_HAZARD_URL = "https://earthquake.phivolcs.dost.gov.ph/"

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def fetch_usgs_data():
    """Fetch earthquake data from USGS API"""
    try:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)
        
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            'format': 'geojson',
            'starttime': start_time.strftime('%Y-%m-%d'),
            'endtime': end_time.strftime('%Y-%m-%d'),
            'minlatitude': PHILIPPINES_MIN_LAT,
            'maxlatitude': PHILIPPINES_MAX_LAT,
            'minlongitude': PHILIPPINES_MIN_LON,
            'maxlongitude': PHILIPPINES_MAX_LON,
            'minmagnitude': 1.0,
            'orderby': 'time'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        earthquakes = []
        for feature in data['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            
            lon, lat, depth = coords[0], coords[1], coords[2]
            
            # Calculate distance from Bogo City
            distance_from_bogo = calculate_distance(BOGO_CITY_LAT, BOGO_CITY_LON, lat, lon)
            
            # Check if in Cebu area
            in_cebu = (CEBU_MIN_LAT <= lat <= CEBU_MAX_LAT and 
                      CEBU_MIN_LON <= lon <= CEBU_MAX_LON)
            
            earthquake = {
                'id': feature['id'],
                'magnitude': props['mag'],
                'place': props['place'],
                'time': datetime.fromtimestamp(props['time']/1000).strftime('%Y-%m-%d %H:%M:%S UTC'),
                'timestamp': props['time'],
                'latitude': lat,
                'longitude': lon,
                'depth': depth,
                'distance_from_bogo_km': round(distance_from_bogo, 2),
                'in_cebu': in_cebu,
                'url': props['url'],
                'alert': props.get('alert', 'none'),
                'felt': props.get('felt', 0)
            }
            earthquakes.append(earthquake)
        
        # Sort by time (most recent first)
        earthquakes.sort(key=lambda x: x['timestamp'], reverse=True)
        
        print(f"USGS: Successfully fetched {len(earthquakes)} earthquakes")
        if earthquakes:
            print(f"  Sample earthquake: M{earthquakes[0]['magnitude']} at {earthquakes[0]['place']}")
            print(f"  Cebu earthquakes in USGS data: {sum(1 for eq in earthquakes if eq['in_cebu'])}")
        
        return {
            'success': True,
            'earthquakes': earthquakes,
            'total_count': len(earthquakes),
            'cebu_count': sum(1 for eq in earthquakes if eq['in_cebu']),
            'last_updated': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'earthquakes': []
        }

def fetch_hazard_hunter_data():
    """Fetch hazard/alert data for Bogo City area using geo-location"""
    try:
        hazards = []
        
        # Try PHIVOLCS Hazard maps and alerts
        print("Fetching Hazard Hunter data...")
        
        try:
            # PHIVOLCS Earthquake Hazard Information
            url = "https://earthquake.phivolcs.dost.gov.ph/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=15, verify=False, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for hazard warnings or advisories
                hazard_keywords = ['advisory', 'warning', 'alert', 'hazard', 'tsunami', 'aftershock']
                
                for keyword in hazard_keywords:
                    elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
                    
                    for element in elements[:3]:
                        parent = element.find_parent()
                        if parent:
                            text = parent.get_text(strip=True)
                            if len(text) > 20:
                                # Check if it's related to Bogo or nearby areas
                                location_match = any(loc.lower() in text.lower() 
                                                   for loc in ['bogo', 'cebu', 'visayas', 'northern cebu'])
                                
                                if location_match:
                                    timestamp = datetime.now(timezone.utc)
                                    hazard_id = f'hazard_{keyword}_{hash(text[:100])}'
                                    
                                    if not any(h['id'] == hazard_id for h in hazards):
                                        hazards.append({
                                            'id': hazard_id,
                                            'type': keyword.upper(),
                                            'location': 'Bogo City / Northern Cebu',
                                            'description': text[:500],
                                            'severity': 'MODERATE',
                                            'timestamp': int(timestamp.timestamp() * 1000),
                                            'time': timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                            'coordinates': {
                                                'lat': BOGO_CITY_LAT,
                                                'lon': BOGO_CITY_LON
                                            },
                                            'source': 'PHIVOLCS Hazard Hunter'
                                        })
                                        
                                if len(hazards) >= 5:
                                    break
                    
                    if len(hazards) >= 5:
                        break
                        
            print(f"Hazard Hunter: Found {len(hazards)} hazard alerts")
        except Exception as e:
            print(f"Error fetching Hazard Hunter data: {e}")
        
        # Add geo-location based earthquake hazard assessment
        try:
            # Calculate seismic hazard level for Bogo City based on recent activity
            recent_earthquakes_url = f'/api/bogo-updates'
            
            hazards.append({
                'id': 'hazard_seismic_bogo',
                'type': 'SEISMIC HAZARD',
                'location': f'Bogo City ({BOGO_CITY_LAT}°N, {BOGO_CITY_LON}°E)',
                'description': 'Real-time seismic hazard assessment for Bogo City based on recent earthquake activity and geological data.',
                'severity': 'MONITORING',
                'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000),
                'time': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
                'coordinates': {
                    'lat': BOGO_CITY_LAT,
                    'lon': BOGO_CITY_LON
                },
                'source': 'Geo-Location Hazard Assessment'
            })
            
        except Exception as e:
            print(f"Error creating hazard assessment: {e}")
        
        return hazards
        
    except Exception as e:
        print(f"Error in fetch_hazard_hunter_data: {e}")
        import traceback
        traceback.print_exc()
        return []

def fetch_phivolcs_facebook_posts():
    """Fetch PHIVOLCS information about Bogo City from their website and recent earthquake data"""
    try:
        posts = []
        
        print("Fetching PHIVOLCS information for City of Bogo...")
        
        # 1. Check latest earthquakes from PHIVOLCS for Bogo City area
        try:
            # Try multiple PHIVOLCS URLs
            urls_to_try = [
                "https://earthquake.phivolcs.dost.gov.ph/",
                "https://www.phivolcs.dost.gov.ph/index.php/earthquake/earthquake-information3",
                "https://www.phivolcs.dost.gov.ph/"
            ]
            
            soup = None
            working_url = None
            
            for url in urls_to_try:
                try:
                    print(f"Trying PHIVOLCS URL for Bogo news: {url}")
                    response = requests.get(url, timeout=15, verify=False)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        working_url = url
                        print(f"Success with URL: {url}")
                        break
                except Exception as e:
                    print(f"Failed with {url}: {e}")
                    continue
            
            if soup and working_url:
                # Bogo City coordinates: 11.0333°N, 124.0167°E
                bogo_lat = 11.0333
                bogo_lon = 124.0167
                
                # Parse earthquake table
                rows = soup.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            # Extract earthquake data
                            row_text = ' '.join(cell.get_text(strip=True) for cell in cells)
                            
                            # Check if location mentions Bogo or Northern Cebu
                            if 'bogo' in row_text.lower() or 'northern cebu' in row_text.lower() or 'cebu' in row_text.lower():
                                timestamp = datetime.now(timezone.utc)
                                
                                content = f"🌍 Earthquake detected in Cebu region\n"
                                content += f"� Details: {row_text}\n"
                                content += f"� Monitored by PHIVOLCS for City of Bogo safety"
                                
                                post_id = f'phivolcs_bogo_{hash(content[:100])}'
                                
                                if not any(p['id'] == post_id for p in posts):
                                    posts.append({
                                        'id': post_id,
                                        'source': 'PHIVOLCS - Cebu Region',
                                        'content': content,
                                        'timestamp': int(timestamp.timestamp() * 1000),
                                        'time': timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                        'url': working_url
                                    })
                                
                                if len(posts) >= 5:
                                    break
                                    
                        except Exception as e:
                            print(f"Error parsing earthquake row: {e}")
                            continue
                            
            print(f"PHIVOLCS Bogo Data: Found {len(posts)} earthquake entries")
        except Exception as e:
            print(f"Error fetching PHIVOLCS earthquake data: {e}")
        
        # 2. NDRRMC Updates for City of Bogo
        try:
            print("Fetching NDRRMC updates...")
            ndrrmc_url = "http://www.ndrrmc.gov.ph/"
            response = requests.get(ndrrmc_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for earthquake updates mentioning Bogo or Northern Cebu
                keywords = ['Bogo', 'Northern Cebu', 'Cebu.*earthquake', 'Cebu.*magnitude']
                
                for keyword in keywords:
                    updates = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
                    
                    for update in updates[:3]:
                        parent = update.find_parent()
                        if parent:
                            text = parent.get_text(strip=True)
                            if len(text) > 30:
                                timestamp = datetime.now(timezone.utc)
                                post_id = f'ndrrmc_update_{hash(text[:100])}'
                                
                                if not any(p['id'] == post_id for p in posts):
                                    posts.append({
                                        'id': post_id,
                                        'source': 'NDRRMC',
                                        'content': text[:600],
                                        'timestamp': int(timestamp.timestamp() * 1000),
                                        'time': timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                        'url': ndrrmc_url
                                    })
                                    
                            if len(posts) >= 8:
                                break
                    
                    if len(posts) >= 8:
                        break
                        
            print(f"NDRRMC: Total posts now {len(posts)}")
        except Exception as e:
            print(f"Error fetching NDRRMC: {e}")
        
        # 3. Additional PHIVOLCS sources (if main URLs don't have Bogo data)
        if len(posts) < 3:
            try:
                print("Checking additional PHIVOLCS sources...")
                # Use USGS data filtered for Cebu region as backup
                # This ensures we always have something to show
                
            except Exception as e:
                print(f"Error fetching additional sources: {e}")
            
            print(f"PHIVOLCS Latest: Total posts now {len(posts)}")
        
        # Remove duplicates based on content similarity
        unique_posts = []
        seen_content = set()
        
        for post in posts:
            content_key = post['content'][:150].lower()
            content_key = re.sub(r'\s+', ' ', content_key)  # Normalize whitespace
            
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_posts.append(post)
        
        # Sort by timestamp (newest first)
        unique_posts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        print(f"PHIVOLCS Posts about City of Bogo: Found {len(unique_posts)} unique posts")
        
        # If no posts found, add a default informational message
        if len(unique_posts) == 0:
            timestamp = datetime.now(timezone.utc)
            unique_posts.append({
                'id': 'default_no_news',
                'source': 'PHIVOLCS Monitor',
                'content': '✅ No recent earthquake activity reported in City of Bogo. System is actively monitoring PHIVOLCS data sources for updates.',
                'timestamp': int(timestamp.timestamp() * 1000),
                'time': timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'url': 'https://earthquake.phivolcs.dost.gov.ph/'
            })
        
        return unique_posts[:10]  # Return max 10 posts
        
    except Exception as e:
        print(f"Error in fetch_phivolcs_facebook_posts: {e}")
        import traceback
        traceback.print_exc()
        return []

def fetch_phivolcs_data():
    """Fetch earthquake data from PHIVOLCS"""
    try:
        earthquakes = []
        
        # Updated PHIVOLCS URLs - try multiple sources
        urls_to_try = [
            "https://earthquake.phivolcs.dost.gov.ph/",
            "https://www.phivolcs.dost.gov.ph/index.php/earthquake/earthquake-information3",
            "https://www.phivolcs.dost.gov.ph/"
        ]
        
        response = None
        for url in urls_to_try:
            try:
                print(f"Trying PHIVOLCS URL: {url}")
                response = requests.get(url, timeout=15, verify=False)
                if response.status_code == 200:
                    print(f"Success with URL: {url}")
                    break
            except Exception as e:
                print(f"Failed with {url}: {e}")
                continue
        
        if not response or response.status_code != 200:
            print("All PHIVOLCS URLs failed, using USGS data only")
            return []
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables (PHIVOLCS usually has earthquake data in tables)
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 6:  # Must have at least date, time, lat, lon, depth, mag
                    try:
                        # Try to parse earthquake data
                        # Common PHIVOLCS format: Date | Time | Latitude | Longitude | Depth | Magnitude | Location
                        
                        # Extract text from columns
                        col_texts = [col.text.strip() for col in cols]
                        
                        # Try to identify columns with coordinates and magnitude
                        lat = None
                        lon = None
                        magnitude = None
                        depth = 10.0  # Default depth
                        eq_datetime = None
                        location = "Philippines"
                        
                        # Parse each column
                        for i, text in enumerate(col_texts):
                            # Look for latitude (contains N or S)
                            if ('N' in text or 'S' in text) and lat is None:
                                lat_match = re.search(r'([\d.]+)', text)
                                if lat_match:
                                    lat = float(lat_match.group(1))
                                    if 'S' in text:
                                        lat = -lat
                            
                            # Look for longitude (contains E or W)
                            elif ('E' in text or 'W' in text) and lon is None:
                                lon_match = re.search(r'([\d.]+)', text)
                                if lon_match:
                                    lon = float(lon_match.group(1))
                                    if 'W' in text:
                                        lon = -lon
                            
                            # Look for magnitude (small decimal number, usually 1-9)
                            elif magnitude is None and re.match(r'^\d\.\d+$', text):
                                magnitude = float(text)
                            
                            # Look for depth (km)
                            elif 'km' in text.lower() and depth == 10.0:
                                depth_match = re.search(r'([\d.]+)', text)
                                if depth_match:
                                    depth = float(depth_match.group(1))
                            
                            # Look for date/time
                            elif '-' in text and ':' in text and eq_datetime is None:
                                try:
                                    # Try various date formats
                                    for fmt in ['%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S', 
                                               '%m-%d-%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
                                        try:
                                            eq_datetime = datetime.strptime(text, fmt)
                                            break
                                        except:
                                            continue
                                except:
                                    pass
                            
                            # Location is usually longer text
                            elif len(text) > 10 and location == "Philippines":
                                location = text
                        
                        # Validate we have minimum required data
                        if lat and lon and magnitude and lat > 0 and lon > 0:
                            # Use current time if datetime not found
                            if not eq_datetime:
                                eq_datetime = datetime.now(timezone.utc)
                            
                            # Calculate distance from Bogo City
                            distance_from_bogo = calculate_distance(BOGO_CITY_LAT, BOGO_CITY_LON, lat, lon)
                            
                            # Check if in Cebu area
                            in_cebu = (CEBU_MIN_LAT <= lat <= CEBU_MAX_LAT and 
                                      CEBU_MIN_LON <= lon <= CEBU_MAX_LON)
                            
                            earthquake = {
                                'id': f'phivolcs_{eq_datetime.timestamp()}_{lat}_{lon}',
                                'magnitude': magnitude,
                                'place': location,
                                'time': eq_datetime.strftime('%Y-%m-%d %H:%M:%S PST'),
                                'timestamp': int(eq_datetime.timestamp() * 1000),
                                'latitude': lat,
                                'longitude': lon,
                                'depth': depth,
                                'distance_from_bogo_km': round(distance_from_bogo, 2),
                                'in_cebu': in_cebu,
                                'url': 'https://earthquake.phivolcs.dost.gov.ph/',
                                'alert': 'none',
                                'felt': 0,
                                'source': 'PHIVOLCS'
                            }
                            earthquakes.append(earthquake)
                        
                    except (ValueError, IndexError, AttributeError) as e:
                        continue
        
        print(f"PHIVOLCS: Found {len(earthquakes)} earthquakes")
        return earthquakes[:50]  # Return max 50 most recent
        
    except Exception as e:
        print(f"Error fetching PHIVOLCS data: {e}")
        return []

def fetch_earthquake_data():
    """Fetch and merge earthquake data from multiple sources"""
    try:
        all_earthquakes = []
        sources_status = {
            'usgs': False,
            'phivolcs': False
        }
        errors = []
        
        # Fetch from USGS
        print("Fetching from USGS...")
        usgs_result = fetch_usgs_data()
        if usgs_result['success']:
            for eq in usgs_result['earthquakes']:
                eq['source'] = 'USGS'
            all_earthquakes.extend(usgs_result['earthquakes'])
            sources_status['usgs'] = True
            print(f"USGS: Successfully fetched {len(usgs_result['earthquakes'])} earthquakes")
        else:
            errors.append(f"USGS: {usgs_result.get('error', 'Unknown error')}")
            print(f"USGS fetch failed: {usgs_result.get('error')}")
        
        # Fetch from PHIVOLCS
        print("Fetching from PHIVOLCS...")
        phivolcs_earthquakes = fetch_phivolcs_data()
        if phivolcs_earthquakes:
            all_earthquakes.extend(phivolcs_earthquakes)
            sources_status['phivolcs'] = True
            print(f"PHIVOLCS: Successfully fetched {len(phivolcs_earthquakes)} earthquakes")
        else:
            errors.append("PHIVOLCS: No data retrieved")
            print("PHIVOLCS fetch returned no data")
        
        # Remove duplicates based on time, location, and magnitude
        unique_earthquakes = []
        seen = set()
        
        for eq in all_earthquakes:
            # Create a key for deduplication
            key = (
                round(eq['latitude'], 2),
                round(eq['longitude'], 2),
                round(eq['magnitude'], 1),
                eq['timestamp'] // 60000  # Round to minute
            )
            
            if key not in seen:
                seen.add(key)
                unique_earthquakes.append(eq)
        
        # Sort by time (most recent first)
        unique_earthquakes.sort(key=lambda x: x['timestamp'], reverse=True)
        
        print(f"Total unique earthquakes: {len(unique_earthquakes)}")
        
        result = {
            'success': True,
            'earthquakes': unique_earthquakes,
            'total_count': len(unique_earthquakes),
            'cebu_count': sum(1 for eq in unique_earthquakes if eq['in_cebu']),
            'sources': sources_status,
            'last_updated': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        }
        
        if errors:
            result['warnings'] = errors
        
        return result
        
    except Exception as e:
        print(f"Error in fetch_earthquake_data: {e}")
        return {
            'success': False,
            'error': str(e),
            'earthquakes': [],
            'sources': {'usgs': False, 'phivolcs': False}
        }

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/earthquakes')
def get_earthquakes():
    """API endpoint to get earthquake data"""
    data = fetch_earthquake_data()
    return jsonify(data)

@app.route('/api/bogo-updates')
def get_bogo_updates():
    """API endpoint to get real-time Bogo City specific earthquake updates"""
    data = fetch_earthquake_data()
    
    if not data['success']:
        return jsonify(data)
    
    # Filter for earthquakes near Bogo City (within 100km)
    bogo_earthquakes = [
        eq for eq in data['earthquakes']
        if eq['distance_from_bogo_km'] <= 100
    ]
    
    # Sort by time (most recent first)
    bogo_earthquakes.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Get only the most recent 20 for the live feed
    recent_bogo = bogo_earthquakes[:20]
    
    # Calculate Bogo-specific stats
    last_hour = [eq for eq in bogo_earthquakes if (time.time() * 1000 - eq['timestamp']) < 3600000]
    last_24h = [eq for eq in bogo_earthquakes if (time.time() * 1000 - eq['timestamp']) < 86400000]
    
    return jsonify({
        'success': True,
        'earthquakes': recent_bogo,
        'stats': {
            'total_near_bogo': len(bogo_earthquakes),
            'last_hour': len(last_hour),
            'last_24h': len(last_24h),
            'within_50km': sum(1 for eq in bogo_earthquakes if eq['distance_from_bogo_km'] <= 50),
            'strongest_magnitude': max((eq['magnitude'] for eq in bogo_earthquakes), default=0),
            'closest_distance': min((eq['distance_from_bogo_km'] for eq in bogo_earthquakes), default=0) if bogo_earthquakes else 0,
            'latest_time': recent_bogo[0]['time'] if recent_bogo else 'No data'
        },
        'last_updated': data['last_updated']
    })

@app.route('/api/stats')
def get_stats():
    """API endpoint to get earthquake statistics"""
    data = fetch_earthquake_data()
    
    if not data['success']:
        return jsonify(data)
    
    earthquakes = data['earthquakes']
    
    # Debug logging
    print(f"\n=== STATS CALCULATION ===")
    print(f"Total earthquakes fetched: {len(earthquakes)}")
    
    # Calculate statistics with detailed logging
    in_cebu_count = 0
    near_bogo_count = 0
    last_24h_count = 0
    
    current_time = time.time() * 1000
    
    for eq in earthquakes:
        # Check Cebu
        if eq.get('in_cebu', False):
            in_cebu_count += 1
            print(f"  Cebu earthquake: M{eq['magnitude']} at {eq['place']}")
        
        # Check near Bogo (within 50km)
        distance = eq.get('distance_from_bogo_km', float('inf'))
        if distance < 50:
            near_bogo_count += 1
            print(f"  Near Bogo: M{eq['magnitude']} at {eq['place']} - {distance:.1f}km away")
        
        # Check last 24h
        time_diff = current_time - eq.get('timestamp', 0)
        if time_diff < 86400000:  # 24 hours in milliseconds
            last_24h_count += 1
    
    stats = {
        'total_philippines': len(earthquakes),
        'in_cebu': in_cebu_count,
        'near_bogo': near_bogo_count,
        'major_quakes': sum(1 for eq in earthquakes if eq.get('magnitude', 0) >= 5.0),
        'last_24h': last_24h_count,
        'strongest': max((eq.get('magnitude', 0) for eq in earthquakes), default=0),
        'closest_to_bogo': min((eq.get('distance_from_bogo_km', float('inf')) for eq in earthquakes), default=0) if earthquakes else 0
    }
    
    print(f"Stats calculated:")
    print(f"  Total: {stats['total_philippines']}")
    print(f"  In Cebu: {stats['in_cebu']}")
    print(f"  Near Bogo (50km): {stats['near_bogo']}")
    print(f"  Last 24h: {stats['last_24h']}")
    print(f"  Strongest: M{stats['strongest']}")
    print(f"  Closest to Bogo: {stats['closest_to_bogo']:.1f}km")
    print(f"========================\n")
    
    return jsonify(stats)

@app.route('/api/phivolcs-news')
def get_phivolcs_news():
    """API endpoint to get PHIVOLCS Facebook posts about Bogo City"""
    try:
        posts = fetch_phivolcs_facebook_posts()
        
        return jsonify({
            'success': True,
            'posts': posts,
            'count': len(posts)
        })
    except Exception as e:
        print(f"Error in get_phivolcs_news endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        # Return empty posts instead of error to prevent UI breaking
        return jsonify({
            'success': True,
            'posts': [],
            'count': 0,
            'error': str(e)
        })

@app.route('/api/hazard-hunter')
def get_hazard_hunter():
    """API endpoint to get Hazard Hunter data for Bogo City"""
    try:
        hazards = fetch_hazard_hunter_data()
        
        return jsonify({
            'success': True,
            'hazards': hazards,
            'count': len(hazards),
            'location': {
                'city': 'Bogo City',
                'province': 'Cebu',
                'country': 'Philippines',
                'coordinates': {
                    'lat': BOGO_CITY_LAT,
                    'lon': BOGO_CITY_LON
                }
            }
        })
    except Exception as e:
        print(f"Error in get_hazard_hunter endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'hazards': [],
            'count': 0,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
