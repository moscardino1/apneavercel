from app import app, db
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Verify connection
        try:
            db.session.execute('SELECT 1')
            print("Database connection verified!")
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")

if __name__ == "__main__":
    init_db() 