from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, ParkingLot, ParkingSpot, Reservation
from config import Config
from flask_caching import Cache


app = Flask(__name__)
cache = Cache(app, config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6380,
    'CACHE_REDIS_DB': 0,
    'CACHE_DEFAULT_TIMEOUT': 60
})
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)
mail = Mail(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# CORS(app, resources={r"/admin/*": {"origins": "http://127.0.0.1:5501"}})
# CORS(app, resources={r"*": {"origins": "*"}})

CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5501"}}, supports_credentials=True)




@app.before_request
def create_tables():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()

# from tasks import sample_task


# @app.route('/', methods=['GET'])
# def home():
#     return (f"<h2>Hello From Backend</h2>")
@app.route('/', methods=['GET'])
def home():
    return '''
    <html>
    <head>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            h2 {
                font-size: 40px;
            }
        </style>
    </head>
    <body>
        <h2>Hello From Backend</h2>
    </body>
    </html>
    '''


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    existing_user = User.query.filter_by(username=data['username']).first()

    if existing_user:
        print("Plain password:", data['password'])
        return jsonify(message="Username already taken!"), 400
    
    print("Plain password:", data['password'])
    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], password=hashed_password, role='user')
    db.session.add(user)
    db.session.commit()
    return jsonify(message='User registered successfully'), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={
            'id': user.id,
            'username':user.username,
            'role':user.role
            })
        return jsonify(token=access_token,
                       role = user.role, 
                       username=user.username)
    return jsonify(message='Invalid credentials'), 401


@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    current_user = get_jwt_identity()
    return jsonify(message=f"Welcome {current_user['username']}! Role: {current_user['role']}")


@app.route('/admin/lots', methods=['POST'])
@jwt_required()
def create_lot():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify(message="Unauthorized"), 403
    
    data = request.get_json()
    if ParkingLot.query.filter_by(name = data['name']).first():
        return jsonify(message='Lot with this name already exists!'), 400
    
    lot = ParkingLot(name = data['name'],
                     address = data['address'],
                     pin_code = data['pin_code'],
                     price = data['price'],
                     total_spots = data['total_spots']
                     )
    db.session.add(lot)
    db.session.commit()

    for _ in range(lot.total_spots):
        spot = ParkingSpot(lot_id=lot.id)
        db.session.add(spot)
    
    db.session.commit()
    return jsonify(message="Parking lot created with spots."), 201


@app.route('/admin/lots', methods=["GET"])
@jwt_required()
# @cache.cached(timeout=120, key_prefix='admin_lots')
def view_all_lots():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify(message="Unauthorized"), 403
    
    lots = ParkingLot.query.all()
    output = []
    for lot in lots:
        output.append({
            "id": lot.id,
            "name": lot.name,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "price": lot.price,
            "total_spots": lot.total_spots
        })
    return jsonify(lots=output)


