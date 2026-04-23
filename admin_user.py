
"""
This script is used to create schools and admin users.

Usage: python admin_user.py
"""

from app.main import create_app, db
from app.models import User, School


def create_school():
    """Function to create a new school."""
    print("\n=== Create a New School ===")
    name = input("Enter the school name: ").strip()
    address = input("Enter the school address: ").strip()
    email = input("Enter the school email: ").strip()
    phone_number = input("Enter the school phone number: ").strip()
    website = input("Enter the school website (optional): ").strip()

    # Check if a school with the same name or email already exists
    existing_school = School.query.filter((School.name == name) | (School.email == email)).first()
    if existing_school:
        print("A school with this name or email already exists.")
        return None

    # Create the school
    school = School(
        name=name,
        address=address,
        email=email,
        phone_number=phone_number,
        website=website if website else None
    )
    db.session.add(school)
    db.session.commit()
    print(f"School '{name}' created successfully!")
    return school


def create_admin():
    """Function to create an admin user."""
    # Initialize the app context
    app = create_app()
    with app.app_context():
        # Check if the admin user already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("Admin user already exists.")
            return

        # List available schools for selection
        schools = School.query.all()
        if not schools:
            print("\nNo schools found. Let's create one first.")
            school = create_school()
            if not school:
                print("Failed to create a school. Admin user creation aborted.")
                return
        else:
            print("\nAvailable Schools:")
            for school in schools:
                print(f"{school.id}: {school.name}")

            try:
                choice = input("\nEnter the ID of the school to associate with this admin user (or type 'new' to create a new school): ").strip()
                if choice.lower() == 'new':
                    school = create_school()
                    if not school:
                        print("Failed to create a school. Admin user creation aborted.")
                        return
                else:
                    school_id = int(choice)
                    school = School.query.get(school_id)
                    if not school:
                        print("Invalid school ID. Admin user creation aborted.")
                        return
            except ValueError:
                print("Invalid input. Admin user creation aborted.")
                return

        # Create the admin user
        admin = User(
            username='admin',
            role='admin',
            school_id=school.id
        )
        admin.set_password('1234567')  # You can change this to a more secure password

        # Add the admin user to the session and commit
        db.session.add(admin)
        db.session.commit()

        print(f"Admin user created successfully for school: {school.name}")


if __name__ == "__main__":
    create_admin()
