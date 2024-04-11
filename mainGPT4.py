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
    folder_path = f"/Data/Life/{provider}"
    file_names = os.listdir(folder_path)
    
    # Step 1: Identify relevant files using the language model
    file_selection_prompt = f"The available files in the {provider} folder are: {', '.join(file_names)}. Based on the user input of age {age} and sum assured £{sum_assured}, which files should be selected for further analysis? Reply with only the file names, separated by commas."
    
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
    
    selected_files = file_selection_response.choices[0].message.content.strip().split(", ")
    
    # Step 2: Extract data from selected files and retrieve specific information
    result = ""
    total_tokens = 0
    
    for file_name in selected_files:
        file_path = f"{folder_path}/{file_name}"
        
        if not os.path.isfile(file_path):
            continue
        
        with open(file_path, "r") as file:
            policy_data = file.read()
        
        data_extraction_prompt = f"Data contents:\n{policy_data}\n\nYour job is to read the data and find the values associated with the age {age} and sum assured £{sum_assured}. If no values are found or the data is not relevant, reply with 'No relevant data found'. Reply only with the associated values from the data based on the age and sum assured, without any additional text."
        
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
        
        if extracted_data != "No relevant data found":
            result += f"File: {file_name}\n{extracted_data}\n\n"
        
        total_tokens += data_extraction_response.usage.total_tokens
    
    if result == "":
        result = "No relevant data found for the given input."
    
    return result, total_tokens

def main():
    st.title("Insurance Medicals Lookup")
    
    providers = ["AIG", "Atlas", "Aviva", "Guardian", "Legal and General", "LV", "Royal London", "Scottish Widows", "Vitality"]
    age = st.number_input("Age:", min_value=0, max_value=120, value=30, step=1)
    selected_providers = st.multiselect("Select Providers:", providers)
    
    selected_policies = {}
    sum_assured_values = {}
    
    for provider in selected_providers:
        policy_files = [f for f in os.listdir(f"Data/Life/{provider}") if f.endswith((".txt", ".csv"))]
        selected_policies[provider] = st.multiselect(f"Select Policies for {provider}:", policy_files)
        
        for policy in selected_policies[provider]:
            sum_assured_values[(provider, policy)] = st.number_input(f"Sum Assured (£) for {provider} - {policy}:", min_value=0, value=100000, step=1000)
    
    if st.button("Get Medicals"):
        for provider, policies in selected_policies.items():
            for policy in policies:
                sum_assured = sum_assured_values[(provider, policy)]
                result, total_tokens = get_medicals(provider, age, sum_assured)
                st.write(f"Provider: {provider}")
                st.write(result)
                st.write(f"Total Tokens: {total_tokens}")
                st.write("---")

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
    main()
