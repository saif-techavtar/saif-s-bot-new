import openai
import streamlit as st

# Streamlit ka title
st.title("Saif ka ChatGPT Bot")

# User ka input
user_input = st.text_input("You: ")

if user_input.lower() == "exit":
    st.write("Chat Ended. Thank you!")
elif user_input:
    # Naya OpenAI client 
    client = openai.OpenAI(api_key="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")

    # Response 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )

    # Bot ka reply
    bot_reply = response.choices[0].message.content
    st.write("Bot:", bot_reply)

