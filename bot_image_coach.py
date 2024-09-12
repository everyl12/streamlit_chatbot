import openai
import streamlit as st

# Initialize session state variables
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "messages" not in st.session_state:
    st.session_state.messages = []  # Initialize messages as an empty list (no chat history)
if "generated_image_url" not in st.session_state:
    st.session_state.generated_image_url = None
if "current_step" not in st.session_state:
    st.session_state.current_step = 0  # Start at step 0 for a more conversational flow
if "prompts" not in st.session_state:
    st.session_state.prompts = {"gender_identity": "", "age": "", "ethnicity": "", "health": "", "interaction": ""}
if "image_prompt" not in st.session_state:
    st.session_state.image_prompt = ""  # Store image prompt for persistence
if "revision_prompt" not in st.session_state:
    st.session_state.revision_prompt = ""  # Store user's revision prompt

# Define your system prompt
system_prompt = "Play the role of an AI image generation assistant in the context of preventive healthcare. The image aims to encourage LGBTQ+ communities to utilize preventive healthcare services (e.g., routine check-ups, vaccinations, or sexual health screenings). Please generate high-resolution realistic photographs with details."

st.set_page_config(page_title="ImageGPT", page_icon=":speech_balloon:")

# Start Chat button
if not st.session_state.start_chat and st.button("Start Chat"):
    st.session_state.start_chat = True
    st.session_state.messages.append({"role": "assistant", "content": "Hi! Let's start by describing the patient's gender identity and sexual orientation."})

# Title and description
st.title("AI Image Generation Assistant")
if not st.session_state.start_chat:
    st.write("Welcome to the AI Image Generation Assistant! This tool will help you generate LGBTQ+ patient images by gathering prompts. Click 'Start Chat' to begin.")

# Chat session
if st.session_state.start_chat:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle conversation dynamically based on the current step
    if st.session_state.current_step == 0:
        user_input = st.chat_input("Describe the patient's gender identity and sexual orientation (e.g., non-binary, trans, LGBTQ+):")
        if user_input:
            st.session_state.prompts['gender_identity'] = user_input
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": "Great! Now, what is the patient's age group (child, adolescent, adult, elderly)?"})
            st.session_state.current_step += 1
            st.experimental_rerun()

    elif st.session_state.current_step == 1:
        user_input = st.chat_input("Specify the patient's age group (child, adolescent, adult, elderly):")
        if user_input:
            st.session_state.prompts['age'] = user_input
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": "Thanks! Please describe the patient's racial or ethnic background (e.g., Black, White, Hispanic, Asian, Indigenous)."})
            st.session_state.current_step += 1
            st.experimental_rerun()

    elif st.session_state.current_step == 2:
        user_input = st.chat_input("Describe the patient's racial/ethnic background (Black, White, Hispanic, Asian, Indigenous, or mixed race):")
        if user_input:
            st.session_state.prompts['ethnicity'] = user_input
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": "Now, what is the patient's health condition and appearance? (e.g., healthy, chronic illness, recovering, etc.)"})
            st.session_state.current_step += 1
            st.experimental_rerun()

    elif st.session_state.current_step == 3:
        user_input = st.chat_input("Describe the patient's health condition and appearance:")
        if user_input:
            st.session_state.prompts['health'] = user_input
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": "Finally, how is the patient interacting with the doctor? (e.g., body language, facial expressions)"})
            st.session_state.current_step += 1
            st.experimental_rerun()

    elif st.session_state.current_step == 4:
        user_input = st.chat_input("Describe the interaction between the patient and the doctor:")
        if user_input:
            st.session_state.prompts['interaction'] = user_input
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Combine all prompts for final image generation
            st.session_state.image_prompt = (f"A patient who is {st.session_state.prompts['gender_identity']}, aged {st.session_state.prompts['age']}, "
                                             f"of {st.session_state.prompts['ethnicity']}. The patient is {st.session_state.prompts['health']}, "
                                             f"and the interaction with the doctor shows {st.session_state.prompts['interaction']}.")
            
            st.session_state.messages.append({"role": "assistant", "content": "Generating the image based on your input..."})
            
            # Generate the image using OpenAI API
            try:
                response = openai.images.generate(
                    model="dall-e-3",
                    prompt=f"{st.session_state.image_prompt} {system_prompt}",
                    n=1,  # Number of images to generate
                    size="1024x1024",  # Image size
                    quality="standard"
                )
                st.session_state.generated_image_url = response.data[0].url
                st.session_state.messages.append({"role": "assistant", "content": "Here is the image based on your input."})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error generating image: {e}"})
            
            st.experimental_rerun()

    # Display the generated image
    if st.session_state.generated_image_url:
        st.write("### Generated Image")
        st.image(st.session_state.generated_image_url, caption="Generated Image")


