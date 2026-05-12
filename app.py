from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file
from database import get_connection
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pymysql
from io import BytesIO

app = Flask(__name__)
app.secret_key = "resume_secret_key"

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            print(f"Error: {e}")
            flash("Email already exists!", "danger")
        finally:
            conn.close()

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("profile"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------- PROFILE ----------------
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        file = request.files.get("profile_pic")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            cursor.execute(
                "UPDATE users SET photo=%s WHERE id=%s",
                (filename, session["user_id"])
            )
            conn.commit()
            flash("Profile photo updated successfully!", "success")
            return redirect(url_for("profile"))

    cursor.execute("SELECT id, name, email, photo FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()
    conn.close()

    return render_template("profile.html", user=user)

# ---------------- RESUME FORM ----------------
@app.route("/resume_form", methods=["GET", "POST"])
def resume_form():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        education = request.form.get("education")
        skills = request.form.get("skills")
        experience = request.form.get("experience")
        projects = request.form.get("projects") # Links are typed directly here
        template = request.form.get("template") or "classic"

        cursor.execute("SELECT resume_id FROM resumes WHERE user_id=%s", (session["user_id"],))
        existing_resume = cursor.fetchone()

        try:
            if existing_resume:
                cursor.execute("""
                    UPDATE resumes 
                    SET education=%s, skills=%s, experience=%s, projects=%s, template=%s 
                    WHERE user_id=%s
                """, (education, skills, experience, projects, template, session["user_id"]))
            else:
                cursor.execute("""
                    INSERT INTO resumes (user_id, education, skills, experience, projects, template) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (session["user_id"], education, skills, experience, projects, template))

            conn.commit()
            flash("Resume updated successfully!", "success")
        except Exception as e:
            conn.rollback()
            print(f"Database Error: {e}")
            flash(f"Error saving data: {e}", "danger")
        finally:
            conn.close()

        return redirect(url_for("resume_form"))

    cursor.execute("SELECT * FROM resumes WHERE user_id=%s", (session["user_id"],))
    resume = cursor.fetchone()
    
    cursor.execute("SELECT name, email FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()
    conn.close()

    return render_template("resume_form.html", user=user, resume=resume)

# ---------------- RESUME PREVIEW ----------------
@app.route("/resume_preview")
def resume_preview():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT name, email, photo FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM resumes WHERE user_id=%s", (session["user_id"],))
    resume = cursor.fetchone()
    conn.close()

    template = resume['template'] if resume and resume['template'] else "classic"
    template_file = f"resume_preview_{template}.html"
    return render_template(template_file, user=user, resume=resume)

# ---------------- PORTFOLIO ----------------
@app.route("/portfolio")
def portfolio():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM resumes WHERE user_id=%s", (session["user_id"],))
    resume = cursor.fetchone()

    try:
        cursor.execute("SELECT * FROM portfolio WHERE user_id=%s", (session["user_id"],))
        portfolio_data = cursor.fetchone()
    except:
        portfolio_data = None

    conn.close()

    return render_template("portfolio.html", user=user, resume=resume, portfolio=portfolio_data)

if __name__ == "__main__":
    app.run(debug=True)