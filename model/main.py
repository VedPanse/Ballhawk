import pandas as pd
import numpy as np
import requests
from pybaseball import statcast_batter, playerid_lookup
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import time
from datetime import datetime, timedelta
import sys

TEAM_NAME_TO_ABBR = {
    "Arizona Diamondbacks": "ARI",
    "Atlanta Braves": "ATL",
    "Baltimore Orioles": "BAL",
    "Boston Red Sox": "BOS",
    "Chicago White Sox": "CWS",
    "Chicago Cubs": "CHC",
    "Cincinnati Reds": "CIN",
    "Cleveland Guardians": "CLE",
    "Colorado Rockies": "COL",
    "Detroit Tigers": "DET",
    "Houston Astros": "HOU",
    "Kansas City Royals": "KC",
    "Los Angeles Angels": "LAA",
    "Los Angeles Dodgers": "LAD",
    "Miami Marlins": "MIA",
    "Milwaukee Brewers": "MIL",
    "Minnesota Twins": "MIN",
    "New York Yankees": "NYY",
    "New York Mets": "NYM",
    "Oakland Athletics": "OAK",
    "Philadelphia Phillies": "PHI",
    "Pittsburgh Pirates": "PIT",
    "San Diego Padres": "SD",
    "San Francisco Giants": "SF",
    "Seattle Mariners": "SEA",
    "St. Louis Cardinals": "STL",
    "Tampa Bay Rays": "TB",
    "Texas Rangers": "TEX",
    "Toronto Blue Jays": "TOR",
    "Washington Nationals": "WSH"
}

def get_team_id_map():
    url = "https://statsapi.mlb.com/api/v1/teams?sportId=1"
    response = requests.get(url)
    data = response.json()
    return {team['abbreviation']: team['id'] for team in data['teams']}

def get_roster(team_abbr, team_id_map=None):
    if team_id_map is None:
        team_id_map = get_team_id_map()
    team_id = team_id_map.get(team_abbr.upper())
    if not team_id:
        raise ValueError(f"Invalid team abbreviation: {team_abbr}")
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster/active"
    response = requests.get(url)
    return [player['person']['fullName'] for player in response.json()['roster']]

def estimate_spray_angle(df):
    return np.degrees(np.arctan2(df['hc_x'] - 125, 198 - df['hc_y']))

def predict_landing_point(launch_speed, launch_angle, spray_angle, distance=None):
    angle_rad = np.radians(spray_angle)
    if distance is None or pd.isna(distance):
        v = launch_speed * 0.44704
        theta = np.radians(launch_angle)
        g = 9.81
        range_1D = (v ** 2 * np.sin(2 * theta)) / g
        distance = range_1D * 3.28084
    distance = max(min(distance, 470), 290)
    x = distance * np.sin(angle_rad)
    y = distance * np.cos(angle_rad)
    return x, y

def get_team_home_runs(team_abbr, start=None, end=None):
    if end is None:
        end = datetime.today().strftime('%Y-%m-%d')
    if start is None:
        start = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    team_id_map = get_team_id_map()
    roster = get_roster(team_abbr, team_id_map)
    all_hr_rows = []
    for name in roster:
        try:
            first, last = name.split()[-2:]
            pid_df = playerid_lookup(last, first)
            if pid_df.empty:
                continue
            pid = pid_df.iloc[0]['key_mlbam']
            df = statcast_batter(start, end, player_id=pid)
            df = df[df['events'] == 'home_run'].dropna(subset=['launch_speed', 'launch_angle', 'hc_x', 'hc_y']).copy()
            if df.empty:
                continue
            df['player_name'] = name
            df['spray_angle_est'] = estimate_spray_angle(df)
            all_hr_rows.append(df)
            time.sleep(0.5)
        except Exception as e:
            print(f"Skipping {name}: {e}")
            continue
    if all_hr_rows:
        return pd.concat(all_hr_rows, ignore_index=True)
    return pd.DataFrame()

def get_stadium_image_url(stadium_name):
    cache_path = "./stadium_cache/stadium_list.csv"
    try:
        df = pd.read_csv(cache_path)
        match = df[df['stadium'] == stadium_name]
        if match.empty or pd.isna(match.iloc[0]['img_link']):
            print(f"[WARNING] No image URL found for '{stadium_name}' in CSV.")
            return None
        url = match.iloc[0]['img_link']
        print(f"[DEBUG] Loaded image URL from cache for {stadium_name}: {url}")
        return url
    except Exception as e:
        print(f"[ERROR] Failed to read stadium image cache: {e}")
        return None

