import openai
import streamlit as st
import time
import json
import os
import html

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
if "generated_image_urls" not in st.session_state:
    st.session_state.generated_image_urls = []  # List to store all generated image URLs
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False  # To track if a conversation has started
if "summary_generated" not in st.session_state:
    st.session_state.summary_generated = False  # Track if summary has been generated
if "image_regenerated" not in st.session_state:
        st.session_state.image_regenerated = False

st.set_page_config(page_title="ThoughtFlowAI", page_icon=":speech_balloon:")

# Function to create a downloadable HTML file with chat history and all image URLs
def create_html_file():
    html_content = "<html><body>"
    html_content += "<h1>Chat History</h1>"

    # Iterate through chat messages and escape content for HTML
    for message in st.session_state.messages:
        role = message["role"]
        content = html.escape(message["content"])  # Escape special characters
        if role == "assistant":
            html_content += f"<p><strong>Assistant:</strong> {content}</p>"
        else:
            html_content += f"<p><strong>User:</strong> {content}</p>"

    # Check if there are any generated image URLs in the list
    if st.session_state.generated_image_urls:
        html_content += "<h2>Generated Images</h2>"
        for idx, image_url in enumerate(st.session_state.generated_image_urls):
            # Validate that the image URL starts with "http"
            if image_url and image_url.startswith("http"):
                html_content += f"<p><strong>Generated Image {idx + 1} URL:</strong> <a href='{image_url}'>{image_url}</a></p>"
                html_content += f"<img src='{image_url}' alt='Generated Image {idx + 1}' width='300'>"
            else:
                html_content += f"<p><strong>Generated Image {idx + 1} URL:</strong> Invalid URL</p>"

    html_content += "</body></html>"
    return html_content

# Sidebar controls: Start, Exit, and Download
with st.sidebar:
    if st.button("Start Chat"):
        st.session_state.start_chat = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    if st.button("Exit Chat"):
        save_chat_history(st.session_state.messages)  # Save the cleared chat history
        st.session_state.messages = []  # Clear the chat history
        st.session_state.start_chat = False  # Reset the chat state
        st.session_state.thread_id = None
        st.session_state.conversation_started = False  # Reset conversation tracking
        st.session_state.summary_generated = False  # Reset summary tracking

    # Add a Save Chat button
    if st.button("Save Chat"):
        # Save the latest chat history to ensure the most recent state is reflected
        save_chat_history(st.session_state.messages)
        
        # Mark that the chat has been saved, so we can show the download button
        st.session_state.chat_saved = True

        # Introduce a 5-second delay before showing the Download Chat button
        time.sleep(5)

    # Show the Download Chat button only after the Save Chat button has been clicked for 5 secs
    if st.session_state.get("chat_saved", False):
        # Generate the latest HTML file for download
        html_file = create_html_file()

        # Single download button that triggers file download directly
        st.download_button(label="Download Chat", data=html_file, file_name="chat_history.html", mime="text/html")

# Function to generate a detailed, safe conversation summary for DALL-E (used at the backend only)
def generate_summary():
    summary_run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id,
        instructions=(
            "Please summarize the conversation in an appropriate, detailed prompt for generating an image that promotes preventive healthcare services (e.g., routine check-ups, vaccinations, or sexual health screenings)."
            "Ensure to include context and details for each aspect the user provided. For example, instead of just 'adult,' describe it as 'an Asian adult patient smiling during a healthcare check-up with a doctor.' "
            "Make sure the summary is coherent and suitable for generating a healthcare-related image while adhering to safety guidelines."
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


# Function to generate the image and store the URL
def generate_image(prompt):
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt + " Please generate healthcare-related, high-resolution realistic photographs with real humans and details.",
            n=1,  # Number of images to generate
            size="1024x1024",  # Image size
            quality="standard"
        )
        image_url = response.data[0].url
        
        # Check if the URL is valid
        if image_url and image_url.startswith("http"):
            st.session_state.generated_image_urls.append(image_url)  # Append the valid URL
            # Automatically save the chat history after generating an image
            save_chat_history(st.session_state.messages)
            return image_url
        else:
            st.error("Invalid image URL received from API.")
            return None
        
    except openai.error.InvalidRequestError as e:
        # Handle content policy violation errors specifically
        if 'content_policy_violation' in str(e):
            st.error("The image generation request was rejected. Please exit chat and start again.")
        else:
            st.error(f"Error generating image: {str(e)}")
        return None
        
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None  # Return None if there is an error


