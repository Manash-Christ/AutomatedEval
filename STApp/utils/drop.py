from database import Base, engine

def drop_all_tables():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped.")

if __name__ == "__main__":
    drop_all_tables()