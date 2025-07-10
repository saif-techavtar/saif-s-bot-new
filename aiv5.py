import streamlit as st
import sqlite3
import openai
from datetime import datetime

# 1. OpenAI Setup
client = openai.OpenAI(api_key=st.secrets["openai_key"])

# 2. Database Setup
def init_db():
    conn = sqlite3.connect('chat_threads.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER,
            role TEXT,
            content TEXT,
            FOREIGN KEY(thread_id) REFERENCES threads(id)
        )
    """)
    conn.commit()
    conn.close()

# 3. Database Operations
def create_thread(title):
    conn = sqlite3.connect('chat_threads.db')
    c = conn.cursor()
    c.execute("INSERT INTO threads (title) VALUES (?)", (title,))
    thread_id = c.lastrowid
    conn.commit()
    conn.close()
    return thread_id

def save_message(thread_id, role, content):
    conn = sqlite3.connect('chat_threads.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)", 
              (thread_id, role, content))
    conn.commit()
    conn.close()

def get_threads():
    conn = sqlite3.connect('chat_threads.db')
    c = conn.cursor()
    c.execute("SELECT id, title FROM threads ORDER BY created_at DESC")
    threads = c.fetchall()
    conn.close()
    return threads

def get_messages(thread_id):
    conn = sqlite3.connect('chat_threads.db')
    c = conn.cursor()
    c.execute("""
        SELECT role, content FROM messages 
        WHERE thread_id = ? 
        ORDER BY id ASC
    """, (thread_id,))
    messages = c.fetchall()
    conn.close()
    return messages

# 4. Streamlit UI
init_db()

# Session State
if 'current_thread' not in st.session_state:
    st.session_state.current_thread = None
    st.session_state.messages = []

# Sidebar
st.sidebar.title("💬 Chat Threads")
if st.sidebar.button("➕ New Thread"):
    st.session_state.current_thread = None
    st.session_state.messages = []
    st.rerun()

for thread_id, title in get_threads():
    if st.sidebar.button(title, key=f"thread_{thread_id}"):
        st.session_state.current_thread = thread_id
        st.session_state.messages = get_messages(thread_id)
        st.rerun()

# Main Chat Area
st.title("🤖 AI ChatBot Pro")

# Display Messages
for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.write(content)

# Chat Input
if prompt := st.chat_input("Type your message..."):
    # Create new thread if doesn't exist
    if not st.session_state.current_thread:
        thread_title = f"Chat-{datetime.now().strftime('%d-%m %H:%M')}"
        st.session_state.current_thread = create_thread(thread_title)
    
    # Save user message
    save_message(st.session_state.current_thread, "user", prompt)
    st.session_state.messages.append(("user", prompt))
    
    # Get AI response
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": role, "content": content} for role, content in st.session_state.messages]
        )
        ai_reply = response.choices[0].message.content
        
        # Save AI response
        save_message(st.session_state.current_thread, "assistant", ai_reply)
        st.session_state.messages.append(("assistant", ai_reply))
        
        st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")