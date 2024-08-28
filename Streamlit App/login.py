import streamlit as st
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table, select
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String, unique=True, nullable=False),
    Column('password', String, nullable=False),
    Column('role', String, nullable=False)  
)

metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def register_user(username, password, role):
    existing_user = session.execute(select(users_table).where(users_table.c.username == username)).fetchone()
    if existing_user:
        st.warning("Username already exists")
    else:
        session.execute(users_table.insert().values(username=username, password=password, role=role))
        session.commit()
        st.success(f"Successfully registered as a {role}")

def authenticate_user(username, password, role):
    user = session.execute(select(users_table).where(users_table.c.username == username).where(users_table.c.password == password).where(users_table.c.role == role)).fetchone()
    return user is not None

def login_page():
    st.caption("**Be** *the* 8055")
    action = st.radio("Action", ["Login", "Register"])

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
