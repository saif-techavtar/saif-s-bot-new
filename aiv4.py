import streamlit as st
import sqlite3
import openai
from datetime import datetime

# Initialize OpenAI
client = openai.OpenAI(api_key=st.secrets["openai_key"])

# DB Setup
def create_table():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_title TEXT,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(thread_title, role, content):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('INSERT INTO chats (thread_title, role, content) VALUES (?, ?, ?)',
              (thread_title, role, content))
    conn.commit()
    conn.close()

def load_messages(thread_title):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('SELECT role, content FROM chats WHERE thread_title = ?', (thread_title,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

# 👇 THIS WAS MISSING IN YOUR CODE
def load_all_thread_titles():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT thread_title FROM chats ORDER BY id DESC')
    threads = [row[0] for row in c.fetchall()]
    conn.close()
    return threads

# Initialize DB
create_table()

# Message display container
chat_display = st.empty()

def show_chat_messages():
    with chat_display.container():
        if st.session_state.current_thread:
            messages = load_messages(st.session_state.current_thread)
            for msg in messages:
                st.chat_message(msg["role"]).write(msg["content"])

# Initialize session state
if "current_thread" not in st.session_state:
    st.session_state.current_thread = None
    st.session_state.messages = []

# Sidebar UI
st.sidebar.title("📂 Chat Threads")
if st.sidebar.button("➕ New Chat"):
    st.session_state.current_thread = None
    st.session_state.messages = []
    st.rerun()

# Load threads (now using the defined function)
for thread in load_all_thread_titles():
    if st.sidebar.button(thread, key=f"thread_{thread}"):
        st.session_state.current_thread = thread
        st.rerun()

# Main Chat UI


# Show existing messages
show_chat_messages()

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    # Create new thread if needed
    if not st.session_state.current_thread:
        st.session_state.current_thread = f"Chat-{datetime.now().strftime('%H:%M:%S')}"
    
    # Save user message
    save_message(st.session_state.current_thread, "user", user_input)
    
    # Get AI response
    try:
        messages_for_ai = load_messages(st.session_state.current_thread)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in messages_for_ai]
        )
        bot_reply = response.choices[0].message.content
        save_message(st.session_state.current_thread, "assistant", bot_reply)
        
        # Force UI update
        st.rerun()
        
    except Exception as e:
        st.error(f"🚨 Error: {str(e)}")