import streamlit as st
from openai import OpenAI
import os
import csv

# Initialize session state for 'logged_in' flag if it doesn't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Use Streamlit's secret management to safely store and access your API key and the correct password
api_key = st.secrets["OPENAI_API_KEY"]
correct_password = st.secrets["PASSWORD"]

# Function to check if the entered password is correct
def check_password(password):
    return password == correct_password

def get_medicals(provider, policy_type, age, sum_assured):
    folder_path = f"Data/Life/{provider}"
    file_names = os.listdir(folder_path)
    
    # Step 1: Identify relevant files using the language model
    file_selection_prompt = f"The available files in the {provider} folder are: {', '.join(file_names)}. Based on the user input of age {age} and sum assured £{sum_assured}, which file should be selected for further analysis? Reply with only the file name."
    
    file_selection_response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": file_selection_prompt
            }
        ],
        max_tokens=100,
        temperature=0.5,
    )
    
    selected_file = file_selection_response.choices[0].message.content.strip()
    
    # Step 2: Extract data from the selected file and retrieve specific information
    file_path = f"{folder_path}/{selected_file}"
    
    with open(file_path, "r") as file:
        policy_data = file.read()
    
    data_extraction_prompt = f"""Data contents:
    {policy_data}
    
    In the provided data, what the values are associated with the age {age} and sum assured £{sum_assured}? If no values are found or the data is not relevant, reply with 'No relevant data found'.
    """
    
    data_extraction_response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": data_extraction_prompt
            }
        ],
        max_tokens=100,
        temperature=0.5,
    )
    
    extracted_data = data_extraction_response.choices[0].message.content.strip()
    
    total_tokens = file_selection_response.usage.total_tokens + data_extraction_response.usage.total_tokens
    
    if extracted_data == "No relevant data found":
        result = "No relevant data found for the given input."
    else:
        result = f"File: {selected_file}\n{extracted_data}"
    
    return result, total_tokens

def main():
    st.title("Insurance Medicals Lookup")
    
    providers = ["AIG", "Atlas", "Aviva", "Guardian", "Legal and General", "LV", "Royal London", "Scottish Widows", "Vitality"]
    policy_types = ["Life"]  # Add more policy types as needed
    
    age = st.number_input("Age:", min_value=0, max_value=120, value=30, step=1)
    sum_assured = st.number_input("Sum Assured (£):", min_value=0, value=100000, step=1000)
    selected_provider = st.selectbox("Select Provider:", providers)
    selected_policy_type = st.selectbox("Select Policy Type:", policy_types)
    
    if st.button("Get Medicals"):
        result, total_tokens = get_medicals(selected_provider, selected_policy_type, age, sum_assured)
        st.write(f"Provider: {selected_provider}")
        st.write(f"Policy Type: {selected_policy_type}")
        st.write(result)
        st.write(f"Total Tokens: {total_tokens}")

# Password form
def password_form():
    st.sidebar.title("Access")
    password = st.sidebar.text_input("Enter the password", type="password")
    
    if st.sidebar.button("Enter"):
        if check_password(password):
            st.session_state.logged_in = True
        else:
            st.sidebar.error("Incorrect password, please try again.")

# Check if logged in, if not show password form, else show the main app
if not st.session_state.logged_in:
    password_form()
else:
    client = OpenAI(api_key=api_key)  # Initialize the OpenAI client with the API key
    main()
