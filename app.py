from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, AddFeedbackForm, DeleteForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_test"
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)

with app.app_context():
    db.create_all()

@app.route('/')
def root():   
    return redirect('/register') 

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User.register(
                        username = form.username.data,
                        password = form.password.data,
                        email = form.email.data,
                        first_name = form.first_name.data,
                        last_name = form.last_name.data)
        
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username

        flash('Successfully Created Your Account!')
        return redirect(f'/users/{new_user.username}')

    return render_template('register-form.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data,
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            flash(f'Welcome back {user.first_name}!')
            return redirect(f'/users/{user.username}')
        else:
            flash("Invalid Username/Password.")
            return redirect('/login')

    return render_template('login-form.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    return redirect('/')

@app.route('/users/<username>')
def user_details(username):
    if "username" not in session or username != session['username']:
        flash("Please login first!")
        return redirect('/login')

    user = User.query.get(username)
    form = DeleteForm()

    return render_template('show-user.html', user=user, form=form)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if "username" not in session or username != session['username']:
            flash("Please login first!")
            return redirect('/login')

    user = User.query.get_or_404(username)

    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    
    return redirect('/register')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if "username" not in session or username != session['username']:
        flash("Please Login First.")
        return redirect('/login')
    
    form = AddFeedbackForm()

    if form.validate_on_submit():
        feedback = Feedback(
            title=form.title.data,
            content=form.content.data,
            username=username
        )

        db.session.add(feedback)
        db.session.commit()
        return redirect(f'/users/{username}')

    return render_template('feedback-form.html', form=form)

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):    
    feedback = Feedback.query.get(feedback_id)
    form = AddFeedbackForm(obj=feedback)

    if "username" not in session or feedback.username != session['username']:
        flash("Please Login First.")
        return redirect('/login')

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        return redirect(f'/users/{feedback.username}')

    return render_template('feedback-update-form.html', form=form)

@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
            flash("Please login first!")
            return redirect('/login')

    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{feedback.username}')