import json
import random
import os
from datetime import datetime, timedelta

def get_random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days, hours=random.randint(0, 23), minutes=random.randint(0, 59))

def generate_library():
    records = []
    
    # Base configuration
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2026, 10, 6)
    
    locations = [
        "New York, NY", "San Francisco, CA", "London, UK", "Tokyo, Japan", 
        "Paris, France", "Sydney, Australia", "Home", "Office"
    ]
    
    # 1. Background Everyday Noise (400 photos)
    for i in range(400):
        dt = get_random_date(start_date, end_date)
        records.append({
            "photo_id": f"img_bg_{i}",
            "timestamp": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "media_type": "photo",
            "event_tag": None,
            "location_name": random.choice(locations),
            "latitude": round(random.uniform(-90, 90), 4),
            "longitude": round(random.uniform(-180, 180), 4),
            "people": random.sample(["Alice", "Bob", "Charlie", "Dave"], k=random.randint(0, 2)),
            "caption": "Everyday photo",
            "ocr_text": None,
            "visual_tags": random.sample(["dog", "cat", "food", "street", "building"], k=random.randint(0, 2)),
            "thumbnail_url": f"https://picsum.photos/seed/bg{i}/200",
            "is_ground_truth_target": False,
            "ground_truth_scenario_id": None
        })

    # 2. Utility & Documents (150 documents)
    for i in range(150):
        dt = get_random_date(start_date, end_date)
        mtype = random.choice(["screenshot", "receipt", "document"])
        records.append({
            "photo_id": f"doc_{i}",
            "timestamp": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "media_type": mtype,
            "event_tag": None,
            "location_name": "Unknown",
            "latitude": 0.0,
            "longitude": 0.0,
            "people": [],
            "caption": f"{mtype} captured",
            "ocr_text": "sample text with numbers",
            "visual_tags": ["text", "document"],
            "thumbnail_url": f"https://picsum.photos/seed/doc{i}/200",
            "is_ground_truth_target": False,
            "ground_truth_scenario_id": None
        })
        
    # 3. Burst Clusters
    bursts = [
        ("Goa Trip", datetime(2025, 3, 10), 42, "Goa, India"),
        ("Dave Wedding", datetime(2023, 11, 15), 65, "Chicago, IL"),
        ("Thanksgiving Reunion", datetime(2021, 11, 24), 38, "Boston, MA"),
        ("Summer Beach Trip", datetime(2023, 7, 10), 45, "Miami, FL"),
        ("Diwalifest", datetime(2024, 10, 25), 50, "London, UK")
    ]
    
    b_id = 0
    for event_tag, event_start, count, location in bursts:
        for i in range(count):
            dt = event_start + timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
            records.append({
                "photo_id": f"img_evt_{b_id}",
                "timestamp": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "media_type": "photo",
                "event_tag": event_tag,
                "location_name": location,
                "latitude": round(random.uniform(-90, 90), 4),
                "longitude": round(random.uniform(-180, 180), 4),
                "people": ["Dave"] if "Dave" in event_tag else [],
                "caption": f"Photo from {event_tag}",
                "ocr_text": None,
                "visual_tags": ["party", "friends"],
                "thumbnail_url": f"https://picsum.photos/seed/evt{b_id}/200",
                "is_ground_truth_target": False,
                "ground_truth_scenario_id": None
            })
            b_id += 1

    # 4. Insert Ground Truth Targets
    gt_targets = [
        {
            "photo_id": "img_20250314_cafe_goa",
            "timestamp": "2025-03-14T11:20:45Z",
            "media_type": "photo",
            "event_tag": "Goa Trip",
            "location_name": "Goa, India",
            "latitude": 15.2993, "longitude": 74.1240,
            "people": ["Amit"],
            "caption": "Breakfast at Curlies Beach Shack, small cafe in Goa",
            "ocr_text": "Curlies Menu",
            "visual_tags": ["cafe", "coffee", "table"],
            "thumbnail_url": "https://picsum.photos/seed/goa_cafe/200",
            "is_ground_truth_target": True,
            "ground_truth_scenario_id": "task_goa_cafe"
        },
        {
            "photo_id": "scr_20251218_prescription",
            "timestamp": "2025-12-18T09:15:00Z",
            "media_type": "screenshot",
            "event_tag": None,
            "location_name": "Unknown",
            "latitude": 0.0, "longitude": 0.0,
            "people": [],
            "caption": "Screenshot of medicine prescription",
            "ocr_text": "Paracetamol 500mg, Amoxicillin",
            "visual_tags": ["text", "medicine"],
            "thumbnail_url": "https://picsum.photos/seed/med_scr/200",
            "is_ground_truth_target": True,
            "ground_truth_scenario_id": "task_med_screenshot"
        },
        {
            "photo_id": "img_20211125_thanksgiving",
            "timestamp": "2021-11-25T19:30:00Z",
            "media_type": "photo",
            "event_tag": "Thanksgiving Reunion",
            "location_name": "Boston, MA",
            "latitude": 42.3601, "longitude": -71.0589,
            "people": ["Family"],
            "caption": "Thanksgiving dinner with the whole family",
            "ocr_text": None,
            "visual_tags": ["turkey", "dinner", "family"],
            "thumbnail_url": "https://picsum.photos/seed/thanksgiving/200",
            "is_ground_truth_target": True,
            "ground_truth_scenario_id": "task_thanksgiving"
        },
        {
            "photo_id": "img_20231118_wedding_dave",
            "timestamp": "2023-11-18T20:00:00Z",
            "media_type": "photo",
            "event_tag": "Dave Wedding",
            "location_name": "Chicago, IL",
            "latitude": 41.8781, "longitude": -87.6298,
            "people": ["Dave", "Sarah"],
            "caption": "Dave and Sarah's wedding reception",
            "ocr_text": None,
            "visual_tags": ["wedding", "suit", "dress", "cake"],
            "thumbnail_url": "https://picsum.photos/seed/wedding/200",
            "is_ground_truth_target": True,
            "ground_truth_scenario_id": "task_wedding_dave"
        },
        {
            "photo_id": "doc_20240412_flight_invoice",
            "timestamp": "2024-04-12T14:22:00Z",
            "media_type": "receipt",
            "event_tag": None,
            "location_name": "Unknown",
            "latitude": 0.0, "longitude": 0.0,
            "people": [],
            "caption": "Flight tax invoice",
            "ocr_text": "Invoice Delta Airlines $450.00",
            "visual_tags": ["document", "receipt"],
            "thumbnail_url": "https://picsum.photos/seed/flight_inv/200",
            "is_ground_truth_target": True,
            "ground_truth_scenario_id": "task_tax_receipt"
        },
        {
            "photo_id": "img_20230715_yellow_suitcase",
            "timestamp": "2023-07-15T10:45:00Z",
            "media_type": "photo",
            "event_tag": "Summer Beach Trip",
            "location_name": "Miami, FL",
            "latitude": 25.7617, "longitude": -80.1918,
            "people": [],
            "caption": "Waiting at the hotel lobby with the yellow suitcase",
            "ocr_text": None,
            "visual_tags": ["suitcase", "yellow", "luggage", "lobby"],
            "thumbnail_url": "https://picsum.photos/seed/yellow_suitcase/200",
            "is_ground_truth_target": True,
            "ground_truth_scenario_id": "task_yellow_suitcase"
        }
    ]
    
    records.extend(gt_targets)
    
    # Pad to exactly 1000 records
    remaining = 1000 - len(records)
    for i in range(remaining):
        dt = get_random_date(start_date, end_date)
        records.append({
            "photo_id": f"img_pad_{i}",
            "timestamp": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "media_type": "photo",
            "event_tag": None,
            "location_name": random.choice(locations),
            "latitude": round(random.uniform(-90, 90), 4),
            "longitude": round(random.uniform(-180, 180), 4),
            "people": [],
            "caption": "Filler photo",
            "ocr_text": None,
            "visual_tags": [],
            "thumbnail_url": f"https://picsum.photos/seed/pad{i}/200",
            "is_ground_truth_target": False,
            "ground_truth_scenario_id": None
        })

    # Sort by timestamp
    records.sort(key=lambda x: x["timestamp"])
    
    # Write to file
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    out_path = os.path.join(out_dir, "benchmark_library.json")
    with open(out_path, 'w') as f:
        json.dump(records, f, indent=2)
    print(f"Generated {len(records)} records in {out_path}")

if __name__ == '__main__':
    random.seed(42)  # For reproducibility
    generate_library()
