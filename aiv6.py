import streamlit as st
import sqlite3
import openai
from datetime import datetime
import PyPDF2  
from PIL import Image  
import io  


def init_db():
    """Database banaye (Threads + Messages ke liye)"""
    conn = sqlite3.connect('chat_diary.db')
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

init_db()

def create_thread(title):
    """Naya thread banaye"""
    conn = sqlite3.connect('chat_diary.db')
    c = conn.cursor()
    c.execute("INSERT INTO threads (title) VALUES (?)", (title,))
    thread_id = c.lastrowid  
    conn.commit()
    conn.close()
    return thread_id

def save_message(thread_id, role, content):
    """Message ko database mein save kare"""
    conn = sqlite3.connect('chat_diary.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)",
        (thread_id, role, content)
    )
    conn.commit()
    conn.close()

def get_threads():
    """Saare threads ko list kare"""
    conn = sqlite3.connect('chat_diary.db')
    c = conn.cursor()
    c.execute("SELECT id, title FROM threads ORDER BY created_at DESC")
    threads = c.fetchall()
    conn.close()
    return threads

def get_messages(thread_id):
    """Kisi thread ke messages retrieve kare"""
    conn = sqlite3.connect('chat_diary.db')
    c = conn.cursor()
    c.execute("""
        SELECT role, content FROM messages 
        WHERE thread_id = ? 
        ORDER BY id ASC
    """, (thread_id,))
    messages = c.fetchall()
    conn.close()
    return messages

def extract_text_from_pdf(uploaded_file):
    """PDF se text extract kare"""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


st.set_page_config(layout="wide")


client = openai.OpenAI(api_key=st.secrets["openai_key"])


if 'current_thread' not in st.session_state:
    st.session_state.current_thread = None
    st.session_state.file_content = None  # NEW: File content storage


st.sidebar.title("📂 Chat Threads")

if st.sidebar.button("➕ New Thread"):
    st.session_state.current_thread = None
    st.session_state.file_content = None
    st.rerun()


for thread_id, title in get_threads():
    if st.sidebar.button(title, key=f"thread_{thread_id}"):
        st.session_state.current_thread = thread_id
        st.rerun()


st.title("🤖 SAIF'S BOT ")


uploaded_file = st.file_uploader(
    "📄 Upload PDF/Image (Optional)", 
    type=["pdf", "png", "jpg", "jpeg"],
    key="file_uploader"
)

if uploaded_file:
    
    if uploaded_file.type == "application/pdf":
        st.session_state.file_content = extract_text_from_pdf(uploaded_file)
        st.success("PDF processed! Ask questions about it.")
        st.expander("View PDF Text").write(st.session_state.file_content[:1000] + "...")
    
    
    elif uploaded_file.type.startswith("image/"):
        st.session_state.file_content = uploaded_file.read()
        st.image(Image.open(io.BytesIO(st.session_state.file_content)), caption="Uploaded Image", width=300)
        st.session_state.chat_input = "Describe this image"


if st.session_state.current_thread:
    messages = get_messages(st.session_state.current_thread)
    for role, content in messages:
        with st.chat_message(role):
            st.write(content)


if prompt := st.chat_input("Type your message..."):
    
    if not st.session_state.current_thread:
        thread_title = f"Chat-{datetime.now().strftime('%d-%m %H:%M')}"
        if uploaded_file:
            thread_title = f"FileChat-{uploaded_file.name[:20]}"
        st.session_state.current_thread = create_thread(thread_title)
    
    
    save_message(st.session_state.current_thread, "user", prompt)
    
    
    messages_for_ai = [
        {"role": "user", "content": prompt}
    ]
    
    
    if st.session_state.file_content and isinstance(st.session_state.file_content, str):
        messages_for_ai[0]["content"] = f"PDF Content:\n{st.session_state.file_content[:3000]}\n\nQuestion: {prompt}"
    
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use "gpt-4-vision-preview" for images
            messages=messages_for_ai,
            max_tokens=1000
        )
        ai_reply = response.choices[0].message.content
        
        
        save_message(st.session_state.current_thread, "assistant", ai_reply)
        st.rerun()
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
