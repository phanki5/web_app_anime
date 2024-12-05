from flask import Flask, render_template, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_bcrypt import Bcrypt
import click
from flask.cli import with_appcontext
from db import db, User, RegisterForm, LoginForm, AnimeList, Genre, add_initial_anime_data



def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SECRET_KEY'] = 'thisisasecretkey'
    
    bcrypt = Bcrypt(app)
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database."""
        with app.app_context():
            db.create_all()
            add_initial_anime_data(app)
        click.echo('Database initialized! and Data added')
    
    @app.route('/')
    def index():
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', form=form, 
                                    error='Invalid username or password.')
        return render_template('login.html', form=form)
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
    # Alle Anime laden
        animes = AnimeList.query.all()
        return render_template('dashboard.html', animes=animes)

    @app.route('/animelist')
    @login_required
    def animelist():
    # Alle Anime laden
        animes = AnimeList.query.all()
        return render_template('animelist.html', animes=animes)
    
    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        return render_template('register.html', form=form)
    
    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)