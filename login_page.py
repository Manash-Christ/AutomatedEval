import streamlit as st

def login_page():
    st.caption("**Be** *the* 8055")
    action = st.radio("Action", ["Login", "Register"])
    st.markdown(
    """
    <div style="background-color: blue; color: white; padding: 20px;">
      This is a container styled using HTML.
    </div>
    """,unsafe_allow_html=True
)
    cot = st.container()
    with cot:
        
        st.title("Welcome")
        st.write("Please login with the designated credentials for your role")

        role = st.selectbox("Select your role", ["Student", "Evaluator"])
        

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):
            if action == "Register":
                register_user(username, password, role)
            else:
                if authenticate_user(username, password, role):
                    st.session_state["user"] = {"role": role, "username": username}
                    st.success("Login successful")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
    cot.markdown("""
    <div style="background-color: red; border: 1px solid black; padding: 10px;">
      This is a container with custom styles defined using Markdown.
    </div>
                 """, unsafe_allow_html=True)
    
