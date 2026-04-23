
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from app import db
import os
from .forms import (
    TeacherForm, ClassForm, GradeForm, AttendanceForm, StudentForm, AssignTeachersForm,
    AssessmentForm, AssessmentResultForm, SubjectForm, SchoolForm, UserForm, AssessmentTypeForm, AssignSubjectToClassForm
)
from .models import (
    User, Student, Teacher, Class, Attendance, Assessment, AssessmentType,
    AssessmentSubjectScore, AssessmentResult, Subject, ClassSubject, TeacherSubject, School
)
from .models import Grade, StudentFee, FeeComponent, FeePayment, ClassFeeComponent
from flask_login import login_user, logout_user, login_required, current_user
from io import BytesIO
import pandas as pd
from docx import Document
from flask import send_from_directory
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
from flask import current_app
from config import Config
from sqlalchemy.orm import joinedload
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate
from io import BytesIO
from flask import send_file, jsonify
import json
from collections import defaultdict


# Create a Blueprint instance
main = Blueprint('main', __name__)
# Login route

@main.route('/')
def index():
    return render_template('index.html', is_authenticated=current_user.is_authenticated)




@main.route('/register_school', methods=['GET', 'POST'])
def register_school():
    form = SchoolForm()
    if form.validate_on_submit():
        school = School(
            name=form.name.data,
            address=form.address.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            website=form.website.data
        )
        db.session.add(school)
        db.session.commit()
        flash('School registered successfully!', 'success')
        return redirect(url_for('main.register_user'))
    return render_template('register_school.html', form=form)


@main.route('/register_user', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('main.register_user'))
        user = User(
            username=form.username.data,
            role=form.role.data,
            school_id=form.school_id.data
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('User registered successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while registering the user.', 'danger')
    return render_template('register_user.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('main.dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('main.teacher.dashboard'))
            else:
                return redirect(url_for('main.student.dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')




@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))

# Student Dashboard (Only accessible by Students)
@main.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role!= 'student':
        return redirect(url_for('main.index'))
    student_name = Student.query.get(current_user.id).name
    return render_template('student_dashboard.html', student_name=student_name)

# Teacher Dashboard (Only accessible by Teachers)
@main.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('main.index'))
    teacher_name = Teacher.query.get(current_user.id).name
    return render_template('teacher_dashboard.html', teacher_name=teacher_name)



# Dashboard (Only accessible by Admins)
@main.route('/dashboard')
@login_required
def dashboard():
    if not current_user.role== 'admin':
        return redirect(url_for('main.index'))
    school_name = School.query.get(current_user.school_id).name
    student_count = Student.query.count()
    teacher_count = Teacher.query.count()
    class_count = Class.query.count()
    return render_template('dashboard.html', school_name=school_name, student_count=student_count,
                           teacher_count=teacher_count, class_count=class_count)

# Report Generation Route
@main.route('/generate_report/<report_type>')
@login_required
def generate_report(report_type):
    # Sample data fetching for report
    data = {
        "Students": pd.read_sql(Student.query.statement, db.session.bind),
        "Teachers": pd.read_sql(Teacher.query.statement, db.session.bind),
        "Classes": pd.read_sql(Class.query.statement, db.session.bind),
        "Grades": pd.read_sql(Grade.query.statement, db.session.bind),
        "Attendance": pd.read_sql(Attendance.query.statement, db.session.bind),
    }
    
    if report_type == "excel":
        with BytesIO() as output:
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            for sheet, df in data.items():
                df.to_excel(writer, sheet_name=sheet, index=False)
            writer.save()
            output.seek(0)
            return send_file(output, attachment_filename="report.xlsx", as_attachment=True)
    
    elif report_type == "word":
        doc = Document()
        for section, df in data.items():
            doc.add_heading(section, level=1)
            table = doc.add_table(rows=1, cols=len(df.columns))
            hdr_cells = table.rows[0].cells
            for i, column in enumerate(df.columns):
                hdr_cells[i].text = column
            for _, row in df.iterrows():
                row_cells = table.add_row().cells
                for i, value in enumerate(row):
                    row_cells[i].text = str(value)
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        return send_file(output, attachment_filename="report.docx", as_attachment=True)




# Grades routes
@main.route('/grades')
def grades():
    grades = Grade.query.all()
    return render_template('grades.html', grades=grades)

# # Attendance routes
# @main.route('/attendance')
# def attendance():
#     attendance = Attendance.query.all()
#     return render_template('attendance.html', attendance=attendance)

# @main.route('/add_attendance', methods=['GET', 'POST'])
# @login_required
# def add_attendance():
#     form = AttendanceForm()
#     if form.validate_on_submit():
#         attendance = Attendance(
#             student_id=form.student_id.data,
#             class_id=form.class_id.data,
#             date=form.date.data,
#             status=form.status.data
#         )
#         db.session.add(attendance)
#         db.session.commit()
#         flash('Attendance record added successfully!')
#         return redirect(url_for('main.attendance'))
#     return render_template('add_attendance.html', form=form)

# @main.route('/attendance')
# def attendance():
#     attendance_records = Attendance.query.join(Student).add_columns(
#         Student.first_name.label("student_name"),
#         Attendance.days_present,
#         Attendance.total_days_opened
#     ).all()

#     return render_template(
#         'attendance.html',
#         attendance_records=attendance_records
    # )

@main.route('/attendance')
@login_required
def attendance():
    # Query attendance records with student names
    attendance_records = (
        db.session.query(
            Attendance.student_id,
            (Student.first_name + " " + Student.last_name).label("student_name"),
            Attendance.days_present,
            Attendance.total_days_opened
        )
        .join(Student, Attendance.student_id == Student.id)
        .all()
    )

    return render_template('attendance.html', attendance_records=attendance_records)


# @main.route('/add_attendance', methods=['GET', 'POST'])
# @login_required
# def add_attendance():
#     form = AttendanceForm()

#     # Fetch all students and join with the classes table
#     students = (
#         db.session.query(
#             Student.id,
#             Student.first_name,
#             Student.last_name,
#             Class.class_name  # Assuming 'class_name' is the correct column in the classes table
#         )
#         .join(Class, Student.class_id == Class.id)
#         .all()
#     )

#     if form.validate_on_submit():
#         student_id = form.student_id.data
#         status = form.status.data  # 'Present' or 'Absent'

#         # Fetch student's class dynamically
#         student = Student.query.get(student_id)
#         if not student:
#             flash("Invalid student selected.", "danger")
#             return redirect(url_for('main.add_attendance'))

#         class_id = student.class_id  # Auto-detect class from Student model

#         # Check if attendance record exists
#         attendance = Attendance.query.filter_by(student_id=student_id, class_id=class_id).first()

#         if attendance:
#             attendance.total_days_opened += 1  # Always increase school days
#             if status == "Present":
#                 attendance.days_present += 1
#         else:
#             # Create a new attendance record
#             attendance = Attendance(
#                 student_id=student_id,
#                 class_id=class_id,
#                 days_present=days_present,
#                 total_days_opened=total_days_opened
#             )
#             db.session.add(attendance)

#         db.session.commit()
#         flash('Attendance record updated successfully!', 'success')
#         return redirect(url_for('main.attendance'))

#     return render_template('add_attendance.html', form=form, students=students)



# @main.route('/add_attendance', methods=['GET', 'POST'])
# @login_required
# def add_attendance():
#     form = AttendanceForm()

#     # Fetch students and their classes
#     students = (
#         db.session.query(
#             Student.id,
#             Student.first_name,
#             Student.last_name,
#             Class.class_name
#         )
#         .join(Class, Student.class_id == Class.id)
#         .all()
#     )

#     # Populate student dropdown
#     form.student_id.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in students]

