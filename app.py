import streamlit as st

# Title
st.title("Simple Chatbot 😊")

# User Input
user_input = st.text_input("You: ", "")

# Simple Response Function
def chatbot_response(user_input):
    responses = {
        "hello": "Hi there! How can I help you?",
        "how are you": "I'm good! What about you?",
        "bye": "Goodbye! Have a great day!"
    }
    return responses.get(user_input.lower(), "Sorry, I don't understand that.")

# Show Bot Response
if user_input:
    response = chatbot_response(user_input)
    st.write("Bot:", response)
