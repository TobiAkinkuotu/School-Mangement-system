The School Managment Portal
The School Management Portal is a school enrollment and performance management system built with Python, Flask, and SQLAlchemy. It allows administrators to manage student, teacher, class, grade, and attendance records through a user-friendly interface. The application provides role-based access (admin), real-time data tracking, and easy report generation (exportable to Microsoft Excel and Word).

Key Features:
1. User authentication and authorization: Administrators can create, update, and delete user accounts, assign roles, and grant permissions.
2. Student management: Add, update, delete, and search for students, including their personal information, academic records, and attendance data.
3. Teacher management: Add, update, delete, and search for teachers, including their personal information and class assignments.
4. Class management: Create, update, delete, and search for classes, including their name, grade, and teacher.
5. Grade management: Assign grades to students, update grades, and search for specific grades and students.
6. Attendance management: Track attendance for students, update attendance records, and generate attendance reports.
7. Role-based access: Administrators have access to all features while other users only have limited access to specific sections.
8. Real-time data tracking: Data updates are reflected immediately in the user interface, ensuring a smooth and efficient workflow.
9. Easy report generation: Exportable reports (Microsoft Excel and Word) are generated for administrators, allowing them to analyze and share data with stakeholders.
10. Customizable dashboards: Administrators can create customizable dashboards to visualize key performance indicators (KPIs) and track progress over time. (note: This feature is yet to be implemented.)


## Secure School Registration

This application uses a secure method for schools to register users, ensuring privacy and preventing unauthorized access.  The key is the use of unique, school-specific registration links or codes.

### School-Specific Registration Links/Codes

Instead of displaying a list of all registered schools, each school is assigned a unique registration link or code. This code is generated when the school initially registers on the platform. This link/code is then used to create a registration page specifically for that school. This approach completely eliminates the need for schools to see other school names.

### How it Works

1. **Code Generation:** When a school registers, the system generates a unique identifier (e.g., a UUID, a short random string, or an incrementing ID).

2. **Database Association:** This unique identifier is then associated with the school in the application's database.

3. **URL Creation:** A registration URL is created using the school's unique code.  For example: `yourplatform.com/register_user?school_code=XYZ123` (where `XYZ123` is the school's unique code).

4. **Distribution:** This unique URL is provided to the school administrator.

### Benefits

* **Privacy:** Schools never see the names of other registered schools.
* **Security:** This method prevents unauthorized user registration for other schools, as only those with the correct unique code can access the registration page.
* **Simplicity:** The registration process is streamlined and simplified for school administrators.  They only need to use their provided link.


Use the link below to check the application in action:
https://schoolmgtportal.pythonanywhere.com/


