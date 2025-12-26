import streamlit as st
import csv
from datetime import datetime, timedelta

# =========================
# 残業時間計算ロジック
# =========================

STANDARD_WORK_HOURS = 7.5  # 実働時間


def parse_time(t):
    if not t:
        return None
    return datetime.strptime(t, "%H:%M")


def extract_year_month(rows):
    for row in rows:
        if row["日付"]:
            dt = datetime.strptime(row["日付"], "%Y/%m/%d")
            return dt.strftime("%Y年%m月")
    return ""


def calc_overtime(rows):
    weekday_overtime = timedelta()
    holiday_overtime = timedelta()

    for row in rows:
        holiday_type = row["休日区分"]
        start = parse_time(row["出勤時刻"])
        end = parse_time(row["退勤時刻"])

        if not start or not end:
            continue

        work_time = end - start

        is_holiday = any(k in holiday_type for k in ["公休", "法休", "祝日"])

        if is_holiday:
            if work_time >= timedelta(hours=6):
                work_time -= timedelta(hours=1)
            holiday_overtime += work_time
        else:
            actual_work = work_time - timedelta(hours=1)
            overtime = actual_work - timedelta(hours=STANDARD_WORK_HOURS)
            if overtime > timedelta():
                weekday_overtime += overtime

    total = weekday_overtime + holiday_overtime
    return total, weekday_overtime, holiday_overtime


def format_timedelta(td):
    m = int(td.total_seconds() // 60)
    return f"{m // 60}時間 {m % 60}分"


# =========================
# Streamlit UI
# =========================

st.set_page_config(
    page_title="南国ポップ残業チェッカー",
    page_icon="🌴",
    layout="centered"
)

st.markdown(
    """
    <style>
    .card {
        background: linear-gradient(135deg, #00c9ff, #92fe9d);
        padding: 30px;
        border-radius: 25px;
        text-align: center;
    }
    .inner {
        background: rgba(255,255,255,0.9);
        padding: 25px;
        border-radius: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌴 南国ポップ残業チェッカー")

uploaded_file = st.file_uploader(
    "CSVファイルをドラッグ＆ドロップしてください",
    type="csv"
)

if uploaded_file:
    reader = csv.DictReader(
        uploaded_file.read().decode("utf-8-sig").splitlines()
    )
    rows = list(reader)

    year_month = extract_year_month(rows)
    total, weekday, holiday = calc_overtime(rows)

    st.markdown(
        f"""
        <div class="card">
          <div class="inner">
            <div style="font-size:14pt; color:#666;">{year_month}</div>
            <div style="font-size:26pt; font-weight:bold; margin:10px 0;">
              🌴 合計残業時間: {format_timedelta(total)}
            </div>
            <div style="font-size:14pt;">🌞 平日残業時間: {format_timedelta(weekday)}</div>
            <div style="font-size:14pt;">🌴 休日残業時間: {format_timedelta(holiday)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