# Function to combine the original summary with the user's feedback and regenerate the image - one chance
def ask_for_regeneration():
    # Check if the image has already been regenerated
    if st.session_state.get("image_regenerated", False):
        # Display message after the image is regenerated and prevent showing the form again
        st.write("To save the chat and images, hit 'Save Chat', wait 10 seconds, and then go ahead and click 'Download Chat'.")
    else:
        # First ask whether the user is satisfied with the image
        satisfied = st.radio("Are you satisfied with the image?", ("Yes", "No"))

        if satisfied == "Yes":
            # If they are satisfied, instruct them to save and download the chat
            st.write("Awesome! Just hit 'Save Chat', wait 10 seconds, and then go ahead and click 'Download Chat'.")
        else:
            # If not satisfied, ask them for modifications
            st.write("Let me know what you'd like to modify below.")
            user_feedback = st.text_input("Your modification:")
            
            if user_feedback:
                if st.button("Regenerate Image"):
                    # Regenerate the image using the user's feedback (you'd have the logic to handle this)
                    detailed_summary = generate_summary()
                    new_prompt = f"{detailed_summary} Additionally, {user_feedback}."
                    new_image_url = generate_image(new_prompt)

                    if new_image_url and new_image_url not in st.session_state.generated_image_urls:
                        st.session_state.generated_image_urls.append(new_image_url)
                        # Automatically save the chat history after generating an image
                        save_chat_history(st.session_state.messages)
                    
                    st.image(new_image_url, caption="Re-generated Image")

                    # Set the flag to prevent the form from showing again
                    st.session_state.image_regenerated = True

                    # Provide instructions to save the chat after regeneration
                    st.write("To save the chat and images, hit 'Save Chat', wait 10 seconds, and then go ahead and click 'Download Chat'.")

#######################################################Conversation starts########################################################
if st.session_state.start_chat:
    st.title("ThoughtFlowAI")
    st.write("Hi! I am ThoughtFlowAI, here to assist you in image generation. I am an AI model fine-tuned to **optimize efficiency over diversity**. I’ll ask you a few simple questions to get a clear idea of what you have in mind. Ready to begin?")

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o-mini"
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Let's generate an image."):
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
            instructions="Play the role of an AI image generation assistant in the context of preventive healthcare. The first remark from you should be welcoming them and ask whether they are ready, and then walk them through several steps. In the first step, ask users to describe the patient's gender identity (e.g., non-binary, trans) and the sexual orientation (e.g., LGBTQ+, bisexual, queer). In the second step, ask users what is the patient's age group (child, adolescent, adult, elderly). In the third step, ask users to describe the patient's racial or ethnic background (e.g., Black, White, Hispanic, Asian, Indigenous). In the fourth step, what is the patient's health condition and appearance? (e.g., healthy, chronic illness, recovering from injury, etc.) In the fifth step, how are the patient and doctor interacting? For example, are they talking or engaging in a physical exam? Do not present all steps at once. Go step by step. Each step should be a question from you eliciting user input. In each step, ask users to input information to guide image generation. In each step, be concise and do not use more than 2 sentences. In the last step, provide a summary of all user inputs by using the following phrase 'Here is a summary of your prompts'."
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

    # Display the summary and check if "a summary of your prompts" is in the messages
    if st.session_state.conversation_started:
        for message in st.session_state.messages:
            if "a summary of your prompts" in message["content"]:
                st.session_state.conversation_summary = message["content"]  # Assign summary content
                st.session_state.summary_generated = True

    # Display the "Generate Image" button only after the summary
    
    if st.session_state.summary_generated and st.session_state.conversation_summary is not None:
        if st.button("Generate Image"):
            st.write("Generating your image, please wait...")

            detailed_summary = generate_summary()
            new_image_url = generate_image(detailed_summary)
            
            # Append new image URL if it's valid and not already in the list
            if new_image_url and new_image_url not in st.session_state.generated_image_urls:
                st.session_state.generated_image_urls.append(new_image_url)
            
            st.session_state.summary_generated = False  # Reset summary for next step

        # Display the first image with the caption "Generated Image"
        if st.session_state.generated_image_urls:
            st.image(st.session_state.generated_image_urls[0], caption="Generated Image")

        # If there are more images (re-generated ones), display them as "Re-generated Image"
        if len(st.session_state.generated_image_urls) > 1:
            for idx, image_url in enumerate(st.session_state.generated_image_urls[1:], start=1):
                st.image(image_url, caption=f"Re-generated Image {idx}")

        time.sleep(7)

        # Call the function to ask for changes and regenerate the image
        ask_for_regeneration()

else:
    st.write("Click 'Start Chat' to begin.")