#     if form.validate_on_submit():
#         student_id = form.student_id.data
#         days_present = form.days_present.data
#         total_days_opened = form.total_days_opened.data

#         # Fetch the student's class automatically
#         student = Student.query.get(student_id)
#         if not student:
#             flash("Invalid student selected.", "danger")
#             return redirect(url_for('main.add_attendance'))

#         class_id = student.class_id  # Auto-detect class

#         # Check if an attendance record exists for this student
#         attendance = Attendance.query.filter_by(student_id=student_id, class_id=class_id).first()

#         if attendance:
#             # Update attendance
#             attendance.days_present = days_present
#             attendance.total_days_opened = total_days_opened
#         else:
#             # Create a new attendance record
#             attendance = Attendance(
#                 student_id=student_id,
#                 class_id=class_id,
#                 days_present=days_present,
#                 total_days_opened=total_days_opened
#             )
#             db.session.add(attendance)

#         db.session.commit()
#         flash('Attendance record updated successfully!', 'success')
#         return redirect(url_for('main.attendance'))

#     return render_template('add_attendance.html', form=form, students=students)


# @main.route('/add_attendance', methods=['GET', 'POST'])
# @login_required
# def add_attendance():
#     form = AttendanceForm()

#     # Fetch students and their associated class names
#     students = (
#         db.session.query(
#             Student.id,
#             Student.first_name,
#             Student.last_name,
#             Class.class_name
#         )
#         .join(Class, Student.class_id == Class.id)
#         .all()
#     )

#     # Ensure the dropdown has at least one default option
#     form.student_id.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in students] or [("", "No Students Available")]
    
#     if form.validate_on_submit():
#         student_id = form.student_id.data
#         class_id = form.class_id.data
#         days_present = form.days_present.data
#         total_days_opened = form.total_days_opened.data

#         # Fetch the student's class automatically
#         student = Student.query.get(student_id)
#         if not student:
#             flash("Invalid student selected.", "danger")
#             return redirect(url_for('main.add_attendance'))

#         class_id = student.class_id  # Auto-detect class

#         # Check if an attendance record exists for this student
#         attendance = Attendance.query.filter_by(student_id=student_id, class_id=class_id).first()

#         if attendance:
#             # Update attendance
#             attendance.days_present = days_present
#             attendance.total_days_opened = total_days_opened
#         else:
#             # Create a new attendance record
#             attendance = Attendance(
#                 student_id=student_id,
#                 class_id=class_id,
#                 days_present=days_present,
#                 total_days_opened=total_days_opened
#             )
#             db.session.add(attendance)

#         db.session.commit()
#         flash('Attendance record updated successfully!', 'success')
#         return redirect(url_for('main.attendance'))

#     return render_template('add_attendance.html', form=form, students=students)


# @main.route('/add_attendance', methods=['GET', 'POST'])
# @login_required
# def add_attendance():
#     form = AttendanceForm()

#     # Fetch students and their associated class names
#     students = (
#         db.session.query(
#             Student.id,
#             Student.first_name,
#             Student.last_name,
#             Class.class_name
#         )
#         .join(Class, Student.class_id == Class.id)
#         .all()
#     )

#     # Ensure the dropdown has at least one default option
#     if students:
#         form.student_id.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in students]
#     else:
#         form.student_id.choices = [("", "No Students Available")]

#     if form.validate_on_submit():
#         student_id = form.student_id.data
#         class_id = form.class_id.data
#         days_present = form.days_present.data
#         total_days_opened = form.total_days_opened.data

#         # Fetch the student's class automatically
#         student = Student.query.get(student_id)
#         if not student:
#             flash("Invalid student selected.", "danger")
#             return redirect(url_for('main.add_attendance'))

#         class_id = student.class_id  # Auto-detect class

#         # Check if an attendance record exists for this student
#         attendance = Attendance.query.filter_by(student_id=student_id, class_id=class_id).first()

#         if attendance:
#             # Update attendance
#             attendance.days_present = days_present
#             attendance.total_days_opened = total_days_opened
#         else:
#             # Create a new attendance record
#             attendance = Attendance(
#                 student_id=student_id,
#                 class_id=class_id,
#                 days_present=days_present,
#                 total_days_opened=total_days_opened
#             )
#             db.session.add(attendance)

#         db.session.commit()
#         flash('Attendance record updated successfully!', 'success')
#         return redirect(url_for('main.attendance'))

#     return render_template('add_attendance.html', form=form, students=students)

@main.route('/add_attendance', methods=['GET', 'POST'])
@login_required
def add_attendance():
    form = AttendanceForm()

    # Fetch students and their associated class names
    students = (
        db.session.query(
            Student.id,
            Student.first_name,
            Student.last_name,
            Class.class_name,
            Class.id.label('class_id')  # Fetch class_id for auto-detection
        )
        .join(Class, Student.class_id == Class.id)
        .all()
    )

    # Set choices for the student_id field
    if students:
        form.student_id.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in students]
    else:
        form.student_id.choices = [("", "No Students Available")]

    if form.validate_on_submit():
        student_id = form.student_id.data
        days_present = form.days_present.data
        total_days_opened = form.total_days_opened.data

        # Fetch the student's class automatically
        student = Student.query.get(student_id)
        if not student:
            flash("Invalid student selected.", "danger")
            return redirect(url_for('main.add_attendance'))

        class_id = student.class_id  # Auto-detect class

        # Check if an attendance record exists for this student
        attendance = Attendance.query.filter_by(student_id=student_id, class_id=class_id).first()

        if attendance:
            # Update attendance
            attendance.days_present = days_present
            attendance.total_days_opened = total_days_opened
        else:
            # Create a new attendance record
            attendance = Attendance(
                student_id=student_id,
                class_id=class_id,
                days_present=days_present,
                total_days_opened=total_days_opened
            )
            db.session.add(attendance)

        db.session.commit()
        flash('Attendance record updated successfully!', 'success')
        return redirect(url_for('main.attendance'))

    return render_template('add_attendance.html', form=form, students=students)

@main.route('/students', methods=['GET'])
def students():
    search_query = request.args.get('search', '').strip().lower()
    if search_query:
        students = Student.query.filter(
            (Student.first_name.ilike(f"%{search_query}%")) |
            (Student.last_name.ilike(f"%{search_query}%")) |
            (Class.class_name.ilike(f"%{search_query}%"))
        ).all()
    else:
        students = Student.query.all()
    return render_template('students.html', students=students)