@app.route('/admin/lots/<int:lot_id>', methods=['PUT'])
@jwt_required()
def edit_lot(lot_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify(message="Unauthorized"), 403
    
    lot = ParkingLot.query.get_or_404(lot_id)
    data = request.get_json()

    lot.name = data.get('name', lot.name)
    lot.address = data.get('address', lot.address)
    lot.pin_code = data.get('pin_code', lot.pin_code)
    lot.price = data.get('price', lot.price)

    db.session.commit()
    return jsonify(message="Parking lot updated.")


@app.route('/admin/lots/<int:lot_id>', methods=['DELETE'])
@jwt_required()
def delete_lot(lot_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify(message="Unauthorized"), 403
    
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied_spots = ParkingSpot.query.filter_by(lot_id = lot.id, status="O").count()

    if occupied_spots > 0:
        return jsonify(message="Cannot delete. Some spots are occupied"), 400
    
    ParkingSpot.query.filter_by(lot_id = lot.id).delete()
    db.session.delete(lot)
    db.session.commit()
    return jsonify(message="Parking lot deleted.")


@app.route('/user/reserve/<int:lot_id>', methods=['POST'])
@jwt_required()
def reserve_spot(lot_id):
    user_data = get_jwt_identity()
    user = User.query.filter_by(id=user_data['id']).first()

    active = Reservation.query.filter_by(user_id = user.id,leaving_time=None).first()
    if active:
        return jsonify(message='You already have a reservation!'), 400
    
    spot = ParkingSpot.query.filter_by(lot_id=lot_id,status='A').first()
    if not spot:
        return jsonify(message='No available spots in this lot'), 404
    
    spot.status = 'O'

    reservation = Reservation(user_id = user.id, 
                              spot_id = spot.id,
                              parking_time=datetime.utcnow()
                              )
    db.session.add(reservation)
    db.session.commit()

    return jsonify(message='Spot reserved', spot_id=spot.id, reservation_id=reservation.id), 201


@app.route('/user/release', methods=['POST'])
@jwt_required()
def release_spot():
    user_data = get_jwt_identity()
    user = User.query.get(user_data['id'])

    reservation = Reservation.query.filter_by(user_id = user.id, leaving_time=None).first()
    if not reservation:
        return jsonify(message='No active reservation found.'), 404
    
    reservation.leaving_time = datetime.utcnow()

    duration = (reservation.leaving_time - reservation.parking_time).total_seconds() / 60
    lot = reservation.spot.lot
    reservation.cost = round((duration/60) * lot.price, 2)

    reservation.spot.status = 'A'
    db.session.commit()

    return jsonify(message='Spot release', cost=reservation.cost), 200


@app.route('/user/reservations', methods=['GET'])
@jwt_required()
def get_user_reservations():
    user_data = get_jwt_identity()
    user = db.session.get(User, user_data['id'])

    reservations = Reservation.query.filter_by(user_id = user.id).all()
    output = []
    for r in reservations:
        lot_name = r.spot.lot.name if r.spot and r.spot.lot else "Deleted Lot"
        output.append({
            'reservation_id': r.id,
            'spot_id': r.spot_id,
            'lot_name': lot_name,
            'parking_time': r.parking_time,
            'leaving_time': r.leaving_time,
            'cost': r.cost
        })
    return jsonify(history = output)


@app.route('/admin/dashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)
def admin_dashboard():
    user = get_jwt_identity()
    if user['role'] != 'admin':
        return jsonify(message="Unauthorized"), 403

    # Fetch lots and spot stats
    lots = ParkingLot.query.all()
    total_spots = ParkingSpot.query.count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    total_users = User.query.filter_by(role='user').count()

    # Calculate total revenue from reservations
    total_revenue = db.session.query(db.func.sum(Reservation.cost)).scalar() or 0

    # Lot-wise summary
    lot_summaries = []
    for lot in lots:
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        available = sum(1 for s in spots if s.status == 'A')
        occupied = sum(1 for s in spots if s.status == 'O')
        lot_summaries.append({
            "id": lot.id,
            "name": lot.name,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "price": lot.price,
            "total_spots": lot.total_spots,
            "available": available,
            "occupied": occupied
        })

    # Recent reservations (last 10)
    recent_reservations = Reservation.query.order_by(Reservation.parking_time.desc()).limit(10).all()
    reservations_list = []
    for r in recent_reservations:
        lot_name = r.spot.lot.name if r.spot and r.spot.lot else "Deleted Lot"
        reservations_list.append({
            "reservation_id": r.id,
            "username": r.user.username,
            "lot": lot_name,
            "spot_id": r.spot_id,
            "start": r.parking_time,
            "end": r.leaving_time,
            "cost": r.cost or 0
        })

    return jsonify({
        "total_lots": len(lots),
        "total_spots": total_spots,
        "available_spots": available_spots,
        "occupied_spots": occupied_spots,
        "total_users": total_users,
        "total_revenue": round(total_revenue, 2),
        "lots": lot_summaries,
        "reservations": reservations_list
    })



@app.route('/user/dashboard', methods=["GET"])
@jwt_required()
# @cache.cached(timeout=30)
def user_dashboard():
    user = get_jwt_identity()
    
    if user['role'] != 'user':
        return jsonify(message="Unauthorized"), 403
    
    reservations = Reservation.query.filter_by(user_id=user['id']).order_by(Reservation.parking_time.desc()).all()

    active = next((r for r in reservations if r.leaving_time is None), None)
    active_info = None
    if active:
        lot = db.session.get(ParkingLot, active.spot.lot_id)
        active_info = {
            "lot_name": lot.name,
            "spot_id": active.spot_id,
            "parked_since": active.parking_time
        }

    total_spent = sum(r.cost for r in reservations if r.cost)
    recent = []
    for r in reservations[:5]:
        lot = db.session.get(ParkingLot, r.spot.lot_id)
        recent.append({
            "lot": lot.name,
            "spot_id": r.spot_id,
            "start": r.parking_time,
            "end": r.leaving_time,
            "cost": r.cost
        })

    return jsonify({
        "active_reservations": active_info,
        "total_reservations": len(reservations),
        "total_amount_spent": total_spent,
        "recent_history": recent
    })


@app.route('/user/lots', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
# @cache.cached(timeout=60, key_prefix='user_lots')
def get_user_lots():
    if request.method == 'OPTIONS':
        return '', 200  # CORS preflight success response

    lots = ParkingLot.query.all()
    result = []
    for lot in lots:
        available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
        result.append({
            "id": lot.id,
            "name": lot.name,
            "address": lot.address,
            "price": lot.price,
            "available_spots": available_spots
        })
    return jsonify(lots=result)

@app.route('/admin/reservations', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, key_prefix='admin_reservations')
def all_reservations():
    user = get_jwt_identity()
    if user['role'] != 'admin':
        return jsonify(message="Unauthorized"), 403

    reservations = Reservation.query.order_by(Reservation.parking_time.desc()).all()
    output = []
    for r in reservations:
        lot_name = r.spot.lot.name if r.spot and r.spot.lot else "Deleted Lot"
        output.append({
            "reservation_id": r.id,
            "username": r.user.username,
            "lot":lot_name,
            "spot_id": r.spot_id,
            "start": r.parking_time,
            "end": r.leaving_time,
            "cost": r.cost or 0
        })

    return jsonify(reservations=output)


@app.route('/run-task', methods=['POST'])
def run_task():
    from tasks import sample_task
    data = request.get_json()
    name = data.get('name', 'Guest')
    task = sample_task.delay(name)
    return jsonify({"message": "Task queued", "task_id": task.id}), 202

@app.route('/task-status/<task_id>')
def task_status(task_id):
    from celery.result import AsyncResult
    from celery_worker import celery
    result = AsyncResult(task_id, app=celery)
    return jsonify({"task_id": task_id, "status": result.status, "result": result.result})

#Test Email Task
@app.route('/send-test-email', methods=['POST'])
def send_test_email():
    data = request.get_json()
    recipient = data.get('email', 'test@example.com')
    # recipient = data.get('email', 'test@mailinator.com')
    from tasks import send_email
    task = send_email.delay(
        subject="Test Email from Parking App",
        recipient=recipient,
        body="Hello! This is a test email from your Flask app with Celery."
    )
    return jsonify({"message": "Email task queued!", "task_id": task.id}), 202

#Trigger Daily Reminder
@app.route('/send-daily-reminder', methods=['POST'])
def trigger_daily_reminder():
    from tasks import send_daily_reminder
    task = send_daily_reminder.delay()
    return jsonify({"message": "Daily reminder task queued!", "task_id": task.id}), 202

#Trigger Monthly Report
@app.route('/send-monthly-report', methods=['POST'])
def trigger_monthly_report():
    from tasks import send_monthly_report
    task = send_monthly_report.delay()
    return jsonify({"message": "Monthly report task queued!", "task_id": task.id}), 202

@app.route('/user/export', methods=['POST'])
@jwt_required()
def export_csv():
    user = get_jwt_identity()
    if user['role'] != 'user':
        return jsonify(message='Unauthorized'), 403
    
    from tasks import export_reservations_csv
    export_reservations_csv.delay(user['id'], user['username'])

    return jsonify(message="Your CSV export is being processed. You'll receive it via email.")

if __name__== '__main__':
    app.run(debug=True)   





