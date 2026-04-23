from flask import Flask, render_template, request, redirect, url_for, flash

from . models import db, StudentFee, FeeComponent, FeePayment

from .routes import main


@main.route('/fee_components')
def fee_components():
    # Fetch all fee components from the database
    components = FeeComponent.query.all()
    return render_template('fee_components.html', components=components)

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
        return redirect(url_for('fee_components'))

    # Fetch all schools for the dropdown
    schools = School.query.all()
    return render_template('add_fee_component.html', schools=schools)

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
        return redirect(url_for('fee_components'))

    # Fetch all schools for the dropdown
    schools = School.query.all()
    return render_template('edit_fee_component.html', component=component, schools=schools)

@main.route('/delete_fee_component/<int:id>', methods=['POST'])
def delete_fee_component(id):
    component = FeeComponent.query.get_or_404(id)
    db.session.delete(component)
    db.session.commit()
    flash('Fee component deleted successfully!', 'success')
    return redirect(url_for('fee_components'))




def generate_fees_for_student(student_id, component_id, amount, academic_year, term):
    """
    Generates a fee record for a student and marks it as unpaid.
    """
    student_fee = StudentFee(
        student_id=student_id,
        component_id=component_id,
        amount=amount,
        academic_year=academic_year,
        term=term,
        payment_status='unpaid'  # Default status
    )
    db.session.add(student_fee)
    db.session.commit()
    return student_fee

def record_payment(student_fee_id, amount_paid, payment_date, payment_method, receipt_number=None, notes=None):
    """
    Records a payment for a student fee and updates the payment status.
    """
    # Fetch the student fee record
    student_fee = StudentFee.query.get(student_fee_id)
    if not student_fee:
        raise ValueError("Student fee record not found.")

    # Record the payment
    payment = FeePayment(
        student_fee_id=student_fee_id,
        amount_paid=amount_paid,
        payment_date=payment_date,
        payment_method=payment_method,
        receipt_number=receipt_number,
        notes=notes
    )
    db.session.add(payment)

    # Check if the total payments cover the fee amount
    total_paid = db.session.query(db.func.sum(FeePayment.amount_paid)).filter(
        FeePayment.student_fee_id == student_fee_id
    ).scalar() or 0

    # Update payment status
    if total_paid >= student_fee.amount:
        student_fee.payment_status = 'paid'
    else:
        student_fee.payment_status = 'unpaid'

    db.session.commit()
    return payment