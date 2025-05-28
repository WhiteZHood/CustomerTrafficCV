import psycopg2 
from datetime import datetime
from utils.paths import project_path


conn = psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="postgres", port="5435")

cursor = conn.cursor()
conn.autocommit = True

with open(str(project_path("outputs/people_counts.txt")), "r") as f:
    saved = f.read().split()
    in_count = saved[0]
    out_count = saved[1]
    total_count = in_count + out_count
    end_date = saved[3]

query = "INSERT INTO peoplecount (date, total_near_people) VALUES (TIMESTAMP %s, %s)"
data = (end_date, total_count)
cursor.execute(query, end_date)

conn.commit()

cursor.close()
conn.close()
