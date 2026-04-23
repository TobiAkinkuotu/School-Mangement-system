
from extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import date
from enum import Enum

from sqlalchemy.orm import backref

class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    registration_code = db.Column(db.String(50), unique=True, nullable=False) # New!
    address = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    website = db.Column(db.String(100), nullable=True)
    school_logo = db.Column(db.String(255), nullable=True)
    principal_name = db.Column(db.String(100), nullable=True)
    

    # Relationships
    users = db.relationship('User', backref='school', lazy=True, cascade="all, delete-orphan")
    students = db.relationship('Student', backref='school', lazy=True, cascade="all, delete-orphan")
    teachers = db.relationship('Teacher', backref='school', lazy=True, cascade="all, delete-orphan")
    classes = db.relationship('Class', backref='school', lazy=True, cascade="all, delete-orphan")
    subjects = db.relationship('Subject', backref='school', lazy=True, cascade="all, delete-orphan")
    fee_components = db.relationship('FeeComponent', backref='school', lazy=True, cascade="all, delete-orphan")
    assessment_types = db.relationship('AssessmentType', backref='school', lazy=True, cascade="all, delete-orphan")

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum('admin', 'teacher', 'student', name='user_roles'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', name='fk_users_school_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', name='fk_users_student_id'), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', name='fk_users_teacher_id'), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    grade_level = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', name='fk_students_school_id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', name='fk_students_class_id'), nullable=False)
    result_url = db.Column(db.String(255), nullable=True)
    teacher_remark = db.Column(db.String(255), nullable=True)
    principal_remark = db.Column(db.String(255), nullable=True)
    principal_signature = db.Column(db.String(255), nullable=True)

    # Other relationships
    grades = db.relationship('Grade', backref='student', lazy=True, cascade="all, delete-orphan")
    attendance = db.relationship('Attendance', backref='student', lazy=True, cascade="all, delete-orphan")
    student_assessments = db.relationship('AssessmentSubjectScore', backref='student', lazy=True, cascade="all, delete-orphan")
    # Relationships
    users = db.relationship('User', backref='student', lazy=True, cascade="all, delete-orphan")



class_teacher_association = db.Table(
    'class_teacher_association',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), primary_key=True),
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'), primary_key=True)
)


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    qualification = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', name='fk_teachers_school_id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', name='fk_teachers_class_id'), nullable=True)

    # Relationships
    teacher_subjects = db.relationship('TeacherSubject', backref='teacher', lazy=True, cascade="all, delete-orphan")
    assigned_classes = db.relationship('Class', secondary=class_teacher_association, backref=db.backref('assigned_teachers', lazy='dynamic'), lazy=True)
    users = db.relationship('User', backref='teacher', lazy=True, cascade="all, delete-orphan")
    

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('name', 'school_id', name='uq_subject_per_school'),
    )

    # Relationships
    teacher_subjects = db.relationship('TeacherSubject', backref='teacher_subject', lazy=True, cascade="all, delete-orphan")
    assessment_scores = db.relationship('AssessmentSubjectScore', backref='subject_ref', lazy=True, cascade="all, delete-orphan")
    class_subjects = db.relationship('ClassSubject', backref='class_subject', overlaps="class_subject,class_subjects,class_per_subjects", lazy=True, cascade="all, delete-orphan")

class ClassSubject(db.Model):
    __tablename__ = 'class_subjects'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    subject = db.relationship('Subject', backref='subjects_per_class')
    class_ = db.relationship('Class', backref='class_per_subjects')


assessment_class_association = db.Table(
    'assessment_class_association',
    db.Column('assessment_id', db.Integer, db.ForeignKey('assessments.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), primary_key=True)
)

# class Assessment(db.Model):
#     __tablename__ = 'assessments'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     assessment_type_id = db.Column(db.Integer, db.ForeignKey('assessment_types.id'), nullable=False)
#     class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
#     academic_session = db.Column(db.String(20), nullable=False)
#     term = db.Column(db.String(20), nullable=False)
#     school_id = db.Column(db.Integer, db.ForeignKey('schools.id', name='fk_assessment_type_school'), nullable=True)

#     __table_args__ = (
#         db.UniqueConstraint('name', 'school_id', name='uq_assessment_per_school'),
#     )

#     # Relationships
#     assessment_subject_scores = db.relationship('AssessmentSubjectScore',
#                                                 backref='assessment',
#                                                 lazy=True,
#                                                 cascade="all, delete-orphan")

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    assessment_type_id = db.Column(db.Integer, db.ForeignKey('assessment_types.id'), nullable=False)
    academic_session = db.Column(db.String(20), nullable=False)
    term = db.Column(db.String(20), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', name='fk_assessment_type_school'), nullable=True)

    # Many-to-Many: One assessment can apply to multiple classes
    classes = db.relationship('Class', secondary=assessment_class_association, backref='assessments')

    assessment_subject_scores = db.relationship(
        'AssessmentSubjectScore',
        backref='assessment',
        lazy=True,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint('name', 'school_id', name='uq_assessment_per_school'),
    )
    
class AssessmentType(db.Model):
    __tablename__ = 'assessment_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

class AssessmentSubjectScore(db.Model):
    __tablename__ = 'assessment_subject_scores'
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', name='fk_assessment_subject_scores_subject_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)

class AssessmentResult(db.Model):
    __tablename__ = 'assessment_results'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    grade = db.Column(db.String(5), nullable=False)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    days_present = db.Column(db.Integer, nullable=False, default=0)
    total_days_opened = db.Column(db.Integer, nullable=False, default=0)

class TeacherSubject(db.Model):
    __tablename__ = 'teacher_subject'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    # Relationship with Subject
    subject = db.relationship('Subject', backref='teachers_subjects')

    def __repr__(self):
        return f"<TeacherSubject teacher_id={self.teacher_id}, subject_id={self.subject_id}>"

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), nullable=False)
    class_level = db.Column(db.String(50), nullable=False)
    class_category = db.Column(db.String(50), nullable=False)
    school_id = db.Column(db.Integer,
                          db.ForeignKey('schools.id',
                                        name='fk_classes_school_id'),
                                        nullable=False)

    students = db.relationship('Student',
                               backref='class_',
                               lazy=True, cascade="all, delete-orphan")
    
    teachers = db.relationship('Teacher',
                               secondary=class_teacher_association,
                               backref='classes',
                               cascade="all, delete-orphan",
                               single_parent=True
                               )

    # Keep only one relationship with ClassFeeComponent
    class_fee_components = db.relationship('ClassFeeComponent', backref='class_', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('class_name', 'school_id', name='uq_class_per_school'),
    )

    @property
    def teacher_names(self):
        return ', '.join([f"{teacher.first_name} {teacher.last_name}" for teacher in self.teachers])



class StudentClassFeePayment(db.Model):
    __tablename__ = 'student_class_fee_payments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_fee_component_id = db.Column(db.Integer, db.ForeignKey('class_fee_components.id'), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    receipt_number = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    
    # Relationships
    student = db.relationship('Student', backref=db.backref('class_fee_payments', cascade="all, delete-orphan"))
    class_fee_component = db.relationship('ClassFeeComponent', backref=db.backref('student_fee_payments', cascade="all, delete-orphan"))



class FeeComponent(db.Model):
    __tablename__ = 'fee_components'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)
    term = db.Column(db.String(20), nullable=False)

    # Relationships
    class_fee_components = db.relationship('ClassFeeComponent', backref='fee_component', lazy=True, cascade="all, delete-orphan")

class ClassFeeComponent(db.Model):
    __tablename__ = 'class_fee_components'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey('fee_components.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)