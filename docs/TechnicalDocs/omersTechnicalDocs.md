
---
layout: default
title: Ömers Technical Docs
parent: Technical Docs
nav_order: 2
---

# Ömers Technical Docs

Hier sind die technischen Dokumentationen von **Ömer**.

## Inhalt

- [Ömers Technical Docs](#ömers-technical-docs)
  - [Inhalt](#inhalt)
  - [Einleitung](#einleitung)
  - [Aufbau der Datenbank](#aufbau-der-datenbank)
    - [Datenbankdiagramm](#datenbankdiagramm)
  - [Login und Register-Funktion](#login-und-register-funktion)
    - [Wie erstellt man ein Admin Account](#wie-erstellt-man-ein-admin-account)
    - [LoginForm](#loginform)
    - [RegisterForm](#registerform)
    - [Login-Route](#login-route)
    - [Register-Route](#register-route)
  - [Authentifizierung und Autorisierung](#authentifizierung-und-autorisierung)

---

## Einleitung

Diese Seite enthält die technischen Details, die von Ömer erstellt wurden.

---

## Aufbau der Datenbank

Die Datenbankstruktur wurde wie folgt modelliert:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class AnimeList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    animes = db.relationship('AnimeList', backref='genre', lazy=True)
```

### Datenbankdiagramm

Ein visuelles Diagramm für die Datenbankstruktur:

```
User
+---------+--------------------+
| id      | Primary Key        |
| username| Unique, Not Null   |
| password| Not Null           |
| is_admin| Boolean (Default)  |
+---------+--------------------+

Genre
+---------+--------------------+
| id      | Primary Key        |
| name    | Unique, Not Null   |
+---------+--------------------+

AnimeList
+---------+--------------------+
| id      | Primary Key        |
| title   | Unique, Not Null   |
| genre_id| Foreign Key -> Genre.id |
| description | Optional       |
+---------+--------------------+
```

---

## Login und Register-Funktion

Die Login- und Register-Funktionen wurden mit **WTForms** implementiert und ermöglichen die Benutzerauthentifizierung.

### Wie erstellt man ein Admin Account

Admin-Command verwenden
In deinem Code gibt es ein Flask-CLI-Kommando, um einen Admin-Benutzer zu erstellen. Verwende diesen Befehl im Terminal:

bash
Code kopieren
flask create-admin <username> <password>
Ersetze <username> und <password> durch deinen gewünschten Benutzernamen und dein Passwort. Beispiel:

bash
flask create-admin Admin securepassword

### LoginForm

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
```

### RegisterForm

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
```

### Login-Route

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', form=form, error='Invalid username or password.')
    return render_template('login.html', form=form)
```

### Register-Route

```python
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
```

---

## Authentifizierung und Autorisierung

Zusätzliche Sicherheitsmaßnahmen wurden implementiert, um den Zugriff auf bestimmte Seiten zu kontrollieren:

1. **Login Required**: Schützt Routen vor unbefugtem Zugriff.
2. **Admin-Berechtigung**: Nur Admin-Benutzer haben Zugriff auf bestimmte Seiten.

---
Eintrag wurde am 16.12.2024 gemacht


