from main import app
from models import User, School
from extensions import db

with app.app_context():
    print("\n=== ADMIN PASSWORD RESET TOOL ===\n")

    admins = (
        db.session.query(User, School)
        .join(School, User.school_id == School.id)
        .filter(User.role == 'admin1')
        .order_by(School.name, User.username)
        .all()
    )

    if not admins:
        print("No admin users found.")
        exit()

    print("Available Admin Users:\n")
    for idx, (user, school) in enumerate(admins, start=1):
        print(f"{idx}. {user.username} | {school.name}")

    try:
        choice = int(input("\nSelect admin number to reset password: "))
        selected_admin = admins[choice - 1][0]
    except (ValueError, IndexError):
        print("Invalid selection.")
        exit()

    new_password = input("Enter new password: ")
    confirm_password = input("Confirm new password: ")

    if new_password != confirm_password:
        print("Passwords do not match.")
        exit()

    if len(new_password) < 8:
        print("Password must be at least 8 characters.")
        exit()

    selected_admin.set_password(new_password)

    try:
        db.session.commit()
        print(f"\n✅ Password reset successful for admin '{selected_admin.username}'")
    except Exception as e:
        db.session.rollback()
        print("❌ Error resetting password:", e)
