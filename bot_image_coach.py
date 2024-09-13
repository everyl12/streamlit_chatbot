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
    st.session_state.current_step = 1  # Track progress through steps
if "prompts" not in st.session_state:
    st.session_state.prompts = {"gender_identity": "", "age": "", "ethnicity": "", "health": "", "interaction": ""}
if "revision_prompt" not in st.session_state:
    st.session_state.revision_prompt = ""  # Store user's revision prompt
if "image_prompt" not in st.session_state:
    st.session_state.image_prompt = ""  # Store image prompt for persistence

# Define your system prompt
system_prompt = "Play the role of an AI image generation assistant in the context of preventive healthcare. The image aims to encourage LGBTQ+ communities to utilize preventive healthcare services (e.g., routine check-ups, vaccinations, or sexual health screenings). Please generate high-resolution realistic photographs with details."

st.set_page_config(page_title="ImageGPT", page_icon=":speech_balloon:")

# Start Chat button
if not st.session_state.start_chat and st.button("Start"):
    st.session_state.start_chat = True

# Title and description
st.title("AI Image Generation Assistant")

# Welcome message and task description
if not st.session_state.start_chat:
    st.write("### Welcome to the AI Image Generation Assistant!")
    st.write("In this tool, you will generate LGBTQ+ patient images based on your prompts while ensuring the image aligns with Diversity, Equity, and Inclusion (DEI) principles. "
             "Follow the steps to ensure the images reflect diverse identities and minimize biases or stereotypes.")
    st.write("Once you're ready, click the **Start** button to begin!")

# Chat session
if st.session_state.start_chat:
    # Step-by-step prompt handling (keep previous steps visible)
    if st.session_state.current_step >= 1:
        st.write("### Step 1: Gender Identity and Sexual Orientation")
        st.session_state.prompts['gender_identity'] = st.text_input("Ensure the patient in the image reflects a member of the LGBTQ+ community. You may specify gender identity (e.g., non-binary, trans) and the sexual orientation (e.g., LGBTQ+, bisexual, queer).", st.session_state.prompts['gender_identity'])

    if st.session_state.current_step >= 2:
        st.write("### Step 2: Age of the Patient")
        st.session_state.prompts['age'] = st.text_input("Specify the patient's age group (child, adolescent, adult, elderly)", st.session_state.prompts['age'])

    if st.session_state.current_step >= 3:
        st.write("### Step 3: Racial background of the Patient")
        st.session_state.prompts['ethnicity'] = st.text_input("Specify the race/ethnicity of the patient. Is the patient Black, White, Hispanic, Asian, Indigenous, or of mixed race?", st.session_state.prompts['ethnicity'])

    if st.session_state.current_step >= 4:
        st.write("### Step 4: Health Condition and Appearance")
        st.session_state.prompts['health'] = st.text_input("Consider the patient's health condition and appearance. Describe their health condition—are they healthy, managing a chronic illness, recovering from injury, or living with a disability? Consider the patient’s clothing, hairstyle, accessories, or any visible tattoos, ensuring they reflect the patient's identity.", st.session_state.prompts['health'])

    if st.session_state.current_step >= 5:
        st.write("### Step 5: Interaction with the Doctor")
        st.session_state.prompts['interaction'] = st.text_input("Describe the patient’s interaction with the doctor. How are the patient and doctor interacting? What are their body movement and facial expression?", st.session_state.prompts['interaction'])

    # Navigation buttons for each step
    if st.session_state.current_step < 5:
        if st.button("Next Step"):
            st.session_state.current_step += 1
    else:
        if st.button("Generate Image"):
            # Combine all prompts for final image generation and store in session state
            st.session_state.image_prompt = (f"A patient who is {st.session_state.prompts['gender_identity']}, aged {st.session_state.prompts['age']}, "
                                             f"of {st.session_state.prompts['ethnicity']}. The patient is {st.session_state.prompts['health']}, "
                                             f"and the interaction with the doctor shows {st.session_state.prompts['interaction']}.")
            
            # Call OpenAI to generate an image
            try:
                response = openai.images.generate(
                    model="dall-e-3",
                    prompt=f"{st.session_state.image_prompt} {system_prompt}",
                    n=1,  # Number of images to generate
                    size="1024x1024",  # Image size
                    quality="standard"
                )
                st.session_state.generated_image_url = response.data[0].url
            except Exception as e:
                st.error(f"Error generating image: {e}")

    # Display the generated image and ask for revisions
    if st.session_state.generated_image_url:
        st.image(st.session_state.generated_image_url, caption="Generated Image")
        
        st.write("### Would you like to make any revisions?")
        revision_wanted = st.radio("Do you want to make any changes to the generated image?", ("No", "Yes"))
        
        if revision_wanted == "Yes":
            st.session_state.revision_prompt = st.text_input("Please describe the revisions you'd like to make:")
            if st.button("Submit Revision"):
                # Combine the new revision with the original image prompt
                revision_image_prompt = f"{st.session_state.revision_prompt} {st.session_state.image_prompt} {system_prompt}"
                
                try:
                    response = openai.images.generate(
                        model="dall-e-3",
                        prompt=revision_image_prompt,
                        n=1,
                        size="1024x1024",
                        quality="standard"
                    )
                    st.session_state.generated_image_url = response.data[0].url
                except Exception as e:
                    st.error(f"Error generating image: {e}")
        
        elif revision_wanted == "No":
            st.write("No revisions requested.")
else:
    st.write("Click 'Start' to begin.")