@main.route('/add_student', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()

    # Populate the choices dynamically for class_id
    form.class_id.choices = [(cls.id, cls.class_name) for cls in Class.query.all()]
    if not form.class_id.choices:
        form.class_id.choices = [(-1, 'No classes available')]

    # Populate the choices dynamically for school_id
    form.school_id.choices = [(sch.id, sch.name) for sch in School.query.all()]
    if not form.school_id.choices:
        form.school_id.choices = [(-1, 'No schools available')]

    if form.validate_on_submit():
        # Handle the form submission
        try:
            if form.class_id.data == -1:
                flash("Please select a valid class.", "warning")
                return render_template('add_student.html', form=form)

            if form.school_id.data == -1:
                flash("Please select a valid school.", "warning")
                return render_template('add_student.html', form=form)

            student = Student(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                date_of_birth=form.date_of_birth.data,
                enrollment_date=form.enrollment_date.data,
                gender=form.gender.data,
                grade_level=form.grade_level.data,
                contact_email=form.contact_email.data,
                school_id=current_user.school_id,
                class_id=form.class_id.data
            )
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('main.students'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while adding the student: {str(e)}", "danger")

    return render_template('add_student.html', form=form)


@main.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

# Teacher route
# @main.route('/teachers')
# def teachers():
#     teachers = Teacher.query.all()
#     return render_template('teachers.html', teachers=teachers)

@main.route('/teachers', methods=['GET'])
def teachers():
    search_query = request.args.get('search', '').strip().lower()
    if search_query:
        teachers = Teacher.query.filter(
            (Teacher.first_name.ilike(f"%{search_query}%")) |
            (Teacher.last_name.ilike(f"%{search_query}%")) |
            (Teacher.qualification.ilike(f"%{search_query}%")) |
            (Teacher.teacher_subjects.any(Subject.name.ilike(f"%{search_query}%")))
        ).all()
    else:
        teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)


@main.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    form = TeacherForm()

    # Populate choices
    form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]

    if form.validate_on_submit():
        # Handle photo upload
        photo_filename = None
        if form.photo.data:
            photo_file = form.photo.data
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(Config.UPLOAD_FOLDER, photo_filename)
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            photo_file.save(photo_path)

        # Save the teacher's data
        teacher = Teacher(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            hire_date=form.hire_date.data,
            phone_number=form.phone_number.data,
            qualification=form.qualification.data,
            address=form.address.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            photo=photo_filename,
            school_id=form.school_id.data
        )
        db.session.add(teacher)
        db.session.commit()

        # Debugging: Check if the teacher is saved
        print(f"Teacher added: {teacher}")

        # Associate teacher with subjects
        try:
            for subject_id in form.subject.data:
                teacher_subject = TeacherSubject(teacher_id=teacher.id, subject_id=subject_id)
                db.session.add(teacher_subject)
                print(f"Added TeacherSubject: {teacher_subject}")
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error adding TeacherSubject: {e}")
            flash("Failed to add subjects for the teacher.")
            return redirect(url_for('main.teachers'))

        flash('Teacher added successfully with photo and details!')
        return redirect(url_for('main.teachers'))

    return render_template('add_teacher.html', form=form)


