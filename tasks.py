from celery_worker import celery
from flask_mail import Message
from app import mail, app
from models import User, Reservation
from datetime import datetime
import csv
from io import StringIO

@celery.task
def send_email(subject, recipient, body):
    with app.app_context():
        msg = Message(subject=subject, recipients=[recipient], body=body)
        mail.send(msg)
    return f"Email sent to {recipient}"

@celery.task
def send_daily_reminder():
    with app.app_context():
        users = User.query.filter_by(role='user').all()
        for user in users:
            email = f"{user.username}@example.com"  
            msg = Message(subject="Daily Parking Reminder",
                          recipients=[email],
                          body="Don't forget to reserve your parking spot today!")
            mail.send(msg)
        return f"Daily reminders sent to {len(users)} users"

@celery.task
def send_monthly_report():
    from app import app
    from sqlalchemy import extract
    from datetime import datetime

    with app.app_context():
        users = User.query.filter_by(role='user').all()
        current_month = datetime.now().month
        current_year = datetime.now().year

        for user in users:
            reservations = Reservation.query.filter(
                Reservation.user_id == user.id,
                extract('month', Reservation.parking_time) == current_month,
                extract('year', Reservation.parking_time) == current_year
            ).all()

            total_spent = sum(r.cost for r in reservations if r.cost)
            total_bookings = len(reservations)

            # Find most used lot
            lot_counts = {}
            for r in reservations:
                if r.spot and r.spot.lot:
                    lot_name = r.spot.lot.name
                    lot_counts[lot_name] = lot_counts.get(lot_name, 0) + 1
                else:
                    print(f"[WARN] Reservation {r.id} has no valid spot or lot.")

            most_used_lot = max(lot_counts, key=lot_counts.get) if lot_counts else "N/A"

            # Compose HTML email
            html_body = f"""
            <h2>Monthly Parking Report</h2>
            <p>Hi {user.username}, here is your activity summary for this month:</p>
            <ul>
                <li><strong>Total Bookings:</strong> {total_bookings}</li>
                <li><strong>Total Amount Spent:</strong> ₹{total_spent:.2f}</li>
                <li><strong>Most Used Parking Lot:</strong> {most_used_lot}</li>
            </ul>
            <p>Thank you for using our Parking App!</p>
            """

            msg = Message("Monthly Parking Report",
                          recipients=[f"{user.username}@example.com"],
                          html=html_body)

            try:
                mail.send(msg)
            except Exception as e:
                print(f"Error sending monthly report to {user.username}: {e}")

    return "Monthly reports sent!"

@celery.task
def export_reservations_csv(user_id, username):
    from app import app
    from models import Reservation
    from flask_mail import Message

    with app.app_context():
        reservations = Reservation.query.filter_by(user_id = user_id).all()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Lot', 'Spot ID', 'Start', 'End', 'Cost'])
        for r in reservations:
            if not r.spot or not r.spot.lot:
                 continue
            writer.writerow([r.spot.lot.name,
                             r.spot_id,
                             str(r.parking_time),
                             str(r.leaving_time) or 'Active',
                             str(r.cost) or '0'
                             ])
        msg = Message("Your Parking History Export",
                       recipients=[f"{username}@example.com"])
        msg.body = 'Attached is your parking history export.'
        msg.attach("parking_history.csv", "text/csv", output.getvalue())

        try:
            mail.send(msg)
            print(f"CSV export sent to {username}")
        except Exception as e:
            print(f"Error sending CSV: {e}")              

    
@celery.task
def print_hello():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"MAD2: Hello from Celery! Time: {now}")
    return f"Hello printed at {now}"
