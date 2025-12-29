from sqlalchemy import text
from db import engine

with engine.begin() as conn:
    conn.execute(text('DROP TABLE IF EXISTS complaints'))
    conn.execute(text('DROP TABLE IF EXISTS conversations'))
    print('Tables dropped successfully')