@main.route('/delete_teacher/<int:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)

    # Delete associated subjects
    TeacherSubject.query.filter_by(teacher_id=teacher.id).delete()

    # Delete the teacher record
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully!')
    return redirect(url_for('main.teachers'))


@main.route('/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    form = TeacherForm(obj=teacher)

    # Populate choices
    form.school_id.choices = [(school.id, school.name) for school in School.query.all()]
    form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]

    if form.validate_on_submit():
        teacher.first_name = form.first_name.data
        teacher.last_name = form.last_name.data
        teacher.email = form.email.data
        teacher.hire_date = form.hire_date.data
        teacher.phone_number = form.phone_number.data
        teacher.qualification = form.qualification.data
        teacher.address = form.address.data
        teacher.date_of_birth = form.date_of_birth.data
        teacher.gender = form.gender.data
        teacher.school_id = form.school_id.data

        # Update subjects
        TeacherSubject.query.filter_by(teacher_id=teacher.id).delete()
        for subject_id in form.subject.data:
            teacher_subject = TeacherSubject(teacher_id=teacher.id, subject_id=subject_id)
            db.session.add(teacher_subject)

        db.session.commit()
        flash('Teacher updated successfully!')
        return redirect(url_for('main.teachers'))

    return render_template('edit_teacher.html', form=form, teacher=teacher)




@main.route('/add_class', methods=['GET', 'POST'])
@login_required
def add_class():
    form = ClassForm()
    teachers = Teacher.query.filter_by(school_id=current_user.school_id).all()

    # Populate form teacher_ids choices dynamically
    form.teacher_ids.choices = [(teacher.id, f"{teacher.first_name} {teacher.last_name}") for teacher in teachers]

    if form.validate_on_submit():
        # Create a new class instance
        new_class = Class(
            class_name=form.class_name.data,
            class_level=form.class_level.data,
            class_category=form.class_category.data,
            school_id=current_user.school_id,
        )

        # Add selected teachers to the class
        selected_teacher_ids = form.teacher_ids.data
        selected_teachers = Teacher.query.filter(Teacher.id.in_(selected_teacher_ids)).all()
        new_class.teachers.extend(selected_teachers)

        try:
            db.session.add(new_class)
            db.session.commit()
            flash('Class added successfully!', 'success')
            return redirect(url_for('main.classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding class: {str(e)}', 'danger')

    return render_template('add_class.html', form=form)


@main.route('/classes')
@login_required
def classes():
    # Query classes, join teachers, and calculate student counts
    classes = db.session.query(
        Class,
        func.count(Student.id).label('student_count')
    ).outerjoin(Student, Student.class_id == Class.id) \
     .filter(Class.school_id == current_user.school_id) \
     .group_by(Class.id).options(joinedload('teachers')).all()

    # The result is a list of tuples: (Class object, student_count)
    return render_template('classes.html', classes=classes)


@main.route('/edit_class/<int:class_id>', methods=['GET', 'POST'])
def edit_class(class_id):
    # Fetch the class by ID
    class_to_edit = Class.query.get_or_404(class_id)

    if request.method == 'POST':
        # Update the class details
        class_to_edit.class_name = request.form['class_name']
        class_to_edit.class_category = request.form['class_category']
        
        try:
            db.session.commit()
            flash('Class updated successfully!', 'success')
            return redirect(url_for('main.classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating class: {str(e)}', 'danger')

    return render_template('edit_class.html', class_to_edit=class_to_edit)

@main.route('/delete_class/<int:class_id>', methods=['GET', 'POST'])
def delete_class(class_id):
    # Fetch the class by ID
    class_to_delete = Class.query.get_or_404(class_id)

    try:
        db.session.delete(class_to_delete)
        db.session.commit()
        flash('Class deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting class: {str(e)}', 'danger')

    return redirect(url_for('main.classes'))



@main.route('/add_grade', methods=['GET', 'POST'])
@login_required
def add_grade():
    form = GradeForm()
    if form.validate_on_submit():
        grade = Grade(
            student_id=form.student_id.data,
            class_id=form.class_id.data,
            score=form.score.data
        )
        db.session.add(grade)
        db.session.commit()
        flash('Grade added successfully!')
        return redirect(url_for('main.grades'))
    return render_template('add_grade.html', form=form)


# Route to display all subjects
@main.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.filter_by(school_id=current_user.school_id).all()
    return render_template('subjects.html', subjects=subjects)

# Route to add a subject
@main.route('/add_subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            school_id=current_user.school_id
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!')
        return redirect(url_for('main.subjects'))
    return render_template('add_subject.html', form=form)



# @main.route('/assign_subject_to_class', methods=['GET', 'POST'])
# @login_required
# def assign_subject_to_class():
#     form = AssignSubjectToClassForm()

#     # Populate the class dropdown
#     form.class_id.choices = [
#         (c.id, c.class_name)  # (value, label)
#         for c in Class.query.filter_by(school_id=current_user.school_id).all()
#     ]

#     # Populate the subject dropdown
#     form.subject_id.choices = [
#         (s.id, s.name)  # (value, label)
#         for s in Subject.query.filter_by(school_id=current_user.school_id).all()
#     ]

#     if form.validate_on_submit():
#         # Create a new ClassSubject record
#         class_subject = ClassSubject(
#             class_id=form.class_id.data,
#             subject_id=form.subject_id.data
#         )
#         db.session.add(class_subject)
#         db.session.commit()
#         flash('Subject assigned to class successfully!', 'success')
#         return redirect(url_for('main.subjects'))

#     return render_template('assign_subject_to_class.html', form=form)

@main.route('/assign_subject_to_class', methods=['GET', 'POST'])
@login_required
def assign_subject_to_class():
    form = AssignSubjectToClassForm()

    # Populate the class dropdown
    form.class_id.choices = [
        (c.id, c.class_name)  # (value, label)
        for c in Class.query.filter_by(school_id=current_user.school_id).all()
    ]

    # Fetch all subjects for the current school
    subjects = Subject.query.filter_by(school_id=current_user.school_id).all()

    if form.validate_on_submit():
        class_id = form.class_id.data
        selected_subjects = request.form.getlist('subjects')  # Get list of selected subject IDs

        # Assign each selected subject to the class
        for subject_id in selected_subjects:
            class_subject = ClassSubject(
                class_id=class_id,
                subject_id=int(subject_id)
            )
            db.session.add(class_subject)
        
        db.session.commit()
        flash('Subjects assigned to class successfully!', 'success')
        return redirect(url_for('main.subjects'))

    return render_template('assign_subject_to_class.html', form=form, subjects=subjects)

from sqlalchemy.orm import aliased


@main.route('/class_subjects')
def view_class_subjects():
    # Define table aliases to prevent ambiguity
    subject_alias = aliased(Subject)

    # Query data and join with classes & subjects
    class_subjects = db.session.query(
        Class.class_name.label("class_name"),
        subject_alias.name.label("subject_name")
    ).join(ClassSubject, Class.id == ClassSubject.class_id) \
     .join(subject_alias, subject_alias.id == ClassSubject.subject_id) \
     .all()

    # Group subjects by class name
    grouped_class_subjects = {}
    for cs in class_subjects:
        grouped_class_subjects.setdefault(cs.class_name, []).append(cs.subject_name)

    return render_template("view_class_subjects.html", grouped_class_subjects=grouped_class_subjects)

@main.route('/edit_class_subject/<class_name>', methods=['GET', 'POST'])
def edit_class_subject(class_name):
    # Fetch subjects linked to the class
    class_obj = Class.query.filter_by(class_name=class_name).first()
    if not class_obj:
        flash("Class not found", "danger")
        return redirect(url_for('main.view_class_subjects'))

    subjects = Subject.query.all()
    class_subjects = ClassSubject.query.filter_by(class_id=class_obj.id).all()
    selected_subjects = [cs.subject_id for cs in class_subjects]

    if request.method == 'POST':
        new_subjects = request.form.getlist('subjects')
        
        # Remove existing subjects not in new selection
        for cs in class_subjects:
            if str(cs.subject_id) not in new_subjects:
                db.session.delete(cs)
        
        # Add new selections
        for subject_id in new_subjects:
            if int(subject_id) not in selected_subjects:
                new_entry = ClassSubject(class_id=class_obj.id, subject_id=int(subject_id))
                db.session.add(new_entry)

        db.session.commit()
        flash("Subjects updated successfully!", "success")
        return redirect(url_for('main.view_class_subjects'))

    return render_template("edit_class_subject.html", class_obj=class_obj, subjects=subjects, selected_subjects=selected_subjects)

@main.route('/delete_class_subject/<class_name>', methods=['GET', 'POST'])
def delete_class_subject(class_name):
    class_obj = Class.query.filter_by(class_name=class_name).first()
    if not class_obj:
        flash("Class not found", "danger")
        return redirect(url_for('main.view_class_subjects'))

    ClassSubject.query.filter_by(class_id=class_obj.id).delete()
    db.session.commit()
    
    flash("Class subjects deleted successfully!", "success")
    return redirect(url_for('main.view_class_subjects'))


# Route to add attendance


# Route to generate a report of all assessment scores
@main.route('/generate_assessment_report/<int:assessment_id>')
@login_required
def generate_assessment_report(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    scores = AssessmentResult.query.filter_by(assessment_id=assessment_id).all()
    data = pd.DataFrame([{
        "Student": f"{score.student.first_name} {score.student.last_name}",
        "Subject": score.subject.name,
        "Marks Obtained": score.marks_obtained
    } for score in scores])
    
    with BytesIO() as output:
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        data.to_excel(writer, index=False, sheet_name='Assessment Scores')
        writer.save()
        output.seek(0)
        return send_file(output, attachment_filename=f"Assessment_{assessment.name}_Report.xlsx", as_attachment=True)


# Route to list all assessment types
@main.route('/assessment_types')
@login_required
def assessment_types():
    if not current_user.role == 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))
    assessment_types = AssessmentType.query.all()
    return render_template('assessment_types.html', assessment_types=assessment_types)

# Route to add an assessment type
@main.route('/add_assessment_type', methods=['GET', 'POST'])
@login_required
def add_assessment_type():
    form = AssessmentTypeForm()
    if not current_user.role == 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Assessment type name is required.', 'danger')
        else:
            new_type = AssessmentType(name=name)
            db.session.add(new_type)
            db.session.commit()
            flash('Assessment type added successfully!', 'success')
            return redirect(url_for('main.assessment_types'))
    return render_template('add_assessment_type.html', form=form)




@main.route('/assessments')
@login_required
def assessments():
    all_assessments = Assessment.query.join(Class,
                                            Assessment.class_id == Class.id).join(AssessmentType,
                                            Assessment.assessment_type_id == AssessmentType.id).add_columns(
        Assessment.id, 
        Assessment.name, 
        Assessment.date, 
        Assessment.academic_session,
        Assessment.term,
        Class.class_name.label('class_name'), 
        AssessmentType.name.label('assessment_type_name') 
    ).all()
    return render_template('assessments.html', assessments=all_assessments)




@main.route('/add_assessment', methods=['GET', 'POST'])
@login_required
def add_assessment():
    form = AssessmentForm()
    form.assessment_type.choices = [(atype.id, atype.name) for atype in AssessmentType.query.all()]
    form.class_id.choices = [(cls.id, cls.class_name) for cls in Class.query.all()]

    if form.validate_on_submit():
        new_assessment = Assessment(
            name=form.name.data,
            date=form.date.data,
            assessment_type_id=form.assessment_type.data,
            class_id=form.class_id.data,
            academic_session=form.academic_session.data,
            term=form.term.data
        )
        db.session.add(new_assessment)
        db.session.commit()
        flash('Assessment added successfully!', 'success')
        return redirect(url_for('main.assessments'))

    return render_template('add_assessment.html', form=form)


@main.route('/edit_assessment/<int:assessment_id>', methods=['GET', 'POST'])
@login_required
def edit_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    form = AssessmentForm(obj=assessment)
    form.assessment_type.choices = [(atype.id, atype.name) for atype in AssessmentType.query.all()]
    form.class_id.choices = [(cls.id, cls.class_name) for cls in Class.query.all()]

    if form.validate_on_submit():
        assessment.name = form.name.data
        assessment.date = form.date.data
        assessment.assessment_type_id = form.assessment_type.data
        assessment.class_id = form.class_id.data
        assessment.academic_session = form.academic_session.data
        assessment.term = form.term.data

        db.session.commit()
        flash('Assessment updated successfully!', 'success')
        return redirect(url_for('main.assessments'))

    return render_template('edit_assessment.html', form=form, assessment=assessment)

@main.route('/delete_assessment/<int:assessment_id>', methods=['POST'])
@login_required
def delete_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    db.session.delete(assessment)
    db.session.commit()
    flash('Assessment deleted successfully!', 'success')
    return redirect(url_for('main.assessments'))


@main.route('/assessment_subject_scores')
def assessment_subject_scores():
    # Get filter parameters from the request
    assessment_id = request.args.get('assessment')
    academic_session = request.args.get('academic_session')
    subject_id = request.args.get('subject')
    student_id = request.args.get('student')
    

    # Base query
    query = db.session.query(
        AssessmentSubjectScore,
        Assessment.name.label('assessment_name'),
        Subject.name.label('subject_name'),
        Student.first_name,
        Student.last_name,
        AssessmentSubjectScore.total_marks,
        Assessment.academic_session
    ).join(
        Assessment, AssessmentSubjectScore.assessment_id == Assessment.id
    ).join(
        Subject, AssessmentSubjectScore.subject_id == Subject.id
    ).join(
        Student, AssessmentSubjectScore.student_id == Student.id
    )

    # Apply filters
    if assessment_id:
        query = query.filter(AssessmentSubjectScore.assessment_id == assessment_id)
    if academic_session:
        query = query.filter(Assessment.academic_session == academic_session)
    if subject_id:
        query = query.filter(AssessmentSubjectScore.subject_id == subject_id)
    if student_id:
        query = query.filter(AssessmentSubjectScore.student_id == student_id)

    # Fetch filtered results
    scores = query.all()

    # Fetch filter options
    assessments = Assessment.query.all()
    academic_sessions = db.session.query(Assessment.academic_session).distinct().all()
    subjects = Subject.query.all()
    students = Student.query.all()

    return render_template(
        'assessment_subject_scores.html',
        scores=scores,
        assessments=assessments,
        academic_sessions=[session[0] for session in academic_sessions],
        subjects=subjects,
        students=students
    )

@main.route('/add_assessment_score', methods=['GET', 'POST'])
def add_assessment_score():
    if request.method == 'POST':
        try:
            # Fetch the data from the form
            academic_session = request.form.get('academic_session')
            assessment_id = int(request.form.get('assessment_id'))
            student_id = int(request.form.get('student_id'))
            class_id = int(request.form.get('class_id'))

            # Get the list of selected subjects (only subjects with checked checkboxes)
            selected_subject_ids = request.form.getlist('selected_subjects')

            # Loop through the selected subjects and collect scores
            for subject_id in selected_subject_ids:
                score_key = f"score_{subject_id}"
                score_value = request.form.get(score_key)

                if score_value:
                    try:
                        total_marks = int(score_value)
                        # Add score entry to the database
                        new_score = AssessmentSubjectScore(
                            assessment_id=assessment_id,
                            subject_id=int(subject_id),
                            student_id=student_id,
                            total_marks=total_marks
                        )
                        db.session.add(new_score)
                    except ValueError:
                        continue

            db.session.commit()
            flash("Assessment scores added successfully!", "success")
            return redirect(url_for('main.assessment_subject_scores'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding assessment scores: {e}", "danger")
            return redirect(url_for('main.add_assessment_score'))

    # Fetch academic sessions, assessments, subjects, and students
    academic_sessions = list(set(assessment.academic_session for assessment in Assessment.query.all()))
    assessments = Assessment.query.all()
    subjects = Subject.query.all()
    students = Student.query.all()
    classes = Class.query.all()

    return render_template(
        'add_assessment_subject_score.html',
        academic_sessions=academic_sessions,
        assessments=assessments,
        subjects=subjects,
        students=students,
        classes=classes
    )


@main.route('/assessment_subject_scores/edit/<int:id>', methods=['GET', 'POST'])
def edit_assessment_subject_score(id):
    # Fetch the record to be edited
    score = AssessmentSubjectScore.query.get_or_404(id)

    # If the form is submitted (POST request), update the score
    if request.method == 'POST':
        # Update the score's fields from the form data
        score.subject_id = request.form['subject_id']
        score.total_marks = request.form['total_marks']

        try:
            # Commit the changes to the database
            db.session.commit()
            flash('Assessment Subject Score updated successfully!', 'success')
            return redirect(url_for('main.assessment_subject_scores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating score: {str(e)}', 'danger')

    # Fetch data for dropdowns
    subjects = Subject.query.all()
    assessments = Assessment.query.all()

    return render_template(
        'edit_assessment_subject_score.html',
        score=score,
        subjects=subjects,
        assessments=assessments
    )


@main.route('/assessment_subject_scores/delete/<int:id>', methods=['POST'])
def delete_assessment_subject_score(id):
    # Fetch the record to be deleted
    score = AssessmentSubjectScore.query.get_or_404(id)

    try:
        # Delete the score from the database
        db.session.delete(score)
        db.session.commit()
        flash('Assessment Subject Score deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting score: {str(e)}', 'danger')

    return redirect(url_for('main.assessment_subject_scores'))


# Route to view all subjects for a class
@main.route('/class_subjects/<int:class_id>')
@login_required
def class_subjects(class_id):
    class_instance = Class.query.get_or_404(class_id)
    subjects = ClassSubject.query.filter_by(class_id=class_id).all()
    return render_template('class_subjects.html', class_instance=class_instance, subjects=subjects)

# Route to add a subject to a class
@main.route('/add_class_subject/<int:class_id>', methods=['GET', 'POST'])
@login_required
def add_class_subject(class_id):
    if not current_user.role == 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))
    class_instance = Class.query.get_or_404(class_id)
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        if not subject_id:
            flash('Subject is required.', 'danger')
        else:
            new_class_subject = ClassSubject(
                class_id=class_id,
                subject_id=subject_id
            )
            db.session.add(new_class_subject)
            db.session.commit()
            flash('Subject added to class successfully!', 'success')
            return redirect(url_for('main.class_subjects', class_id=class_id))
    subjects = Subject.query.filter_by(school_id=current_user.school_id).all()
    return render_template('add_class_subject.html', class_instance=class_instance, subjects=subjects)




# def generate_result_sheet(student):
#     buffer = BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=A4)

#     # Title Section
#     pdf.setFont("Helvetica-Bold", 14)
#     pdf.drawCentredString(300, 800, "UNIVERSITY OF  CONSULTANCY SCHOOLS")
#     pdf.setFont("Helvetica", 12)
#     pdf.drawCentredString(300, 780, "University of Benin, Ekehuan Road Campus, P.M.B. 1154, Benin City")
#     pdf.drawCentredString(300, 760, "INDIVIDUAL STUDENT'S ASSESSMENT SHEET")
#     pdf.drawCentredString(300, 740, "JUNIOR SECONDARY SCHOOL")

#     # Student Details
#     pdf.setFont("Helvetica", 10)BENIN
#     pdf.drawString(50, 710, f"RESULT ID: {student['result_id']}")
#     pdf.drawString(250, 710, f"SEX: {student['sex']}")
#     pdf.drawString(400, 710, f"TERM: {student['term']}")
#     pdf.drawString(50, 690, f"NAME OF STUDENT: {student['name']}")
#     pdf.drawString(250, 690, f"SESSION: {student['session']}")
#     pdf.drawString(400, 690, f"NO. OF TIMES PRESENT: {student['times_present']}")
#     pdf.drawString(50, 670, f"CLASS: {student['class_name']}")
#     pdf.drawString(250, 670, f"NO. OF TIMES SCHOOL OPENED: {student['times_opened']}")

#     # Subject Table Headers
#     pdf.setFont("Helvetica-Bold", 10)
#     y_start = 650
#     headers = ["SUBJECT", "CONTINUOUS ASSESSMENT", "TERM SUMMARY"]
#     pdf.drawString(50, y_start, headers[0])
#     pdf.drawString(200, y_start, headers[1])
#     pdf.drawString(450, y_start, headers[2])

#     # Table Data
#     y = y_start - 20
#     pdf.setFont("Helvetica", 9)

#     for subject in student['subjects']:
#         pdf.drawString(50, y, subject['name'])
#         pdf.drawString(200, y, f"{subject['ca_scores']}")
#         pdf.drawString(450, y, f"{subject['term_summary']}")
#         y -= 20
#         if y < 100:
#             pdf.showPage()
#             y = 750

#     # Footer Section
#     pdf.setFont("Helvetica-Bold", 10)
#     pdf.drawString(50, 80, f"Term Grand Total: {student['grand_total']}")
#     pdf.drawString(250, 80, f"Overall Grade: {student['overall_grade']}")
#     pdf.drawString(400, 80, f"Next Term Begins: {student['next_term']}")

#     # Save the PDF
#     pdf.save()
#     buffer.seek(0)

#     return buffer



# @main.route('/download_result/<int:student_id>')
# def download_result(student_id):
#     # Replace this with actual student data from your database
#     student = {
#         "result_id": "UCS2024/JSS1A/1564460",
#         "name": "Maxwell Oduwa Amadasun",
#         "sex": "Male",
#         "term": "1st Term",
#         "session": "2024/2025",
#         "times_present": 112,
#         "times_opened": 112,
#         "class_name": "JSS 1A",
#         "subjects": [
#             {"name": "English Language", "ca_scores": "10, 20, 15", "term_summary": "GOOD"},
#             {"name": "Mathematics", "ca_scores": "15, 18, 20", "term_summary": "EXCELLENT"},
#             {"name": "Computer Science", "ca_scores": "5, 15, 10", "term_summary": "PASS"},
#             # Add more subjects here...
#         ],
#         "grand_total": 929,
#         "overall_grade": "C",
#         "next_term": "2025-01-06"
#     }

#     pdf_buffer = generate_result_sheet(student)
#     return send_file(
#         pdf_buffer,
#         as_attachment=True,
#         download_name=f"{student['name']}_result.pdf",
#         mimetype='application/pdf'
#     )

# def generate_result_sheet(student):
#     buffer = BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=A4)

#     # Title Section
#     pdf.setFont("Helvetica-Bold", 14)
#     pdf.drawCentredString(300, 800, "UNIVERSITY OF BENIN CONSULTANCY SCHOOLS")
#     pdf.setFont("Helvetica", 12)
#     pdf.drawCentredString(300, 780, "University of Benin, Ekehuan Road Campus, P.M.B. 1154, Benin City")
#     pdf.drawCentredString(300, 760, "INDIVIDUAL STUDENT'S ASSESSMENT SHEET")
#     pdf.drawCentredString(300, 740, "JUNIOR SECONDARY SCHOOL")

#     # Student Details
#     pdf.setFont("Helvetica", 10)
#     pdf.drawString(50, 710, f"RESULT ID: {student['result_id']}")
#     pdf.drawString(250, 710, f"SEX: {student['sex']}")
#     pdf.drawString(400, 710, f"TERM: {student['term']}")
#     pdf.drawString(50, 690, f"NAME OF STUDENT: {student['name']}")
#     pdf.drawString(250, 690, f"SESSION: {student['session']}")
#     pdf.drawString(400, 690, f"NO. OF TIMES PRESENT: {student['times_present']}")
#     pdf.drawString(50, 670, f"CLASS: {student['class_name']}")
#     pdf.drawString(250, 670, f"NO. OF TIMES SCHOOL OPENED: {student['times_opened']}")

#     # Subject Table Headers
#     pdf.setFont("Helvetica-Bold", 10)
#     y_start = 650
#     headers = ["SUBJECT", "CONTINUOUS ASSESSMENT", "TERM SUMMARY"]
#     pdf.drawString(50, y_start, headers[0])
#     pdf.drawString(200, y_start, headers[1])
#     pdf.drawString(450, y_start, headers[2])

#     # Table Data
#     y = y_start - 20
#     pdf.setFont("Helvetica", 9)

#     for subject in student['subjects']:
#         pdf.drawString(50, y, subject['name'])
#         pdf.drawString(200, y, f"{subject['ca_scores']}")
#         pdf.drawString(450, y, f"{subject['term_summary']}")
#         y -= 20
#         if y < 100:
#             pdf.showPage()
#             y = 750

#     # Footer Section
#     pdf.setFont("Helvetica-Bold", 10)
#     pdf.drawString(50, 80, f"Term Grand Total: {student['grand_total']}")
#     pdf.drawString(250, 80, f"Overall Grade: {student['overall_grade']}")
#     pdf.drawString(400, 80, f"Next Term Begins: {student['next_term']}")

#     # Save the PDF
#     pdf.save()
#     buffer.seek(0)

#     return buffer

def generate_result_sheet(student):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    # Title Section
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(300, 800, f"{student['school_name']}")  # Dynamic school name
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(300, 780, f"{student['school_address']}")  # Dynamic school address
    pdf.drawCentredString(300, 760, "INDIVIDUAL STUDENT'S ASSESSMENT SHEET")
    pdf.drawCentredString(300, 740, "JUNIOR SECONDARY SCHOOL")

    # Student Details
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 710, f"RESULT ID: {student['result_id']}")
    pdf.drawString(250, 710, f"SEX: {student['sex']}")
    pdf.drawString(400, 710, f"TERM: {student['term']}")
    pdf.drawString(50, 690, f"NAME OF STUDENT: {student['name']}")
    pdf.drawString(250, 690, f"SESSION: {student['session']}")
    pdf.drawString(400, 690, f"NO. OF TIMES PRESENT: {student['times_present']}")
    pdf.drawString(50, 670, f"CLASS: {student['class_name']}")
    pdf.drawString(250, 670, f"NO. OF TIMES SCHOOL OPENED: {student['times_opened']}")

    # Subject Table Headers
    pdf.setFont("Helvetica-Bold", 10)
    y_start = 650
    headers = ["SUBJECT", "CONTINUOUS ASSESSMENT", "TERM SUMMARY"]
    pdf.drawString(50, y_start, headers[0])
    pdf.drawString(200, y_start, headers[1])
    pdf.drawString(450, y_start, headers[2])

    # Table Data
    y = y_start - 20
    pdf.setFont("Helvetica", 9)

    for subject in student['subjects']:
        pdf.drawString(50, y, subject['name'])
        pdf.drawString(200, y, f"{subject['ca_scores']}")
        pdf.drawString(450, y, f"{subject['term_summary']}")
        y -= 20
        if y < 100:
            pdf.showPage()
            y = 750

    # Footer Section
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, 80, f"Term Grand Total: {student['grand_total']}")
    pdf.drawString(250, 80, f"Overall Grade: {student['overall_grade']}")
    pdf.drawString(400, 80, f"Next Term Begins: {student['next_term']}")

    # Save the PDF
    pdf.save()
    buffer.seek(0)

    return buffer

# @main.route('/download_result_sheet/<int:student_id>')
# def download_result_sheet(student_id):
#     try:
#         # Fetch student personal details
#         student_record = Student.query.filter_by(id=student_id).first()
#         if not student_record:
#             return jsonify({"error": "Student not found"}), 404

#         # Fetch student academic records
#         subjects = AssessmentSubjectScore.query.filter_by(student_id=student_id).all()
#         assessments = Assessment.query.filter_by(class_id=student_record.class_id).all()

#         # Calculate attendance
#         attendance_records = Attendance.query.filter_by(student_id=student_id).all()
#         times_present = sum(1 for record in attendance_records if record.status == 'present')
#         times_opened = len(attendance_records)

#         # Prepare student data for the result sheet
#         student = {
#             "result_id": student_record.id,
#             "name": f"{student_record.first_name} {student_record.last_name}",
#             "sex": student_record.gender,
#             "term": assessments[0].term if assessments else "N/A",
#             "session": assessments[0].academic_session if assessments else "N/A",
#             "times_present": times_present,
#             "times_opened": times_opened,
#             "class_name": student_record.class_.class_name,
#             "subjects": [
#                 {
#                     "name": subject.subject.name,
#                     "ca_scores": subject.total_marks,
#                     "term_summary": subject.total_marks  # Assuming term summary is the total marks
#                 }
#                 for subject in subjects
#             ],
#             "grand_total": sum(subject.total_marks for subject in subjects),
#             "overall_grade": "A",  # Placeholder, you can calculate this based on your grading system
#             "next_term": "2023-09-01"  # Placeholder, you can fetch this from your database
#         }

#         # Generate the PDF
#         pdf_buffer = generate_result_sheet(student)
#         return send_file(
#             pdf_buffer,
#             as_attachment=True,
#             download_name=f"{student['name']}_result.pdf",
#             mimetype='application/pdf'
#         )
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@main.route('/download_result_sheet/<int:student_id>')
def download_result_sheet(student_id):
    try:
        # Fetch student personal details
        student_record = Student.query.filter_by(id=student_id).first()
        if not student_record:
            return jsonify({"error": "Student not found"}), 404

        # Fetch school details using the student's school_id
        school_record = School.query.filter_by(id=student_record.school_id).first()
        if not school_record:
            return jsonify({"error": "School not found"}), 404

        # Fetch student academic records
        subjects = AssessmentSubjectScore.query.filter_by(student_id=student_id).all()
        assessments = Assessment.query.filter_by(class_id=student_record.class_id).all()

        # Calculate attendance
        attendance_records = Attendance.query.filter_by(student_id=student_id).all()
        times_present = sum(1 for record in attendance_records if record.days_present == 'present')
        times_opened = len(attendance_records)

        # Prepare student data for the result sheet
        student = {
            "result_id": student_record.id,
            "name": f"{student_record.first_name} {student_record.last_name}",
            "sex": student_record.gender,
            "term": assessments[0].term if assessments else "N/A",
            "session": assessments[0].academic_session if assessments else "N/A",
            "times_present": times_present,
            "times_opened": times_opened,
            "class_name": student_record.class_.class_name,
            "subjects": [
                {
                    "name": subject.subject.name,
                    "ca_scores": subject.total_marks,
                    "term_summary": subject.total_marks  # Assuming term summary is the total marks
                }
                for subject in subjects
            ],
            "grand_total": sum(subject.total_marks for subject in subjects),
            "overall_grade": "A",  # Placeholder, you can calculate this based on your grading system
            "next_term": "2023-09-01",  # Placeholder, you can fetch this from your database
            "school_name": school_record.name,  # Add school name
            "school_address": school_record.address  # Add school address
        }

        # Generate the PDF
        pdf_buffer = generate_result_sheet(student)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"{student['name']}_result.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/download_result/<int:student_id>')
def download_result(student_id):
    try:
        # Fetch student personal details
        student_record = Student.query.filter_by(id=student_id).first()
        if not student_record:
            return jsonify({"error": "Student not found"}), 404

        # Fetch student academic records
        subjects = AssessmentSubjectScore.query.filter_by(student_id=student_id).all()
        if not subjects:
            return jsonify({"error": "No subjects found for this student"}), 404

        # Fetch assessment details (assuming one assessment for the student/session)
        assessment = Assessment.query.first()
        if not assessment:
            return jsonify({"error": "No assessment found for this student"}), 404

        students_assessment = Assessment.query.filter_by(id=assessment.id).first()
        if not students_assessment:
            return jsonify({"error": "No assessment found for this student"}), 404
        else:
            # Your code here
            # ...
            pass

        classes = Class.query.first()

        class_records = Class.query.filter_by(id=classes.id).first()

        student = {
            "result_id": student_record.id,  # Corrected here
            "name": f"{student_record.first_name} {student_record.last_name}",
            "sex": student_record.gender,
            "term": students_assessment.term,
            "session": students_assessment.academic_session,  # Corrected source of academic_session
            "class_name": class_records.class_name,
            "subjects": [
                {
                    "name": subject.subject_id,
                    "ca_scores": ", ".join(map(str, [assessment.ca1, assessment.ca2, assessment.ca3])),
                    "term_summary": subject.term_summary
                }
                for subject in subjects
            ],
            "grand_total": sum(subject.total_score for subject in subjects),
            "overall_grade": student_record.overall_grade,
            "next_term": student_record.next_term
        }

        # Generate the PDF
        pdf_buffer = generate_result_sheet(student)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"{student['name']}_result.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@main.route('/assign_teachers', methods=['GET', 'POST'])
@login_required
def assign_teachers():
    # Create the form
    form = AssignTeachersForm()

    # Get the classes and teachers for the current school
    classes = Class.query.filter_by(school_id=current_user.school_id).all()
    teachers = Teacher.query.filter_by(school_id=current_user.school_id).all()

    # Populate the form choices dynamically
    form.class_id.choices = [(cls.id, cls.class_name) for cls in classes]
    form.teacher_ids.choices = [(teacher.id, f"{teacher.first_name} {teacher.last_name}") for teacher in teachers]

    if form.validate_on_submit():
        class_id = form.class_id.data
        selected_teacher_ids = form.teacher_ids.data

        # Fetch the class and selected teachers
        selected_class = Class.query.get(class_id)
        selected_teachers = Teacher.query.filter(Teacher.id.in_(selected_teacher_ids)).all()

        # Clear existing teachers to avoid duplicates
        selected_class.teachers = []

        # Add new teachers to the class
        selected_class.teachers.extend(selected_teachers)

        try:
            db.session.commit()
            flash('Teachers assigned successfully!', 'success')
            return redirect(url_for('main.classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error assigning teachers: {str(e)}', 'danger')


    return render_template('assign_teachers.html', form=form)


# School Fees Management

fee_components = {
    "Tuition Fee": "Fee for academic instruction and resources.",
    "Registration Fee": "Fee for enrollment in the academic year.",
    "PTA Levy": "Parent-Teacher Association levy for school activities.",
    "Sports Fee": "Fee for participation in sports and physical activities.",
    "Uniform Fee": "Cost of school uniforms.",
    "Textbooks/Workbooks": "Cost of textbooks and workbooks for the academic year.",
    "Examination Fee": "Fee for conducting examinations and assessments.",
    "ICT Fee": "Fee for access to ICT facilities and resources.",
    "Medical Fee": "Fee for access to medical facilities and services.",
    "Miscellaneous": "Additional fees for other school-related activities."
}

# Save as JSON file
with open("fee_components.json", "w") as file:
    json.dump(fee_components, file, indent=4)


@main.route('/fee_components')
def fee_components():
    # Fetch all fee components from the database
    components = FeeComponent.query.all()
    return render_template('fee_components.html', components=components)

#
# Load fee components from the JSON file
with open("fee_components.json", "r") as file:
    fee_components_from_json = json.load(file)


@main.route('/add_fee_component', methods=['GET', 'POST'])
def add_fee_component():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        description = request.form['description']
        school_id = request.form['school_id']

        # Create a new FeeComponent
        component = FeeComponent(
            name=name,
            description=description,
            school_id=school_id
        )
        db.session.add(component)
        db.session.commit()
        flash('Fee component added successfully!', 'success')
        return redirect(url_for('main.fee_components'))

    # Fetch all schools for the dropdown
    schools = School.query.all()
    return render_template('add_fee_component.html', schools=schools)

# @main.route('/add_fee_component_to_class', methods=['GET', 'POST'])
# def add_fee_component_to_class():
#     if request.method == 'POST':
#         # Get the selected class ID
#         class_id = request.form['class_id']

#         # Get the list of selected component IDs
#         selected_components = request.form.getlist('selected_components')

#         # Loop through all selected fee components
#         for component_id in selected_components:
#             # Get the amount for the selected component
#             amount_field = f"amount_{component_id}"
#             if amount_field in request.form and request.form[amount_field]:
#                 amount = float(request.form[amount_field])

#                 # Add the fee component to the database
#                 class_fee_component = ClassFeeComponent(
#                     class_id=class_id,
#                     component_id=int(component_id),
#                     amount=amount
#                 )
#                 db.session.add(class_fee_component)

#         db.session.commit()
#         flash('Selected fee components added to class successfully!', 'success')
#         return redirect(url_for('main.view_class_fees', class_id=class_id))
    
#     # Fetch all classes and fee components for the form
#     classes = Class.query.all()
#     components = FeeComponent.query.all()
#     return render_template('add_fee_component_to_class.html', classes=classes, components=components)


@main.route('/add_fee_component_to_class', methods=['GET', 'POST'])
def add_fee_component_to_class():
    if request.method == 'POST':
        # Get the list of selected class IDs
        selected_classes = request.form.getlist('selected_classes')

        # Get the list of selected component IDs
        selected_components = request.form.getlist('selected_components')

        # Loop through all selected classes and fee components
        for class_id in selected_classes:
            for component_id in selected_components:
                # Get the amount for the selected component
                amount_field = f"amount_{component_id}"
                if amount_field in request.form and request.form[amount_field]:
                    amount = float(request.form[amount_field])

                    # Add the fee component to the database for the current class
                    class_fee_component = ClassFeeComponent(
                        class_id=int(class_id),
                        component_id=int(component_id),
                        amount=amount
                    )
                    db.session.add(class_fee_component)

        # Commit all changes to the database
        db.session.commit()
        flash('Selected fee components added to the selected classes successfully!', 'success')
        return redirect(url_for('main.view_class_fees', class_id=class_id))  # Adjust the redirect as needed
    
    # Fetch all classes and fee components for the form
    classes = Class.query.all()
    components = FeeComponent.query.all()
    return render_template('add_fee_component_to_class.html', classes=classes, components=components)


@main.route('/edit_fee_component/<int:id>', methods=['GET', 'POST'])
def edit_fee_component(id):
    component = FeeComponent.query.get_or_404(id)
    if request.method == 'POST':
        # Update the fee component
        component.name = request.form['name']
        component.description = request.form['description']
        component.school_id = request.form['school_id']
        db.session.commit()
        flash('Fee component updated successfully!', 'success')
        return redirect(url_for('main.fee_components'))

    # Fetch all schools for the dropdown
    schools = School.query.all()
    return render_template('edit_fee_component.html', component=component, schools=schools)

@main.route('/delete_fee_component/<int:id>', methods=['POST'])
def delete_fee_component(id):
    component = FeeComponent.query.get_or_404(id)
    db.session.delete(component)
    db.session.commit()
    flash('Fee component deleted successfully!', 'success')
    return redirect(url_for('main.fee_components'))


@main.route('/student_fees')
def student_fees():
    # Fetch all student fees
    fees = StudentFee.query.all()
    return render_template('view_fees.html', fees=fees)


@main.route('/generate_class_fees_pdf', methods=['GET'])
def generate_class_fees_pdf():

    # Fetch the first school (adjust based on your requirements)
    school = School.query.first()

    # Handle case when no school is found
    if not school:
        return "School information not found", 404

    # Fetch the latest assessment or a specific one
    assessment = Assessment.query.first()

    # Handle case when no assessment is found
    if not assessment:
        return "Assessment information not found", 404

    # Example school information
    school_name = school.name
    school_address = school.address
    academic_session = assessment.academic_session

    # Fetch class fees data
    classes = Class.query.all()
    class_fees = []
    for cls in classes:
        # Fetch fee components for each class
        fee_components = ClassFeeComponent.query.filter_by(class_id=cls.id).all()
        total_fee = sum([component.amount for component in fee_components])
        class_fees.append({
            "class_name": cls.class_name,
            "total_fee": total_fee,
            "fee_breakdown": [(comp.fee_component.name, comp.amount) for comp in fee_components]
        })

    # Generate the PDF
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Add School Header
    elements.append(Table(
        [[school_name], [school_address], [academic_session]],
        style=TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]),
        colWidths=[500]
    ))

    elements.append(Table([[" "]]))  # Spacer

    # Add Class Fees Table
    data = [["Class Name", "Total Fee (₦)", "Fee Breakdown"]]
    for class_fee in class_fees:
        fee_breakdown_text = "\n".join([f"{name}: ₦{amount}" for name, amount in class_fee['fee_breakdown']])
        data.append([class_fee['class_name'], f"₦{class_fee['total_fee']}", fee_breakdown_text])

    table = Table(data, colWidths=[150, 100, 250])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    pdf.build(elements)

    # Return the PDF as a downloadable file
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="class_fees.pdf", mimetype='application/pdf')

