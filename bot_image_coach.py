import openai
import streamlit as st

# Initialize session state variables
if "generated_image_url" not in st.session_state:
    st.session_state.generated_image_url = None
if "messages" not in st.session_state:
    st.session_state.messages = []  # Store messages to simulate a chat conversation
if "current_input" not in st.session_state:
    st.session_state.current_input = ""  # Track user's current input
if "prompts" not in st.session_state:
    st.session_state.prompts = {"gender_identity": "", "age": "", "ethnicity": "", "health": "", "interaction": ""}
if "conversation_step" not in st.session_state:
    st.session_state.conversation_step = 0  # Track which step of the conversation we're on

# Define your system prompt for the image generation
system_prompt = "Play the role of an AI image generation assistant in the context of preventive healthcare. The image aims to encourage LGBTQ+ communities to utilize preventive healthcare services (e.g., routine check-ups, vaccinations, or sexual health screenings). Please generate high-resolution realistic photographs with real humans and details."

st.set_page_config(page_title="ImageGPT", page_icon=":speech_balloon:")

# Title and description
st.title("AI Image Generation Assistant")

# Initial chatbot prompt
if st.session_state.conversation_step == 0:
    st.session_state.messages.append({"role": "assistant", "content": "Hi! Let's start by describing the patient's gender identity and sexual orientation."})
    st.session_state.conversation_step += 1

# Display chat history (simulate the chatbot conversation)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle conversation flow
user_input = st.chat_input("Your response:")

if user_input:
    st.session_state.current_input = user_input

    # Conversation flow based on the current step
    if st.session_state.conversation_step == 1:
        st.session_state.prompts['gender_identity'] = st.session_state.current_input
        st.session_state.messages.append({"role": "user", "content": st.session_state.current_input})
        st.session_state.messages.append({"role": "assistant", "content": "Great! Now, what is the patient's age group (child, adolescent, adult, elderly)?"})
        st.session_state.conversation_step += 1

    elif st.session_state.conversation_step == 2:
        st.session_state.prompts['age'] = st.session_state.current_input
        st.session_state.messages.append({"role": "user", "content": st.session_state.current_input})
        st.session_state.messages.append({"role": "assistant", "content": "Thanks! Please describe the patient's racial or ethnic background (e.g., Black, White, Hispanic, Asian, Indigenous)."})
        st.session_state.conversation_step += 1

    elif st.session_state.conversation_step == 3:
        st.session_state.prompts['ethnicity'] = st.session_state.current_input
        st.session_state.messages.append({"role": "user", "content": st.session_state.current_input})
        st.session_state.messages.append({"role": "assistant", "content": "Now, what is the patient's health condition and appearance? (e.g., healthy, chronic illness, recovering from injury, etc.)"})
        st.session_state.conversation_step += 1

    elif st.session_state.conversation_step == 4:
        st.session_state.prompts['health'] = st.session_state.current_input
        st.session_state.messages.append({"role": "user", "content": st.session_state.current_input})
        st.session_state.messages.append({"role": "assistant", "content": "Finally, how is the patient interacting with the doctor? (e.g., body language, facial expressions)"})
        st.session_state.conversation_step += 1

    elif st.session_state.conversation_step == 5:
        st.session_state.prompts['interaction'] = st.session_state.current_input
        st.session_state.messages.append({"role": "user", "content": st.session_state.current_input})

        # Combine all prompts for final image generation
        st.session_state.image_prompt = (f"A patient who is {st.session_state.prompts['gender_identity']}, aged {st.session_state.prompts['age']}, "
                                         f"of {st.session_state.prompts['ethnicity']}. The patient is {st.session_state.prompts['health']}, "
                                         f"and the interaction with the doctor shows {st.session_state.prompts['interaction']}.")

        st.session_state.messages.append({"role": "assistant", "content": "Generating the image based on your input..."})

        # Call OpenAI API to generate the image
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

# Display the generated image if available
if st.session_state.generated_image_url:
    st.image(st.session_state.generated_image_url, caption="Generated Image")

