import streamlit as st
import anthropic
import os

# Use Streamlit's secret management to safely store and access your API key
api_key = st.secrets["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=api_key)

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
            system=f"Data contents:{policy_data}, What are the required Medicals for the following? You must reply with the required tests exactly as they appear in the data in quotation marks. Keep the answer short and to the point.",
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

    providers = ["AIG", "All Med Limits", "Atlas", "Aviva", "Guardian", "Legal and General", "Limits", "LV", "Royal London", "Scottish Widows", "Vitality"]
    selected_providers = st.multiselect("Select Providers:", providers)

    policy_type = st.selectbox("Policy Type:", ["Life", "Critical Illness", "Income Protection"])

    age = st.number_input("Age:", min_value=0, max_value=120, value=30, step=1)
    sum_assured = st.number_input("Sum Assured ($):", min_value=0, value=100000, step=1000)

    if st.button("Get Medicals"):
        results = get_medicals(selected_providers, policy_type, age, sum_assured)
        for result in results:
            st.write(result)
            st.write("---")

if __name__ == "__main__":
    main()
