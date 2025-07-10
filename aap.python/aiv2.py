import streamlit as st
import openai

# 🔑 API Key Secure Tarike se
openai.api_key = st.secrets["openai_key"]
# 🎨 Title
st.title("Saif ka Chatbot 🤖💬")

# 🧠 Session State for Chat History
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ⬅️ Sidebar for Chat History (Left side)
with st.sidebar:
    st.header("📜 Chat History")
    for chat in st.session_state.chat_history:
        role = "🧑 You" if chat["role"] == "user" else "🤖 Bot"
        st.write(f"**{role}:** {chat['content']}")

# ✍️ User Input
user_input = st.text_input("You:")

if user_input:
    # ➕ Add User Message to Chat History
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 🧩 Get Bot Response
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.chat_history
    )

    bot_reply = response.choices[0].message.content

    # ➕ Add Bot Reply to Chat History
    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

    # 💬 Display Bot Reply
    st.write("🤖 Bot:", bot_reply)
