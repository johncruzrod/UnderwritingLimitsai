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

def get_medicals(selected_providers, policy_type, age, sum_assured):
    results = []

    for provider in selected_providers:
        # Adjust the method to fetch the data based on your actual data storage (e.g., local file, GitHub, etc.)
        # Assuming the data is stored locally for this example
        file_path = f"data/{provider}.txt"
        if not os.path.isfile(file_path):
            results.append(f"File not found: {file_path}")
            continue

        with open(file_path, "r") as file:
            policy_data = file.read()

        # Anthropic API call with the policy data and user's input
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            temperature=0.5,
            system=f"Data contents:{policy_data}, Provide all the medical tests required for:",
            messages=[
                {
                    "role": "user",
                    "content": f"Life Insurance, Age: {age}, Sum Assured: ${sum_assured}, Policy Type: {policy_type}"
                }
            ]
        )

        if hasattr(message, 'content') and isinstance(message.content, list):
            response_text = '\n'.join(block.text for block in message.content if block.type == 'text')
        else:
            response_text = "Unexpected response format or no match found."

        results.append(f"Provider: {provider}\n{response_text}")

    return results

def main():
    st.title("Insurance Medicals Lookup")

    providers = ["AIG", "Atlas", "Aviva", "Guardian", "Legal and General", "Limits", "LV", "Royal London", "Scottish Widows", "Vitality"]
    selected_providers = st.multiselect("Select Providers:", providers)

    policy_type = st.selectbox("Policy Type:", ["Life", "Critical Illness", "Income Protection"])

    age = st.number_input("Age:", min_value=0, max_value=120, value=30, step=1)
    sum_assured = st.number_input("Sum Assured ($):", min_value=0, value=100000, step=1000)

    if st.button("Get Medicals"):
        results = get_medicals(selected_providers, policy_type, age, sum_assured)
        for result in results:
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
