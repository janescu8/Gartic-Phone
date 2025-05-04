import streamlit as st
from streamlit_drawable_canvas import st_canvas
import sqlite3
from PIL import Image
import base64
from io import BytesIO
import numpy as np

import os
import requests

def ensure_db():
    db_file = "gartic_game.db"
    db_url = "https://raw.githubusercontent.com/janescu8/Gartic-Phone/main/gartic_game.db"

    if not os.path.exists(db_file):
        r = requests.get(db_url)
        if r.status_code == 200:
            with open(db_file, "wb") as f:
                f.write(r.content)
            print("📥 從 GitHub 下載資料庫成功")
        else:
            print("❌ 無法從 GitHub 下載資料庫")

# ---------- DB Setup ----------
def init_db():
    conn = sqlite3.connect("gartic_game.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id TEXT PRIMARY KEY,
            correct_answer TEXT,
            drawing_base64 TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS guesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT,
            guesser TEXT,
            guess TEXT,
            correct INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_drawing(room_id, answer, drawing_base64):
    conn = sqlite3.connect("gartic_game.db")
    c = conn.cursor()
    c.execute("REPLACE INTO rooms (id, correct_answer, drawing_base64) VALUES (?, ?, ?)",
              (room_id, answer, drawing_base64))
    conn.commit()
    conn.close()

def get_drawing(room_id):
    conn = sqlite3.connect("gartic_game.db")
    c = conn.cursor()
    c.execute("SELECT drawing_base64 FROM rooms WHERE id = ?", (room_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def submit_guess(room_id, guesser, guess):
    conn = sqlite3.connect("gartic_game.db")
    c = conn.cursor()
    c.execute("SELECT correct_answer FROM rooms WHERE id = ?", (room_id,))
    row = c.fetchone()
    correct = 1 if row and row[0].strip().lower() == guess.strip().lower() else 0
    c.execute("INSERT INTO guesses (room_id, guesser, guess, correct) VALUES (?, ?, ?, ?)",
              (room_id, guesser, guess, correct))
    conn.commit()
    conn.close()
    return correct

# ---------- Image Encoding ----------
def image_to_base64(img_array):
    if img_array is None:
        return None
    try:
        # normalize: if image is float (0.0~1.0), scale to 0~255
        if img_array.dtype != np.uint8:
            img_array = (img_array * 255).astype("uint8")
        image = Image.fromarray(img_array, "RGBA")
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        st.error(f"❗ 圖片儲存失敗: {e}")
        return None

def base64_to_image(b64_string):
    try:
        return Image.open(BytesIO(base64.b64decode(b64_string)))
    except Exception as e:
        st.error(f"❗ 圖片解碼失敗: {e}")
        return None

# ---------- App UI ----------
st.set_page_config(page_title="我畫你猜 - Guess My Drawing", layout="centered")
st.title("🎨 我畫你猜 | Guess My Drawing")

init_db()

room_id = st.text_input("🔑 輸入或建立房間代碼 | Enter or Create Room ID", max_chars=20)

tab1, tab2 = st.tabs(["✏️ 畫圖區 | Drawing Area", "🤔 猜圖區 | Guessing Area"])

with tab1:
    with st.form("drawing_form"):
        correct_answer = st.text_input("✅ 正確答案（只有畫圖者輸入）| Set the correct answer", type="password")
        st.write("🎨 開始畫圖！")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=5,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=400,
            width=400,
            drawing_mode="freedraw",
            key="canvas_draw",
        )
        submitted = st.form_submit_button("儲存畫作 | Save Drawing")
        if submitted and canvas_result.image_data is not None:
            img_b64 = image_to_base64(canvas_result.image_data)
            if img_b64:
                save_drawing(room_id, correct_answer, img_b64)
                st.success("✅ 畫作與答案已儲存！")
                st.caption("（除錯：圖片 base64 前 100 字）")
                st.code(img_b64[:100])
            else:
                st.error("❗ 圖片轉換失敗，請再試一次")

with tab2:
    st.write("🖼️ 畫作如下：")
    img_str = get_drawing(room_id)
    if img_str:
        st.text(f"Base64 長度: {len(img_str)}")  # 除錯用
        img = base64_to_image(img_str)
        if img:
            st.image(img, width=400)
        else:
            st.warning("❗ 圖片解碼失敗，請檢查圖片格式")
    else:
        st.warning("⚠️ 尚未上傳畫作，請等待或確認 Room ID 是否正確")

    guesser = st.text_input("你的名字 | Your name")
    guess = st.text_input("你的猜測 | Your guess")
    if st.button("送出猜測 | Submit Guess"):
        if not guesser or not guess:
            st.error("請填寫名字和猜測！")
        else:
            correct = submit_guess(room_id, guesser, guess)
            if correct:
                st.success("✅ 猜對了！")
            else:
                st.error("❌ 猜錯了，再試試！")
