from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, g, session
from extensions import db
import os
from forms import (
    TeacherForm, ClassForm, GradeForm, AttendanceForm, StudentForm, AssignTeachersForm,
    AssessmentForm, AssessmentResultForm, SubjectForm, SchoolForm, UserForm, AssessmentTypeForm, 
    AssignSubjectToClassForm, LoginForm, RemarksForm  # RemarksForm added here
)
from models import (
    User, Student, Teacher, Class, Attendance, Assessment, AssessmentType,
    AssessmentSubjectScore, AssessmentResult, Subject, ClassSubject, TeacherSubject, School,
    Grade, FeeComponent, StudentClassFeePayment, ClassFeeComponent  # Combined model imports
)
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
from reportlab.lib.pagesizes import A4, letter # Only import A4 and letter once
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image # Combined reportlab imports
from flask import send_file, jsonify
import json
from collections import defaultdict
from sqlalchemy.orm import aliased
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # Combined styles import
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader  # Only import ImageReader once
import uuid
from flask_wtf.csrf import validate_csrf, generate_csrf # Combined csrf imports
import datetime
from models import assessment_class_association


def school_required(model, school_field="school_id"):
    """Decorator to restrict access to objects linked to the logged-in user's school."""
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You must be logged in to access this page.", "warning")
                return redirect(url_for('main.index'))

            if not current_user.school_id:
                flash("You are not linked to any school.", "warning")
                return redirect(url_for('main.dashboard'))

            # Fetch the requested object from the database
            obj = model.query.get(kwargs.get("id"))
            if not obj:
                flash("Requested resource not found.", "danger")
                return redirect(url_for('main.dashboard'))

            # Check if the object's school_id matches the user's school_id
            if getattr(obj, school_field) != current_user.school_id:
                flash("You do not have permission to access this resource.", "danger")
                return redirect(url_for('main.dashboard'))

            return f(*args, **kwargs)
        return wrapped_function
    return decorator


def filter_by_school(model, school_field="school_id"):
    """Decorator to filter query results so that users only see data from their school."""
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You must be logged in to access this page.", "warning")
                return redirect(url_for('main.index'))

            if not current_user.school_id:
                flash("You are not linked to any school.", "danger")
                return redirect(url_for('main.dashboard'))

            # Modify the function to return only data linked to the user's school
            filtered_data = model.query.filter_by(**{school_field: current_user.school_id})

            return f(filtered_data, *args, **kwargs)
        return wrapped_function
    return decorator

def admin_access(func):
    """Decorator to allow admin users to access any route."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.role == 'admin':
            return func(*args, **kwargs)  # Admin has access

        # If not admin, let the original function's access control handle it
        return func(*args, **kwargs)
    return decorated_function

# ADMIN ONLY ACCESS
def admin_required(func):
    """Decorator to restrict access to admin users."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
            # flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('main.index'))  # Or any other appropriate redirect
        return func(*args, **kwargs)
    return decorated_function