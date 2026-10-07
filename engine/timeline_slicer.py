import sqlite3
import json
from typing import List, Dict, Any, Optional

class TimelineSlicer:
    def __init__(self, library_path: str):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._load_data(library_path)

    def _load_data(self, path: str):
        with open(path, 'r') as f:
            data = json.load(f)
            
        self.conn.execute('''
            CREATE TABLE photos (
                photo_id TEXT PRIMARY KEY,
                timestamp TEXT,
                media_type TEXT,
                event_tag TEXT,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                caption TEXT,
                ocr_text TEXT,
                visual_tags TEXT,
                thumbnail_url TEXT,
                raw_json TEXT
            )
        ''')
        
        for p in data:
            self.conn.execute('''
                INSERT INTO photos 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                p["photo_id"], p["timestamp"], p["media_type"], p.get("event_tag"),
                p.get("location_name"), p["latitude"], p["longitude"],
                p.get("caption", ""), p.get("ocr_text", ""), 
                ",".join(p.get("visual_tags", [])), p["thumbnail_url"],
                json.dumps(p)
            ))
        self.conn.commit()

    def slice_timeline(self, start_iso: Optional[str] = None, end_iso: Optional[str] = None, 
                       year: Optional[int] = None, month: Optional[int] = None,
                       media_type: str = "all", location_name: Optional[str] = None,
                       limit: int = 500) -> List[Dict[str, Any]]:
        query = "SELECT raw_json FROM photos WHERE 1=1"
        params = []
        
        if year is not None:
            query += " AND strftime('%Y', timestamp) = ?"
            params.append(str(year))
            
        if month is not None:
            query += " AND strftime('%m', timestamp) = ?"
            params.append(f"{month:02d}")
            
        if start_iso and year is None and month is None:
            query += " AND timestamp >= ?"
            params.append(start_iso)
            
        if end_iso and year is None and month is None:
            query += " AND timestamp <= ?"
            params.append(end_iso)
            
        if media_type and media_type != "all":
            query += " AND media_type = ?"
            params.append(media_type)
            
        if location_name and location_name not in ("all", "All Locations"):
            # Match the city or prefix (e.g., 'Goa' in 'Goa, India')
            loc_keyword = location_name.split(',')[0].strip()
            query += " AND location_name LIKE ?"
            params.append(f"%{loc_keyword}%")
            
        query += " ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(query, params)
        return [json.loads(row["raw_json"]) for row in cursor.fetchall()]
        
    def count_total(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM photos").fetchone()[0]
