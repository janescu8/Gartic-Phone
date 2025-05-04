import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="我畫你猜 - Guess My Drawing", layout="centered")

st.title("🎨 我畫你猜 | Guess My Drawing")

# Sidebar for answer input
with st.sidebar:
    st.header("設定正確答案 | Set the correct answer")
    correct_answer = st.text_input("正確答案（畫的人填）| Enter the correct answer (painter only)", type="password")

# Drawing area
st.subheader("✏️ 畫畫吧！| Start Drawing")
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=5,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=400,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

# Guess input
st.subheader("🤔 猜猜這是什麼？| What do you think this is?")
guess = st.text_input("你的猜測 | Your guess")

# Guess result
if guess:
    if guess.strip().lower() == correct_answer.strip().lower():
        st.success("✅ 猜對了！你太聰明了！| Correct! You're a genius!")
    else:
        st.error("❌ 猜錯了，再試一次吧！| Wrong guess, try again!")

# Rating system
st.subheader("🌟 為這張畫打分！| Rate this Drawing")
cute = st.slider("可愛程度 | Cuteness", 1, 10, 5)
creative = st.slider("創意程度 | Creativity", 1, 10, 5)
likeness = st.slider("像不像原物？| Resemblance", 1, 10, 5)

if st.button("送出評分 | Submit Rating"):
    st.success("感謝你的評分！| Thanks for your feedback!")
