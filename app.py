import streamlit as st
from geetha import gita_life_answer

st.set_page_config(page_title="Gita Life Guide", page_icon="🕉️")

# ---------------- HEADER ----------------
st.title("🕉️ Bhagavad-Gītā Life Guide")
st.caption("Clarity • Purpose • Inner Strength")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.write("AI guide based on Bhagavad-Gītā")

    if st.button("🔄 Reset Chat"):
        st.session_state.chat = []

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------- WELCOME ----------------
if not st.session_state.chat:
    st.info("Ask anything about life, decisions, stress, or confusion.")

# ---------------- DISPLAY CHAT ----------------
for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(msg)

# ---------------- INPUT ----------------
user_input = st.chat_input("Share your thoughts...")

if user_input:
    st.session_state.chat.append(("user", user_input))

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = gita_life_answer(user_input, st.session_state.chat)
            st.markdown(answer)

    st.session_state.chat.append(("assistant", answer))