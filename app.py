from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from models import Feedback, connect_db, db, User
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://bimgxxgngqzrkc:c495d199b50ad89509ca0130359d6cc8da88e3b41b5968796696ecab4b0e0327@ec2-54-146-84-101.compute-1.amazonaws.com:5432/da68np7ml6lhso"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "harrison"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# connect_db(app)
# db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def homepage():
    """Show homepage with links to site areas."""

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""

    form = RegisterForm()

    if form.validate_on_submit():
        f_name = form.first_name.data
        l_name = form.last_name.data
        email = form.email.data
        u_name = form.username.data
        pwd = form.password.data
        get_verified = User.verify(u_name)
        if not get_verified:
            
            hashed_pwd = User.register(pwd)

            user = User(first_name=f_name, last_name=l_name, email=email, username=u_name, password=hashed_pwd)
            db.session.add(user)
            db.session.commit()

            session["username"] = user.username
        else:
            flash("username already taken!")
            form.username.errors = ["username already taken."]
            return render_template("register.html", form=form)

        # on successful login, redirect to secret page
        return redirect("/secret")

    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(name, pwd)

        if user:
            session["username"] = user.username  # keep logged in
            return redirect(f"/user/{user.username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)
# end-login    

@app.route("/user/<username>")
def user_page(username):
    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")
    else:

        user = User.query.filter_by(username=username).first()
        return render_template("user_page.html", user=user)


@app.route("/secret")
def secret():
    """Example hidden page for logged-in users only."""

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")

        # alternatively, can return HTTP Unauthorized status:
        #
        # from werkzeug.exceptions import Unauthorized
        # raise Unauthorized()

    else:
        return render_template("secret.html")


@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("username")

    return redirect("/")


@app.route("/user/<username>/feedback", methods=["GET", "POST"])
def add_feedback(username):
    """Feedback """

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")
    else:

        form = FeedbackForm()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            feedback = Feedback(title=title, content=content, username=username)
            db.session.add(feedback)
            db.session.commit()


            return redirect(f"/user/{username}")

        else:
            return render_template("feedback.html", form=form)


# @app.route("/user/<username>/edit")
# def edit(username):
    
#     Feedback.title = request.form["title"]
#     Feedback.content = request.form["content"]
#     db.session.add(feedback)
#     db.session.commit()
#     return redirect(f"/user/{username}")

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def edit_feedback(feedback_id):
    """shows form and update the database after edit"""
    if "username" not in session:
        flash("Log in to add a feedback")
        return redirect("/")
    else:

        feedback = Feedback.query.get(feedback_id)
        form = FeedbackForm()
        if form.validate_on_submit():
            # this does not pre popullate my edit form. though i am using the same form 
            # to add and update
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            return redirect(f"/user/{feedback.username}")
        else:
            return render_template("edit_feedback.html", form=form)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    if "username" not in session:
        flash("You can not delete this feedback")
        return redirect("/")
    else:
        feedback = Feedback.query.get(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        flash("Successfully deleted!")
        return redirect(f"/user/{feedback.username}")
    
# wondering why this delete view works even as a get request
@app.route("/user/<username>/delete")
def delete_my_account(username):
    if "username" not in session:
        flash("You can not delete this account")
    else:
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
        session.pop("username")
        flash("Successfully deleted!")
        return redirect("/")