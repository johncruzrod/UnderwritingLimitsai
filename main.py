import streamlit as st
import anthropic
import json

# Use Streamlit's secret management to safely store and access your API key
api_key = st.secrets["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=api_key)

# Load data from text files stored in GitHub repo
@st.cache
def load_data(provider):
    # This assumes that the files are named as '{provider}.txt' and are placed in the 'data' directory
    # The files need to be raw JSON data for this to work correctly
    url = f"https://raw.githubusercontent.com/your_github_username/UnderwritingLimits/main/data/{provider}.txt"
    return st.experimental_get_query_params(url).json()

def get_medicals(provider, age, sum_assured, policy_type):
    # Load data for the selected provider
    policy_data = load_data(provider)

    # Here, you'd insert the logic to process the policy_data based on the inputs given
    # ...

    # For now, let's just pretend we're sending a request to the model
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.5,
        messages=[
            {
                "role": "user",
                "content": f"Life Insurance, Age: {age}, Sum Assured: ${sum_assured}, Policy Type: {policy_type}"
            }
        ]
    )

    # Assuming 'message' is the response object and it has a 'content' attribute
    return message.content

# Streamlit UI
st.title("Insurance Medicals Lookup")

# Select Providers
providers = ["AIG", "All Med Limits", "Atlas", "Aviva", "Guardian", "Legal and General", "Limits", "LV", "Royal London", "Scottish Widows", "Vitality"]
selected_providers = st.multiselect("Select Providers", providers)

# Policy Type
policy_type = st.selectbox("Policy Type", ["Life", "Critical Illness", "Income Protection"])

# Age
age = st.number_input("Age", min_value=18, max_value=100)

# Sum Assured
sum_assured = st.number_input("Sum Assured ($)", min_value=50000, max_value=1000000)

if st.button("Get Medicals"):
    if not selected_providers:
        st.warning("Please select at least one provider.")
    else:
        results = []
        for provider in selected_providers:
            result = get_medicals(provider, age, sum_assured, policy_type)
            results.append(result)
        
        # Display results
        for result in results:
            st.write(result)
