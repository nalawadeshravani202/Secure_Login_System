from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

from models import db, User
from forms import RegisterForm, LoginForm

auth = Blueprint("auth", __name__)
bcrypt = Bcrypt()


@auth.route("/")
def home():
    return redirect(url_for("auth.login"))


@auth.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    form = RegisterForm()

    if form.validate_on_submit():

        existing_email = User.query.filter_by(email=form.email.data).first()

        if existing_email:
            flash("Email already exists!", "danger")
            return redirect(url_for("auth.register"))

        existing_username = User.query.filter_by(username=form.username.data).first()

        if existing_username:
            flash("Username already exists!", "danger")
            return redirect(url_for("auth.register"))

        hashed_password = bcrypt.generate_password_hash(
            form.password.data
        ).decode("utf-8")

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful! Please Login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(
                user.password,
                form.password.data):

            login_user(user)

            flash("Login Successful!", "success")

            return redirect(url_for("auth.dashboard"))

        flash("Invalid Email or Password!", "danger")

    return render_template("login.html", form=form)


@auth.route("/dashboard")
@login_required
def dashboard():

    return render_template("dashboard.html")


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully.", "success")

    return redirect(url_for("auth.login"))