@main.route('/generate_class_fees', methods=['GET'])
def generate_class_fees():
    return render_template('generate_fees.html')



@main.route('/generate_fees', methods=['GET', 'POST'])
def generate_fees():
    if request.method == 'POST':
        student_id = request.form['student_id']
        component_id = request.form['component_id']
        amount = float(request.form['amount'])
        academic_year = request.form['academic_year']
        term = request.form['term']

        fee = StudentFee(
            student_id=student_id,
            component_id=component_id,
            amount=amount,
            academic_year=academic_year,
            term=term,
            payment_status='unpaid'
        )
        db.session.add(fee)
        db.session.commit()
        return redirect(url_for('main.view_fees', student_id=student_id))
    return render_template('generate_fees.html')

@main.route('/view_fees', methods=['GET'])
def view_fees():
    student_id = request.args.get('student_id')
    fees = []
    if student_id:
        fees = StudentFee.query.filter_by(student_id=student_id).all()
    return render_template('view_fees.html', fees=fees, student_id=student_id)


@main.route('/class_fee_components', methods=['GET'])
def display_class_fee_components():
    # Fetch all records from ClassFeeComponent
    class_fee_components = ClassFeeComponent.query.all()

    # Group fees by class
    grouped_fees = defaultdict(list)
    for component in class_fee_components:
        grouped_fees[component.class__.class_name].append(component)

    # Render the template and pass the grouped data
    return render_template(
        'class_fee_components.html', 
        grouped_fees=grouped_fees
    )

