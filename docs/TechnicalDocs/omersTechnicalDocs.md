
---
layout: default
title: Ömers Technical Docs
parent: Technical Docs
nav_order: 2
---

# Ömers Technical Docs

(Erstellt am 16.12.2024, 23:15 Uhr)

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
  - [Ban-Funktion \& is\_banned-Spalte](#ban-funktion--is_banned-spalte)
  - [Erweiterungen und Fixes](#erweiterungen-und-fixes)
    - [Anime-Bilder über API hinzufügen](#anime-bilder-über-api-hinzufügen)
    - [Neues Datenbankmodell für Bilder](#neues-datenbankmodell-für-bilder)
    - [Fix für doppelte Einträge](#fix-für-doppelte-einträge)
    - [Vorteile der Änderungen](#vorteile-der-änderungen)
---

## Einleitung

Diese Seite enthält die technischen Details, die von Ömer erstellt wurden.  
Alle Beispiele beziehen sich auf eine Flask-Applikation mit SQLAlchemy, Flask-Login und WTForms.

---

## Aufbau der Datenbank

Die Datenbankstruktur wurde wie folgt modelliert (Beispiel):

```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)     # Admin-Flag
    is_banned = db.Column(db.Boolean, default=False)    # Ban-Flag

class AnimeList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    # evtl. foreign keys oder viele-zu-viele genre-relationen
    # Genre-FKs oder M2M mit Genre

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # Bei Many-to-One: animes = db.relationship('AnimeList', backref='genre', lazy=True)
```

### Datenbankdiagramm

```
User
+---------+--------------------+
| id      | PK                 |
| username| Unique, Not Null   |
| password| Not Null           |
| is_admin| Boolean (Default)  |
| is_banned| Boolean (Default) |
+---------+--------------------+

Genre
+---------+--------------------+
| id      | PK                 |
| name    | Unique, Not Null   |
+---------+--------------------+

AnimeList
+---------+--------------------+
| id      | PK                 |
| title   | Unique, Not Null   |
| description | Optional        |
| ... evtl. genre_id, etc.     |
+---------+--------------------+
```

---

## Login und Register-Funktion

Die Login- und Register-Funktionen wurden mit **WTForms** implementiert und ermöglichen die Benutzerauthentifizierung via Flask-Login.

### Wie erstellt man ein Admin Account

Wir haben ein Flask-CLI-Kommando definiert, um einen Admin-Benutzer zu erstellen. Beispiel:

```
flask create-admin <username> <password>
```

Das erstellt (oder überschreibt nicht existierende) Benutzer mit `is_admin=True`.

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
            # Ban-Check
            if user.is_banned:
                return render_template('login.html', form=form, error='This account is banned.')
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

Zusätzliche Sicherheitsmaßnahmen, um Seitenzugriff zu kontrollieren:

1. **Flask-Login** – Der Decorator `@login_required` schützt sensible Routen.  
2. **Admin-Berechtigung** – Nur `current_user.is_admin` darf bestimmte Views aufrufen. Beispiel:

```python
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return "Zugriff verweigert", 403
    users = User.query.all()
    return render_template('admin_users.html', users=users)
```

---

## Ban-Funktion & is_banned-Spalte

```bash
# Datenbank-Spalte hinzufügen
flask db upgrade
```

```python
@app.route('/admin/ban_user/<int:user_id>', methods=['POST'])
def admin_ban_user(user_id):
    target_user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    if action == 'ban':
        target_user.is_banned = True
    elif action == 'unban':
        target_user.is_banned = False
    db.session.commit()
    return redirect(url_for('admin_users'))
```

## Erweiterungen und Fixes

### Anime-Bilder über API hinzufügen

- Wir haben die Funktionalität implementiert, um fehlende Bilder in der Anime-Datenbank zu aktualisieren.
- Dazu haben wir einen festen API-Key für die TMDB API (`TMDB_API_KEY`) genutzt.
- Mit dem CLI-Befehl `flask update-images` können alle Einträge aktualisiert werden.
- Die Methode `add_images_to_anime(app, TMDB_API_KEY)` wurde hinzugefügt, um Bilder basierend auf der API zu fetchen und in der Datenbank zu speichern.

### Neues Datenbankmodell für Bilder

- In der Tabelle `AnimeList` wurde eine neue Spalte `image_url` hinzugefügt, um die URL für die Anime-Bilder zu speichern.

```python
class AnimeList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)  # URL für das Bild
```

- Nach Hinzufügen der Spalte wurde `flask db upgrade` ausgeführt, um die Datenbank zu migrieren.

### Fix für doppelte Einträge

- Es wurde festgestellt, dass die Tabelle `AnimeList` doppelte Einträge enthielt.
- Dies wurde behoben, indem die `title`-Spalte als `unique=True` markiert wurde und bestehende doppelte Einträge bereinigt wurden.
- Die SQLAlchemy-Logik prüft jetzt beim Einfügen, ob der Titel bereits existiert.

```python
existing_anime = AnimeList.query.filter_by(title=anime_title).first()
if not existing_anime:
    new_anime = AnimeList(title=anime_title, description=anime_description, image_url=image_url)
    db.session.add(new_anime)
    db.session.commit()
```

### Vorteile der Änderungen

- Die Anime-Liste enthält jetzt Bilder, die aus der API automatisch hinzugefügt werden.
- Es gibt keine doppelten Einträge mehr in der Datenbank.
- Die Anwendung bietet einen CLI-Befehl zur einfachen Aktualisierung der Bilder.

---
