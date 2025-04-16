import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "Yourpass")  # Secure it
app.config["MYSQL_DB"] = "databasename"

mysql = MySQL(app)

# Flask-Mail Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "abc@gmail.com"  # Your Gmail address
app.config["MAIL_PASSWORD"] = "hzxt xjlm ---- ----"  # The app-specific password generated
mail = Mail(app)

# File Upload Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Utility to check allowed file extensions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[1], password):
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password),
            )
            mysql.connection.commit()
            cursor.close()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"An error occurred during registration: {e}", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/animals")
def animals():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM animals")
        animal_data = cursor.fetchall()
        cursor.close()
        return render_template("animals.html", animals=animal_data)
    except Exception as e:
        flash(f"Error fetching animals: {e}", "danger")
        return redirect(url_for("home"))


@app.route("/donate", methods=["GET", "POST"])
def donate():
    if request.method == "POST":
        name = request.form["name"]
        animal = request.form["animal"]
        email = request.form["email"]
        description = request.form["description"]

        # Handle file upload
        file = request.files.get("image")
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
        else:
            flash("Invalid or no image file uploaded.", "warning")

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO donations (name, animal, email, description, image_path) VALUES (%s, %s, %s, %s, %s)",
                (name, animal, email, description, filename),
            )
            mysql.connection.commit()
            cursor.close()
            
            flash("Donation details submitted successfully!", "success")
            
            # Sending notification email to the admin
            admin_email = "sakshipawar9846@example.com"  # Replace with your admin email address
            subject = "New Animal Donation Submission"
            message_body = f"""
            A new donation has been submitted.

            Name: {name}
            Animal: {animal}
            Contact Email: {email}
            Description: {description}
            Image Path: {filename if filename else "No image uploaded"}
            """
            
            # Sending email to admin
            msg = Message(subject, sender="abc@gmail.com", recipients=[admin_email])
            msg.body = message_body
            try:
                mail.send(msg)
                print("Notification email sent successfully!")
            except Exception as e:
                print(f"Failed to send email: {e}")
        
        except Exception as e:
            flash(f"Error submitting donation: {e}", "danger")
        
        return redirect(url_for("donate"))

    return render_template("donate.html")


@app.route("/adopt", methods=["GET", "POST"])
def adopt():
    if request.method == "POST":
        name = request.form["name"]
        animal = request.form["animal"]
        email = request.form["email"]

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO adoption_requests (name, animal, email) VALUES (%s, %s, %s)",
                (name, animal, email),
            )
            mysql.connection.commit()
            cursor.close()

            admin_email = "admin@example.com"  # Replace with admin's email
            subject = "New Adoption Request"
            message_body = f"Name: {name}\nAnimal: {animal}\nContact Email: {email}"

            msg = Message(subject, sender=app.config["MAIL_USERNAME"], recipients=[admin_email])
            msg.body = message_body
            mail.send(msg)

            flash("Adoption request submitted successfully!", "success")
        except Exception as e:
            flash(f"Error submitting adoption request: {e}", "danger")

        return redirect(url_for("home"))

    return render_template("adopt.html")




@app.route("/champs", methods=["GET", "POST"])
def champs():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        camp_type = request.form["camp_type"]

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO champs (name, email, phone, camp_type) VALUES (%s, %s, %s, %s)",
                (name, email, phone, camp_type),
            )
            mysql.connection.commit()
            cursor.close()

            flash("Successfully registered for the camp!", "success")

            # Send confirmation email
            subject = "Champs Registration Successful"
            message_body = f"""
            Dear {name},

            Thank you for registering for the {camp_type} camp!
            We look forward to seeing you.

            Best regards,
            The Champs Team 🐾
            """

            msg = Message(subject, sender=app.config["MAIL_USERNAME"], recipients=[email])
            msg.body = message_body
            mail.send(msg)

        except Exception as e:
            flash(f"Error: {e}", "danger")

        return redirect(url_for("champs"))  # ✅ Inside function

    return render_template("champs.html")  # ✅ Inside function

if __name__ == "__main__":
    app.run(debug=True)
