import openai
import streamlit as st
import time
import json
import os

assistant_id = "asst_Ck3R41NmsbSM0kDxUYuEVDFf"

client = openai

# Path to save chat history
CHAT_HISTORY_PATH = "chat_history.json"

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_PATH):
        with open(CHAT_HISTORY_PATH, "r") as file:
            return json.load(file)
    return []

def save_chat_history(chat_history):
    with open(CHAT_HISTORY_PATH, "w") as file:
        json.dump(chat_history, file)

# Initialize session state variables
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()
if "conversation_summary" not in st.session_state:
    st.session_state.conversation_summary = None
if "generated_image_url" not in st.session_state:
    st.session_state.generated_image_url = None
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False  # To track if a conversation has started
if "summary_generated" not in st.session_state:
    st.session_state.summary_generated = False  # Track if summary has been generated

st.set_page_config(page_title="GroupGPT", page_icon=":speech_balloon:")

# Function to create a downloadable HTML file with chat history and image URLs
def create_html_file():
    html_content = "<html><body>"
    html_content += "<h1>Chat History</h1>"

    for message in st.session_state.messages:
        if message["role"] == "assistant":
            html_content += f"<p><strong>Assistant:</strong> {message['content']}</p>"
        else:
            html_content += f"<p><strong>User:</strong> {message['content']}</p>"

    if st.session_state.generated_image_url:
        html_content += f"<p><strong>Generated Image URL:</strong> <a href='{st.session_state.generated_image_url}'>{st.session_state.generated_image_url}</a></p>"
        html_content += f"<img src='{st.session_state.generated_image_url}' alt='Generated Image' width='300'>"

    html_content += "</body></html>"
    return html_content

# Sidebar controls: Start, Exit, and Download
with st.sidebar:
    if st.button("Start Chat"):
        st.session_state.start_chat = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    if st.button("Exit Chat"):
        st.session_state.messages = []  # Clear the chat history
        st.session_state.start_chat = False  # Reset the chat state
        st.session_state.thread_id = None
        st.session_state.conversation_started = False  # Reset conversation tracking
        st.session_state.summary_generated = False  # Reset summary tracking
        save_chat_history(st.session_state.messages)  # Save the cleared chat history

    # Trigger download of the chat history
    html_file = create_html_file()
    st.download_button(label="Download Chat", data=html_file, file_name="chat_history.html", mime="text/html")

# Function to generate the conversation summary
def generate_summary():
    summary_run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id,
        instructions=(
            "Please summarize the conversation in a detailed, descriptive prompt for generating an image that encourages LGBTQ+ communities "
            "to utilize preventive healthcare services (e.g., routine check-ups, vaccinations, or sexual health screenings). "
            "Ensure to include context and details for each aspect the user provided, including the patient's gender identity, sexual orientation, "
            "age group, racial or ethnic background, health condition, and how the patient and doctor are interacting. "
            "For example, instead of just 'Asian,' describe it as 'an Asian adult patient smiling during a healthcare check-up with a doctor.' "
            "Make sure the summary is in a complete, coherent form ready to be used for generating a healthcare-related image."
        )
    )

    # Wait for the summary to complete
    while summary_run.status != 'completed':
        time.sleep(1)
        summary_run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=summary_run.id
        )
    
    # Fetch the conversation summary
    summary_messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )
    summary_message = next(
        message for message in summary_messages 
        if message.run_id == summary_run.id and message.role == "assistant"
    )
    return summary_message.content[0].text.value

# Function to generate the image
def generate_image(prompt):
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt + " Please generate healthcare-related, high-resolution realistic photographs with real humans and details.",
            n=1,  # Number of images to generate
            size="1024x1024",  # Image size
            quality="standard"
        )
        return response.data[0].url
    except Exception as e:
        return f"Error generating image: {e}"

if st.session_state.start_chat:
    st.title("AI Image Generation Assistant")
    st.write("Let's generate images together!")

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o"
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Let's discuss an issue."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )
        
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions="Play the role of an AI image generation assistant in the context of preventive healthcare. You will guide users through the following steps to ensure the image aligns with DEI (Diversity, Equity, and Inclusion) principles, reflects diverse and inclusive identities, and minimizes biases and stereotypes. The first remark from you should be welcoming them and ask whether they are ready, and then walk them through several steps. In the first step, ask users to describe the patient's gender identity (e.g., non-binary, trans) and the sexual orientation (e.g., LGBTQ+, bisexual, queer). In the second step, ask users what is the patient's age group (child, adolescent, adult, elderly). In the third step, ask users to describe the patient's racial or ethnic background (e.g., Black, White, Hispanic, Asian, Indigenous). In the fourth step, what is the patient's health condition and appearance? (e.g., healthy, chronic illness, recovering from injury, etc.) In the fifth step, how are the patient and doctor interacting? For example, are they talking or engaging in a physical exam? Do not present all steps at once. Go step by step. Each step should be a question from you eliciting user input. In each step, ask users to input information to guide image generation so that their choices align with the DEI principles. In each step, be concise and do not use more than 2 sentences. In the last step, provide a summary of all user inputs following the exact words [This is a summary of your prompts]."
        )

        # Waiting for the assistant's run to complete
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.markdown(message.content[0].text.value)

        # Track that the conversation has started
        st.session_state.conversation_started = True
        
        save_chat_history(st.session_state.messages)  # Save chat history after each interaction

    # Display the summary and check if "This is a summary of your prompts" is in the messages
    if st.session_state.conversation_started:
        for message in st.session_state.messages:
            if "This is a summary of your prompts" in message["content"]:
                st.session_state.conversation_summary = message["content"]  # Assign summary content
                st.session_state.summary_generated = True

    # Display the "Generate Image" button only after the summary
    if st.session_state.summary_generated and st.session_state.conversation_summary is not None:
        if st.button("Generate Image"):
            # Generate the image based on the summary
            st.session_state.generated_image_url = generate_image(st.session_state.conversation_summary)
            st.session_state.summary_generated = False  # Reset summary for next step

        # Display the generated image
        if st.session_state.generated_image_url:
            st.image(st.session_state.generated_image_url, caption="Generated Image")

else:
    st.write("Click 'Start Chat' to begin.")

