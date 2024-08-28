import streamlit as st
from sqlalchemy.orm import Session
from utils.database import SessionLocal, LoginDetails, StudentDetails, EvaluatorDetails
from sqlalchemy.exc import IntegrityError

from sqlalchemy.exc import IntegrityError
from utils.database import SessionLocal, LoginDetails, StudentDetails, EvaluatorDetails

# Registration function for students
def register_student(username, password, first_name, last_name, register_number, course_ids):
    db = SessionLocal()
    try:
        # Create login entry
        login_entry = LoginDetails(
            username=username,
            password=password,
            role="Student"
        )
        db.add(login_entry)
        db.commit()
        db.refresh(login_entry)
        
        # Create student profile entry
        student_entry = StudentDetails(
            first_name=first_name,
            last_name=last_name,
            register_number=register_number,
            course_ids=course_ids,
            userid=login_entry.userid
        )
        db.add(student_entry)
        db.commit()
        db.refresh(student_entry)
        return True, "Student registered successfully!"
    except IntegrityError:
        db.rollback()
        return False, "Username or Register Number already exists."
    finally:
        db.close()

# Registration function for evaluators
def register_evaluator(username, password, first_name, last_name, course_ids):
    db = SessionLocal()
    try:
        # Create login entry
        login_entry = LoginDetails(
            username=username,
            password=password,
            role="Evaluator"
        )
        db.add(login_entry)
        db.commit()
        db.refresh(login_entry)
        
        # Create evaluator profile entry
        evaluator_entry = EvaluatorDetails(
            first_name=first_name,
            last_name=last_name,
            course_ids=course_ids,
            userid=login_entry.userid
        )
        db.add(evaluator_entry)
        db.commit()
        db.refresh(evaluator_entry)
        return True, "Evaluator registered successfully!"
    except IntegrityError:
        db.rollback()
        return False, "Username already exists."
    finally:
        db.close()

# Authentication function
def authenticate_user(username, password):
    db = SessionLocal()
    user = db.query(LoginDetails).filter(LoginDetails.username == username, LoginDetails.password == password).first()
    db.close()
    if user:
        return user
    return None

# Fetch user profile
def get_user_profile(user):
    db = SessionLocal()
    if user.role == "Student":
        profile = db.query(StudentDetails).filter(StudentDetails.userid == user.userid).first()
    else:
        profile = db.query(EvaluatorDetails).filter(EvaluatorDetails.userid == user.userid).first()
    db.close()
    return profile
