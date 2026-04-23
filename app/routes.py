<<<<<<< HEAD

# from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, g, session
# from extensions import db
# import os
# from forms import (
#     TeacherForm, ClassForm, GradeForm, AttendanceForm, StudentForm, AssignTeachersForm,
#     AssessmentForm, AssessmentResultForm, SubjectForm, SchoolForm, UserForm, AssessmentTypeForm, AssignSubjectToClassForm, LoginForm
# )
# from models import (
#     User, Student, Teacher, Class, Attendance, Assessment, AssessmentType,
#     AssessmentSubjectScore, AssessmentResult, Subject, ClassSubject, TeacherSubject, School
# )
# from models import Grade, FeeComponent, StudentClassFeePayment, ClassFeeComponent
# from flask_login import login_user, logout_user, login_required, current_user
# from io import BytesIO
# import pandas as pd
# from docx import Document
# from flask import send_from_directory
# from sqlalchemy.sql import func
# from werkzeug.utils import secure_filename
# from flask import current_app
# from config import Config
# from sqlalchemy.orm import joinedload
# from reportlab.lib.pagesizes import A4, letter
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# from reportlab.platypus import Table, TableStyle, SimpleDocTemplate
# from io import BytesIO
# from flask import send_file, jsonify
# import json
# from collections import defaultdict
# from sqlalchemy.orm import aliased

# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from io import BytesIO
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
# from reportlab.lib import colors
# from io import BytesIO
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
# from reportlab.lib import colors
# from reportlab.lib.utils import ImageReader
# from flask import g
# from utils import school_required, filter_by_school
# import uuid
# from flask_wtf.csrf import validate_csrf
# from forms import RemarksForm

# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from io import BytesIO
# import os
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
# from reportlab.lib.units import inch
# from reportlab.lib.utils import ImageReader
# from reportlab.lib.enums import TA_CENTER
# from reportlab.platypus import Image
# from flask_wtf.csrf import generate_csrf

=======
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a
from utils import *
from forms import ResetPasswordForm

# Blueprint instance
main = Blueprint('main', __name__)


<<<<<<< HEAD
=======
@main.errorhandler(403)  # Access Denied
def access_denied(error):
    return render_template('access_denied.html'), 403

@main.errorhandler(404)  # Not Found
def not_found(error):
    return render_template('not_found.html'), 404

@main.errorhandler(500)  # Server Error
def server_error(error):
    return render_template('server_error.html'), 500


>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a
@main.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main.before_request
def load_school_details():
    if current_user.is_authenticated:
        """
        Check if school details exist in session
        """
        if 'school_name' not in session or 'school_logo' not in session:
            school = School.query.get(current_user.school_id)
            if school:
                g.school_name = school.name
                g.school_logo = school.school_logo if school.school_logo else 'static/uploads/default-logo.png'
                session['school_name'] = g.school_name
                session['school_logo'] = g.school_logo
        else:
            g.school_name = session['school_name']
            g.school_logo = session['school_logo']
    else:
        g.school_name = "School Management Portal"
        g.school_logo = "uploads/default-logo.png"


@main.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)

            """
            Store school details in session & `g`
            """
            if user.school_id:
                school = School.query.get(user.school_id)
                if school:
                    g.school_name = school.name
                    g.school_logo = school.school_logo if school.school_logo else 'uploads/default-logo.png'
                    session['school_name'] = g.school_name
                    session['school_logo'] = g.school_logo

            # Redirect based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            if user.role == 'admin':
                return redirect(url_for('main.dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('main.teacher_dashboard'))
            else:
                return redirect(url_for('main.student_dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template('index.html',
                           form=form,
                           is_authenticated=current_user.is_authenticated)



# School Registration
def generate_unique_code():
    return str(uuid.uuid4())

@main.route('/register_school', methods=['GET', 'POST'])
def register_school():
    form = SchoolForm()
    if form.validate_on_submit():
        school_logo_path = None

        if form.school_logo.data:
            logo_file = form.school_logo.data
            filename = secure_filename(logo_file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            filepath = os.path.join(upload_folder, filename)

            """
            Check if the upload folder exists; create it if it doesn't
            """
            os.makedirs(upload_folder, exist_ok=True)

            try:
                logo_file.save(filepath)
                school_logo_path = f'static/images/school_logos/{filename}'
                flash('Logo uploaded successfully!', 'success')
            except Exception as e:
                flash(f'Error uploading logo: {e}', 'danger')
                print(f"Logo upload error: {e}")
                """
                Logging the full traceback for debugging:
                """
                import traceback
                traceback.print_exc()

        registration_code = str(uuid.uuid4())
        school = School(
            name=form.name.data,
            address=form.address.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            school_logo=school_logo_path,
            website=form.website.data,
            principal_name=form.principal_name,
            registration_code=registration_code
        )

        try:
            db.session.add(school)
            db.session.commit()
            flash('School registered successfully!  Provide this registration link to the school: ' +
                  url_for('main.register_user', school_code=registration_code, _external=True), 'success')

            return redirect(url_for('main.school_confirmation', school_id=school.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Database error: {e}", "danger")
            print(f"Database error: {e}")
            import traceback
            traceback.print_exc()

    return render_template('register_school.html', form=form)


@main.route('/school_confirmation/<int:school_id>')
def school_confirmation(school_id):
    school = School.query.get_or_404(school_id)
    return render_template('school_confirmation.html', school=school)


@main.route('/schools')
@login_required
@admin_required
def schools():
    schools = School.query.all()
    return render_template('schools.html', schools=schools)

# Delete a school
@main.route('/delete/<int:id>')
@login_required
@admin_required
def delete_school(id):
    school = School.query.get_or_404(id)
    db.session.delete(school)
    db.session.commit()
    return redirect(url_for('main.schools'))

# Edit school details
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_school(id):
    school = School.query.get_or_404(id)
    form = SchoolForm(obj=school)

    photo_filename = None

    if form.validate_on_submit():
        print("Form is valid")
        print("Form Data:", form.data)

        school.name = form.name.data
        school.address = form.address.data
        school.email = form.email.data
        school.phone_number = form.phone_number.data
        school.website = form.website.data
        school.principal_name = form.principal_name.data
        school.school_logo = photo_filename

        """Handle photo upload"""
        if form.school_logo.data:
            try:
                photo_file = form.school_logo.data
                photo_filename = secure_filename(photo_file.filename)
                photo_path = os.path.join(Config.UPLOAD_FOLDER, photo_filename)
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

                """Delete old logo if it exists and store the full path"""
                if school.school_logo:
                    old_photo_path = os.path.join(Config.UPLOAD_FOLDER, school.school_logo)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)

                photo_file.save(photo_path)
                school.school_logo = photo_filename

                flash('Logo updated successfully!', 'success')

            except Exception as e:
                flash(f'Error updating logo: {e}', 'danger')
                print(f"Logo update error: {e}")

        try:
            db.session.commit()
            flash('School updated successfully!', 'success')
            return redirect(url_for('main.schools'))
        except Exception as e:
            db.session.rollback()
            flash(f"Database error: {e}", "danger")
            print(f"Database error: {e}")
            return render_template('edit_schools.html', school=school, form=form)

    else:
        print("Form is not valid. Errors:", form.errors)

    return render_template('edit_schools.html', school=school, form=form)

# User registration (Only School can register user in their school)
@main.route('/register_user', methods=['GET', 'POST'])
@login_required
@admin_required
def register_user():
    if not current_user.is_authenticated:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('main.index'))

    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    school_code = request.args.get('school_code')
    if not school_code:
        flash('Invalid registration link.', 'danger')
        return redirect(url_for('main.index'))

    school = School.query.filter_by(registration_code=school_code).first()
    if not school:
        flash('Invalid school code.', 'danger')
        return redirect(url_for('main.index'))

    students = Student.query.filter_by(school_id=school.id).all()
    print("student details is:" ,students)

    teachers = Teacher.query.filter_by(school_id=school.id).all()
    print("teacher details is:" ,teachers)

    form = UserForm()
    form.school_id.choices = [(school.id, school.name)]
    form.school_id.data = school.id
    form.school_id.render_kw = {'readonly': True}

    form.student_id.choices = [(s.id, f"{s.first_name} {s.last_name} ({s.id})") for s in students]
    form.teacher_id.choices = [(t.id, f"{t.first_name} {t.last_name}") for t in teachers]

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('main.register_user', school_code=school_code))

        user = User(
            username=form.username.data,
            role=form.role.data,
            school_id=school.id,
            student_id=None,
            teacher_id=None
        )

        if form.role.data == 'student':
            student = Student.query.get(form.student_id.data)
            if student:
                user.student_id = student.id
            else:
                flash("Invalid student selected.", "danger")
                return render_template('register_user.html',
                                       form=form,
                                       school_name=school.name,
                                       school_code=school_code)

        elif form.role.data == 'teacher':
            teacher = Teacher.query.get(form.teacher_id.data)
            if teacher:
                user.teacher_id = teacher.id
            else:
                flash("Invalid teacher selected.", "danger")
                return render_template('register_user.html',
                                       form=form,
                                       school_name=school.name,
                                       school_code=school_code)

        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('User registered successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e: # Catch potential exceptions
            db.session.rollback()
            flash(f'An error occurred while registering the user: {e}', 'danger')
            #Log the error for debugging.
            print(f"Registration Error: {e}")
            return render_template('register_user.html',
                                   form=form,
                                   school_name=school.name,
                                   school_code=school_code)

    return render_template(
        'register_user.html',
        form=form,
        school_name=school.name,
        school_code=school_code
    )


@main.route('/reset_user_password', methods=['GET', 'POST'])
@login_required
def reset_user_password():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()

    # Fetch users with their schools
    users = (
        db.session.query(User, School)
        .join(School, User.school_id == School.id)
        .order_by(School.name, User.username)
        .all()
    )

    # Populate dropdown: user_id | "Username - School"
    form.user_id.choices = [
        (u.id, f"{u.username} — {s.name}")
        for u, s in users
    ]

    if form.validate_on_submit():
        user = User.query.get(form.user_id.data)
        if not user:
            flash('Invalid user selected.', 'danger')
            return redirect(url_for('main.reset_user_password'))

        user.set_password(form.new_password.data)

        try:
            db.session.commit()
            flash(f'Password reset successfully for {user.username}.', 'success')
            return redirect(url_for('main.reset_user_password'))
        except Exception as e:
            db.session.rollback()
            flash('Error resetting password.', 'danger')
            print(e)

    return render_template(
        'reset_user_password.html',
        form=form
    )



@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))

# Student Dashboard (Only accessible by Students)
@main.route('/student/dashboard')
@login_required
def student_dashboard():
    # if current_user.role != 'student':
    #     return redirect(url_for('main.index'))

    if current_user.role != 'student' and current_user.role != 'admin':
        return redirect(url_for('main.index'))

    if current_user.role == 'admin':
        # Admin logic: Allow viewing any student's dashboard
        student_id = request.args.get('student_id') #Get student id from the url.
        if student_id:
            student = Student.query.get(student_id)
        else:
            flash("Please provide a student ID in the URL.", "warning")
            return redirect(url_for('main.index'))
    else:
        # Student logic: View their own dashboard
        student = Student.query.filter_by(id=current_user.student_id).first()

    # Get student details linked to the current user
    # student = Student.query.filter_by(id=current_user.student_id).first()
    print('student details:', student)
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('main.index'))

    # Fetch associated school
    school = student.school
    if not school:
        flash('Student is not linked to a school.', 'danger')
        return redirect(url_for('main.index'))

    # Fetch the student's grades & results
    grades = Grade.query.filter_by(student_id=student.id).all()

    assessments = (
        db.session.query(AssessmentSubjectScore, Subject.name)
        .join(Subject, AssessmentSubjectScore.subject_id == Subject.id)
        .filter(AssessmentSubjectScore.student_id == current_user.student_id)
        .distinct(Subject.name)
        .all()
    )



    return render_template(
        'student_dashboard.html',
        student=student,
        school=school,
        grades=grades,
        assessments=assessments
    )


# Teacher Dashboard (Only accessible by Teachers)
# @main.route('/teacher/dashboard')
# @login_required
# def teacher_dashboard():
#     if current_user.role != 'teacher':
#         return redirect(url_for('main.index'))

#     try:
#         teacher_name = Teacher.query.filter_by(id=current_user.teacher_id).first()
#         print('this is teacher name:', teacher_name)
#         # school = teacher.school
#         school = School.query.get(current_user.school_id)

#         if not teacher_name:
#             flash("Teacher information not found.", "danger")
#             return redirect(url_for('main.index'))

#         # teacher_name = Teacher.query.filter_by(id=current_user.teacher_id).first()
#         # print('this is teacher name:', teacher_name)
#         # # school = teacher.school
#         # school = School.query.get(current_user.school_id)


#         if not school:
#             flash("Teacher is not associated with a school.", "danger")
#             return redirect(url_for('main.index'))
        
#         classes_taught = Class.query.join(Class.teachers).filter(
#             Teacher.id == current_user.id,
#             Class.school_id == school.id
#         ).all()

#         return render_template('teacher_dashboard.html',
#                                teacher_name=teacher_name,
#                                classes_taught=classes_taught,
#                                teacher=teacher_name,
#                                school_name=school.name)

#     except Exception as e:
#         print(f"Error in teacher dashboard route: {e}")
#         flash("An error occurred while accessing the dashboard. Please try again later.", "danger")
#         return redirect(url_for('main.index'))

@main.route('/teacher/dashboard')
@login_required
# @admin_access
def teacher_dashboard():
    if current_user.role != 'teacher' and current_user.role != 'admin':
        return redirect(url_for('main.index'))

    try:  # Start of try block
        teacher_name = Teacher.query.filter_by(id=current_user.teacher_id).first()
        print('this is teacher name:', teacher_name)
        school = School.query.get(current_user.school_id)
        print('this is school:', school)

        if not teacher_name:
            flash("Teacher information not found.", "danger")
            return redirect(url_for('main.index'))

        if not school:
            flash("Teacher is not associated with a school.", "danger")
            return redirect(url_for('main.index'))

        classes_taught = Class.query.join(Class.teachers).filter(
            Teacher.id == current_user.teacher_id,
            Class.school_id == school.id
        ).all()
        print('this is classes_taught:', classes_taught)

        return render_template('teacher_dashboard.html',
                               teacher_name=teacher_name,
                               classes_taught=classes_taught,
                               teacher=teacher_name,
                               school_name=school.name)

    except Exception as e: # Correct indentation for except clause
        print(f"Error in teacher dashboard route: {e}")
        flash("An error occurred while accessing the dashboard. Please try again later.", "danger")
        return redirect(url_for('main.index'))
    
# Dashboard (Only accessible by Admins)
@main.route('/dashboard')
@login_required
@admin_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))

    try:
        school = School.query.get(current_user.school_id)

        if not school:
            flash("No school linked to your account or invalid school ID.", "danger")
            return redirect(url_for('main.index'))

        school_name = school.name

        student_count = Student.query.filter_by(school_id=current_user.school_id).count()
        teacher_count = Teacher.query.filter_by(school_id=current_user.school_id).count()
        class_count = Class.query.filter_by(school_id=current_user.school_id).count()

        return render_template('dashboard.html',
                               school_name=school_name,
                               student_count=student_count,
                               teacher_count=teacher_count,
                               class_count=class_count,
                               school=school)

    except Exception as e:
        print(f"Error in dashboard route: {e}")
        flash("An error occurred while accessing the dashboard. Please try again later.", "danger")
        return redirect(url_for('main.index'))

# Report Generation Route

""" 
This route below is still be worked on
"""
@main.route('/generate_report/<report_type>')
@login_required
def generate_report(report_type):

    # Fetching data for report
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


