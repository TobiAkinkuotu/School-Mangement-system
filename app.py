from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker
from typing import Optional
from models import Base, User, Student, Teacher, SchoolClass, Subject, Grade, Attendance
from datetime import datetime
import os

app = FastAPI()

# Database Setup
sqlite_url = "sqlite:///school.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Templates & Static Files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    # Initial Admin
    if not db.execute(select(User).where(User.username == "admin")).first():
        admin = User(username="admin", role="admin", hashed_password="")
        admin.set_password("admin123")
        db.add(admin)
        db.commit()
    
    # Default Subject for testing
    if not db.execute(select(Subject)).first():
        math = Subject(name="Mathematics", code="MATH101")
        db.add(math)
        db.commit()
    db.close()

# --- Auth Helper ---
def get_current_user(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("username")
    if not username:
        return None
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    return user

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user: Optional[User] = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "current_user": user})

@app.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if not user or not user.verify_password(password):
        return RedirectResponse(url="/?error=1", status_code=303)
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="username", value=username, httponly=True)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("username")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    if user.role == "admin":
        stats = {
            "students": db.query(Student).count(),
            "teachers": db.query(Teacher).count(),
            "classes": db.query(SchoolClass).count(),
        }
        return templates.TemplateResponse(
            "dashboard.html", 
            {"request": request, "current_user": user, "stats": stats}
        )
    
    elif user.role == "student" and user.student_id:
        student = db.get(Student, user.student_id)
        if not student:
            return RedirectResponse(url="/logout", status_code=303)
        
        grades = db.execute(select(Grade).where(Grade.student_id == student.id).limit(5)).scalars().all()
        attendance = db.execute(select(Attendance).where(Attendance.student_id == student.id)).scalars().all()
        
        total_days = len(attendance)
        present_days = sum(1 for a in attendance if a.status == "present")
        absent_days = total_days - present_days
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        
        avg_grade = sum(g.score for g in grades) / len(grades) if grades else 0
        
        return templates.TemplateResponse(
            "student_dashboard.html",
            {
                "request": request, 
                "current_user": user, 
                "student": student,
                "grades": grades,
                "total_days": total_days,
                "present_days": present_days,
                "absent_days": absent_days,
                "attendance_rate": attendance_rate,
                "avg_grade": avg_grade
            }
        )
    
    # Fallback for teacher or undefined role
    return templates.TemplateResponse("dashboard.html", {"request": request, "current_user": user, "stats": {}})

@app.get("/students", response_class=HTMLResponse)
async def students(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    all_students = db.execute(select(Student)).scalars().all()
    return templates.TemplateResponse(
        "students.html", 
        {"request": request, "current_user": user, "students": all_students}
    )

@app.get("/students/add", response_class=HTMLResponse)
async def add_student_view(
    request: Request,
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("add_student.html", {"request": request, "current_user": user})

@app.post("/students/add")
async def add_student(
    first_name: str = Form(...),
    last_name: str = Form(...),
    registration_number: str = Form(...),
    gender: str = Form(...),
    date_of_birth: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
    new_student = Student(
        first_name=first_name,
        last_name=last_name,
        registration_number=registration_number,
        gender=gender,
        date_of_birth=dob
    )
    db.add(new_student)
    db.commit()
    return RedirectResponse(url="/students", status_code=303)

@app.get("/teachers", response_class=HTMLResponse)
async def teachers(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    all_teachers = db.execute(select(Teacher)).scalars().all()
    return templates.TemplateResponse(
        "teachers.html", 
        {"request": request, "current_user": user, "teachers": all_teachers}
    )

@app.get("/teachers/add", response_class=HTMLResponse)
async def add_teacher_view(
    request: Request,
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("add_teacher.html", {"request": request, "current_user": user})

@app.post("/teachers/add")
async def add_teacher(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    new_teacher = Teacher(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone
    )
    db.add(new_teacher)
    db.commit()
    return RedirectResponse(url="/teachers", status_code=303)

@app.get("/settings/academic", response_class=HTMLResponse)
async def academic_settings(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    classes = db.execute(select(SchoolClass)).scalars().all()
    subjects = db.execute(select(Subject)).scalars().all()
    return templates.TemplateResponse(
        "classes_subjects.html", 
        {"request": request, "current_user": user, "classes": classes, "subjects": subjects}
    )

@app.get("/settings/class/add", response_class=HTMLResponse)
async def add_class_view(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("add_class.html", {"request": request, "current_user": user})

@app.post("/settings/class/add")
async def add_class(
    name: str = Form(...),
    grade_level: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    new_class = SchoolClass(name=name, grade_level=grade_level)
    db.add(new_class)
    db.commit()
    return RedirectResponse(url="/settings/academic", status_code=303)

@app.get("/settings/subject/add", response_class=HTMLResponse)
async def add_subject_view(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("add_subject.html", {"request": request, "current_user": user})

@app.post("/settings/subject/add")
async def add_subject(
    name: str = Form(...),
    code: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    new_subject = Subject(name=name, code=code)
    db.add(new_subject)
    db.commit()
    return RedirectResponse(url="/settings/academic", status_code=303)

@app.get("/attendance", response_class=HTMLResponse)
async def attendance(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    records = db.execute(select(Attendance)).scalars().all()
    return templates.TemplateResponse(
        "attendance.html", 
        {"request": request, "current_user": user, "records": records}
    )

@app.get("/attendance/record", response_class=HTMLResponse)
async def record_attendance_view(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    students = db.execute(select(Student)).scalars().all()
    today = datetime.utcnow().date().strftime('%Y-%m-%d')
    return templates.TemplateResponse(
        "record_attendance.html", 
        {"request": request, "current_user": user, "students": students, "today": today}
    )

@app.post("/attendance/record")
async def record_attendance(
    student_id: int = Form(...),
    attendance_date: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    date_obj = datetime.strptime(attendance_date, '%Y-%m-%d').date()
    new_record = Attendance(
        student_id=student_id,
        attendance_date=date_obj,
        status=status
    )
    db.add(new_record)
    db.commit()
    return RedirectResponse(url="/attendance", status_code=303)

@app.get("/grades", response_class=HTMLResponse)
async def grades(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    all_grades = db.execute(select(Grade)).scalars().all()
    return templates.TemplateResponse(
        "grades.html", 
        {"request": request, "current_user": user, "grades": all_grades}
    )

@app.get("/grades/add", response_class=HTMLResponse)
async def add_grade_view(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    students = db.execute(select(Student)).scalars().all()
    subjects = db.execute(select(Subject)).scalars().all()
    return templates.TemplateResponse(
        "add_grade.html", 
        {"request": request, "current_user": user, "students": students, "subjects": subjects}
    )

@app.post("/grades/add")
async def add_grade(
    student_id: int = Form(...),
    subject_id: int = Form(...),
    score: float = Form(...),
    term: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    new_grade = Grade(
        student_id=student_id,
        subject_id=subject_id,
        score=score,
        term=term
    )
    db.add(new_grade)
    db.commit()
    return RedirectResponse(url="/grades", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
