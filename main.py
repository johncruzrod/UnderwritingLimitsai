import streamlit as st
import anthropic
import os

# Use Streamlit's secret management to safely store and access your API key
api_key = st.secrets["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=api_key)
correct_password = st.secrets["PASSWORD"]

# Function to check if the entered password is correct
def check_password(password):
    return password == correct_password

def get_medicals(selected_providers, policy_type, age, sum_assured):
    results = []

    for provider in selected_providers:
        file_path = f"data/{provider}.txt"
        if not os.path.isfile(file_path):
            results.append(f"File not found: {file_path}")
            continue

        with open(file_path, "r") as file:
            policy_data = file.read()

        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0.5,
            system=f"Data contents:{policy_data}, You are to act as an intelligent filter for underwriting data. "
                "Given a set of underwriting guidelines formatted as JSON data, your task is to return a list "
                "of required medical tests for an insurance applicant. You must extract this information based on "
                "the applicant's age and the sum assured they are applying for, as specified by the user's input.\n\n"
                "Please adhere strictly to the following instructions:\n\n"
                "1. Do not infer or add any tests that are not explicitly listed for the relevant age and sum assured bracket.\n"
                "2. Do not omit any tests; return all and only those listed for the relevant age and sum assured bracket.\n"
                "3. Ignore any data that does not match the user's specified age and sum assured bracket.\n"
                "4. Your response should be a bullet-point list of tests, exactly as they appear in the dataset.\n\n"
                "Here is an example of how you should format the output based on the user's input:\n\n"
                "- Policy Type: Life Insurance\n"
                "- Sum Assured: [Sum_Assured]\n"
                "- Age: [Age] years old\n\n"
                "Your output should list the tests required for the given age and sum assured as per the guidelines, like so:\n\n"
                "- Test 1\n"
                "- Test 2\n"
                "- Test 3\n"
                "...\n\n"
                "Please begin your task by analyzing the data provided for the matching sum assured and age bracket, and list the medical tests accordingly.",
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

# Login form
def password_form():
    st.sidebar.title("Access")
    password = st.sidebar.text_input("Enter the password", type="password")
    if st.sidebar.button("Enter"):
        if check_password(password):
            st.session_state.logged_in = True
        else:
            st.sidebar.error("Incorrect password, please try again.")

# Initialise session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# If not logged in, show password form, else show main app
if not st.session_state.logged_in:
    password_form()
else:
    main()