@main.route('/attendance')
@login_required
@admin_required
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

#     # Fetch students and their associated class names
#     students = (
#         db.session.query(
#             Student.id,
#             Student.first_name,
#             Student.last_name,
#             Class.class_name,
#             Class.id.label('class_id')
#         )
#         .join(Class, Student.class_id == Class.id)
#         .all()
#     )

#     # Set choices for the student_id field
#     if students:
#         form.student_id.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in students]
#     else:
#         form.student_id.choices = [("", "No Students Available")]

#     if form.validate_on_submit():
#         student_id = form.student_id.data
#         days_present = form.days_present.data
#         total_days_opened = form.total_days_opened.data

#         # Fetch the student's class automatically
#         student = Student.query.get(student_id)
#         if not student:
#             flash("Invalid student selected.", "danger")
#             return redirect(url_for('main.add_attendance'))

#         class_id = student.class_id

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
@admin_access
def add_attendance():
    form = AttendanceForm()

    if current_user.role != 'admin':
        teacher = Teacher.query.filter_by(id=current_user.teacher_id).first()
        if not teacher:
            abort(403)
            return "This is a restricted area for only teachers and admin"

        teacher_classes = [c.id for c in teacher.classes]
    else:
        teacher_classes = [c.id for c in Class.query.all()]

    # Fetch students and their associated class names, filtered by teacher's classes
    students = (
        db.session.query(
            Student.id,
            Student.first_name,
            Student.last_name,
            Class.class_name,
            Class.id.label('class_id')
        )
        .join(Class, Student.class_id == Class.id)
        .filter(Class.id.in_(teacher_classes))
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

        class_id = student.class_id

        # Check if the student's class is assigned to the teacher
        if class_id not in teacher_classes:
            flash("You are not authorized to mark attendance for this student.", "danger")
            return redirect(url_for('main.add_attendance'))

        # Check if an attendance record exists for this student
        attendance = Attendance.query.filter_by(student_id=student_id, class_id=class_id).first()

        if attendance:
            # Prevent re-entry and display an error
            flash("Attendance record already exists for this student. If you want to update the attendance record, first remove the old record.", "danger")
            return redirect(url_for('main.add_attendance'))
        
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
        flash('Attendance record updated successfully! Click on add attendance to add another attendance record.', 'success')
        return redirect(url_for('main.attendance'))

    return render_template('add_attendance.html', form=form, students=students)

@main.route('/students', methods=['GET'])
@login_required
@admin_required
def students():
    """Display students only linked to the logged-in user's school."""
    search_query = request.args.get('search', '').strip().lower()

    if not current_user.school_id:
        flash("You are not linked to any school.", "warning")
        return redirect(url_for('main.dashboard'))

    query = Student.query.filter_by(school_id=current_user.school_id)

    if search_query:
        query = query.join(Class).filter(
            (Student.first_name.ilike(f"%{search_query}%")) |
            (Student.last_name.ilike(f"%{search_query}%")) |
            (Class.class_name.ilike(f"%{search_query}%"))
        )

    students = query.all()

    return render_template('students.html', students=students)

# Student enrollment
@main.route('/add_student', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    form = StudentForm()

    # Get the current user's school
    current_school = current_user.school

    if not current_school:
        flash("You are not associated with any school. Please contact an administrator.", "warning")
        return redirect(url_for('main.index'))

    # Populate class choices for the current user's school ONLY
    form.class_id.choices = [(cls.id, cls.class_name) for cls in Class.query.filter_by(school_id=current_school.id).all()]
    if not form.class_id.choices:
        form.class_id.choices = [(-1, 'No classes available for your school')]

    # Pre-fill School name and disabled
    form.school_id.choices = [(current_school.id, current_school.name)]
    form.school_id.data = current_school.id
    form.school_id.render_kw = {'readonly': True}


    if form.validate_on_submit():
        if form.class_id.data == -1:
            flash("Please select a valid class.", "warning")
            return render_template('add_student.html', form=form)

        try:
            student = Student(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                date_of_birth=form.date_of_birth.data,
                enrollment_date=form.enrollment_date.data,
                gender=form.gender.data,
                grade_level=form.grade_level.data,
                contact_email=form.contact_email.data,
                school_id=current_school.id,
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


# Edit Students Details
@main.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)

    if student.school_id != current_user.school_id:
        flash("You do not have permission to edit this student.", "danger")
        return redirect(url_for('main.students'))

    form = StudentForm(obj=student)

    form.class_id.choices = [(cls.id, cls.class_name) for cls in Class.query.filter_by(school_id=student.school_id).all()]
    if not form.class_id.choices:
        form.class_id.choices = [(-1, 'No classes available for your school')]

    form.school_id.choices = [(student.school_id, student.school.name)]
    form.school_id.data = student.school_id
    form.school_id.render_kw = {'readonly': True}


    if form.validate_on_submit():
        if form.class_id.data == -1:
            flash("Please select a valid class.", "warning")
            return render_template('edit_student.html', form=form)

        try:
            student.first_name = form.first_name.data
            student.last_name = form.last_name.data
            student.date_of_birth = form.date_of_birth.data
            student.enrollment_date = form.enrollment_date.data
            student.gender = form.gender.data
            student.grade_level = form.grade_level.data
            student.contact_email = form.contact_email.data
            student.class_id = form.class_id.data
            # No need to update school_id, as it's disabled
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('main.students'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating the student: {str(e)}", "danger")

    return render_template('edit_student.html', form=form, student=student)

# Delete student records
@main.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)

    if student.school_id != current_user.school_id:
        flash("You do not have permission to delete this student.", "danger")
        return redirect(url_for('main.students'))

    try:
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting the student: {str(e)}", "danger")

    return redirect(url_for('main.students'))


# View, Creating, editing and deleting Teachers Records
@main.route('/teachers', methods=['GET'])
@login_required
@admin_required
def teachers():
    search_query = request.args.get('search', '').strip().lower()

    current_user_school = current_user.school

    if not current_user_school:
      return redirect(url_for('main.dashboard'))

    if search_query:
        teachers = Teacher.query.filter(
            (Teacher.school == current_user_school) &
            (
                (Teacher.first_name.ilike(f"%{search_query}%")) |
                (Teacher.last_name.ilike(f"%{search_query}%")) |
                (Teacher.qualification.ilike(f"%{search_query}%")) |
                (Teacher.teacher_subjects.any(Subject.name.ilike(f"%{search_query}%")))
            )
        ).all()
    else:
        teachers = Teacher.query.filter(Teacher.school == current_user_school).all()

    return render_template('teachers.html', teachers=teachers)


@main.route('/add_teacher', methods=['GET', 'POST'])
@login_required
@admin_required
def add_teacher():
    form = TeacherForm()

    current_school = current_user.school
    if not current_school:
        flash("You are not associated with any school.", "warning")
        return redirect(url_for('main.index'))

    # Filter schools and subjects by the logged-in user's school
    form.school_id.choices = [(current_school.id, current_school.name)]
    form.school_id.data = current_school.id
    form.school_id.render_kw = {'readonly': True}

    form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.filter_by(school_id=current_school.id).all()]
    if not form.subject.choices:
        form.subject.choices = [(-1, 'No subjects available for your school')]

    if form.validate_on_submit():
        if form.subject.data and form.subject.data[0] == -1:
            flash("Please select at least one valid subject.", "warning")
            return render_template('add_teacher.html', form=form)

        photo_filename = None
        if form.photo.data:
            photo_file = form.photo.data
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(Config.UPLOAD_FOLDER, photo_filename)
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            photo_file.save(photo_path)

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
            school_id=current_school.id
        )

        try:
            db.session.add(teacher)
            db.session.commit()

            if form.subject.data and form.subject.data[0] != -1:
                for subject_id in form.subject.data:
                    teacher_subject = TeacherSubject(teacher_id=teacher.id, subject_id=subject_id)
                    db.session.add(teacher_subject)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
            return render_template('add_teacher.html', form=form)

        flash('Teacher added successfully!')
        return redirect(url_for('main.teachers'))

    return render_template('add_teacher.html', form=form)


@main.route('/delete_teacher/<int:teacher_id>', methods=['POST'])
@login_required
@admin_required
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
@admin_required
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


