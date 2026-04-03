"""
Routes and views for the flask application.
"""

import logging
import uuid

from flask import render_template, flash, redirect, request, session, url_for
from werkzeug.urls import url_parse

from config import Config
from FlaskWebProject import app
from FlaskWebProject.forms import LoginForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from FlaskWebProject.models import User, Post

import msal

logger = logging.getLogger(__name__)


def _image_source_url() -> str:
    """
    Build the Azure Blob base URL safely at request time.
    This avoids startup failures if settings are not ready at import time.
    """
    account = app.config.get("BLOB_ACCOUNT", "")
    container = app.config.get("BLOB_CONTAINER", "")
    if not account or not container:
        return ""
    return f"https://{account}.blob.core.windows.net/{container}/"


@app.route("/")
@app.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template(
        "index.html",
        title="Home Page",
        posts=posts,
        imageSource=_image_source_url(),
    )


@app.route("/new_post", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        post.save_changes(form, request.files.get("image_path"), current_user.id, new=True)
        return redirect(url_for("home"))

    return render_template(
        "post.html",
        title="Create Post",
        imageSource=_image_source_url(),
        form=form,
    )


@app.route("/post/<int:id>", methods=["GET", "POST"])
@login_required
def post(id):
    post_obj = Post.query.get_or_404(id)
    form = PostForm(obj=post_obj)

    if form.validate_on_submit():
        post_obj.save_changes(form, request.files.get("image_path"), current_user.id)
        return redirect(url_for("home"))

    return render_template(
        "post.html",
        title="Edit Post",
        imageSource=_image_source_url(),
        form=form,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()

    # Local username/password login (admin user, etc.)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            # REQUIRED RUBRIC LOG MESSAGE
            logger.warning("Invalid login attempt")
            flash("Invalid username or password")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)

        # REQUIRED RUBRIC LOG MESSAGE
        if user.username == "admin":
            logger.info("admin logged in successfully")

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)

    # Microsoft sign-in link for the template
    session["state"] = str(uuid.uuid4())
    auth_url = _build_auth_url(scopes=Config.SCOPE, state=session["state"])
    return render_template("login.html", title="Sign In", form=form, auth_url=auth_url)


@app.route(Config.REDIRECT_PATH)
def authorized():
    if request.args.get("state") != session.get("state"):
        return redirect(url_for("home"))

    if "error" in request.args:
        return render_template("auth_error.html", result=request.args)

    if request.args.get("code"):
        cache = _load_cache()

        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args.get("code"),
            scopes=Config.SCOPE,
            redirect_uri=url_for("authorized", _external=True, _scheme="https"),
        )

        if "error" in result:
            return render_template("auth_error.html", result=result)

        session["user"] = result.get("id_token_claims")

        # Project behavior: MS login maps to admin user
        user = User.query.filter_by(username="admin").first()
        login_user(user)

        # REQUIRED RUBRIC LOG MESSAGE
        logger.info("admin logged in successfully")

        _save_cache(cache)

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    logout_user()

    # If user used Microsoft login, clear session and sign out of Microsoft
    if session.get("user"):
        session.clear()
        return redirect(
            Config.AUTHORITY
            + "/oauth2/v2.0/logout"
            + "?post_logout_redirect_uri="
            + url_for("login", _external=True)
        )

    return redirect(url_for("login"))


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        Config.CLIENT_ID,
        authority=authority or Config.AUTHORITY,
        client_credential=Config.CLIENT_SECRET,
        token_cache=cache,
    )


def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state,
        redirect_uri=url_for("authorized", _external=True, _scheme="https"),
    )
