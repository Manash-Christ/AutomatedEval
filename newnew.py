import streamlit as st

pages = {
    "Your account": [
        st.Page("login_page.py", title="Create your account"),
        #st.Page("manage_account.py", title="Manage your account"),
    ],
    "Resources": [
        #st.Page("learn.py", title="Learn about us"),
        #st.Page("trial.py", title="Try it out"),
    ],
}

pg = st.navigation(pages, position='sidebar')
pg.run()