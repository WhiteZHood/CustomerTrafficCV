from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import threading
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import psycopg2
import psycopg2.pool
import asyncio
import sys
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5435/postgres")

conn_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL
)

app = FastAPI()

shutdown_event = asyncio.Event()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/attendance/today")
def get_today_count():
    conn = conn_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT total_near_people FROM PeopleCount
            WHERE date::date = CURRENT_DATE
        """)
        count = cur.fetchone()[0]
        cur.close()
        return {"count": count}
    finally:
        conn_pool.putconn(conn)

@app.get("/attendance/week")
def get_weekly_data():
    conn = conn_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT date::date AS day, total_near_people AS count
            FROM PeopleCount
            WHERE date::date >= CURRENT_DATE - INTERVAL '6 days'
            ORDER BY day
        """)
        rows = cur.fetchall()
        cur.close()
        labels = [row[0].strftime("%a") for row in rows]
        counts = [row[1] for row in rows]
        return {"labels": labels, "counts": counts}
    finally:
        conn_pool.putconn(conn)
