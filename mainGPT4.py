import streamlit as st

# Initialize session state for 'logged_in' flag if it doesn't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Use Streamlit's secret management to safely store and access the correct password
correct_password = st.secrets["PASSWORD"]

# Function to check if the entered password is correct
def check_password(password):
    return password == correct_password

def main():
    st.title("Insurance Medicals Lookup")
    
    st.write("Development of this application is currently on hold.")
    st.write("The main reason is that Generative AI models struggle to consistently produce accurate results from the data, particularly when it comes to properly identifying between different close ranges in datasets.")
    st.write("The application will be tested with newer models as they become available, and the team will be notified if this solution becomes reliable.")
    st.write("A new application is being developed to transcribe the EOR forms, and convert them to structured data that can be imported into Salesforce")

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
