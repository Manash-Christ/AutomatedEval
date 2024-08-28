import os
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError

# Database setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Models
class LoginDetails(Base):
    __tablename__ = 'login_details'
    userid = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    student = relationship("StudentDetails", back_populates="login", uselist=False)
    evaluator = relationship("EvaluatorDetails", back_populates="login", uselist=False)

class StudentDetails(Base):
    __tablename__ = 'student_details'
    student_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    register_number = Column(String(50), unique=True, nullable=False)
    course_ids = Column(String(200), nullable=True)  # Comma-separated course IDs
    userid = Column(Integer, ForeignKey('login_details.userid'))
    login = relationship("LoginDetails", back_populates="student")
    reports = relationship("ReportDetails", back_populates="student")

class EvaluatorDetails(Base):
    __tablename__ = 'evaluator_details'
    evaluator_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    course_ids = Column(String(200), nullable=True)  # Comma-separated course IDs
    userid = Column(Integer, ForeignKey('login_details.userid'))
    login = relationship("LoginDetails", back_populates="evaluator")
    reports = relationship("ReportDetails", back_populates="evaluator")

class ReportDetails(Base):
    __tablename__ = 'report_details'
    report_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('student_details.student_id'))
    evaluator_id = Column(Integer, ForeignKey('evaluator_details.evaluator_id'), nullable=True)
    course_id = Column(String(50), nullable=False)
    transcript = Column(Text, nullable=False)  # New column for storing the transcript
    questions = Column(Text, nullable=True)
    score = Column(Integer, nullable=False, default=0)
    report = Column(Text, nullable=False, default="Evaluation Pending")
    student = relationship("StudentDetails", back_populates="reports")
    evaluator = relationship("EvaluatorDetails", back_populates="reports")



def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    create_tables()
