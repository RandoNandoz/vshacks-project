import firebase_admin
import firebase_admin.auth as fb_auth
import dotenv
import requests
import os

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

bp = Blueprint("auth", __name__, url_prefix="/auth")

# initalize firebase app
# don't leak the credentials, please
cred = firebase_admin.credentials.Certificate(
    "pathfindr/vshacks-project-firebase-adminsdk-guz81-a5d561efbc.json"
)
firebase_admin.initialize_app(cred)


@bp.route("/register", methods=("GET", "POST"))
def register():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        if not email:
            error = "Email is required."
        elif not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                # create user in firebase
                user = fb_auth.create_user(
                    email=email,
                    email_verified=False,
                    password=password,
                    display_name=username,
                )
                print("Successfully created new user: {0}".format(user.uid))
                flash("Sucessfully Registered!", "success")

                # set session variables, redirect to index
                session.clear()
                session["user_id"] = user.uid
                session["username"] = username
                session["email"] = email

                return redirect(url_for("index"))

            except fb_auth.EmailAlreadyExistsError as e:
                error = e.default_message
                flash(error, "error")
        else:
            flash(error, "error")  # type: ignore # error guaranteed to be set, pylance is just dumb
    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email, password)

        if not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."

        if error is None:
            print(os.getcwd())
            dotenv.load_dotenv(".apikeys")
            FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
            FIREBASE_SIGN_IN_ENDPOINT = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
            data = {"email": email, "password": password}
            # send request to firebase
            res = requests.post(FIREBASE_SIGN_IN_ENDPOINT, data=data)
            if res.status_code == 200:
                # set session variables, redirect to index
                session.clear()
                session["user_id"] = res.json()["localId"]
                session["username"] = res.json()["displayName"]
                session["email"] = email
                flash("Successfully logged in!", "success")
                return redirect(url_for("index"))
                
    return render_template("auth/login.html")
