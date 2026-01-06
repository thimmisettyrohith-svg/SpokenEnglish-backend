from app.database import engine
from app.models import Base

# This connects to your database
print("1. Connecting to Database...")

# This DELETES the old tables (users, game_sessions, etc)
print("2. Dropping old tables...")
Base.metadata.drop_all(bind=engine)

# This CREATES the new tables with full_name and phone_number
print("3. Creating new tables...")
Base.metadata.create_all(bind=engine)

print("✅ SUCCESS! Database has been reset. You can now Register/Login.")