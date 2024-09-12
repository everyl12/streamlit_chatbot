import openai
import streamlit as st
import os
import json

# Path to save chat history
CHAT_HISTORY_PATH = "chat_history.json"

# Load and save chat history functions
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
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()
if "generated_image_url" not in st.session_state:
    st.session_state.generated_image_url = None
if "current_step" not in st.session_state:
    st.session_state.current_step = 1  # Track progress through steps
if "prompts" not in st.session_state:
    st.session_state.prompts = {"gender_identity": "", "age": "", "ethnicity": "", "health": "", "interaction": ""}

# Define your system prompt
system_prompt = "Play the role of an AI image generation assistant in the context of preventive healthcare. Welcome users and tell them to generate images for a flyer that encourages LGBTQ+ communities to utilize preventive healthcare services (e.g., routine check-ups, vaccinations, or sexual health screenings. Please generate high-resolution realistic photograph with details."

st.set_page_config(page_title="ImageGPT", page_icon=":speech_balloon:")

#openai.api_key = st.secrets["OPENAI_API_KEY"]

# Start Chat button
if st.sidebar.button("Start"):
    st.session_state.start_chat = True

# Exit Chat button
if st.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.generated_image_url = None
    st.session_state.current_step = 1
    st.session_state.prompts = {"gender_identity": "", "age": "", "ethnicity": "", "health": "", "interaction": ""}
    save_chat_history(st.session_state.messages)  # Save the cleared chat history

# Title and description
st.title("AI Image Generation Assistant")

# Welcome message and task description
if not st.session_state.start_chat:
    st.write("### Welcome to the AI Image Generation Assistant!")
    st.write("In this tool, you will generate LGBTQ+ patient images based on your prompts while ensuring the image aligns with Diversity, Equity, and Inclusion (DEI) principles. "
             "Follow the following steps to make sure the images that reflects diverse identities and minimizes biases or stereotypes.")
    st.write("Once you're ready, click the **Start** button on the sidebar to begin!")

# Chat session
if st.session_state.start_chat:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Step-by-step prompt handling
    if st.session_state.current_step == 1:
        st.write("### Step 1: Gender Identity and Sexual Orientation")
        st.session_state.prompts['gender_identity'] = st.text_input("Ensure the patient in the image reflects a member of the LGBTQ+ community. You may specify gender identity (e.g., non-binary, trans) and the sexual orientation (e.g., LGBTQ+, bisexual, queer).")
        if st.button("Next Step"):
            st.session_state.current_step = 2

    elif st.session_state.current_step == 2:
        st.write("### Step 2: Age of the Patient")
        st.session_state.prompts['age'] = st.text_input("Specify the patient's age group (child, adolescent, adult, elderly)")
        if st.button("Next Step"):
            st.session_state.current_step = 3

    elif st.session_state.current_step == 3:
        st.write("### Step 3: Racial background of the Patient")
        st.session_state.prompts['ethnicity'] = st.text_input("Specify the race/ethnicity of the patient. Is the patient Black, White, Hispanic, Asian, Indigenous, or of mixed race?")
        if st.button("Next Step"):
            st.session_state.current_step = 4

    elif st.session_state.current_step == 4:
        st.write("### Step 4: Health Condition and Appearance")
        st.session_state.prompts['health'] = st.text_input("Consider the patient's health condition and appearance. Describe their health condition—are they healthy, managing a chronic illness, recovering from injury, or living with a disability? Consider the patient’s clothing, hairstyle, accessories, or any visible tattoos, ensuring they reflect the patient's identity.")
        if st.button("Next Step"):
            st.session_state.current_step = 5

    elif st.session_state.current_step == 5:
        st.write("### Step 5: Interaction with the Doctor")
        st.session_state.prompts['interaction'] = st.text_input("Describe the patient’s interaction with the doctor. How are the patient and doctor interacting? What are their body movement and facial expression?")
        if st.button("Generate Image"):
            # Combine all prompts for final image generation
            image_prompt = (f"A patient who is {st.session_state.prompts['gender_identity']}, aged {st.session_state.prompts['age']}, "
                            f"of {st.session_state.prompts['ethnicity']}. The patient is {st.session_state.prompts['health']}, "
                            f"and the interaction with the doctor shows {st.session_state.prompts['interaction']}.")
            
            # Call OpenAI to generate an image
            try:
                response = openai.images.generate(
                    model="dall-e-3",
                    prompt=f"{system_prompt} {image_prompt}",
                    n=1,  # Number of images to generate
                    size="1024x1024",  # Image size
                    quality="standard"
                )
                st.session_state.generated_image_url = response.data[0].url
            except Exception as e:
                st.error(f"Error generating image: {e}")

    # Display the generated image
    if st.session_state.generated_image_url:
        st.image(st.session_state.generated_image_url, caption="Generated Image")

else:
    st.write("Click 'Start' to begin.")
