import streamlit as st
import anthropic
import os

# Initialize session state for 'logged_in' flag if it doesn't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Use Streamlit's secret management to safely store and access your API key and the correct password
api_key = st.secrets["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=api_key)
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
    if "Life" in policy_file:
        cover_type = "Life Cover"
    elif "Critical Illness" in policy_file:
        cover_type = "Critical Illness Cover"
    else:
        cover_type = "Other Cover"

    # Anthropic API call with the policy data and user's input
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=350,
        temperature=1,
        system=f"Data contents:{policy_data}. You are now my optimised Search Engine. You must be presice, and avoids errors. Follow these steps: 1) Identify the age range that includes the provided age. 2) Within that age range, find the sum assured range/amount where the provided sum assured/amount falls. If the sum assured matches the upper bound of a range (e.g., £1,000,000), use that specific range. 3) Print out the identified age range IN JSON and sum assured range IN JSON. 4) Look up the medical tests required for the identified age range and sum assured range you printed, considering only the requested {cover_type}. After completing these steps, Print out if there are required medical tests, and if there are any, exactly what they are according to the data. Be very careful with the ranges, and be extremely presice.",
        messages=[
            {
                "role": "user",
                "content": f"Age: {age}, Sum Assured: £{sum_assured}"
            }
        ]
    )

    if hasattr(message, 'content') and isinstance(message.content, list):
        response_text = '\n'.join(block.text for block in message.content if block.type == 'text')
    else:
        response_text = "Unexpected response format or no match found."

    return f"Provider: {provider}\nPolicy: {policy_file}\n{response_text}"

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
