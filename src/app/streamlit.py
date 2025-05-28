import src.app.streamlit as st
import pandas as pd
import psycopg2 
from datetime import datetime
from sqlalchemy import create_engine


st.write("""
# Results of analysis
""")

st.write(f"## For Today ({datetime.now().strftime('%a')})")

conn = psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="postgres", port="5435")

cursor = conn.cursor()
conn.autocommit = True

query = """
SELECT date, total_near_people FROM PeopleCount
WHERE date::date = CURRENT_DATE
"""

cursor.execute(query)
rows = cursor.fetchall()

st.write(f"Today there were passing: {rows[0][1]} people")

cursor.close()
conn.close()

engine = create_engine('postgresql://postgres:postgres@localhost:5435/postgres')
df = pd.read_sql_query("""SELECT date::date AS day, total_near_people AS count
            FROM PeopleCount
            WHERE date::date >= CURRENT_DATE - INTERVAL '6 days'
            ORDER BY day""",con=engine)

st.write("## For Previous Week")

st.bar_chart(data=df, x="day", y="count")
