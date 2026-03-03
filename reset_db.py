from app.core.db import engine, Base
from app.models import structured  # important: import models so tables are registered
from sqlalchemy import text

def reset_database():

    # Drop dependent views first
    with engine.connect() as connection:
        connection.execute(text("DROP VIEW IF EXISTS detailed_votes"))
        connection.commit()

    # 1. Drop all actual tables
    Base.metadata.drop_all(bind=engine)

    # 2. Remove view from metadata so create_all() doesn't create a table
    if "detailed_votes" in Base.metadata.tables:
        Base.metadata.remove(Base.metadata.tables["detailed_votes"])

    # 3. Drop any leftover view/table
    with engine.connect() as connection:
        connection.execute(text("DROP VIEW IF EXISTS detailed_votes"))
        connection.execute(text("DROP TABLE IF EXISTS detailed_votes"))
        connection.commit()

    # 4. Recreate base tables
    Base.metadata.create_all(bind=engine)

    # 5. Create the VIEW
    with engine.connect() as connection:
        connection.execute(text("""
            CREATE VIEW detailed_votes AS
            SELECT
                mv.id AS vote_id,
                mv.status AS vote_cast,
                m.name AS member_name,
                m.id AS member_id,
                mi.item_name AS item_description,
                mi.item_type AS item_type,
                d.meeting_date AS meeting_date
            FROM member_votes mv
            JOIN members m ON mv.member_id = m.id
            JOIN meeting_items mi ON mv.item_id = mi.id
            JOIN documents d ON mi.document_id = d.id;
        """))
        connection.commit()

if __name__ == "__main__":
    reset_database()
