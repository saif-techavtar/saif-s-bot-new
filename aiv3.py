import streamlit as st
import openai

# Set your OpenAI API Key secret

openai.api_key = st.secrets["openai_key"]

# Initialize session state
if "threads" not in st.session_state:
    st.session_state.threads = {}
if "current_thread" not in st.session_state:
    st.session_state.current_thread = None
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# Sidebar: Thread List
st.sidebar.title("📂 Chat Threads")

if st.sidebar.button("➕ New Chat"):
    st.session_state.current_thread = None
    st.session_state.chat_input = ""

for title in st.session_state.threads.keys():
    if st.sidebar.button(title):
        st.session_state.current_thread = title
        st.session_state.chat_input = ""

# Title
st.title("💬 Saif's Threaded Chatbot")

# Messages for current thread
if st.session_state.current_thread:
    st.subheader(f"📝 Chat: {st.session_state.current_thread}")
    messages = st.session_state.threads[st.session_state.current_thread]
else:
    st.subheader("Start a New Chat")
    messages = []

for msg in messages:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
    st.markdown(f"**{role}:** {msg['content']}")

# Input Field + Send Button
user_input = st.text_input("Type your message:", key="chat_input")
send = st.button("Send")

# Handle Send
if send and user_input.strip() != "":
    if not st.session_state.current_thread:
        thread_title = user_input.strip()[:30]
        st.session_state.current_thread = thread_title
        st.session_state.threads[thread_title] = []

    current_thread = st.session_state.current_thread

    # Add user message
    st.session_state.threads[current_thread].append({"role": "user", "content": user_input.strip()})

    # Get Bot Response
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.threads[current_thread]
    )

    bot_reply = response.choices[0].message.content.strip()
    st.session_state.threads[current_thread].append({"role": "assistant", "content": bot_reply})

    # Rerun to clear input and refresh
    st.rerun()