@main.route('/assign_teachers', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_teachers():
    form = AssignTeachersForm()

    current_school = current_user.school
    if not current_school:
        flash("You are not associated with any school.", "warning")
        return redirect(url_for('main.index'))

    # Filter classes and teachers by the logged-in user's school
    classes = Class.query.filter_by(school_id=current_school.id).all()
    teachers = Teacher.query.filter_by(school_id=current_school.id).all()

    if not classes:
        flash("No classes available. Add a class first.", "warning")
    if not teachers:
        flash("No teachers available. Add a teacher first.", "warning")

    form.class_id.choices = [(cls.id, cls.class_name) for cls in classes]
    form.teacher_ids.choices = [(teacher.id, f"{teacher.first_name} {teacher.last_name}") for teacher in teachers]

    if form.validate_on_submit():
        class_id = form.class_id.data
        selected_teacher_ids = form.teacher_ids.data

        selected_class = Class.query.get_or_404(class_id)

        if selected_class.school_id != current_school.id:
             flash("You do not have permission to modify this class.", "danger")
             return redirect(url_for('main.classes'))

        selected_teachers = Teacher.query.filter(Teacher.id.in_(selected_teacher_ids)).all()

        # Check if all selected teachers belong to the current school
        for teacher in selected_teachers:
            if teacher.school_id != current_school.id:
                flash("One or more selected teachers do not belong to your school.", "danger")
                return redirect(url_for('main.assign_teachers'))

        selected_class.teachers = selected_teachers

        try:
            db.session.commit()
            flash('Teachers assigned successfully!', 'success')
            return redirect(url_for('main.classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error assigning teachers: {str(e)}', 'danger')

    return render_template('assign_teachers.html', form=form)



# Classes management
@main.route('/add_class', methods=['GET', 'POST'])
@login_required
@admin_required
def add_class():
    form = ClassForm()
    teachers = Teacher.query.filter_by(school_id=current_user.school_id).all()

    # Populate form teacher_ids choices dynamically
    if teachers:
        form.teacher_ids.choices = [(teacher.id, f"{teacher.first_name} {teacher.last_name}") for teacher in teachers]
    else:
        flash("No teachers are available for your school. Please add a teacher first.", "warning")
        form.teacher_ids.choices = [(-1, "No teachers are available for your school. Please add a teacher first.")]


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
@admin_required
def classes():
    classes_data = db.session.query(
        Class,
        func.count(Student.id).label('student_count')
    ).outerjoin(Student, Student.class_id == Class.id) \
     .filter(Class.school_id == current_user.school_id) \
     .group_by(Class.id).options(joinedload('teachers')).all()

    # Separate Class objects and student counts
    classes = []
    for class_obj, student_count in classes_data:
        classes.append({
            'class': class_obj,
            'student_count': student_count
        })

    return render_template('classes.html', classes=classes)

@main.route('/edit_class/<int:class_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_class(class_id):
    class_to_edit = Class.query.get_or_404(class_id)

    if class_to_edit.school_id != current_user.school_id:
        flash("You do not have permission to edit this class.", "danger")
        return redirect(url_for('main.classes'))

    if request.method == 'POST':
        class_to_edit.class_name = request.form['class_name']
        class_to_edit.class_category = request.form['class_category']
        class_to_edit.class_level = request.form['class_level']
        try:
            db.session.commit()
            flash('Class updated successfully!', 'success')
            return redirect(url_for('main.classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating class: {str(e)}', 'danger')

    return render_template('edit_class.html', class_to_edit=class_to_edit)

@main.route('/delete_class/<int:class_id>', methods=['POST'])
@login_required
@admin_required
def delete_class(class_id):
    class_to_delete = Class.query.get_or_404(class_id)

    if class_to_delete.school_id != current_user.school_id:
        flash("You do not have permission to delete this class.", "danger")
        return redirect(url_for('main.classes'))

    try:
        # SQLAlchemy should handle the association table automatically
        db.session.delete(class_to_delete)
        db.session.commit()
        flash('Class deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting class: {str(e)}', 'danger')

    return redirect(url_for('main.classes'))

# Students Grades Management
@main.route('/add_grade', methods=['GET', 'POST'])
@login_required
@admin_required
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


# School subjects Management
@main.route('/subjects')
@login_required
@admin_required
def subjects():
    subjects = Subject.query.filter_by(school_id=current_user.school_id).all()
    return render_template('subjects.html', subjects=subjects)


@main.route('/add_subject', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subject():
    # Ensure the user is linked to a school
    if not current_user.school_id:
        flash("You are not linked to any school.", "danger")
        return redirect(url_for('main.index'))

    # Ensure only admins can add subjects
    if current_user.role != 'admin':
        flash("You are not authorized to add subjects.", "danger")
        return redirect(url_for('main.index'))

    form = SubjectForm()

    if form.validate_on_submit():
        # Ensure the subject does not already exist in the school
        existing_subject = Subject.query.filter_by(name=form.name.data, school_id=current_user.school_id).first()
        if existing_subject:
            flash("This subject already exists in your school.", "warning")
            return redirect(url_for('main.add_subject'))

        # Create and save the new subject
        subject = Subject(
            name=form.name.data.strip(),
            school_id=current_user.school_id
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('main.subjects'))

    return render_template('add_subject.html', form=form)

@main.route('/assign_subject_to_class', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_subject_to_class():
    form = AssignSubjectToClassForm()

    # Populate the class dropdown
    form.class_id.choices = [
        (c.id, c.class_name)  # (value, label)
        for c in Class.query.filter_by(school_id=current_user.school_id).all()
    ]
    if not form.class_id.choices:
        form.class_id.choices = [(-1, "No classes are available for your school. Please add a class first.")]

    # Fetch all subjects for the current school
    subjects = Subject.query.filter_by(school_id=current_user.school_id).all()

    if form.validate_on_submit():
        class_id = form.class_id.data
        selected_subjects = request.form.getlist('subjects')

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


@main.route('/class_subjects')
@login_required
@admin_required
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
@login_required
@admin_required
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

@main.route('/class_subjects/<int:class_id>')
@login_required
@admin_required
def class_subjects(class_id):
    class_instance = Class.query.get_or_404(class_id)
    subjects = ClassSubject.query.filter_by(class_id=class_id).all()
    return render_template('class_subjects.html', class_instance=class_instance, subjects=subjects)


# Route to add a subject to a class
@main.route('/add_class_subject/<int:class_id>', methods=['GET', 'POST'])
@login_required
@admin_required
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



@main.route('/delete_class_subject/<class_name>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_class_subject(class_name):
    class_obj = Class.query.filter_by(class_name=class_name).first()
    if not class_obj:
        flash("Class not found", "danger")
        return redirect(url_for('main.view_class_subjects'))

    ClassSubject.query.filter_by(class_id=class_obj.id).delete()
    db.session.commit()

    flash("Class subjects deleted successfully!", "success")
    return redirect(url_for('main.view_class_subjects'))


# Student Assessment Management
@main.route('/generate_assessment_report/<int:assessment_id>')
@login_required
@admin_required
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


@main.route('/assessment_types')
@login_required
@admin_required
def assessment_types():
    if not current_user.role == 'admin'and current_user.school_id is None:
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))

    assessment_types = AssessmentType.query.filter(AssessmentType.school_id == current_user.school_id).all()

    return render_template('assessment_types.html', assessment_types=assessment_types)

@main.route('/assessment_type')
@login_required
@admin_required
def assessment_type():
    if not current_user.role == 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))

    # Filter assessment types by the logged-in user's school
    assessment_types = AssessmentType.query.all()

    return render_template('assessment_types.html', assessment_types=assessment_types)

@main.route('/add_assessment_type', methods=['GET', 'POST'])
@login_required
@admin_required
def add_assessment_type():
    form = AssessmentTypeForm()

    # Restrict access to admins
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash('Assessment type name is required.', 'danger')
        else:
            try:
                school_id = current_user.school_id

                # Check if the assessment type exists for this school
                existing_type = AssessmentType.query.filter_by(name=name, school_id=school_id).first()
                if existing_type:
                    flash('An assessment type with this name already exists for your school.', 'warning')
                else:
                    new_type = AssessmentType(name=name.strip(), school_id=school_id)
                    db.session.add(new_type)
                    db.session.commit()
                    flash('Assessment type added successfully!', 'success')
                    return redirect(url_for('main.assessment_types'))

            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('add_assessment_type.html', form=form)


@main.route('/edit_assessment_type/<int:assessment_type_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_assessment_type(assessment_type_id):
    if not current_user.role == 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))

    assessment_type = AssessmentType.query.get_or_404(assessment_type_id)

    if request.method == 'GET':
        form = AssessmentTypeForm()
        form.name.data = assessment_type.name
        return render_template('edit_assessment_type.html', assessment_type=assessment_type, form=form)

    if request.method == 'POST':
        form = AssessmentTypeForm(request.form)
        if form.validate_on_submit():
            assessment_type.name = form.name.data
            try:
                db.session.commit()
                flash('Assessment type updated successfully!', 'success')
                return redirect(url_for('main.assessment_types'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'danger')
        else:
            flash('Error in form', 'danger')
            return render_template('edit_assessment_type.html',
                                   assessment_type=assessment_type,
                                   form=form)


@main.route('/delete_assessment_type/<int:assessment_type_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_assessment_type(assessment_type_id):
    if not current_user.role == 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.index'))

    assessment_type = AssessmentType.query.get_or_404(assessment_type_id)
    try:
        db.session.delete(assessment_type)
        db.session.commit()
        flash('Assessment type deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    return redirect(url_for('main.assessment_types'))

# @main.route('/assessments')
# @login_required
# @admin_required
# def assessments():
#     all_assessments = Assessment.query.join(Class, Assessment.class_id == Class.id) \
#         .join(AssessmentType, Assessment.assessment_type_id == AssessmentType.id) \
#         .filter(Class.school_id == current_user.school_id).add_columns(
#             Assessment.id,
#             Assessment.name,
#             Assessment.date,
#             Assessment.academic_session,
#             Assessment.term,
#             Class.class_name.label('class_name'),
#             AssessmentType.name.label('assessment_type_name')
#         ) \
#         .all()

#     return render_template('assessments.html', assessments=all_assessments)


@main.route('/assessments')
@login_required
@admin_required
def assessments():
    all_assessments = db.session.query(
        Assessment.id,
        Assessment.name,
        Assessment.date,
        Assessment.academic_session,
        Assessment.term,
        AssessmentType.name.label('assessment_type_name'),
        func.group_concat(Class.class_name, ', ').label('class_names')  # Fetching multiple classes per assessment
    ) \
    .join(AssessmentType, Assessment.assessment_type_id == AssessmentType.id) \
    .outerjoin(assessment_class_association, assessment_class_association.c.assessment_id == Assessment.id) \
    .outerjoin(Class, Class.id == assessment_class_association.c.class_id) \
    .filter(Assessment.school_id == current_user.school_id) \
    .group_by(Assessment.id, AssessmentType.name) \
    .all()

    return render_template('assessments.html', assessments=all_assessments)




# @main.route('/add_assessment', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def add_assessment():
#     if not current_user.role == 'admin':
#         flash('You are not allowed to access this resource', 'danger')
#         return redirect(url_for('main.index'))

#     school = School.query.get(current_user.school_id)
#     if not school:
#         flash("School information not found.", "danger")
#         return redirect(url_for('main.index'))

#     form = AssessmentForm()

#     if form:
#         form.assessment_type.choices = [(atype.id, atype.name) for atype in AssessmentType.query.all()]
#     else:
#         form.assessment_type.choices = [(-1, "No assessment types are available. Please add an assessment type first.")]
        

#     form.class_id.choices = [
#         (cls.id, cls.class_name)
#         for cls in Class.query.filter_by(school_id=school.id).all()
#     ]


#     if form.validate_on_submit():
#         new_assessment = Assessment(
#             name=form.name.data,
#             date=form.date.data,
#             assessment_type_id=form.assessment_type.data,
#             class_id=form.class_id.data,
#             academic_session=form.academic_session.data,
#             term=form.term.data,
#             school_id=school.id
#         )
#         db.session.add(new_assessment)
#         db.session.commit()
#         flash('Assessment added successfully!', 'success')
#         return redirect(url_for('main.assessments'))

#     return render_template('add_assessment.html', form=form)

@main.route('/add_assessment', methods=['GET', 'POST'])
@login_required
@admin_required
def add_assessment():
    if not current_user.role == 'admin':
        flash('You are not allowed to access this resource', 'danger')
        return redirect(url_for('main.index'))

    school = School.query.get(current_user.school_id)
    if not school:
        flash("School information not found.", "danger")
        return redirect(url_for('main.index'))

    form = AssessmentForm()

<<<<<<< HEAD
    if form:
        form.assessment_type.choices = [(atype.id, atype.name) for atype in AssessmentType.query.all()]
    else:
        form.assessment_type.choices = [(-1, "No assessment types are available. Please add an assessment type first.")]


    form.class_id.choices = [
        (cls.id, cls.class_name)
        for cls in Class.query.filter_by(school_id=school.id).all()
    ]

=======
    # Populate dropdowns
    form.assessment_type.choices = [(atype.id, atype.name) for atype in AssessmentType.query.all()]
    form.class_ids.choices = [(cls.id, cls.class_name) for cls in Class.query.filter_by(school_id=school.id).all()]
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a

    if form.validate_on_submit():
        selected_classes = Class.query.filter(Class.id.in_(form.class_ids.data)).all()

        new_assessment = Assessment(
            name=form.name.data,
            date=form.date.data,
            assessment_type_id=form.assessment_type.data,
            academic_session=form.academic_session.data,
            term=form.term.data,
            school_id=school.id,
            classes=selected_classes  # Many-to-many relationship
        )
        
        db.session.add(new_assessment)
        db.session.commit()

        flash('Assessment added successfully!', 'success')
        return redirect(url_for('main.assessments'))

    return render_template('add_assessment.html', form=form)

# @main.route('/edit_assessment/<int:assessment_id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def edit_assessment(assessment_id):
#     assessment = Assessment.query.get_or_404(assessment_id)
#     form = AssessmentForm(obj=assessment)
#     form.assessment_type.choices = [(atype.id, atype.name) for atype in AssessmentType.query.all()]
#     form.class_id.choices = [(cls.id, cls.class_name) for cls in Class.query.all()]

#     if form.validate_on_submit():
#         assessment.name = form.name.data
#         assessment.date = form.date.data
#         assessment.assessment_type_id = form.assessment_type.data
#         assessment.class_id = form.class_id.data
#         assessment.academic_session = form.academic_session.data
#         assessment.term = form.term.data

#         db.session.commit()
#         flash('Assessment updated successfully!', 'success')
#         return redirect(url_for('main.assessments'))

#     return render_template('edit_assessment.html', form=form, assessment=assessment)

@main.route('/edit_assessment/<int:assessment_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    form = AssessmentForm(obj=assessment)

    # Populate assessment type choices
    form.assessment_type.choices = [(atype.id, atype.name) for atype in AssessmentType.query.all()]

    # Populate class choices (multi-select)
    form.class_ids.choices = [(cls.id, cls.class_name) for cls in Class.query.all()]
    
    # Preselect already assigned classes
    form.class_ids.data = [cls.id for cls in assessment.classes]

    if form.validate_on_submit():
        assessment.name = form.name.data
        assessment.date = form.date.data
        assessment.assessment_type_id = form.assessment_type.data
        assessment.academic_session = form.academic_session.data
        assessment.term = form.term.data

        # Update classes (many-to-many)
        selected_classes = Class.query.filter(Class.id.in_(form.class_ids.data)).all()
        assessment.classes = selected_classes  # Assign multiple classes

        db.session.commit()
        flash('Assessment updated successfully!', 'success')
        return redirect(url_for('main.assessments'))

    return render_template('edit_assessment.html', form=form, assessment=assessment)


# @main.route('/delete_assessment/<int:assessment_id>', methods=['POST'])
# @login_required
# @admin_required
# def delete_assessment(assessment_id):
#     assessment = Assessment.query.get_or_404(assessment_id)
#     db.session.delete(assessment)
#     db.session.commit()
#     flash('Assessment deleted successfully!', 'success')
#     return redirect(url_for('main.assessments'))

@main.route('/delete_assessment/<int:assessment_id>', methods=['POST'])
@login_required
@admin_required
def delete_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Clear associations with classes before deleting the assessment
    assessment.classes.clear()

    db.session.delete(assessment)
    db.session.commit()
    
    flash('Assessment deleted successfully!', 'success')
    return redirect(url_for('main.assessments'))



@main.route('/assessment_subject_scores')
@login_required
@admin_required
def assessment_subject_scores():
    # Ensure the user is linked to a school
    if not current_user.school_id:
        flash("No school linked to your account.", "danger")
        return redirect(url_for('main.index'))

    school_id = current_user.school_id

    # Get filter parameters from the request
    assessment_id = request.args.get('assessment')
    academic_session = request.args.get('academic_session')
    subject_id = request.args.get('subject')
    student_id = request.args.get('student')
    class_id = request.args.get('class_id') # Get class_id from request

    # Base query with school filtering
    query = db.session.query(
        AssessmentSubjectScore.id.label('score_id'),
        AssessmentSubjectScore,
        Assessment.name.label('assessment_name'),
        Subject.name.label('subject_name'),
        Student.first_name,
        Student.last_name,
        AssessmentSubjectScore.total_marks,
        Assessment.academic_session,
        Class.class_name
    ).join(
        Assessment, AssessmentSubjectScore.assessment_id == Assessment.id
    ).join(
        Subject, AssessmentSubjectScore.subject_id == Subject.id
    ).join(
        Student, AssessmentSubjectScore.student_id == Student.id
    ).filter(
        Student.school_id == school_id,
        Class.school_id == school_id
    )

    # Apply additional filters
    if assessment_id:
        query = query.filter(AssessmentSubjectScore.assessment_id == assessment_id)
    if academic_session:
        query = query.filter(Assessment.academic_session == academic_session)
    if subject_id:
        query = query.filter(AssessmentSubjectScore.subject_id == subject_id)
    if student_id:
        query = query.filter(AssessmentSubjectScore.student_id == student_id)
    if class_id:
        query = query.filter(ClassSubject.class_id == class_id)


    # Fetch filtered results
    scores = query.all()
    # print('scores:', scores)

    # Fetch filter options, ensuring they are linked to the same school
    assessments = Assessment.query.filter_by(school_id=school_id).all()
    academic_sessions = db.session.query(Assessment.academic_session).filter_by(school_id=school_id).distinct().all()
    subjects = Subject.query.filter_by(school_id=school_id).all()
    students = Student.query.filter_by(school_id=school_id).all()
    classes = Class.query.filter_by(school_id=school_id).all()
    class_subjects = ClassSubject.query.join(Class).filter(Class.school_id == school_id).options(joinedload(ClassSubject.subject)).all()
    # class_subjects = ClassSubject.query.filter_by(school_id=school_id).all() # if class_id else ClassSubject.query.filter_by(school_id=school_id).all()
    print('this is class subjects:', class_subjects)
    print('this is class assessment:', assessments)

    # Handle form submission for score editing and deletion
    if request.method == 'POST':
        if 'edit_score' in request.form:
            score_id = request.form.get('edit_score')
            return redirect(url_for('main.edit_assessment_subject_score', score_id=score_id))
        elif 'delete_score' in request.form:
            score_id = request.form.get('delete_score')
            score = AssessmentSubjectScore.query.get_or_404(score_id)
            if score.student.school_id != current_user.school_id or not current_user.role == 'admin':
                flash("You don't have permission to delete this score.", "danger")
                return redirect(url_for('main.assessment_subject_scores'))

            try:
                db.session.delete(score)
                db.session.commit()
                flash("Score deleted successfully.", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error deleting score: {str(e)}", "danger")
            return redirect(url_for('main.assessment_subject_scores'))

    csrf_token = generate_csrf()

    return render_template(
        'assessment_subject_scores.html',
        scores=scores,
        assessments=assessments,
        academic_sessions=[session[0] for session in academic_sessions],
        subjects=subjects,
        students=students,
        csrf_token=csrf_token,
        classes=classes,
        is_admin=current_user.role == 'admin',
        class_subjects=class_subjects
    )


@main.route('/edit_assessment_subject_score/<int:score_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_assessment_subject_score(score_id):
    score = AssessmentSubjectScore.query.get_or_404(score_id)

    # Ensure the user is linked to the correct school and is an admin
    if score.student.school_id != current_user.school_id or not current_user.role == 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('main.assessment_subject_scores'))

    if request.method == 'POST':
        try:
            score.total_marks = request.form.get('total_marks')
            db.session.commit()
            flash("Assessment score updated successfully.", "success")
            return redirect(url_for('main.assessment_subject_scores'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating score: {str(e)}", "danger")

    return render_template('edit_assessment_subject_score.html', score=score)


# @main.route('/delete_assessment_subject_score/<int:score_id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def delete_assessment_subject_score(score_id):
#     # scores = AssessmentSubjectScore.query.all() #or some form of filter.
#     # for score in scores:
#     #     print(score.id) #prints the id of each score.
#     score = AssessmentSubjectScore.query.get_or_404(score_id)
#     # print('this is score id:', score)

#     # Check user authorization
#     if not current_user.role == 'admin':
#         return jsonify({"success": False, "message": "Unauthorized access."}), 403
    
#     # Validate CSRF token
#     # csrf_token = request.form.get('csrf_token')
#     # if not csrf_token or csrf_token != session.get('_csrf_token'):
#     #     return jsonify({"success": False, "message": "Invalid CSRF token."}), 400

#     try:
#         db.session.delete(score)
#         db.session.commit()
#         return render_template('assessment_subject_score.html')
#         return jsonify({"success": True, "message": "Assessment score deleted successfully."})
#     except Exception as commit_error:
#         db.session.rollback()
#         print(f"Commit error: {str(commit_error)}")
#         flash(f"Error committing changes: {str(commit_error)}", "danger")
#         return jsonify({"success": False, "message": f"Error deleting score: {str(commit_error)}"}), 500

@main.route('/delete_assessment_subject_score/<int:score_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_assessment_subject_score(score_id):
    score = AssessmentSubjectScore.query.get_or_404(score_id)

    # Check user authorization
    if not current_user.role == 'admin':
<<<<<<< HEAD
        return jsonify({"success": False, "message": "Unauthorized access."}), 403

    # Validate CSRF token
    csrf_token = request.form.get('csrf_token')
    if not csrf_token or csrf_token != session.get('_csrf_token'):
        return jsonify({"success": False, "message": "Invalid CSRF token."}), 400
=======
        flash("Unauthorized access.", "danger")
        return redirect(url_for('main.assessment_subject_scores'))  # Redirect on failure
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a

    try:
        db.session.delete(score)
        db.session.commit()
        flash("Assessment score deleted successfully.", "success")  # Flash success message
        return redirect(url_for('main.assessment_subject_scores'))  # Redirect on success

    except Exception as commit_error:
        db.session.rollback()
        print(f"Commit error: {str(commit_error)}")
        flash(f"Error deleting score: {str(commit_error)}", "danger")
        return redirect(url_for('main.assessment_subject_scores')) #redirect with error message.
    
@main.route('/delete_multiple_assessment_subject_scores', methods=['POST'])
@login_required
@admin_required
def delete_multiple_assessment_subject_scores():
    if not current_user.role == 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('main.assessment_subject_scores'))

    delete_ids = request.form.getlist('delete_ids')

    if not delete_ids:
        flash("No scores selected for deletion.", "warning")
        return redirect(url_for('main.assessment_subject_scores'))

    try:
        for score_id in delete_ids:
            score = AssessmentSubjectScore.query.get(score_id)
            if score and score.student.school_id == current_user.school_id:
                db.session.delete(score)
        db.session.commit()
        flash("Selected scores deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting scores: {str(e)}", "danger")

    return redirect(url_for('main.assessment_subject_scores'))


# main.route('/api/assessment_subject_scores', methods=['GET', 'POST'])
# def get_scores():
#     scores = AssessmentSubjectScore.query.all()
#     return jsonify([{
#         'id': score.id,
#         'assessment_id': score.assessment_id,
#         'subject_id': score.subject_id,
#         'student_id': score.student_id,
#         'total_marks': score.total_marks
#     } for score in scores])

# @main.route('/api/assessment_subject_scores/<int:id>', methods=['PUT'])
# def update_score(id):
#     data = request.json
#     score = AssessmentSubjectScore.query.get(id)
#     if not score:
#         return jsonify({'error': 'Score not found'}), 404
    
#     score.total_marks = data.get('total_marks', score.total_marks)
#     db.session.commit()
#     return jsonify({'message': 'Score updated successfully'})

# @main.route('/api/assessment_subject_scores/<int:id>', methods=['DELETE'])
# def delete_score(id):
#     score = AssessmentSubjectScore.query.get(id)
#     if not score:
#         return jsonify({'error': 'Score not found'}), 404
    
#     db.session.delete(score)
#     db.session.commit()
#     return jsonify({'message': 'Score deleted successfully'})

# @main.route('/scores', methods=['GET', 'POST'])
# def scores():
#     assessments = Assessment.query.all()
#     students = db.session.query(Student, Class.class_name).join(Class, Student.class_id == Class.id).all()
#     subjects = Subject.query.all()

#     if request.method == 'GET':
#         all_scores = AssessmentSubjectScore.query.all()
#         scores_list = [{'id': s.id, 'assessment_id': s.assessment_id, 'subject_id': s.subject_id, 'student_id': s.student_id, 'total_marks': s.total_marks} for s in all_scores]
#         students_list = [{'id': student.id, 'name': f"{student.first_name} {student.last_name}", 'class_name': class_name} for student, class_name in students] # Corrected line
#         return render_template('assessment_subject_scores.html', scores=scores_list, assessments=assessments, students=students_list, subjects=subjects)

#     elif request.method == 'POST':
#         data = request.get_json()
#         subject_marks = data.get('subject_marks', [])
#         for item in subject_marks:
#             new_score = AssessmentSubjectScore(
#                 assessment_id=data['assessment_id'],
#                 subject_id=item['subject_id'],
#                 student_id=data['student_id'],
#                 total_marks=item['total_marks']
#             )
#             db.session.add(new_score)
#         db.session.commit()
#         all_scores = AssessmentSubjectScore.query.all()
#         scores_list = [{'id': s.id, 'assessment_id': s.assessment_id, 'subject_id': s.subject_id, 'student_id': s.student_id, 'total_marks': s.total_marks} for s in all_scores]
#         students = db.session.query(Student, Class.class_name).join(Class, Student.class_id == Class.id).all()
#         students_list = [{'id': student.id, 'name': f"{student.first_name} {student.last_name}", 'class_name': class_name} for student, class_name in students] # Corrected line
#         return render_template('assessment_subject_scores.html', scores=scores_list, assessments=assessments, students=students_list, subjects=subjects)

# @main.route('/scores', methods=['GET', 'POST'])
# def scores():
#     assessments = Assessment.query.all()
#     students = db.session.query(Student, Class.class_name).join(Class, Student.class_id == Class.id).all()
#     all_subjects = Subject.query.all() #Get all subjects

#     if request.method == 'GET':
#         all_scores = AssessmentSubjectScore.query.all()
#         scores_list = []
#         for score in all_scores:
#             assessment = Assessment.query.get(score.assessment_id)
#             subject = Subject.query.get(score.subject_id)
#             student = Student.query.get(score.student_id)
#             if student:
#                 student_class = Class.query.get(student.class_id)
#                 student_name = f"{student.first_name} {student.last_name}"
#                 class_name = student_class.class_name if student_class else "Class Not Found"
#             else:
#                 student_name = "Student Not Found"
#                 class_name = "Class Not Found"

#             scores_list.append({
#                 'id': score.id,
#                 'assessment_name': assessment.name if assessment else "Assessment Not Found",
#                 'subject_name': subject.name if subject else "Subject Not Found",
#                 'student_name': student_name,
#                 'total_marks': score.total_marks
#             })
#         students_list = [{'id': student.id, 'name': f"{student.first_name} {student.last_name}", 'class_name': class_name} for student, class_name in students]
#         return render_template('assessment_subject_scores.html', scores=scores_list, assessments=assessments, students=students_list, subjects=subjects)

#     elif request.method == 'POST':
#         data = request.get_json()
#         subject_marks = data.get('subject_marks', [])
#         for item in subject_marks:
#             new_score = AssessmentSubjectScore(
#                 assessment_id=data['assessment_id'],
#                 subject_id=item['subject_id'],
#                 student_id=data['student_id'],
#                 total_marks=item['total_marks']
#             )
#             db.session.add(new_score)
#         db.session.commit()
#         all_scores = AssessmentSubjectScore.query.all()
#         scores_list = []
#         for score in all_scores:
#             assessment = Assessment.query.get(score.assessment_id)
#             subject = Subject.query.get(score.subject_id)
#             student = Student.query.get(score.student_id)
#             if student:
#                 student_class = Class.query.get(student.class_id)
#                 student_name = f"{student.first_name} {student.last_name}"
#                 class_name = student_class.class_name if student_class else "Class Not Found"
#             else:
#                 student_name = "Student Not Found"
#                 class_name = "Class Not Found"
#             scores_list.append({
#                 'id': score.id,
#                 'assessment_name': assessment.name if assessment else "Assessment Not Found",
#                 'subject_name': subject.name if subject else "Subject Not Found",
#                 'student_name': student_name,
#                 'total_marks': score.total_marks
#             })
#         students = db.session.query(Student, Class.class_name).join(Class, Student.class_id == Class.id).all()
#         students_list = [{'id': student.id, 'name': f"{student.first_name} {student.last_name}", 'class_name': class_name} for student, class_name in students]
#         return render_template('assessment_subject_scores.html', scores=scores_list, assessments=assessments, students=students_list, subjects=subjects)

# @main.route('/scores', methods=['GET', 'POST'])
# def scores():
#     assessments = Assessment.query.all()
#     students = db.session.query(Student, Class.class_name).join(Class, Student.class_id == Class.id).all()
#     all_subjects = Subject.query.all()

#     # **Function to Get Scores List**
#     def get_scores_list():
#         all_scores = (
#             db.session.query(
#                 AssessmentSubjectScore.id,
#                 Assessment.name.label('assessment_name'),
#                 Subject.name.label('subject_name'),
#                 Student.first_name,
#                 Student.last_name,
#                 Class.class_name,
#                 AssessmentSubjectScore.total_marks
#             )
#             .join(Assessment, AssessmentSubjectScore.assessment_id == Assessment.id)
#             .join(Subject, AssessmentSubjectScore.subject_id == Subject.id)
#             .join(Student, AssessmentSubjectScore.student_id == Student.id)
#             .join(Class, Student.class_id == Class.id)
#             .all()
#         )

#         return [
#             {
#                 'id': score.id,
#                 'assessment_name': score.assessment_name if score.assessment_name else "Assessment Not Found",
#                 'subject_name': score.subject_name if score.subject_name else "Subject Not Found",
#                 'student_name': f"{score.first_name} {score.last_name}",
#                 'total_marks': score.total_marks
#             }
#             for score in all_scores
#         ]

#     # **Function to Get Class-Subject Map**
#     def get_class_subject_map():
#         class_subjects = db.session.query(ClassSubject.class_id, Subject.id, Subject.name) \
#                                    .join(Subject, ClassSubject.subject_id == Subject.id).all()

#         class_subject_map = {}
#         for class_id, subject_id, subject_name in class_subjects:
#             if class_id not in class_subject_map:
#                 class_subject_map[class_id] = []
#             class_subject_map[class_id].append({'id': subject_id, 'name': subject_name})

#         return class_subject_map

#     if request.method == 'GET':
#         scores_list = get_scores_list()
#         students_list = [{'id': student.id, 'name': f"{student.first_name} {student.last_name}", 'class_name': class_name, 'class_id': student.class_id} for student, class_name in students]
#         student_class_subject_map = get_class_subject_map()

#         return render_template(
#             'assessment_subject_scores.html',
#             scores=scores_list,
#             assessments=assessments,
#             students=students_list,
#             subjects=all_subjects,
#             student_class_subject_map=student_class_subject_map
#         )

#     elif request.method == 'POST':
#         data = request.get_json()
        
#         if not data or 'assessment_id' not in data or 'student_id' not in data or 'subject_marks' not in data:
#             return jsonify({"error": "Missing required fields"}), 400
        
#         subject_marks = data.get('subject_marks', [])
#         for item in subject_marks:
#             if 'subject_id' not in item or 'total_marks' not in item:
#                 return jsonify({"error": "Invalid subject marks format"}), 400
            
#             new_score = AssessmentSubjectScore(
#                 assessment_id=data['assessment_id'],
#                 subject_id=item['subject_id'],
#                 student_id=data['student_id'],
#                 total_marks=item['total_marks']
#             )
#             db.session.add(new_score)
        
#         db.session.commit()
        
#         scores_list = get_scores_list()
#         students_list = [{'id': student.id, 'name': f"{student.first_name} {student.last_name}", 'class_name': class_name, 'class_id': student.class_id} for student, class_name in students]
#         student_class_subject_map = get_class_subject_map()

#         return render_template(
#             'assessment_subject_scores.html',
#             scores=scores_list,
#             assessments=assessments,
#             students=students_list,
#             subjects=all_subjects,
#             student_class_subject_map=student_class_subject_map
#         )

# @main.route('/scores/<int:id>', methods=['GET', 'PUT', 'DELETE'])
# def score(id):
#     score = AssessmentSubjectScore.query.get_or_404(id)
#     if request.method == 'GET':
#         return jsonify({
#             'id': score.id,
#             'assessment_id': score.assessment_id,
#             'subject_id': score.subject_id,
#             'student_id': score.student_id,
#             'total_marks': score.total_marks
#         })
#     elif request.method == 'PUT':
#         data = request.get_json()
#         score.assessment_id = data['assessment_id']
#         score.subject_id = data['subject_id']
#         score.student_id = data['student_id']
#         score.total_marks = data['total_marks']
#         db.session.commit()
#         return jsonify({'message': 'Score updated'})
#     elif request.method == 'DELETE':
#         db.session.delete(score)
#         db.session.commit()
#         return jsonify({'message': 'Score deleted'})


# @main.route('/scores/<int:id>', methods=['GET', 'PUT', 'DELETE'])
# def score(id):
#     score = AssessmentSubjectScore.query.get_or_404(id)
#     if request.method == 'GET':
#         return jsonify({
#             'id': score.id,
#             'assessment_id': score.assessment_id,
#             'subject_id': score.subject_id,
#             'student_id': score.student_id,
#             'total_marks': score.total_marks
#         })
#     elif request.method == 'PUT':
#         data = request.get_json()
#         score.assessment_id = data['assessment_id']
#         score.subject_id = data['subject_id']
#         score.student_id = data['student_id']
#         score.total_marks = data['total_marks']
#         db.session.commit()
#         return jsonify({'message': 'Score updated'})
#     elif request.method == 'DELETE':
#         db.session.delete(score)
#         db.session.commit()
#         return jsonify({'message': 'Score deleted'})
        




# @main.route('/add_assessment_score', methods=['GET', 'POST'])
# @login_required
# def add_assessment_score():
#     if not current_user.school_id:
#         flash("You are not linked to any school.", "danger")
#         return redirect(url_for('main.index'))

#     school_id = current_user.school_id

#     if request.method == 'POST':
#         try:
#             # Fetch the data from the form
#             academic_session = request.form.get('academic_session')
#             assessment_id = int(request.form.get('assessment_id'))
#             student_id = int(request.form.get('student_id'))
#             class_id = int(request.form.get('class_id'))

#             # Get the list of selected subjects (only subjects with checked checkboxes)
#             selected_subject_ids = request.form.getlist('selected_subjects')

#             # Ensure the assessment and student belong to the logged-in user's school
#             assessment = Assessment.query.filter_by(id=assessment_id, school_id=school_id).first()
#             student = Student.query.filter_by(id=student_id, school_id=school_id).first()

#             if not assessment or not student:
#                 flash("Invalid selection. Please choose valid records from your school.", "danger")
#                 return redirect(url_for('main.add_assessment_score'))

#             # Loop through the selected subjects and collect scores
#             for subject_id in selected_subject_ids:
#                 score_key = f"score_{subject_id}"
#                 score_value = request.form.get(score_key)

#                 if score_value:
#                     try:
#                         total_marks = int(score_value)

#                         # Ensure the subject belongs to the school
#                         subject = Subject.query.filter_by(id=int(subject_id), school_id=school_id).first()
#                         if not subject:
#                             flash(f"Invalid subject selection: {subject_id}.", "danger")
#                             continue

#                         # Add score entry to the database
#                         new_score = AssessmentSubjectScore(
#                             assessment_id=assessment_id,
#                             subject_id=int(subject_id),
#                             student_id=student_id,
#                             total_marks=total_marks
#                         )
#                         db.session.add(new_score)

#                     except ValueError:
#                         flash(f"Invalid score for subject ID {subject_id}.", "danger")
#                         continue

#             db.session.commit()
#             flash("Assessment scores added successfully!", "success")
#             return redirect(url_for('main.assessment_subject_scores'))

#         except Exception as e:
#             db.session.rollback()
#             flash(f"Error adding assessment scores: {e}", "danger")
#             return redirect(url_for('main.add_assessment_score'))

#     # Fetch only data belonging to the logged-in user's school
#     academic_sessions = list(set(assessment.academic_session for assessment in Assessment.query.filter_by(school_id=school_id).all()))
#     assessments = Assessment.query.filter_by(school_id=school_id).all()
#     subjects = Subject.query.filter_by(school_id=school_id).all()
#     students = Student.query.filter_by(school_id=school_id).all()
#     classes = Class.query.filter_by(school_id=school_id).all()

#     return render_template(
#         'add_assessment_subject_score.html',
#         academic_sessions=academic_sessions,
#         assessments=assessments,
#         subjects=subjects,
#         students=students,
#         classes=classes
#     )

@main.route('/add_assessment_score', methods=['GET', 'POST'])
@login_required
# @admin_required
def add_assessment_score():
    if not current_user.school_id:
        flash("You are not linked to any school.", "danger")
        return redirect(url_for('main.index'))

    school_id = current_user.school_id

    if request.method == 'POST':
        try:
            # Fetch the data from the form
            academic_session = request.form.get('academic_session')
            assessment_id = int(request.form.get('assessment_id'))
            student_id = int(request.form.get('student_id'))
            class_id = int(request.form.get('class_id'))

            # Get the list of selected subjects (only subjects with checked checkboxes)
            selected_subject_ids = request.form.getlist('selected_subjects')

            # Ensure the assessment and student belong to the logged-in user's school
            assessment = Assessment.query.filter_by(id=assessment_id, school_id=school_id).first()
            student = Student.query.filter_by(id=student_id, school_id=school_id).first()

            if not assessment or not student:
                flash("Invalid selection. Please choose valid records from your school.", "danger")
                return redirect(url_for('main.add_assessment_score'))

            #Authorization check
            if current_user.role == 'teacher':
                teacher = Teacher.query.filter_by(id=current_user.teacher_id).first()
                if not teacher:
                    flash("Teacher not found.", "danger")
                    return redirect(url_for('main.index'))

                teacher_classes = [c.id for c in teacher.classes]

                if student.class_id not in teacher_classes:
                    flash("You are not authorized to record assessment scores for this student.", "danger")
                    return redirect(url_for('main.add_assessment_score'))

            # Loop through the selected subjects and collect scores
            for subject_id in selected_subject_ids:
                score_key = f"score_{subject_id}"
                score_value = request.form.get(score_key)

                if score_value:
                    try:
                        total_marks = int(score_value)

                        # Ensure the subject belongs to the school
                        # subject = ClassSubject.query.filter_by(id=int(subject_id), school_id=school_id).first()
                        subject = ClassSubject.query.join(Class).filter(Class.school_id == school_id).options(joinedload(ClassSubject.subject)).all()

                        if not subject:
                            flash(f"Invalid subject selection: {subject_id}.", "danger")
                            continue

                        # Add score entry to the database
                        new_score = AssessmentSubjectScore(
                            assessment_id=assessment_id,
                            subject_id=int(subject_id),
                            student_id=student_id,
                            total_marks=total_marks
                        )
                        db.session.add(new_score)

                    except ValueError:
                        flash(f"Invalid score for subject ID {subject_id}.", "danger")
                        continue

            db.session.commit()
            flash("Assessment scores added successfully!", "success")
            return redirect(url_for('main.assessment_subject_scores'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding assessment scores: {e}", "danger")
            return redirect(url_for('main.add_assessment_score'))

    # Fetch only data belonging to the logged-in user's school
    academic_sessions = list(set(assessment.academic_session for assessment in Assessment.query.filter_by(school_id=school_id).all()))
    assessments = Assessment.query.filter_by(school_id=school_id).all()
    subjects = Subject.query.filter_by(school_id=school_id).all()
    classes = Class.query.filter_by(school_id=school_id).all()
    class_subjects = ClassSubject.query.join(Class).filter(Class.school_id == school_id).options(joinedload(ClassSubject.subject)).all()


    #Filter students based on role.
    if current_user.role == 'teacher':
        teacher = Teacher.query.filter_by(id=current_user.teacher_id).first()
        teacher_classes = [c.id for c in teacher.classes]
        students = Student.query.filter(Student.school_id == school_id, Student.class_id.in_(teacher_classes)).all()
    else:
        students = Student.query.filter_by(school_id=school_id).all()

    return render_template(
        'add_assessment_subject_score.html',
        academic_sessions=academic_sessions,
        assessments=assessments,
        subjects=subjects,
        students=students,
        classes=classes,
        class_subjects=class_subjects
    )

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
@login_required
@admin_required
def fee_components():
    # Ensure the user is linked to a school
    if not current_user.school_id:
        flash("No school linked to your account.", "danger")
        return redirect(url_for('main.index'))

    school_id = current_user.school_id  # Get logged-in user's school

    # Fetch only fee components related to the user's school
    components = FeeComponent.query.filter_by(school_id=school_id).all()

    return render_template('fee_components.html', components=components)

<<<<<<< HEAD
# calculate score grade of students
def calculate_grade(total_score):
    if 70 <= total_score <= 100:
        return 'A', 'Excellent'
    elif 60 <= total_score < 70:
        return 'B', 'Very Good'
    elif 50 <= total_score < 60:
        return 'C', 'Good'
    elif 45 <= total_score < 50:
        return 'D', 'Pass'
    else:
        return 'E', 'Weak'

=======
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a

# Load fee components from the JSON file
with open("fee_components.json", "r") as file:
    fee_components_from_json = json.load(file)


<<<<<<< HEAD
#     heading_style = ParagraphStyle('Heading', parent=styles['h2'])
#     heading_style.alignment = 1

#     normal_style = ParagraphStyle('Normal', parent=styles['Normal'])
#     normal_style.alignment = 0

#     # Retrieve logo path from DB
#     logo_path = student.get("school_logo")
#     # logo_path = student.school_logo
#     background_logo_path = None
=======
@main.route('/add_fee_component', methods=['GET', 'POST'])
@login_required
@admin_required
def add_fee_component():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        academic_year = request.form['academic_year']
        term = request.form['term']
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a

        # Use current_user to get the logged-in user's school
        school_id = current_user.school_id

        component = FeeComponent(
            name=name,
            description=description,
            school_id=school_id,
            academic_year=academic_year,
            term=term
        )
        db.session.add(component)
        db.session.commit()
        flash('Fee component added successfully!', 'success')
        return redirect(url_for('main.fee_components'))

    # Filter schools based on the logged-in user
    schools = School.query.filter_by(id=current_user.school_id).all()
    return render_template('add_fee_component.html', schools=schools)


@main.route('/add_fee_component_to_class', methods=['GET', 'POST'])
@login_required
@admin_required
def add_fee_component_to_class():
    school = School.query.filter_by(id=current_user.school_id).first()

    if not school:
        flash("No school assigned to your account.", "danger")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        selected_classes = request.form.getlist('selected_classes')
        selected_components = request.form.getlist('selected_components')
        academic_year = request.form['academic_year']
        term = request.form['term']

        for class_id in selected_classes:
            for component_id in selected_components:
                amount_field = f"amount_{component_id}"
                if amount_field in request.form and request.form[amount_field]:
                    amount = float(request.form[amount_field])

                    class_obj = Class.query.get(class_id)
                    if class_obj and class_obj.school_id == current_user.school_id:
                        component = FeeComponent.query.get(component_id)
                        if component and component.school_id == current_user.school_id:

                            existing_class_fee = ClassFeeComponent.query.join(FeeComponent).filter(
                                ClassFeeComponent.class_id == class_id,
                                FeeComponent.id == component_id,
                                FeeComponent.academic_year == academic_year,
                                FeeComponent.term == term,
                                FeeComponent.school_id == current_user.school_id
                            ).first()

                            if existing_class_fee:
                                # Update existing ClassFeeComponent
                                existing_class_fee.amount = amount
                            else:
                                # Create a *new* ClassFeeComponent for the class and existing FeeComponent
                                class_fee_component = ClassFeeComponent(
                                    class_id=int(class_id),
                                    component_id=int(component_id),
                                    amount=amount
                                )
                                db.session.add(class_fee_component)

                        else:
                            flash(f"Error: Fee component with ID {component_id} not found or doesn't belong to your school.", 'danger')
                            return redirect(url_for('main.add_fee_component_to_class'))
                    else:
                        flash(f"Error: Class with ID {class_id} does not belong to your school.", 'danger')
                        return redirect(url_for('main.add_fee_component_to_class'))

        db.session.commit()
        flash('Fee components added/updated successfully!', 'success')
        return redirect(url_for('main.generate_fees'))
    
    academic_years = [
        year.academic_year
        for year in db.session.query(FeeComponent.academic_year).filter_by(school_id=current_user.school_id).distinct().all()
    ]


    classes = Class.query.filter_by(school_id=school.id).all()
    components = FeeComponent.query.filter_by(school_id=school.id).all()
    return render_template('add_fee_component_to_class.html', classes=classes, components=components, academic_years=academic_years)


@main.route('/edit_fee_component/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_fee_component(id):
    component = FeeComponent.query.get_or_404(id)

    if component.school_id != current_user.school_id:
        flash("You don't have permission to edit this fee component.", "danger")
        return redirect(url_for('main.fee_components'))

    if request.method == 'POST':
        component.name = request.form['name']
        component.description = request.form['description']
        db.session.commit()
        flash('Fee component updated successfully!', 'success')
        return redirect(url_for('main.fee_components'))

    schools = School.query.filter_by(id=current_user.school_id).all()
    return render_template('edit_fee_component.html', component=component, schools=schools)


@main.route('/delete_fee_component/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_fee_component(id):
    component = FeeComponent.query.get_or_404(id)
    if component.school_id != current_user.school_id:
        flash("You don't have permission to delete this fee component.", "danger")
        return redirect(url_for('main.fee_components'))
    db.session.delete(component)
    db.session.commit()
    flash('Fee component deleted successfully!', 'success')
    return redirect(url_for('main.fee_components'))


@main.route('/view_class_fees', methods=['GET'])
@login_required
def view_class_fees():
    class_id = request.args.get('class_id')
    academic_year = request.args.get('academic_year')
    term = request.args.get('term')

    classes = Class.query.filter_by(school_id=current_user.school_id).all()
    selected_class = None
    fees = None

    if class_id and academic_year and term:
        class_id = int(class_id)
        selected_class = Class.query.get(class_id)

        if selected_class and selected_class.school_id == current_user.school_id:
            fees = ClassFeeComponent.query.join(FeeComponent).filter(
                ClassFeeComponent.class_id == class_id,
                FeeComponent.school_id == current_user.school_id,
                FeeComponent.academic_year == academic_year,
                FeeComponent.term == term
            ).all()

        else:
            flash("Invalid class selection.", "danger")
            return redirect(url_for('main.view_fees'))

    academic_years = [
        year.academic_year
        for year in db.session.query(FeeComponent.academic_year).filter_by(school_id=current_user.school_id).distinct().all()
    ]
    return render_template('view_fees.html',
                           classes=classes,
                           fees=fees,
                           selected_class=selected_class,
                           selected_class_id=class_id,
                           selected_academic_year=academic_year,
                           selected_term=term,
                           academic_years=academic_years)


@main.route('/generate_class_fees_pdf', methods=['GET'])
@login_required
def generate_class_fees_pdf():
    class_id = request.args.get('class_id')
    academic_year = request.args.get('academic_year')
    term = request.args.get('term')

    if not class_id or not academic_year or not term:
        flash("Please select Class, Academic Year, and Term.", "danger")
        return redirect(url_for('main.generate_class_fees'))

    try:
        school = School.query.filter_by(id=current_user.school_id).first()

        if not school:
            return "School information not found", 404

        school_name = school.name
        school_address = school.address

        classes = Class.query.filter_by(school_id=school.id, id=class_id).all()

        if not classes:
            flash("Class not found or does not belong to your school.", "danger")
            return redirect(url_for('main.generate_class_fees'))

        class_fees = []
        for cls in classes:
            fee_components = ClassFeeComponent.query.join(FeeComponent).filter(
                ClassFeeComponent.class_id == cls.id,
                FeeComponent.school_id == current_user.school_id,
                FeeComponent.academic_year == academic_year,
                FeeComponent.term == term
            ).all()

            total_fee = sum(comp.amount for comp in fee_components)
            class_fees.append({
                "class_name": cls.class_name,
                "total_fee": total_fee,
                "fee_breakdown": [(comp.fee_component.name, comp.amount) for comp in fee_components]
            })

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        elements.append(Table(
            [[school_name], [school_address], [academic_year]],
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]),
            colWidths=[500]
        ))

        elements.append(Table([[" "]]))

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

        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="class_fees.pdf", mimetype='application/pdf')

    except Exception as e:
        print(f"Error generating PDF: {e}")
        flash(f"An error occurred while generating the PDF: {e}", "danger")
        return redirect(url_for('main.generate_class_fees'))
    


@main.route('/generate_fees', methods=['GET'])
@login_required
def generate_fees():
    # Fetch the logged-in user's school
    school = School.query.filter_by(id=current_user.school_id).first()

    if not school:
        flash("No school assigned to your account.", "danger")
        return redirect(url_for('main.index'))

    classes = Class.query.filter_by(school_id=school.id).all()

    # Fetch distinct academic years from ClassFeeComponent, filtered by school
    academic_years = [
        year.academic_year
        for year in db.session.query(FeeComponent.academic_year).filter_by(school_id=current_user.school_id).distinct().all()
    ]

    return render_template(
        'generate_fees.html',
        school=school,
        classes=classes,
        academic_years=academic_years
    )
    

@main.route('/generate_class_fees', methods=['GET'])
@login_required
def generate_class_fees():
    classes = Class.query.filter_by(school_id=current_user.school_id).all()
    return render_template('generate_class_fees.html',
                           selected_academic_year=request.args.get('academic_year'),
                           selected_term=request.args.get('term'),
                           selected_class_id=request.args.get('class_id'),
                           classes = classes
                           )


@main.route('/class_fee_components', methods=['GET'])
@login_required
def display_class_fee_components():
    """Fetch all records from ClassFeeComponent"""
    class_fee_components = ClassFeeComponent.query.all()

    # Group fees by class
    grouped_fees = defaultdict(list)
    for component in class_fee_components:
        grouped_fees[component.class__.class_name].append(component)

    return render_template(
        'class_fee_components.html', 
        grouped_fees=grouped_fees
    )

@main.route('/remove_fee_component_from_class/<int:class_fee_component_id>', methods=['POST'])
@login_required
@admin_required
def remove_fee_component_from_class(class_fee_component_id):
    class_fee_component = ClassFeeComponent.query.get_or_404(class_fee_component_id)
    class_id = class_fee_component.class_id
    db.session.delete(class_fee_component)
    db.session.commit()
    flash('Fee component removed from class successfully!', 'success')
    return redirect(url_for('main.view_class_fees', class_id=class_id))

"""
DO NOT DELETE
This is a placeholder for the record_payment function."""

@main.route('/record_payment', methods=['GET', 'POST'])
@login_required
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



file_directory = "static/results"
os.makedirs(file_directory, exist_ok=True)
if not os.path.exists(file_directory):
    os.makedirs(file_directory)

# Students results generation and management

# calculate score grade of students
def calculate_grade(total_score):
    if 70 <= total_score <= 100:
        return 'A', 'Excellent'
    elif 60 <= total_score < 70:
        return 'B', 'Very Good'
    elif 50 <= total_score < 60:
        return 'C', 'Good'
    elif 45 <= total_score < 50:
        return 'D', 'Pass'
    else:
        return 'E', 'Weak'
    
# def calculate_overall_grade(grand_total, num_subjects):
#     average = grand_total / num_subjects if num_subjects > 0 else 0
#     if average >= 70:
#         return "A"
#     elif 60 <= average < 70:
#         return "B"
#     elif 50 <= average < 60:
#         return "C"
#     elif 45 <= average < 50:
#         return "D"
#     else:
#         return "E"
    
"""
DO NOT DELETE
"""
# Route for creating the result sheet
# def create_student_result_pdf(student):
#     buffer = BytesIO()
#     pdf = SimpleDocTemplate(buffer, pagesize=A4)
#     styles = getSampleStyleSheet()
#     width, height = A4
#     elements = []

#     # --- Improved Styling ---
#     # Create some custom paragraph styles for better control
#     title_style = ParagraphStyle('Title', parent=styles['h1'])
#     title_style.alignment = 1
#     title_style.textColor = colors.red

#     heading_style = ParagraphStyle('Heading', parent=styles['h2'])
#     heading_style.alignment = 1
    
#     normal_style = ParagraphStyle('Normal', parent=styles['Normal'])
#     normal_style.alignment = 0
    
#     # Retrieve logo path from DB
#     logo_path = student.get("school_logo")
#     # logo_path = student.school_logo
#     background_logo_path = None

#     if logo_path:
#         if not logo_path.startswith("uploads/"):
#             logo_path = f"uploads/{os.path.basename(logo_path)}"

#         BASE_STATIC_DIR = os.path.join(os.getcwd(), "static")
#         full_logo_path = os.path.join(BASE_STATIC_DIR, logo_path)
#         full_logo_path = os.path.abspath(full_logo_path)

#         # Use logo as page background image for the result sheet
#         if os.path.exists(full_logo_path):
#             background_logo_path = full_logo_path
#             img = Image(full_logo_path, width=75, height=75, kind='proportional')
#             elements.append(img)
#         else:
#             print(f"Logo file not found: {full_logo_path}")
#             elements.append(Paragraph("School Logo Not Found", styles['Normal']))

#     elements.append(Paragraph(student['school_name'], title_style))
#     elements.append(Paragraph(student['school_address'], heading_style))
#     elements.append(Paragraph("INDIVIDUAL STUDENT'S ASSESSMENT SHEET", heading_style))
#     elements.append(Paragraph("JUNIOR SECONDARY SCHOOL", heading_style))

#     # Student Details Table
#     student_details_data = [
#         ["RESULT ID:", student['result_id'], "SEX:", student['sex'], "TERM:", student['term']],
#         ["NAME OF STUDENT:", student['name'], "SESSION:", student['session'], "CLASS:", student['class_name']],
#         [
#             Paragraph("NO. OF TIMES<br/>PRESENT", styles['Normal']),
#             student['times_present'],
#             Paragraph("NO. OF TIMES<br/>SCHOOL OPENED", styles['Normal']),
#             student['times_opened'], "POSITION:", student['class_name']
#         ],
#     ]
#     student_details_table = Table(student_details_data, colWidths=[120, 130, 60, 60, 80, 80])
#     student_details_table.setStyle(TableStyle([
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
#         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#     ]))
#     elements.append(student_details_table)
#     elements.append(Spacer(1, 0.1*inch))  # Add space *after* student details table


#     # Subject Data and Table
#     subject_data = []
#     grand_total = 0
#     passes = 0
#     for subject in student['subjects']:
#         total_score = subject.get('CA1', 0) + subject.get('CA2', 0) + subject.get('EXAMINATION', 0)
#         grade, remark = calculate_grade(total_score)
#         grand_total += total_score
#         if grade in ['A', 'B', 'C']:
#             passes += 1
#         subject_data.append([subject['name'],
#                             subject.get('CA1', 0),
#                             subject.get('CA2', 0),
#                             subject.get('EXAMINATION', 0),
#                             total_score, grade, remark])

#     overall_grade = calculate_grade(grand_total / len(student['subjects'])) if student['subjects'] else ("N/A", "N/A")

#     student['overall_grade'] = overall_grade[0]

<<<<<<< HEAD
        component = FeeComponent(
            name=name,
            description=description,
            school_id=school_id,
            academic_year=academic_year,
            term=term
        )
        db.session.add(component)
        db.session.commit()
        flash('Fee component added successfully!', 'success')
        return redirect(url_for('main.fee_components'))

    # Filter schools based on the logged-in user
    schools = School.query.filter_by(id=current_user.school_id).all() # Only show the logged in user's school
    return render_template('add_fee_component.html', schools=schools)


@main.route('/add_fee_component_to_class', methods=['GET', 'POST'])
@login_required
def add_fee_component_to_class():
    school = School.query.filter_by(id=current_user.school_id).first()

    if not school:
        flash("No school assigned to your account.", "danger")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        selected_classes = request.form.getlist('selected_classes')
        selected_components = request.form.getlist('selected_components')
        academic_year = request.form['academic_year']
        term = request.form['term']

        for class_id in selected_classes:
            for component_id in selected_components:
                amount_field = f"amount_{component_id}"
                if amount_field in request.form and request.form[amount_field]:
                    amount = float(request.form[amount_field])

                    class_obj = Class.query.get(class_id)
                    if class_obj and class_obj.school_id == current_user.school_id:
                        component = FeeComponent.query.get(component_id)
                        if component and component.school_id == current_user.school_id:

                            existing_class_fee = ClassFeeComponent.query.join(FeeComponent).filter(
                                ClassFeeComponent.class_id == class_id,
                                FeeComponent.id == component_id,
                                FeeComponent.academic_year == academic_year,
                                FeeComponent.term == term,
                                FeeComponent.school_id == current_user.school_id
                            ).first()

                            if existing_class_fee:
                                # Update existing ClassFeeComponent
                                existing_class_fee.amount = amount
                            else:
                                # Create a *new* ClassFeeComponent for the class and existing FeeComponent
                                class_fee_component = ClassFeeComponent(
                                    class_id=int(class_id),
                                    component_id=int(component_id),  # Use existing component ID
                                    amount=amount
                                )
                                db.session.add(class_fee_component)  # Add the NEW ClassFeeComponent

                        else:
                            flash(f"Error: Fee component with ID {component_id} not found or doesn't belong to your school.", 'danger')
                            return redirect(url_for('main.add_fee_component_to_class'))
                    else:
                        flash(f"Error: Class with ID {class_id} does not belong to your school.", 'danger')
                        return redirect(url_for('main.add_fee_component_to_class'))

        db.session.commit()
        flash('Fee components added/updated successfully!', 'success')
        return redirect(url_for('main.generate_fees'))

    # GET request handling (same as before)
    academic_years = [
        year.academic_year
        for year in db.session.query(FeeComponent.academic_year).filter_by(school_id=current_user.school_id).distinct().all()
    ]


    classes = Class.query.filter_by(school_id=school.id).all()
    components = FeeComponent.query.filter_by(school_id=school.id).all()
    return render_template('add_fee_component_to_class.html', classes=classes, components=components, academic_years=academic_years)


@main.route('/edit_fee_component/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_fee_component(id):
    component = FeeComponent.query.get_or_404(id)

    # Make sure the component belongs to the logged-in user's school
    if component.school_id != current_user.school_id:
        flash("You don't have permission to edit this fee component.", "danger")
        return redirect(url_for('main.fee_components'))

    if request.method == 'POST':
        component.name = request.form['name']
        component.description = request.form['description']
        # School_id is not changeable after component creation.
        db.session.commit()
        flash('Fee component updated successfully!', 'success')
        return redirect(url_for('main.fee_components'))

    schools = School.query.filter_by(id=current_user.school_id).all()
    return render_template('edit_fee_component.html', component=component, schools=schools)


@main.route('/delete_fee_component/<int:id>', methods=['POST'])
@login_required
def delete_fee_component(id):
    component = FeeComponent.query.get_or_404(id)
    if component.school_id != current_user.school_id:
        flash("You don't have permission to delete this fee component.", "danger")
        return redirect(url_for('main.fee_components'))
    db.session.delete(component)
    db.session.commit()
    flash('Fee component deleted successfully!', 'success')
    return redirect(url_for('main.fee_components'))


@main.route('/view_class_fees', methods=['GET'])
@login_required
def view_class_fees():
    class_id = request.args.get('class_id')
    academic_year = request.args.get('academic_year')
    term = request.args.get('term')

    classes = Class.query.filter_by(school_id=current_user.school_id).all()
    selected_class = None
    fees = None

    if class_id and academic_year and term:
        class_id = int(class_id)
        selected_class = Class.query.get(class_id)

        if selected_class and selected_class.school_id == current_user.school_id:
            fees = ClassFeeComponent.query.join(FeeComponent).filter(
                ClassFeeComponent.class_id == class_id,
                FeeComponent.school_id == current_user.school_id,
                FeeComponent.academic_year == academic_year, # Filter by academic year
                FeeComponent.term == term # Filter by term
            ).all()

        else:
            flash("Invalid class selection.", "danger")
            return redirect(url_for('main.view_fees'))

    academic_years = [
        year.academic_year
        for year in db.session.query(FeeComponent.academic_year).filter_by(school_id=current_user.school_id).distinct().all()
    ]
    return render_template('view_fees.html',
                           classes=classes,
                           fees=fees,
                           selected_class=selected_class,
                           selected_class_id=class_id,
                           selected_academic_year=academic_year,
                           selected_term=term,
                           academic_years=academic_years)


@main.route('/generate_class_fees_pdf', methods=['GET'])
@login_required
def generate_class_fees_pdf():
    class_id = request.args.get('class_id')
    academic_year = request.args.get('academic_year')
    term = request.args.get('term')

    if not class_id or not academic_year or not term:
        flash("Please select Class, Academic Year, and Term.", "danger")
        return redirect(url_for('main.generate_class_fees'))

    try:  # Add a try-except block for debugging
        school = School.query.filter_by(id=current_user.school_id).first()
=======
#     header_row_1 = [
#         "SUBJECT",
#         Paragraph("CONTINUOUS ASSESSMENT", styles["h3"]),
#         Spacer(1, 1), Spacer(1, 1), Spacer(1, 1),
#         Paragraph("TERM SUMMARY", styles["h3"]),
#         Spacer(1, 1),
#     ]
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a

#     header_row_2 = ["SUBJECT", "CA1", "CA2", "EXAMINATION", "TOTAL", "GRADE", "REMARK"]
#     full_subject_data = [header_row_1, header_row_2] + subject_data

#     subject_table = Table(full_subject_data, colWidths=[150, 50, 50, 80, 50, 50, 100])
#     subject_table.setStyle(TableStyle([
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('ALIGN', (0, 0), (0, -1), 'LEFT'),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         # ('BACKGROUND', (1, 2), (4, -1), colors.beige),
#         # ('BACKGROUND', (5, 2), (6, -1), colors.beige),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BACKGROUND', (1, 0), (4, 0), colors.lightgrey),
#         ('BACKGROUND', (5, 0), (6, 0), colors.lightgrey),
#         ('SPAN', (1, 0), (4, 0)),
#         ('SPAN', (5, 0), (6, 0)),
#         ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),

#     ]))

#     elements.append(subject_table)  # Add to elements list
#     elements.append(Spacer(1, 0.1*inch))  # Add space *after* subject table


#     # Summary and Grading Key Tables
#     term_average = grand_total / len(student['subjects']) if student['subjects'] else 0

#     summary_data = [
#         ["Term Grand Total:", str(grand_total)],
#         ["Term Average:", f"{term_average:.2f}"],
#         ["Number of Subject Passes:", str(passes)],
#         ["Overall Grade:", student.get("overall_grade", "N/A")],
#     ]
#     summary_table = Table(summary_data, colWidths=[150, 80])
#     summary_table.setStyle(TableStyle([
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#     ]))

#     grading_key_data = [
#         ["Figures", "Grade", "Remark"],
#         ["70 - 100", "A", "Excellent"],
#         ["60 - 69", "B", "Very Good"],
#         ["50 - 59", "C", "Good"],
#         ["45 - 49", "D", "Pass"],
#         ["0 - 44", "E", "Weak"],
#     ]

#     grading_key_table = Table(grading_key_data, colWidths=[80, 60, 80])
#     grading_key_table.setStyle(TableStyle([
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#     ]))


#     # --- Positioning the tables using Spacer and nested tables ---
#     # Create a nested table to hold summary and grading key side-by-side
#     nested_table_data = [[summary_table, grading_key_table]]
#     nested_table = Table(nested_table_data, colWidths=[250, 250]) # Adjust colWidths as needed
#     nested_table.setStyle(TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center the nested tables
#         ('VALIGN', (0, 0), (-1, -1), 'TOP'),    # Align tables to the top
#     ]))

#     # elements.append(Spacer(20, 1*inch))  # Add some space before the tables
#     elements.append(nested_table) # add the nested table
#     elements.append(Spacer(1, 0.5*inch))  # Add space after tables


<<<<<<< HEAD
    except Exception as e:
        print(f"Error generating PDF: {e}")
        flash(f"An error occurred while generating the PDF: {e}", "danger")
        return redirect(url_for('main.generate_class_fees'))

=======
#     # --- Remarks and Signature ---
#     elements.append(Paragraph("Class Teacher Remark: __________________________", styles['Normal']))
#     elements.append(Paragraph("Principal Remark: __________________________", styles['Normal']))
#     elements.append(Spacer(1, 0.5*inch))  # Add space before the signature
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a



#     # Create a centered style (or modify an existing one)
#     centered_style = ParagraphStyle('Centered', parent=styles['Normal'])  # Inherit from Normal
#     centered_style.alignment = TA_CENTER

#     signature_text = "____________________________"  # Or get it dynamically
#     signature_line = "PRINCIPAL'S SIGNATURE"  # Or get it dynamically

#     elements.append(Paragraph(signature_text, centered_style))  # Use the centered style
#     elements.append(Spacer(1, 0.1*inch))
#     elements.append(Paragraph(signature_line, centered_style))  # Use the centered style

<<<<<<< HEAD
    return render_template(
        'generate_fees.html',
        school=school,
        classes=classes,
        academic_years=academic_years
    )

=======
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a

#     # Build PDF with background image
#     def add_background(canvas, doc):
#         if background_logo_path:
#             bg_image = ImageReader(background_logo_path)
#             canvas.setFillAlpha(0.2)  # Set transparency
#             canvas.drawImage(bg_image, 100, 200, width=400, height=400, preserveAspectRatio=True, mask='auto')
#             canvas.setFillAlpha(1)  # Reset transparency

#     pdf.build(elements, onFirstPage=add_background, onLaterPages=add_background)
#     buffer.seek(0)

#     return buffer


# @main.route('/download_result_sheet/<int:student_id>')
# def download_result_sheet(student_id):
#     try:
#         student_record = Student.query.filter_by(id=student_id, school_id=current_user.school_id).first()  # Filter by school
#         if not student_record:
#             return jsonify({"error": "Student not found or does not belong to your school"}), 404

#         school_record = School.query.filter_by(id=student_record.school_id).first()  # No change needed here, already filtered above
#         if not school_record:
#             return jsonify({"error": "School not found"}), 404

#         # Get class subjects for the student's class and the current school
#         class_subjects = ClassSubject.query.filter_by(class_id=student_record.class_id).all()
#         subjects = [cs.subject for cs in class_subjects if cs.subject.school_id == current_user.school_id]

<<<<<<< HEAD
    # Render the template and pass the grouped data
    return render_template(
        'class_fee_components.html',
        grouped_fees=grouped_fees
    )

# @main.route('/view_class_fees/<int:class_id>')
# def view_class_fees(class_id):
#     # Fetch the specific class by its ID
#     selected_class = Class.query.get_or_404(class_id)


#     class_fee_components = ClassFeeComponent.query.filter_by(class_id=class_id).all()
#     return render_template('view_class_fees.html', selected_class=selected_class, class_fee_components=class_fee_components)
=======

#         if not subjects:
#             return jsonify({"error": "No subjects found for this class in your school."}), 404
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a

#         assessments = Assessment.query.filter_by(class_id=student_record.class_id, school_id=current_user.school_id).all() # Filter by school

#         attendance_records = Attendance.query.filter_by(student_id=student_id).all()

#         times_present = sum(1 for record in attendance_records if record.days_present == 'present')
#         times_opened = len(attendance_records)

#         subject_scores = {}
#         for subject in subjects: # Iterate through the actual subjects, not the subject_scores
#             subject_name = subject.name
#             subject_scores[subject_name] = {'CA1': 0, 'CA2': 0, 'EXAMINATION': 0}

#             for assessment in assessments:
#                 # Find the corresponding SubjectScore for this assessment and subject
#                 subject_score = AssessmentSubjectScore.query.filter_by(
#                     assessment_id=assessment.id,
#                     student_id=student_id,
#                     subject_id=subject.id # Add subject id to the query
#                 ).first()

#                 if subject_score:
#                     if 'CA1' in assessment.name:
#                         subject_scores[subject_name]['CA1'] = subject_score.total_marks
#                     elif 'CA2' in assessment.name:
#                         subject_scores[subject_name]['CA2'] = subject_score.total_marks
#                     elif 'EXAMINATION' in assessment.name:
#                         subject_scores[subject_name]['EXAMINATION'] = subject_score.total_marks

#         grand_total = sum(sum(scores.values()) for scores in subject_scores.values())

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
#                     "name": subject,
#                     "CA1": scores['CA1'],
#                     "CA2": scores['CA2'],
#                     "EXAMINATION": scores['EXAMINATION']
#                 }
#                 for subject, scores in subject_scores.items()
#             ],
#             "grand_total": grand_total,
#             "overall_grade": "A", # You'll need logic to calculate this
#             "next_term": "2023-09-01", # You'll need logic to determine this
#             "school_name": school_record.name,
#             "school_address": school_record.address,
#             "school_logo": school_record.school_logo
#         }

#         pdf_buffer = create_student_result_pdf(student)
#         return send_file(
#             pdf_buffer,
#             as_attachment=True,
#             download_name=f"{student['name']}_result.pdf",
#             mimetype='application/pdf'
#         )
#     except Exception as e:
#         print(f"Error in download_result_sheet: {e}") # Keep this for debugging
#         return jsonify({"error": str(e)}), 500

# @main.route('/download_result')
# def download_result_page():
#     return render_template('download_result.html')

"""
DO NOT DELETE ABOVE CODE
"""
def create_student_result_pdf(student_dict):
    """Generate a student result PDF using ReportLab and return the file path."""
<<<<<<< HEAD

    file_path = os.path.join(file_directory, f"result_{student_dict['name']}_{student_dict['result_id']}.pdf")
=======
    
    file_path = os.path.join(file_directory, f"result_{student_dict['name']}.pdf")
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        topMargin=0.2 * inch,
        bottomMargin=0.2 * inch
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Title'], alignment=1, textColor=colors.red)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], alignment=1)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], alignment=0)

    elements = []

    # Retrieve logo path from DB
    logo_path = student_dict.get("school_logo")
    background_logo_path = None

    if logo_path:
        if not logo_path.startswith("uploads/"):
            logo_path = f"uploads/{os.path.basename(logo_path)}"

        BASE_STATIC_DIR = os.path.join(os.getcwd(), "static")
        full_logo_path = os.path.join(BASE_STATIC_DIR, logo_path)
        full_logo_path = os.path.abspath(full_logo_path)

        # Use logo as page background image for the result sheet
        if os.path.exists(full_logo_path):
            background_logo_path = full_logo_path
            img = Image(full_logo_path, width=75, height=75, kind='proportional')
            elements.append(img)
        else:
            print(f"Logo file not found: {full_logo_path}")
            elements.append(Paragraph("School Logo Not Found", styles['Normal']))

    elements.append(Paragraph(student_dict['school_name'], title_style))
    elements.append(Paragraph(student_dict['school_address'], heading_style))
    elements.append(Paragraph("INDIVIDUAL STUDENT'S ASSESSMENT SHEET", heading_style))
    elements.append(Paragraph(student_dict['class_category'], heading_style))

    # Student Details Table
    student_details_data = [
        ["RESULT ID:", student_dict['result_id'], "SEX:", student_dict['sex'], "TERM:", student_dict['term']],
        ["NAME OF STUDENT:", student_dict['name'], "SESSION:", student_dict['session'], "CLASS:", student_dict['class_name']],
        [
            Paragraph("NO. OF TIMES<br/>PRESENT", styles['Normal']),
            student_dict['times_present'],
            Paragraph("NO. OF TIMES<br/>SCHOOL OPENED", styles['Normal']),
            student_dict['times_opened'], "POSITION:", student_dict['class_position']
        ],
    ]
    student_details_table = Table(student_details_data, colWidths=[120, 130, 60, 60, 80, 80])
    student_details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(student_details_table)
    elements.append(Spacer(1, 0.1*inch))


    # Subject Data and Table
    subject_data = []
    grand_total = 0
    passes = 0
    for subject in student_dict['subjects']:
        total_score = subject.get('CA1', 0) + subject.get('CA2', 0) + subject.get('EXAMINATION', 0)
        grade, remark = calculate_grade(total_score)
        grand_total += total_score
        if grade in ['A', 'B', 'C']:
            passes += 1
        subject_data.append([subject['name'],
                            subject.get('CA1', 0),
                            subject.get('CA2', 0),
                            subject.get('EXAMINATION', 0),
                            total_score, grade, remark])

    overall_grade = calculate_grade(grand_total / len(student_dict['subjects'])) if student_dict['subjects'] else ("N/A", "N/A")

    student_dict['overall_grade'] = overall_grade[0]

    header_row_1 = [
        "SUBJECT",
        Paragraph("CONTINUOUS ASSESSMENT", styles["h3"]),
        Spacer(1, 1), Spacer(1, 1), Spacer(1, 1),
        Paragraph("TERM SUMMARY", styles["h3"]),
        Spacer(1, 1),
    ]

    header_row_2 = ["SUBJECT", "CA1", "CA2", "EXAMINATION", "TOTAL", "GRADE", "REMARK"]
    header_row_3 = [" ", "20", "20", "60", "100", " ", " "]

    full_subject_data = [header_row_1, header_row_2, header_row_3] + subject_data

    subject_table = Table(full_subject_data, colWidths=[150, 50, 50, 80, 50, 50, 100])
    subject_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (7, 0), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (1, 0), (6, 0), colors.lightgrey),
        ('BACKGROUND', (1, 1), (4, 1), colors.lightgrey),
        ('SPAN', (1, 0), (4, 0)),
        ('SPAN', (5, 0), (6, 0)),
        # ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
        ('SPAN', (0, 0), (0, 2)), # Merge SUBJECT cells
        ('SPAN', (5, 1), (5, 2)), # Merge GRADE with the cell below
        ('SPAN', (6, 1), (6, 2)), # Merge REMARK with the cell below
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Vertically center all text
    ]))

    # header_row_1 = [
    #     "SUBJECT",
    #     Paragraph("CONTINUOUS ASSESSMENT", styles["h3"]),
    #     Spacer(1, 1), Spacer(1, 1), Spacer(1, 1),
    #     Paragraph("TERM SUMMARY", styles["h3"]),
    #     Spacer(1, 1),
    # ]

    # header_row_2 = ["SUBJECT", "CA1", "CA2", "EXAMINATION", "TOTAL", "GRADE", "REMARK"]
    # full_subject_data = [header_row_1, header_row_2] + subject_data

    # header_row_3 = [" ", "20", "20", "60", "100", " ", " "]
    # full_subject_data = [header_row_1, header_row_2, header_row_3] + subject_data

    # subject_table = Table(full_subject_data, colWidths=[150, 50, 50, 80, 50, 50, 100])
    # subject_table.setStyle(TableStyle([
    #     ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    #     ('FONTSIZE', (0, 0), (-1, -1), 10),
    #     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    #     ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    #     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    #     # ('BACKGROUND', (1, 2), (4, -1), colors.beige),
    #     # ('BACKGROUND', (5, 2), (6, -1), colors.beige),
    #     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    #     ('BACKGROUND', (1, 0), (4, 0), colors.lightgrey),
    #     ('BACKGROUND', (5, 0), (6, 0), colors.lightgrey),
    #     ('SPAN', (1, 0), (4, 0)),
    #     ('SPAN', (5, 0), (6, 0)),
    #     ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
    #     ('SPAN', (0, 0), (0, 2)), # Merge SUBJECT cells
    #     ('SPAN', (5, 0), (5, 1)), # Merge GRADE with the cell below
    #     ('SPAN', (6, 0), (6, 1)), # Merge REMARK with the cell below

    # ]))
   

    elements.append(subject_table)
    elements.append(Spacer(1, 0.1*inch))


    # Summary and Grading Key Tables
    term_average = grand_total / len(student_dict['subjects']) if student_dict['subjects'] else 0

    summary_data = [
        ["Term Grand Total:", str(grand_total)],
        ["Term Average:", f"{term_average:.2f}"],
        ["Number of Subject Passes:", str(passes)],
        ["Overall Grade:", student_dict.get("overall_grade", "N/A")],
    ]
    summary_table = Table(summary_data, colWidths=[150, 80])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    grading_key_data = [
        ["Figures", "Grade", "Remark"],
        ["70 - 100", "A", "Excellent"],
        ["60 - 69", "B", "Very Good"],
        ["50 - 59", "C", "Good"],
        ["45 - 49", "D", "Pass"],
        ["0 - 44", "E", "Weak"],
    ]

    grading_key_table = Table(grading_key_data, colWidths=[80, 60, 80])
    grading_key_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))


    # A nested table to hold summary and grading key side-by-side
    nested_table_data = [[summary_table, grading_key_table]]
    nested_table = Table(nested_table_data, colWidths=[300, 300])
    nested_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(nested_table)
    elements.append(Spacer(1, 0.2*inch))

    # Get remarks and signature dynamically
    teacher_remark = student_dict.get("teacher_remark", "No remark provided.")
    principal_remark = student_dict.get("principal_remark", "No remark provided.")
    principal_signature_path = student_dict.get("principal_signature", None)

    print('teachers remark is:', teacher_remark)
    print('principals remark is:', principal_remark)


    table_data = [
    [Paragraph("<b>Class Teacher's Remark:</b>", styles['Normal']), teacher_remark],
    [Paragraph("<b>Principal's Remark:</b>", styles['Normal']), principal_remark]
    ]
    print('table data details is:', table_data)

    table = Table(table_data, colWidths=[150, 400])
    table.setStyle(TableStyle([
        ('LINEBELOW', (1, 0), (1, -1), 1, 'black'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.0 * inch))


    # --- Signature Section ---
    centered_style = ParagraphStyle('Centered', parent=styles['Normal'], alignment=TA_CENTER)

    if principal_signature_path and os.path.exists(principal_signature_path):
        signature_path = os.path.join("static", "uploads", "signature.png")
        signature = Image(signature_path, width=100, height=40)
        elements.append(signature)
    else:
        elements.append(Paragraph("<b>____________________________</b>", centered_style))

    elements.append(Paragraph(f"<b>{student_dict.get('principal_name')}</b>", centered_style))
    elements.append(Paragraph("<b>(PRINCIPAL)</b>", centered_style))

    # Build PDF with background image
    def add_background(canvas, doc):
        if background_logo_path:
            bg_image = ImageReader(background_logo_path)
            canvas.setFillAlpha(0.2)
            canvas.drawImage(bg_image, 100, 200, width=400, height=400,
                             preserveAspectRatio=True, mask='auto')
            canvas.setFillAlpha(1)

    # Generate PDF
    doc.build(elements, onFirstPage=add_background, onLaterPages=add_background)

    return f"/results/result_{student_dict['name']}.pdf"


# Adding principal signature to students results
UPLOAD_FOLDER = "static/uploads/signatures"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@main.route("/upload_signature", methods=["GET", "POST"])
@login_required
@admin_required
def upload_signature():
    form = RemarksForm()

    # Populate student choices dynamically
    students = Student.query.filter_by(school_id=current_user.school_id).all()
    student_choices = [(str(student.id), f"{student.first_name} {student.last_name} ({student.id})") for student in students]
    form.student_id.choices = student_choices

    # Populate student class choices dynamically
    classes = [(str(c.id), c.class_name) for c in current_user.school.classes]
    form.student_class.choices = classes

    # Populate academic session and term choices dynamically (from Assessment model)
    assessments = Assessment.query.filter_by(school_id=current_user.school_id).all()
    academic_sessions = set([assessment.academic_session for assessment in assessments])
    term_choices = set([assessment.term for assessment in assessments])

    form.academic_session.choices = [(session, session) for session in academic_sessions]
    form.term.choices = [(term, term) for term in term_choices]


    if form.validate_on_submit():
        student_id = form.student_id.data
        student_class = form.student_class.data
        academic_session = form.academic_session.data
        term = form.term.data
        teacher_remark = form.teacher_remark.data
        principal_remark = form.principal_remark.data
        signature_file = form.signature.data

        student = Student.query.filter_by(id=student_id, school_id=current_user.school_id).first()
        if not student:
            flash("Student not found or does not belong to your school!", "danger")
            return redirect(url_for("upload_signature"))

        assessment = Assessment.query.filter_by(class_id=student.class_id,
                                                school_id=current_user.school_id,
                                                academic_session=academic_session,
                                                term=term).order_by(Assessment.date.desc()).first()
        if not assessment:
            flash("Assessment record not found for the selected session and term!", "danger")
            return redirect(url_for("upload_signature"))

        filename = secure_filename(signature_file.filename)
        signature_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        signature_file.save(signature_path)

        student.class_id = student_class
        student.teacher_remark = teacher_remark
        student.principal_remark = principal_remark
        student.principal_signature = signature_path
        student.academic_session = academic_session
        student.term = term
        db.session.commit()

        flash("Remarks and signature uploaded successfully!", "success")
        return redirect(url_for("main.upload_signature"))

    return render_template("upload_signature.html", form=form)

# Teachers/principal results remarks
@main.route("/submit_remarks", methods=["POST"])
@login_required
@admin_required
def submit_remarks():
    form = RemarksForm()
    if form.validate_on_submit():
        student_id = form.student_id.data
        student_class = form.student_class.data
        teacher_remark = form.teacher_remark.data
        principal_remark = form.principal_remark.data
        signature_file = form.signature.data

    if not all([student_id, student_class, teacher_remark, principal_remark, signature_file]):
        flash("All fields are required!", "danger")
        return redirect(url_for("upload_signature"))

    # Fetch student details, ensuring they belong to the admin's school
    student = Student.query.filter_by(id=student_id, school_id=current_user.school_id).first()
    if not student:
        flash("Student not found or does not belong to your school!", "danger")
        return redirect(url_for("upload_signature"))

    # Fetch academic session and term from Assessment DB
    assessment = Assessment.query.filter_by(student_id=student_id).first()
    if not assessment:
        flash("Assessment record not found!", "danger")
        return redirect(url_for("upload_signature"))

    academic_session = assessment.academic_session
    term = assessment.term

    # Save the uploaded signature file
    filename = secure_filename(signature_file.filename)
    signature_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    signature_file.save(signature_path)

    # Update student record
    student.class_id = student_class
    student.teacher_remark = teacher_remark
    student.principal_remark = principal_remark
    student.principal_signature = signature_path
    student.academic_session = academic_session
    student.term = term
    db.session.commit()


    flash("Remarks and signature uploaded successfully!", "success")
    return redirect(url_for("upload_signature", student=student, academic_session=academic_session, term=term))


def calculate_class_position(student_id, class_id, term):
    print(f"Calculating class position for student_id: {student_id}, class_id: {class_id}, term: {term}")

    class_students = (
        db.session.query(Student.id, db.func.sum(AssessmentSubjectScore.total_marks).label('total'))
        .join(AssessmentSubjectScore, Student.id == AssessmentSubjectScore.student_id)
        .join(Assessment, AssessmentSubjectScore.assessment_id == Assessment.id)
        .filter(Student.class_id == class_id,
                # Assessment.academic_session == academic_session,
                Assessment.term == term,
                Student.school_id == current_user.school_id)
        .group_by(Student.id)
        .order_by(db.desc('total'))
        .all()
    )

    print("Class students:", class_students) # debugging purposes

    if not class_students:
        print("No students found for this class and session.")
        return None

    for index, (student_id_in_class, total) in enumerate(class_students):
        print(f"  student_id_in_class: {student_id_in_class}") # debugging purposes
        if int(student_id_in_class) == int(student_id):
            position = index + 1
            print('student position:', position)
            return format_position(position)
    return None



def format_position(position):
    if 10 <= position % 100 <= 20:
        suffix = 'TH'
    else:
        suffix = {1: 'ST', 2: 'ND', 3: 'RD'}.get(position % 10, 'TH')
    return f"{position}{suffix}"


@main.route('/generate-results', methods=['GET', 'POST'])
@login_required
@admin_required
def generate_results():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        abort(403)
        return "This is a restricted area for only teachers and admin"

        # return redirect(url_for('main.index'))

    # Filter students and classes by the logged-in admin's school
    students = Student.query.filter_by(school_id=current_user.school_id).all()
    classes = Class.query.filter_by(school_id=current_user.school_id).all()

    # Get distinct academic sessions related to the logged-in user's school
    academic_sessions = (
        db.session.query(Assessment.academic_session)
        .join(AssessmentSubjectScore, Assessment.id == AssessmentSubjectScore.assessment_id)
        .join(Student, Student.id == AssessmentSubjectScore.student_id)
        .filter(Student.school_id == current_user.school_id)
        .distinct()
        .all()
    )
    academic_sessions = [session[0] for session in academic_sessions]
    print('session is:', academic_sessions)


    if request.method == 'POST':
        student_id = request.form.get('student')
        class_id = request.form.get('class')
        academic_session = request.form.get('academic_session')

        # Ensure the selected student and class belong to the logged-in user's school
        student = Student.query.filter_by(id=student_id, school_id=current_user.school_id).first()
        class_obj = Class.query.filter_by(id=class_id, school_id=current_user.school_id).first()

        if not student or not class_obj:
            flash('Invalid selection. Please choose valid student and class.', 'danger')
            return redirect(url_for('main.generate_results'))

        # student_record = (
        #     db.session.query(
        #         Student.id,
        #         Student.first_name,
        #         Student.last_name,
        #         Student.contact_email,
        #         Student.teacher_remark,
        #         Student.principal_remark,
        #         Student.principal_signature,
        #         School.name.label("school_name"),
        #         School.address.label("school_address"),
        #         School.principal_name,
        #         Student.gender.label("sex"),
        #         School.school_logo,
        #         Assessment.academic_session,
        #         Assessment.term
        #     )
        #     .join(School, Student.school_id == School.id)
        #     .filter(Student.id == student_id, Student.school_id == current_user.school_id)
        #     .first()
        # )

        # student_record = (
        #     db.session.query(
        #         Student.id,
        #         Student.first_name,
        #         Student.last_name,
        #         Student.contact_email,
        #         Student.teacher_remark,
        #         Student.principal_remark,
        #         Student.principal_signature,
        #         School.name.label("school_name"),
        #         School.address.label("school_address"),
        #         School.principal_name,
        #         Student.gender.label("sex"),
        #         School.school_logo,
        #         Assessment.academic_session,
        #         Assessment.term
        #     )
        #     .join(School, Student.school_id == School.id)  
        #     .join(AssessmentSubjectScore, AssessmentSubjectScore.student_id == Student.id)  # Ensure a valid link
        #     .join(Assessment, Assessment.id == AssessmentSubjectScore.assessment_id)  # Correct join to Assessment
        #     .filter(Student.id == student_id, Student.school_id == current_user.school_id)
        #     .first()
        # )

        student_record = (
            db.session.query(
                Student.id,
                Student.first_name,
                Student.last_name,
                Student.contact_email,
                Student.teacher_remark,
                Student.principal_remark,
                Student.principal_signature,
<<<<<<< HEAD
                School.name.label("school_name"), School.address.label("school_address"),
                Student.gender.label("sex"), School.school_logo
=======
                School.name.label("school_name"),
                School.address.label("school_address"),
                School.principal_name,
                Student.gender.label("sex"),
                School.school_logo,
                Assessment.academic_session,
                Assessment.term
            )
            .join(School, Student.school_id == School.id)  
            .join(AssessmentSubjectScore, AssessmentSubjectScore.student_id == Student.id)  
            .join(Assessment, Assessment.id == AssessmentSubjectScore.assessment_id)  
            .filter(
                Student.id == student_id, 
                Student.school_id == current_user.school_id
>>>>>>> 6ce13e0b12f10a070169f908fdde69ce1d0b665a
            )
            .first()  # Fetch only the selected student's record
        )


        if not student_record:
            flash('Invalid selection. Please choose a valid student.', 'danger')
            return redirect(url_for('main.generate_results'))

        # Get attendance records for the student
        attendance_record = Attendance.query.filter_by(student_id=student_id).first()

        if attendance_record:
            times_present = attendance_record.days_present
            times_opened = attendance_record.total_days_opened
        else:
            times_present = 0
            times_opened = 0

        # Get subjects and scores for the student
        class_subjects = ClassSubject.query.filter_by(class_id=class_id).all()
        subjects = [cs.subject for cs in class_subjects if cs.subject.school_id == current_user.school_id]
        print('class subjects:', class_subjects)
        print('subjects:', subjects)

        assessment = None

        # subject_scores = {}
        # for subject in subjects:
        #     subject_name = subject.name
        #     subject_scores[subject_name] = {'CA1': 0, 'CA2': 0, 'EXAMINATION': 0, 'TOTAL': 0}

        #     assessments = Assessment.query.filter_by(class_id=class_id, school_id=current_user.school_id).all()
        #     for assessment in assessments:
        #         subject_score = AssessmentSubjectScore.query.filter_by(
        #             assessment_id=assessment.id,
        #             student_id=student_id,
        #             subject_id=subject.id
        #         ).first()

        #         if subject_score:
        #             if 'CA1' in assessment.name:
        #                 subject_scores[subject_name]['CA1'] = subject_score.total_marks
        #             elif 'CA2' in assessment.name:
        #                 subject_scores[subject_name]['CA2'] = subject_score.total_marks
        #             elif 'EXAMINATION' in assessment.name:
        #                 subject_scores[subject_name]['EXAMINATION'] = subject_score.total_marks
        
        # subject_scores[subject_name]['TOTAL'] = sum(subject_scores[subject_name].values())

        # subject_scores = {}

        # assessments = Assessment.query.filter_by(
        #     class_id=class_id, 
        #     school_id=current_user.school_id
        # ).all()

        # for assessment in assessments:
        #     for subject in subjects:
        #         subject_name = subject.name
                
        #         # Initialize subject scores for each student
        #         if subject_name not in subject_scores:
        #             subject_scores[subject_name] = {'CA1': 0, 'CA2': 0, 'EXAMINATION': 0, 'TOTAL': 0}

        #         subject_score = AssessmentSubjectScore.query.filter_by(
        #             assessment_id=assessment.id,
        #             student_id=student_id,
        #             subject_id=subject.id
        #         ).first()

        #         if subject_score:
        #             if 'CA1' in assessment.name:
        #                 subject_scores[subject_name]['CA1'] = subject_score.total_marks
        #             elif 'CA2' in assessment.name:
        #                 subject_scores[subject_name]['CA2'] = subject_score.total_marks
        #             elif 'EXAMINATION' in assessment.name:
        #                 subject_scores[subject_name]['EXAMINATION'] = subject_score.total_marks

        #         # Calculate TOTAL properly per subject
        #         subject_scores[subject_name]['TOTAL'] = (
        #             subject_scores[subject_name]['CA1']
        #             + subject_scores[subject_name]['CA2']
        #             + subject_scores[subject_name]['EXAMINATION']
        #         )


        # # term = assessment.term if assessment else "N/A"
        # grand_total = sum(scores['TOTAL'] for scores in subject_scores.values())

        subject_scores = {}

        # Alias the association table
        assessment_class_alias = aliased(assessment_class_association)

        assessments = db.session.query(Assessment).join(
            assessment_class_alias, assessment_class_alias.c.assessment_id == Assessment.id
        ).filter(
            assessment_class_alias.c.class_id == class_id,  # Filter assessments for the class
            Assessment.school_id == current_user.school_id
        ).all()

        if not assessments:
            print(f"No assessments found for class_id={class_id}")  # Debugging line

        for assessment in assessments:
            # Dynamically fetch subjects related to this class
            subjects = ClassSubject.query.filter_by(class_id=class_id).all()

            if not subjects:
                print(f"No subjects found for class_id={class_id}")  # Debugging line

            for subject in subjects:
                subject_name = subject.subject.name  # Access the related Subject model

                # Initialize subject scores for each student
                if subject_name not in subject_scores:
                    subject_scores[subject_name] = {'CA1': 0, 'CA2': 0, 'EXAMINATION': 0, 'TOTAL': 0}

                subject_score = AssessmentSubjectScore.query.filter_by(
                    assessment_id=assessment.id,
                    student_id=student_id,
                    subject_id=subject.id
                ).first()
                print('this is subject scores:', subject_score)

                if not subject_score:
                    print(f"No scores found for student {student_id}, subject {subject_name}")

                if subject_score:
                    if 'CA1' in assessment.name:
                        subject_scores[subject_name]['CA1'] = subject_score.total_marks
                    elif 'CA2' in assessment.name:
                        subject_scores[subject_name]['CA2'] = subject_score.total_marks
                    elif 'EXAMINATION' in assessment.name:
                        subject_scores[subject_name]['EXAMINATION'] = subject_score.total_marks

                # Calculate TOTAL properly per subject
                subject_scores[subject_name]['TOTAL'] = (
                    subject_scores[subject_name]['CA1']
                    + subject_scores[subject_name]['CA2']
                    + subject_scores[subject_name]['EXAMINATION']
                )

        # Calculate Grand Total
        grand_total = sum(scores['TOTAL'] for scores in subject_scores.values())







        # grand_total = sum(sum(scores.values()) for scores in subject_scores.values())
        # overall_grade = calculate_grade(grand_total, len(subjects))

        # Calculate student positions
        # class_position = calculate_class_position(student_id, class_id, term)

        # student_dict = {
        #     "result_id": student_record.id,
        #     "name": f"{student_record.first_name} {student_record.last_name}",
        #     "email": student_record.contact_email,
        #     "school_name": student_record.school_name,
        #     "school_address": student_record.school_address,
        #     "sex": student_record.sex,
        #     "session": student_record.academic_session,
        #     "class_name": class_obj.class_name,
        #     "term": student_record.term, # assessment.term if assessment else "N/A",
        #     "times_present": times_present,
        #     "times_opened": times_opened,
        #     "teacher_remark": student_record.teacher_remark,
        #     "principal_remark": student_record.principal_remark,
        #     "principal_signature": student_record.principal_signature,
        #     "class_category": class_obj.class_category,
        #     "principal_name": student_record.principal_name,
        #     "subjects": [
        #         {
        #             "name": subject,
        #             "CA1": scores['CA1'],
        #             "CA2": scores['CA2'],
        #             "EXAMINATION": scores['EXAMINATION'],
        #             "TOTAL": scores['TOTAL']
        #         }
        #         for subject, scores in subject_scores.items()
        #     ],
        #     "grand_total": grand_total,
        #     "overall_grade": "A",  # calculation logic already done above"""
        #     # "next_term": "2023-09-01",  """not yet done"""
        #     "school_logo": student_record.school_logo,
        #     "class_position": class_position
        # }

        student_dict = {
            "result_id": student_record.id,
            "name": f"{student_record.first_name} {student_record.last_name}",
            "email": student_record.contact_email,
            "school_name": student_record.school_name,
            "school_address": student_record.school_address,
            "sex": student_record.sex,
            "session": student_record.academic_session,
            "class_name": class_obj.class_name,
            "term": student_record.term,
            "times_present": times_present,
            "times_opened": times_opened,
            "teacher_remark": student_record.teacher_remark,
            "principal_remark": student_record.principal_remark,
            "principal_signature": student_record.principal_signature,
            "class_category": class_obj.class_category,
            "principal_name": student_record.principal_name,
            "subjects": [
                {
                    "name": subject,
                    "CA1": scores['CA1'],
                    "CA2": scores['CA2'],
                    "EXAMINATION": scores['EXAMINATION'],
                    "TOTAL": scores['TOTAL']
                }
                for subject, scores in subject_scores.items()
            ],
            "grand_total": sum(scores['TOTAL'] for scores in subject_scores.values()),
            "overall_grade": "A",  # Add actual calculation if needed
            "school_logo": student_record.school_logo,
            "class_position": calculate_class_position(student_id, class_id, student_record.term)
        }


        # Format the result_id
        if student_record:
            school_name = student_record.school_name
            school_initials = "".join(word[0].upper() for word in school_name.split())
            current_year = datetime.datetime.now().year
            class_name = class_obj.class_name
            student_id_formatted = f"{student_record.id:04d}"  # Pad with leading zeros to 4 digits

            student_dict["result_id"] = f"{school_initials}/{current_year}/{class_name}/{student_id_formatted}"

        pdf_url = create_student_result_pdf(student_dict)

        # Save the PDF URL to the student's dashboard
        student.result_url = pdf_url
        db.session.commit()

        flash('Results generated successfully!', 'success')
        return redirect(url_for('main.list_students_result'))

    return render_template('generate_results.html', students=students, classes=classes, academic_sessions=academic_sessions)



# def calculate_class_position(student_id, class_id, academic_session, term):
#     print(f"Calculating class position for student_id: {student_id}, class_id: {class_id}, session: {academic_session}, term: {term}")

#     class_students = (
#         db.session.query(Student.id, db.func.sum(AssessmentSubjectScore.total_marks).label('total'))
#         .join(AssessmentSubjectScore, Student.id == AssessmentSubjectScore.student_id)
#         .join(Assessment, AssessmentSubjectScore.assessment_id == Assessment.id)
#         .filter(Student.class_id == class_id,
#                 Assessment.academic_session == academic_session,
#                 Assessment.term == term,
#                 Student.school_id == current_user.school_id)
#         .group_by(Student.id)
#         .order_by(db.desc('total'))
#         .all()
#     )

#     print("Class students:", class_students) # Print the query result.

#     if not class_students:
#         print("No students found for this class and session.")
#         return None

#     for index, (student_id_in_class, total) in enumerate(class_students):
#         if student_id_in_class == student_id:
#             return index + 1  # Return only the position
#     return None  # Return None if student not found

@main.route('/results/<filename>')
@login_required
def serve_results(filename):
    return send_from_directory('static/results', filename)


@main.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(file_directory, filename, as_attachment=True)


@main.route('/list_students_result', methods=['GET'])
@login_required
@admin_required
def list_students_result():
    students = Student.query.with_entities(
        Student.id,
        Student.result_url,
        Student.teacher_remark,
        Student.principal_remark,
        Student.principal_signature
    ).all()
    return render_template('list_students_results.html', students=students)

@main.route('/students_result/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student_result(student_id):
    student = Student.query.get_or_404(student_id)

    form = RemarksForm()
    if form.validate_on_submit():
        student.result_url = request.form['result_url']
        student.teacher_remark = request.form['teacher_remark']
        student.principal_remark = request.form['principal_remark']
        student.principal_signature = request.form['principal_signature']

        db.session.commit()

        return redirect(url_for('main.list_students_result', student_id=student.id))

    return render_template('edit_student_results.html', student=student, form=form)


@main.route('/students_result/delete/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def delete_student_result(student_id):
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        if 'delete_result_url' in request.form:
            student.result_url = None
        if 'delete_teacher_remark' in request.form:
            student.teacher_remark = None
        if 'delete_principal_remark' in request.form:
            student.principal_remark = None
        if 'delete_principal_signature' in request.form:
            student.principal_signature = None
        
        db.session.commit()
        return redirect(url_for('main.list_students_result'))