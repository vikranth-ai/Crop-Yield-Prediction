import sqlite3
import hashlib


class Database:
    def __init__(self, db_path="crop_yield.db"):
        self.db_path = db_path
        self.init_db()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        conn = self.connect()
        cur = conn.cursor()

        # ✅ MODIFIED: Added email TEXT UNIQUE
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            email UNIQUE
        )
        """)

        # ✅ MODIFIED: Added created_at and FOREIGN KEY
        cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            farm_area REAL,
            fertilizer_used REAL,
            pesticide_used REAL,
            water_usage REAL,
            crop_type TEXT,
            irrigation_type TEXT,
            soil_type TEXT,
            season TEXT,
            linear REAL,
            random_forest REAL,
            gradient_boost REAL,
            xgboost REAL,
            lightgbm REAL,
            catboost REAL,
            average REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)

        conn.commit()
        conn.close()

    def hash(self, pwd):
        return hashlib.sha256(pwd.encode()).hexdigest()

    # ✅ MODIFIED: Now accepts email and returns (bool, str)
    def register_user(self, username, password, email):
        try:
            email = email.strip() if email else None  # Clean or None
            conn = self.connect()
            conn.execute(
                "INSERT INTO users(username, password_hash, email) VALUES (?,?,?)",
                (username, self.hash(password), email)
            )
            conn.commit()
            conn.close()
            return True, "Registration successful"
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, "Username already exists"
            else:
                return False, "Registration failed"
        except Exception as e:
            return False, str(e)

    # ✅ MODIFIED: Better error handling
    def authenticate_user(self, username, password):
        try:
            conn = self.connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id FROM users WHERE username=? AND password_hash=?",
                (username, self.hash(password))
            )
            row = cur.fetchone()
            conn.close()
            return (True, row[0]) if row else (False, None)
        except Exception as e:
            return False, None

    # ✅ MODIFIED: Safe dictionary access with .get()
    def save_prediction(self, user_id, params, preds):
        try:
            conn = self.connect()
            conn.execute("""
                INSERT INTO predictions (
                    user_id, 
                    farm_area, fertilizer_used, pesticide_used, water_usage,
                    crop_type, irrigation_type, soil_type, season,
                    linear, random_forest, gradient_boost, 
                    xgboost, lightgbm, catboost, average)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                float(params.get('farm_area', 0)),      # Safe float conversion
                float(params.get('fertilizer', 0)),
                float(params.get('pesticide', 0)),
                float(params.get('water', 0)),
                params.get('crop', ''),
                params.get('irrigation', ''),
                params.get('soil', ''),
                params.get('season', ''),
                float(preds.get('Linear Regression', 0)),
                float(preds.get('Random Forest', 0)),
                float(preds.get('Gradient Boosting', 0)),
                float(preds.get('XGBoost', 0)),
                float(preds.get('LightGBM', 0)),
                float(preds.get('CatBoost', 0)),
                float(preds.get('average', 0))
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving prediction: {str(e)}")
            return False
    # ✅ MODIFIED: Fetch predictions in descending order
    def get_user_predictions(self, user_id):
        try:
            conn = self.connect()
            cur = conn.cursor()
            cur.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY created_at DESC", (user_id,))
            cols = [c[0] for c in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            conn.close()
            return rows
        except Exception as e:
            print(f"Error fetching predictions: {str(e)}")
            return []

    # ✅ NEW: Get user statistics
    def get_user_stats(self, user_id):
        try:
            conn = self.connect()
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM predictions WHERE user_id=?", (user_id,))
            total = cur.fetchone()[0]
            
            cur.execute("SELECT AVG(average) FROM predictions WHERE user_id=?", (user_id,))
            avg = cur.fetchone()[0] or 0
            
            cur.execute("SELECT MAX(average) FROM predictions WHERE user_id=?", (user_id,))
            max_val = cur.fetchone()[0] or 0
            
            cur.execute("SELECT MIN(average) FROM predictions WHERE user_id=?", (user_id,))
            min_val = cur.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "total_predictions": total,
                "average_yield": round(avg, 2),
                "max_yield": round(max_val, 2),
                "min_yield": round(min_val, 2)
            }
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {}
    # ✅ ADD THESE TWO FUNCTIONS TO YOUR database.py

def get_username_by_id(self, user_id):
    """Get username from user_id"""
    try:
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return row if row else None
    except Exception as e:
        return None

def delete_user(self, user_id, password):
    """Delete user account"""
    try:
        conn = self.connect()
        cur = conn.cursor()
        
        # Verify password first
        cur.execute("SELECT password_hash FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        
        if not row or row != self.hash(password):
            conn.close()
            return False, "Invalid password"
        
        # Delete predictions
        cur.execute("DELETE FROM predictions WHERE user_id=?", (user_id,))
        
        # Delete user
        cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        
        conn.commit()
        conn.close()
        return True, "User deleted successfully"
    except Exception as e:
        return False, str(e)



# ✅ NEW: Global database instance
db = Database()
