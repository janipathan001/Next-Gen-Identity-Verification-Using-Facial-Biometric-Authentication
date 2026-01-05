from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from models.user_model import register_user
from models.auth_model import login_user
from models.dashboard_model import get_user_profile, get_login_statistics, get_security_score
import os
import re

app = Flask(__name__)

# Configuration
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config["MONGO_URI"] = os.getenv('MONGO_URI', "mongodb://localhost:27017/face_auth_db")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Make MongoDB collections accessible
users_collection = mongo.db.users
login_logs_collection = mongo.db.login_logs

# ------------------- HELPER FUNCTIONS ------------------- #

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    return len(password) >= 8

def validate_name(name):
    """Validate name is not empty"""
    return len(name.strip()) > 0

# ------------------- ROUTES ------------------- #

@app.route("/")
def home():
    """Home/Welcome page route"""
    if "email" in session:
        return redirect(url_for("dashboard"))
    return render_template("welcome.html")

@app.route("/welcome")
def welcome():
    """Explicit welcome page route"""
    if "email" in session:
        return redirect(url_for("dashboard"))
    return render_template("welcome.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route"""
    if "email" in session:
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        try:
            # Get and sanitize form data
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            # Validation
            if not all([name, email, password]):
                flash("All fields are required", "danger")
                return render_template("register.html")
            
            if not validate_name(name):
                flash("Please enter a valid name", "danger")
                return render_template("register.html")
            
            if not validate_email(email):
                flash("Invalid email format", "danger")
                return render_template("register.html")
            
            if not validate_password(password):
                flash("Password must be at least 8 characters", "danger")
                return render_template("register.html")

            # Register user
            success, msg = register_user(name, email, password)
            if success:
                flash("Registration successful! Please login.", "success")
                return redirect(url_for("login"))
            else:
                flash(msg, "danger")
                return render_template("register.html")
                
        except Exception as e:
            flash(f"An error occurred during registration: {str(e)}", "danger")
            return render_template("register.html")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login route"""
    if "email" in session:
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        try:
            # Get and sanitize form data
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            # Validation
            if not all([email, password]):
                flash("Email and password are required", "danger")
                return render_template("login.html")
            
            if not validate_email(email):
                flash("Invalid email format", "danger")
                return render_template("login.html")

            # Authenticate user
            success, result = login_user(email, password)
            if success:
                session["email"] = email
                session.permanent = False  # Session expires when browser closes
                flash("Login successful! Welcome back.", "success")
                return redirect(url_for("dashboard"))
            else:
                flash(result, "danger")
                return render_template("login.html")
                
        except Exception as e:
            flash(f"An error occurred during login: {str(e)}", "danger")
            return render_template("login.html")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    """User dashboard route"""
    if "email" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("login"))

    try:
        email = session["email"]
        
        # Get user data
        profile = get_user_profile(email)
        
        if not profile:
            flash("User profile not found. Please login again.", "danger")
            session.pop("email", None)
            return redirect(url_for("login"))
        
        stats = get_login_statistics(email)
        security = get_security_score(stats.get("success_rate", 0))

        return render_template(
            "dashboard.html",
            profile=profile,
            stats=stats,
            security=security
        )
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "danger")
        return redirect(url_for("login"))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    """User logout route"""
    session.pop("email", None)
    flash("Logged out successfully", "info")
    return redirect(url_for("welcome"))

# ------------------- ERROR HANDLERS ------------------- #

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    flash("Page not found", "warning")
    return redirect(url_for("welcome"))

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    flash("An internal error occurred. Please try again.", "danger")
    return redirect(url_for("welcome"))

# ------------------- CONTEXT PROCESSOR ------------------- #

@app.context_processor
def inject_user():
    """Inject user session status into all templates"""
    return {
        'logged_in': 'email' in session,
        'user_email': session.get('email', None)
    }

# ------------------- RUN ------------------- #

if __name__ == "__main__":
    # Only use debug mode in development
    app.run(debug=True, host='0.0.0.0', port=5000)