# app.py
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import click
from sqlalchemy import func

# Lokales db.py (Modelle, Forms, usw.)
from db import db, User, RegisterForm, LoginForm, AnimeList, Genre, Bookmark
from db import add_initial_anime_data, add_images_to_anime

# Zusätzliche Form-Klasse für PW-Reset
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import InputRequired, EqualTo

#############################
# HIER: DEIN FEST VERANKERTER API-KEY
#############################
TMDB_API_KEY = "ef7f5e8e25c2a88ca040df3c3abe7518"
#############################

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SECRET_KEY'] = 'thisisasecretkey'  # In Produktion niemals hart im Code!

    # Flask-Extensions
    bcrypt = Bcrypt(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ----------------------------------------------------
    #                  CLI COMMANDS
    # ----------------------------------------------------
    @app.cli.command('init-db')
    def init_db_command():
        with app.app_context():
            db.create_all()
            add_initial_anime_data(app)
            add_images_to_anime(app, TMDB_API_KEY)
        click.echo('Database initialized, anime data added, and images fetched!')

    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('password')
    def create_admin_command(username, password):
        with app.app_context():
            existing = User.query.filter_by(username=username).first()
            if existing:
                click.echo(f"User '{username}' exists already.")
                return
            hashed = bcrypt.generate_password_hash(password).decode('utf-8')
            new_admin = User(username=username, password=hashed, is_admin=True)
            db.session.add(new_admin)
            db.session.commit()
            click.echo(f"Admin '{username}' created.")

    # ----------------------------------------------------
    #                  ROUTES
    # ----------------------------------------------------
    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                if user.is_banned:
                    return render_template('login.html', form=form, error='This account is banned.')
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', form=form, error='Invalid username or password.')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        return render_template('register.html', form=form)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/marketplace')
    @login_required
    def marketplace():
        return render_template('marketplace.html')

    @app.route('/settings')
    @login_required
    def settings():
        return render_template('settings.html')

    class ResetPasswordForm(FlaskForm):
        old_password = PasswordField(validators=[InputRequired()])
        new_password = PasswordField(
            validators=[InputRequired(), EqualTo('confirm_password', message='Passwords must match')]
        )
        confirm_password = PasswordField(validators=[InputRequired()])
        submit = SubmitField("Change Password")

    @app.route('/reset_password', methods=['GET', 'POST'])
    @login_required
    def reset_password():
        form = ResetPasswordForm()
        if form.validate_on_submit():
            if not bcrypt.check_password_hash(current_user.password, form.old_password.data):
                return render_template('reset_password.html', form=form, error='Old password is incorrect.')
            hashed_new = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = hashed_new
            db.session.commit()
            return redirect(url_for('settings'))
        return render_template('reset_password.html', form=form)

    @app.route('/animelist', methods=['GET'])
    @login_required
    def animelist():
        sort_options = {
            'score': AnimeList.score,
            'titel': AnimeList.titel,
            'releasedate': AnimeList.releasedate
        }

        sort_by = request.args.get('sort_by', 'score')
        order = request.args.get('order', 'desc')

        selected_genres = request.args.getlist('genre')
        selected_categories = request.args.getlist('category')

        all_genres = Genre.query.order_by(Genre.name.asc()).all()
        distinct_categories = db.session.query(AnimeList.Category).distinct().order_by(AnimeList.Category.asc()).all()
        all_categories = [c[0] for c in distinct_categories]

        query = AnimeList.query

        if selected_genres:
            query = (query
                     .join(AnimeList.genres)
                     .filter(Genre.name.in_(selected_genres))
                     .group_by(AnimeList.anime_id)
                     .having(func.count(AnimeList.anime_id) == len(selected_genres)))

        if selected_categories:
            query = query.filter(AnimeList.Category.in_(selected_categories))

        sort_column = sort_options.get(sort_by, AnimeList.score)
        if order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        animes = query.limit(200).all()

        user_bookmarked_ids = {bookmark.anime_id for bookmark in Bookmark.query.filter_by(user_id=current_user.id).all()}

        return render_template(
            'animelist.html',
            animes=animes,
            all_genres=all_genres,
            selected_genres=selected_genres,
            all_categories=all_categories,
            selected_categories=selected_categories,
            current_sort=sort_by,
            current_order=order,
            user_bookmarked_ids=user_bookmarked_ids
        )

    @app.route('/bookmark/<int:anime_id>', methods=['POST'])
    @login_required
    def bookmark(anime_id):
        existing = Bookmark.query.filter_by(user_id=current_user.id, anime_id=anime_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            flash('Bookmark removed!', 'success')
        else:
            new_bookmark = Bookmark(user_id=current_user.id, anime_id=anime_id)
            db.session.add(new_bookmark)
            db.session.commit()
            flash('Bookmark added!', 'success')
        return redirect(url_for('animelist'))

    @app.route('/my_bookmarks', methods=['GET'])
    @login_required
    def my_bookmarks():
        bookmarked_animes = AnimeList.query.join(Bookmark).filter(Bookmark.user_id == current_user.id).all()
        return render_template('my_bookmarks.html', bookmarked_animes=bookmarked_animes)

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            return "Zugriff verweigert", 403

        user_count = User.query.count()
        banned_users = User.query.filter_by(is_banned=True).count()
        anime_count = AnimeList.query.count()

        return render_template(
            'admin_dashboard.html',
            user_count=user_count,
            banned_users=banned_users,
            anime_count=anime_count
        )

    @app.route('/admin/users')
    @login_required
    def admin_users():
        if not current_user.is_admin:
            return "Zugriff verweigert", 403
        users = User.query.all()
        return render_template('admin_users.html', users=users)

    @app.route('/admin/ban_user/<int:user_id>', methods=['POST'])
    @login_required
    def admin_ban_user(user_id):
        if not current_user.is_admin:
            return "Zugriff verweigert", 403
        target_user = User.query.get_or_404(user_id)
        action = request.form.get('action')
        if action == 'ban':
            target_user.is_banned = True
        elif action == 'unban':
            target_user.is_banned = False
        db.session.commit()
        return redirect(url_for('admin_users'))

    @app.route('/admin/reset_user_password/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def admin_reset_user_password(user_id):
        if not current_user.is_admin:
            return "Zugriff verweigert", 403
        target_user = User.query.get_or_404(user_id)
        if request.method == 'POST':
            new_pw = request.form.get('new_password')
            hashed = bcrypt.generate_password_hash(new_pw).decode('utf-8')
            target_user.password = hashed
            db.session.commit()
            return redirect(url_for('admin_users'))
        return render_template('admin_reset_password.html', user=target_user)

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
