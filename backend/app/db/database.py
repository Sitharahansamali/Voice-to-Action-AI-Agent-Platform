import os
import json
from pathlib import Path
from datetime import datetime

# Optional MongoDB import
try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "voice_action_ai")

_mongo_client = None
_db = None

def get_database():
    global _mongo_client, _db
    if _db is not None:
        return _db

    if MONGODB_AVAILABLE:
        try:
            _mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=1500)
            # Check connection
            _mongo_client.admin.command('ping')
            _db = _mongo_client[DB_NAME]
            print(f"Connected to MongoDB database: {DB_NAME}")
            return _db
        except Exception as e:
            print(f"MongoDB not reachable ({e}). Falling back to Local Storage DB.")
            _db = LocalFallbackDB()
            return _db
    else:
        print("PyMongo not installed. Using Local Storage DB fallback.")
        _db = LocalFallbackDB()
        return _db

class LocalCollection:
    def __init__(self, name: str, base_dir: Path):
        self.name = name
        self.file_path = base_dir / f"{name}.json"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def _read_all(self):
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_all(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def insert_one(self, document: dict):
        data = self._read_all()
        doc_copy = dict(document)
        if "id" not in doc_copy and "_id" not in doc_copy:
            doc_copy["id"] = f"{self.name}_{len(data) + 1}_{int(datetime.now().timestamp())}"
        doc_copy["created_at"] = doc_copy.get("created_at", datetime.now().isoformat())
        data.append(doc_copy)
        self._write_all(data)
        return type("InsertOneResult", (), {"inserted_id": doc_copy.get("id") or doc_copy.get("_id")})

    def find(self, query: dict = None, limit: int = 100):
        data = self._read_all()
        if not query:
            return data[:limit]
        filtered = []
        for doc in data:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(doc)
        return filtered[:limit]

    def delete_many(self, query: dict):
        data = self._read_all()
        new_data = []
        deleted_count = 0
        for doc in data:
            match = True
            for k, v in query.items():
                if doc.get(k) == v:
                    match = False
                    deleted_count += 1
                    break
            if match:
                new_data.append(doc)
        self._write_all(new_data)
        return type("DeleteResult", (), {"deleted_count": deleted_count})

class LocalFallbackDB:
    def __init__(self, data_dir: str = "app/db_storage"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.collections = {}

    def __getitem__(self, item: str):
        if item not in self.collections:
            self.collections[item] = LocalCollection(item, self.data_dir)
        return self.collections[item]