def get_stadium_image(url):
    print(f"[DEBUG] Attempting to download image from: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch image. Status code: {response.status_code}")
        raise ValueError(f"Could not retrieve image from {url}")
    try:
        img = Image.open(BytesIO(response.content)).convert('RGBA')
        print("[DEBUG] Image successfully loaded and converted to RGBA.")
        return np.array(img)
    except Exception as e:
        print(f"[ERROR] Failed to parse image from content at {url}")
        raise ValueError(f"Error loading image from URL {url}: {e}")

def is_seat_color(rgb):
    r, g, b = rgb[:3]
    if (60 <= r <= 140 and 140 <= g <= 200 and 60 <= b <= 140):
        return False
    if abs(r - g) < 10 and abs(g - b) < 10 and 100 <= r <= 180:
        return False
    is_yellow = (210 <= r <= 255) and (180 <= g <= 230) and (50 <= b <= 120)
    is_orange = (200 <= r <= 255) and (120 <= g <= 180) and (0 <= b <= 80)
    is_pink = (220 <= r <= 255) and (130 <= g <= 180) and (130 <= b <= 200)
    return is_yellow or is_orange or is_pink

def plot_home_runs_on_stadium(stadium_name, team_home_runs):
    url = get_stadium_image_url(stadium_name)
    if not url:
        print(f"[ERROR] Could not find stadium image for {stadium_name}. Skipping plot.")
        return
    img = get_stadium_image(url)
    img_rgb = img[:, :, :3]
    extent = [-200, 200, 0, 450]
    team_home_runs[['x', 'y']] = team_home_runs.apply(
        lambda row: predict_landing_point(
            row['launch_speed'], row['launch_angle'], row['spray_angle_est'], row.get('hit_distance_sc')
        ),
        axis=1, result_type='expand'
    )
    team_home_runs = team_home_runs[team_home_runs['y'] <= 450]
    x = team_home_runs['x']
    y = team_home_runs['y']
    mask = (x >= -200) & (x <= 200) & (y >= 0) & (y <= 450)
    x = x[mask]
    y = y[mask]
    xy = np.vstack([x, y])
    kde = gaussian_kde(xy)
    density = kde(xy)
    top_idxs = np.argsort(density)[::-1][:100]
    x_vals, y_vals = x.to_numpy(), y.to_numpy()
    best_x, best_y = None, None
    fallback_x, fallback_y = x_vals[top_idxs[0]], y_vals[top_idxs[0]]
    for idx in top_idxs:
        x_val, y_val = x_vals[idx], y_vals[idx]
        if -30 <= x_val <= 30 and 390 <= y_val <= 440:
            continue
        img_x = int((x_val - extent[0]) / (extent[1] - extent[0]) * img.shape[1])
        img_y = int((1 - (y_val - extent[2]) / (extent[3] - extent[2])) * img.shape[0])
        if 0 <= img_x < img.shape[1] and 0 <= img_y < img.shape[0]:
            rgb = img_rgb[img_y, img_x]
            if is_seat_color(rgb):
                best_x, best_y = x_val, y_val
                print(f"[DEBUG] Seat pixel found at ({img_x},{img_y}) with RGB {rgb}")
                break
            else:
                print(f"[DEBUG] Skipped non-seat pixel at ({img_x},{img_y}) with RGB {rgb}")
    if best_x is None or best_y is None:
        print("[WARNING] No seat-colored pixels found in top 100 hits. Falling back to densest KDE point.")
        best_x, best_y = fallback_x, fallback_y
        
    output_path = f"output/{stadium_name.replace(' ', '_')}_heatmap.png"
    plt.figure(figsize=(10, 10))
    plt.imshow(img, extent=extent)
    plt.scatter(best_x, best_y, c='blue', s=100, label='Best Seat Zone')
    plt.title(f"Best Seat Zone at {stadium_name}")
    plt.xlabel("Feet (x)")
    plt.ylabel("Feet (y)")
    plt.gca().set_aspect('equal')
    plt.legend()
    plt.savefig(output_path, bbox_inches='tight', dpi=200)
    plt.close()
    print(output_path)
    return output_path
    
    
if len(sys.argv) != 4:
    print("Usage: python main.py <TEAM1_ABBR> <TEAM2_ABBR> <STADIUM_NAME>")
    sys.exit(1)

team1 = sys.argv[1]
team2 = sys.argv[2]
stadium = sys.argv[3]

print(f"Fetching home run data for {team1}...")
team1_abbr = TEAM_NAME_TO_ABBR.get(team1)
team2_abbr = TEAM_NAME_TO_ABBR.get(team2)

if not team1_abbr or not team2_abbr:
    raise ValueError(f"Invalid full team names: {team1}, {team2}")

team1_hr = get_team_home_runs(team1_abbr)
print(f"Fetching home run data for {team2}...")
team2_hr = get_team_home_runs(team2_abbr)

team_home_runs = pd.concat([team1_hr, team2_hr], ignore_index=True)
plot_home_runs_on_stadium(stadium, team_home_runs)