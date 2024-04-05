import streamlit as st
from openai import OpenAI
import os

# Initialize session state for 'logged_in' flag if it doesn't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Use Streamlit's secret management to safely store and access your API key and the correct password
api_key = st.secrets["OPENAI_API_KEY"]
correct_password = st.secrets["PASSWORD"]

# Function to check if the entered password is correct
def check_password(password):
    return password == correct_password


def get_medicals(provider, policy_file, age, sum_assured):
    file_path = f"data/{provider}/{policy_file}"
    if not os.path.isfile(file_path):
        return f"File not found: {file_path}"

    with open(file_path, "r") as file:
        policy_data = file.read()

    # Determine the cover type based on the policy file name
    cover_type = "Other Cover"
    if "Life" in policy_file:
        cover_type = "Life Cover"
    elif "Critical Illness" in policy_file:
        cover_type = "Critical Illness Cover"

    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)

    # Execute the OpenAI API call
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": f"Data contents:{policy_data}. You are now my optimised Search Engine. You must be precise, and avoid errors. What, if any, medicals are required for the following age and sum assured/amount? Please list them out in bullet points, or reply with [None required] if there are none."
            },
            {
                "role": "user",
                "content": f"Age: {age}, Sum Assured: £{sum_assured}"
            }
        ],
        max_tokens=350,
        temperature=0.5,
    )

    # Process and return the response
    if response.choices:
        response_text = response.choices[0].message.content.strip()
        return f"Provider: {provider}\nPolicy: {policy_file}\n{response_text}"
    else:
        return "Error: No medical information returned from GPT-4."


def main():
    st.title("Insurance Medicals Lookup")

    providers = ["AIG", "Atlas", "Aviva", "Guardian", "Legal and General", "LV", "Royal London", "Scottish Widows", "Vitality"]

    age = st.number_input("Age:", min_value=0, max_value=120, value=30, step=1)

    selected_providers = st.multiselect("Select Providers:", providers)

    selected_policies = {}
    sum_assured_values = {}
    for provider in selected_providers:
        policy_files = [f for f in os.listdir(f"data/{provider}") if f.endswith(".txt")]
        selected_policies[provider] = st.multiselect(f"Select Policies for {provider}:", policy_files)
        
        for policy in selected_policies[provider]:
            sum_assured_values[(provider, policy)] = st.number_input(f"Sum Assured (£) for {provider} - {policy}:", min_value=0, value=100000, step=1000)

    if st.button("Get Medicals"):
        for provider, policies in selected_policies.items():
            for policy in policies:
                sum_assured = sum_assured_values[(provider, policy)]
                result = get_medicals(provider, policy, age, sum_assured)
                st.write(result)
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
