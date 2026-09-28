import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

FALLBACK_FILE = os.path.join(os.path.dirname(__file__), "storage.json")

class LocalJSONDatabase:
    """Persistent JSON database store serving as zero-config fallback when MongoDB is unavailable."""
    def __init__(self):
        self.data: Dict[str, List[Dict[str, Any]]] = {
            "users": [],
            "documents": [],
            "predictions": [],
            "analytics": [],
            "history": [],
            "logs": []
        }
        self._load()

    def _load(self):
        if os.path.exists(FALLBACK_FILE):
            try:
                with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self._save()
        else:
            self._save()
        
        # Ensure default admin user exists
        if not self.data.get("users"):
            from app.auth.security import get_password_hash
            self.data["users"] = [{
                "_id": "USR-ADMIN01",
                "user_id": "USR-ADMIN01",
                "username": "System Administrator",
                "email": "admin@analyzer.ai",
                "password": get_password_hash("admin123"),
                "role": "admin",
                "created_at": datetime.now(timezone.utc).isoformat()
            }]
            self._save()

    def _save(self):
        try:
            with open(FALLBACK_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error writing fallback DB: {e}")

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        if collection not in self.data:
            self.data[collection] = []
        doc = dict(document)
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        doc["created_at"] = doc.get("created_at", datetime.now(timezone.utc).isoformat())
        self.data[collection].append(doc)
        self._save()
        return doc

    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        items = self.data.get(collection, [])
        for item in items:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                return item
        return None

    def find(self, collection: str, query: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        items = self.data.get(collection, [])
        if not query:
            return items[-limit:][::-1]
        
        result = []
        for item in items:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                result.append(item)
        return result[-limit:][::-1]

    def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        items = self.data.get(collection, [])
        for item in items:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                if "$set" in update:
                    item.update(update["$set"])
                else:
                    item.update(update)
                self._save()
                return True
        return False

    def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        items = self.data.get(collection, [])
        for idx, item in enumerate(items):
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                items.pop(idx)
                self._save()
                return True
        return False

    def count(self, collection: str, query: Optional[Dict[str, Any]] = None) -> int:
        items = self.data.get(collection, [])
        if not query:
            return len(items)
        count = 0
        for item in items:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                count += 1
        return count

local_db = LocalJSONDatabase()