@main.route('/view_class_fees/<int:class_id>')
def view_class_fees(class_id):
    # Fetch the specific class by its ID
    selected_class = Class.query.get_or_404(class_id)
    
   
    class_fee_components = ClassFeeComponent.query.filter_by(class_id=class_id).all()
    return render_template('view_class_fees.html', selected_class=selected_class, class_fee_components=class_fee_components)



@main.route('/remove_fee_component_from_class/<int:class_fee_component_id>', methods=['POST'])
def remove_fee_component_from_class(class_fee_component_id):
    class_fee_component = ClassFeeComponent.query.get_or_404(class_fee_component_id)
    class_id = class_fee_component.class_id
    db.session.delete(class_fee_component)
    db.session.commit()
    flash('Fee component removed from class successfully!', 'success')
    return redirect(url_for('main.view_class_fees', class_id=class_id))

@main.route('/record_payment', methods=['GET', 'POST'])
def record_payment():
    if request.method == 'POST':
        student_fee_id = request.form['student_fee_id']
        amount_paid = float(request.form['amount_paid'])
        payment_date = request.form['payment_date']
        payment_method = request.form['payment_method']
        receipt_number = request.form.get('receipt_number')
        notes = request.form.get('notes')

        payment = FeePayment(
            student_fee_id=student_fee_id,
            amount_paid=amount_paid,
            payment_date=payment_date,
            payment_method=payment_method,
            receipt_number=receipt_number,
            notes=notes
        )
        db.session.add(payment)

        # Update payment status
        student_fee = StudentFee.query.get(student_fee_id)
        total_paid = db.session.query(db.func.sum(FeePayment.amount_paid)).filter(
            FeePayment.student_fee_id == student_fee_id
        ).scalar() or 0
        if total_paid >= student_fee.amount:
            student_fee.payment_status = 'paid'
        else:
            student_fee.payment_status = 'unpaid'
        db.session.commit()
        return redirect(url_for('main.view_fees', student_id=student_fee.student_id))
    return render_template('record_payment.html')
