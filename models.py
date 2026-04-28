from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, Date, DateTime, Float
from datetime import date, datetime
import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, index=True)
    hashed_password = Column(String(128))
    role = Column(String(20))
    teacher_id = Column(Integer, ForeignKey("teacher.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=True)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    registration_number = Column(String(20), unique=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    class_id = Column(Integer, ForeignKey("school_class.id"), nullable=True)

class Teacher(Base):
    __tablename__ = "teacher"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    email = Column(String(120), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)

class SchoolClass(Base):
    __tablename__ = "school_class"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    grade_level = Column(String(20), nullable=True)
    teacher_id = Column(Integer, ForeignKey("teacher.id"), nullable=True)

class Subject(Base):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    code = Column(String(10), unique=True)

class Grade(Base):
    __tablename__ = "grade"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student.id"))
    subject_id = Column(Integer, ForeignKey("subject.id"))
    score = Column(Float)
    term = Column(String(20), nullable=True)
    date_recorded = Column(DateTime, default=datetime.utcnow)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student.id"))
    attendance_date = Column(Date, default=lambda: datetime.utcnow().date())
    status = Column(String(10))
