---
layout: default
title: "Technical Docs"
parent: "AnimeMarketPlace"  
nav_order: 1
---

Erstellt: 16.12.2024  
Aktualisiert: 13.02.2025  

---

## Inhaltsverzeichnis

1. [Einleitung](#einleitung)  
2. [Login und Registrierung](#1-login-und-registrierung)  
3. [Authentifizierung und Autorisierung](#2-authentifizierung-und-autorisierung)  
4. [Ban-Funktion](#3-ban-funktion)  
5. [Funktionalitäten](#4-funktionalitäten)  
   - [Marketplace](#marketplace)  
   - [Request und Response (Nachrichtensystem)](#request-und-response-nachrichtensystem)  
   - [Bookmarks](#bookmarks)  
   - [Admin-Dashboard](#admin-dashboard)  
   - [Passwort-Zurücksetzen (Settings)](#passwort-zurücksetzen-settings)  
   - [Inbox](#inbox)  
6. [Erweiterungen und Fixes](#5-erweiterungen-und-fixes)  
   - [Bilderintegration](#bilderintegration)  
   - [Vermeidung doppelter Einträge](#vermeidung-doppelter-einträge)  
   - [Fehlerbehebung bei Responses](#fehlerbehebung-bei-responses)  
   - [Vorteile der Anpassungen](#vorteile-der-anpassungen)  
7. [Verwendete Technologien](#7-verwendete-technologien)  
8. [Zusammenfassung](#zusammenfassung)  

---

## Einleitung

Diese Dokumentation beschreibt alle wesentlichen Funktionalitäten der Anwendung in einer einheitlichen Form. Der Fokus liegt auf den konzeptionellen Abläufen und Besonderheiten der Plattform, ohne explizite Referenzen zu Datenbank-Details oder Quellcode.

---

## 1. Login und Registrierung

Die Anwendung bietet eine grundlegende Authentifizierungsfunktion:

- **Registrierung**  
  Nutzerinnen und Nutzer legen mit Benutzername und Passwort ein Konto an.  
  Ist der Benutzername bereits vergeben, wird eine Fehlermeldung ausgegeben.

- **Login**  
  Nach erfolgreicher Registrierung erfolgt die Anmeldung mit denselben Daten.  
  Bei korrekter Eingabe werden Nutzer*innen in den internen Bereich weitergeleitet.

Mit dieser Basis können alle Personen personalisierte Aktionen durchführen, z. B. das Erstellen oder Anfragen von Angeboten.

### Codebeispiele

```python
# Login-Route (Beispiel)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Optional: Ban-Check
            if user.is_banned:
                flash('This account is banned.')
                return render_template('login.html', form=form)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)


# Registrierungs-Route (Beispiel)
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
```

---

## 2. Authentifizierung und Autorisierung

Zur Steuerung der Zugriffe kommen folgende Prinzipien zum Einsatz:

- **Login-Prüfung**: Nur korrekt angemeldete Personen erhalten Zugriff auf geschützte Bereiche.  
- **Rollenverwaltung**: Administratorinnen und Administratoren verfügen über weiterführende Rechte, z. B. zum Sperren von Konten.

Damit ist sichergestellt, dass nur berechtigte Personen bestimmte Funktionen ausführen dürfen.

### Codebeispiele
```python
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user, login_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Seite, auf die umgeleitet wird, falls user nicht eingeloggt ist

# --------------------------------------------------
# Datenbankmodell (Beispiel)
# --------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Flag für Adminrechte

    # Flask-Login braucht diese Methode:
    def get_id(self):
        return str(self.id)

# --------------------------------------------------
# Flask-Login: User loader
# --------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --------------------------------------------------
# Beispiel: Geschützte Route
# --------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    # Nur eingeloggte Nutzer können diese Seite sehen
    return render_template('dashboard.html')

# --------------------------------------------------
# Beispiel: Admin-Route
# --------------------------------------------------
@app.route('/admin_only')
@login_required
def admin_only():
    if not current_user.is_admin:
        # Falls kein Admin: Zugriff verweigert
        return "Zugriff verweigert", 403
    # Falls Admin: Zugriff erlaubt
    return render_template('admin_panel.html')

# --------------------------------------------------
# Login Route (Kurzfassung)
# --------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Beispielhafter Code: Formular auswerten,
    # Nutzer in der DB suchen und bei Erfolg einloggen.
    if ...:  # Bedingung: validiertes Formular
        user = User.query.filter_by(username='demo').first()
        # Passwortcheck etc.
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html')
```
---

## 3. Ban-Funktion

Um Verstöße gegen Richtlinien zu ahnden, existiert eine Ban-Funktion:

- **Sperren**  
  Wird ein Konto als problematisch eingestuft, kann eine Administratorin bzw. ein Administrator dieses sperren.  
  Gesperrte Personen können sich zwar anmelden, erhalten aber nur eine Fehlermeldung und keinen Zugriff auf interne Inhalte.

- **Entsperren**  
  Bei Bedarf lässt sich die Sperre durch einen administrativen Eingriff wieder aufheben.

Auf diese Weise bleibt die Plattform geschützt vor dauerhaften Störungen und Missbrauch.

### Codebeispiele
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)  # Wichtig für Ban-Funktion

@app.route('/admin/ban_user/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    # Zugriff nur für Admins
    if not current_user.is_admin:
        return "Zugriff verweigert", 403
    
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')  # 'ban' oder 'unban'
    
    # Ban-Status setzen
    user.is_banned = (action == 'ban')
    db.session.commit()

    return redirect(url_for('admin_dashboard'))
```

---

## 4. Funktionalitäten

### Marketplace

Ein Kernbereich der Anwendung ist der Marketplace, wo Angebote eingestellt werden können:

- **Übersicht**  
  Alle Einträge sind in einer Liste ersichtlich und enthalten wichtige Angaben wie Titel und Preis.  
- **Eintrag erstellen**  
  Über ein Formular können Nutzer*innen ein neues Angebot anlegen.  
- **Verwaltung**  
  Eigene Einträge lassen sich bearbeiten oder entfernen, um den Marktplatz aktuell zu halten.

  ### Codebeispiele
  ```python

  class OfferList(db.Model):
    offer_id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    Offer_Type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    @app.route("/marketplace")
    @login_required
    def marketplace():
    """Zeigt eine Übersicht aller verfügbaren Angebote."""
    offers = OfferList.query.all()
    return render_template("marketplace.html", offers=offers)

    @ app.route("/marketplace_entry", methods=["GET", "POST"])
    @login_required
    def marketplace_entry():
    """Formular zum Erstellen eines neuen Angebots."""
    if request.method == "POST":
        anime_name = request.form.get("anime_name")
        price = request.form.get("price")
        offer_type = request.form.get("offer_type")

        new_offer = OfferList(
            titel=anime_name,
            price=float(price),
            Offer_Type=offer_type,
            user_id=current_user.id
        )
        db.session.add(new_offer)
        db.session.commit()
        return redirect(url_for("marketplace"))

    return render_template("marketplace_entry.html")
  ```

### Request und Response (Nachrichtensystem)

Zusätzlich bietet das System eine interne Nachrichtenabwicklung zwischen Anbietenden und Interessierten:

- **Request (Anfrage)**  
  Bei Interesse an einem Angebot können Nutzer*innen eine Nachricht direkt an die anbietende Person senden.  
- **Response (Antwort)**  
  Die Anbieterin bzw. der Anbieter beantwortet diese Anfrage. Bei Bedarf lassen sich weitere Antworten hinzufügen, was zu einem übersichtlichen Gesprächsverlauf führt.

Hierdurch wird die Kommunikation vereinfacht, da alle Details direkt geklärt werden können, ohne externe Plattformen zu nutzen.

### Codebeispiele
```python
class Request(db.Model):
    __tablename__ = "request"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey("offer_list.offer_id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    responded = db.Column(db.Boolean, default=False)  # Kennzeichnet, ob die Anfrage bereits beantwortet wurde

class Response(db.Model):
    __tablename__ = "response"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey("offer_list.offer_id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey("request.id"), nullable=False)
    parent_response_id = db.Column(db.Integer, db.ForeignKey("response.id"), nullable=True)

@app.route("/request_offer/<int:offer_id>", methods=["POST"])
@login_required
def request_offer(offer_id):
    """Route zum Senden einer Anfrage (Request) für ein bestimmtes Angebot."""
    offer = OfferList.query.get_or_404(offer_id)

    # Verhindert, dass der Anbieter sich selbst eine Anfrage schickt
    if offer.user_id == current_user.id:
        flash("You cannot request your own offer.", "danger")
        return redirect(url_for("marketplace"))

    message = request.form.get("message")
    if not message:
        flash("Message is missing.", "danger")
        return redirect(url_for("marketplace"))

    new_request = Request(
        user_id=current_user.id,
        offer_id=offer_id,
        message=message,
        responded=False
    )
    db.session.add(new_request)
    db.session.commit()
    flash("Request sent successfully!", "success")
    return redirect(url_for("marketplace"))

@app.route("/send_response/<int:request_id>", methods=["POST"])
@login_required
def send_response(request_id):
    """Route zum Antworten (Response) auf eine eingegangene Anfrage."""
    req = Request.query.get_or_404(request_id)

    # Nur der Anbieter, dem das Offer gehört, darf antworten
    if req.offer.user_id != current_user.id:
        return "Zugriff verweigert", 403

    response_text = request.form.get("response_message", "")
    new_response = Response(
        user_id=current_user.id,
        offer_id=req.offer_id,
        message=response_text,
        request_id=request_id
    )
    db.session.add(new_response)

    # Markiere die ursprüngliche Anfrage als beantwortet
    req.responded = True
    db.session.commit()

    flash("Response sent successfully.", "success")
    return redirect(url_for("inbox", selected_req_id=request_id))

``` 

### Bookmarks

Für eine persönliche Verwaltung von Einträgen steht eine Merkliste zur Verfügung:

- **Bookmark setzen**  
  Ein Klick fügt den gewünschten Inhalt der eigenen Liste hinzu.  
- **Bookmark entfernen**  
  Die Einträge lassen sich jederzeit wieder von der Merkliste nehmen.  
- **Merkliste anzeigen**  
  Zeigt alle gespeicherten Inhalte in einer eigenen Ansicht an.

### Codebeispiele
```python
class Bookmark(db.Model):
    __tablename__ = "bookmarks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey("anime_list.anime_id"), nullable=False)

@app.route("/bookmark/<int:anime_id>", methods=["POST"])
@login_required
def bookmark(anime_id):
    """Fügt das angegebene Anime-Objekt zur Merkliste hinzu oder entfernt es, falls bereits vorhanden."""
    existing_bookmark = Bookmark.query.filter_by(user_id=current_user.id, anime_id=anime_id).first()
    
    if existing_bookmark:
        # Löst das Bookmark auf
        db.session.delete(existing_bookmark)
        db.session.commit()
        flash("Bookmark removed!", "success")
    else:
        # Legt ein neues Bookmark an
        new_bookmark = Bookmark(user_id=current_user.id, anime_id=anime_id)
        db.session.add(new_bookmark)
        db.session.commit()
        flash("Bookmark added!", "success")
    
    return redirect(url_for("animelist"))

```

### Admin-Dashboard

Administrierende haben Zugriff auf ein eigenes Dashboard, in dem sie verschiedene Kennzahlen sehen und verwaltungstechnische Funktionen ausführen können:

- **Statistiken**  
  Anzeige der Anzahl von Nutzenden, gesperrten Konten oder erstellten Angeboten.  
- **Ban- und Unban-Aktionen**  
  Verwaltung auffälliger Benutzerkonten.

  ### Codebeispiele
```python
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    """Beispielhafte Admin-Übersicht mit grundlegenden Statistiken."""
    # Zugriff nur für Admins
    if not current_user.is_admin:
        return "Zugriff verweigert", 403
    
    # Einige Beispielwerte
    user_count = User.query.count()
    banned_users_count = User.query.filter_by(is_banned=True).count()
    offers_count = OfferList.query.count()
    
    return render_template(
        "admin_dashboard.html",
        user_count=user_count,
        banned_users_count=banned_users_count,
        offers_count=offers_count
    )

```

### Passwort-Zurücksetzen (Settings)

Um die Kontosicherheit zu erhöhen, besteht die Möglichkeit, das Passwort eigenständig zu ändern:

1. Eingabe des alten Passworts zur Verifizierung  
2. Festlegen des neuen Passworts (mit doppelter Eingabe)  
3. Übernahme der Änderung und sofortige Wirksamkeit  

### Codebeispiele
```python
class ResetPasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        EqualTo("confirm_password", message="Passwords must match")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Change Password")

@app.route("/reset_password", methods=["GET", "POST"])
@login_required
def reset_password():
    """Route zum Ändern des eigenen Passworts."""
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Überprüfung, ob das alte Passwort korrekt ist
        if not bcrypt.check_password_hash(current_user.password, form.old_password.data):
            flash("Old password is incorrect.", "danger")
            return render_template("reset_password.html", form=form)
        
        # Neues Passwort hashen und speichern
        hashed_new = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
        current_user.password = hashed_new
        db.session.commit()
        
        flash("Password changed successfully.", "success")
        return redirect(url_for("settings"))  # Annahme: "settings" ist eine entsprechende Seite
    return render_template("reset_password.html", form=form)

```

### Inbox

Alle eingehenden und beantworteten Anfragen werden in einer zentralen Inbox zusammengeführt:

- **Offene Anfragen**  
  Zeigt, welche Nachrichten noch unbeantwortet sind.  
- **Abgeschlossene Gespräche**  
  Bietet Überblick über frühere Unterhaltungen.  

So lassen sich sämtliche Konversationen an einem Ort verwalten und bequem fortführen.

### Codebeispiele
```python
@app.route("/inbox")
@login_required
def inbox():
    """
    Zeigt dem aktuellen User (Anbieter) alle eingegangenen Anfragen:
    - 'pending_requests': Anfragen, die noch nicht beantwortet wurden
    - 'responded_requests': Anfragen, zu denen es bereits eine Antwort gibt
    """
    # Nur Anfragen anzeigen, deren Angebot zum aktuellen Nutzer gehört
    pending_requests = Request.query.join(OfferList).filter(
        OfferList.user_id == current_user.id,
        Request.responded == False
    ).all()

    responded_requests = Request.query.join(OfferList).filter(
        OfferList.user_id == current_user.id,
        Request.responded == True
    ).all()

    return render_template(
        "inbox.html",
        pending_requests=pending_requests,
        responded_requests=responded_requests
    )

```
---

## 5. Erweiterungen und Fixes

### Bilderintegration

Werden für Einträge (z. B. Serien oder Artikel) Bilder benötigt, kann ein optionaler API-Zugriff genutzt werden, um fehlendes Bildmaterial automatisch zu ergänzen. Dadurch erhalten die Einträge ein einheitliches Erscheinungsbild.

### Vermeidung doppelter Einträge

Bei der Erstellung neuer Inhalte wird geprüft, ob ein Eintrag mit derselben Bezeichnung bereits existiert. Auf diese Weise entstehen keine Duplikate, was die Daten konsistent hält.

### Fehlerbehebung bei Responses

Es wurde ein Problem festgestellt, bei dem Antworten (Responses) nicht angezeigt wurden. Dieser Fehler hing mit einem Datenbankfeld zusammen, das ursprünglich auf `0` stand und dadurch die Darstellung verhinderte. Durch eine Anpassung auf den Wert `1` werden nun alle Responses korrekt angezeigt.

### Vorteile der Anpassungen

- **Bessere Übersichtlichkeit**: Keine mehrfachen Inhalte, klare Anzeige aller Angebote und Meldungen.  
- **Höhere Zuverlässigkeit**: Dank automatischer Bildpflege und korrekter Anzeige des Nachrichtenverlaufs.  
- **Einfache Administration**: Administrierende können gesperrte Konten, Statistiken und sämtliche Plattform-Daten überblicken.  

---

## 7. Verwendete Technologien

In der Entwicklung und Umsetzung dieses Projektes kamen unter anderem folgende Werkzeuge und Frameworks zum Einsatz:

- **Flask**: Als Micro-Webframework in Python, das Routen-Steuerung und grundlegende Server-Funktionen übernimmt.  
- **SQLAlchemy**: Objektorientierte Datenbank-Abstraktion (ORM) für eine einfache und übersichtliche Verwaltung von Datenbanktabellen.  
- **Flask-Login**: Verwaltung von Sessions und Nutzeranmeldungen, inklusive Prüfung von Berechtigungen.  
- **WTForms**: Erleichtert die Erstellung und Validierung von Formularen (z. B. für Registration, Login, Angebots-Erstellung).  
- **Optionaler API-Zugriff** (z. B. TMDB): Zum Abrufen fehlender Bildinformationen bei Einträgen.

Alle genannten Technologien fügen sich nahtlos ineinander, um eine stabile und leicht erweiterbare Plattform zu gewährleisten.

---

## Zusammenfassung

Diese Dokumentation fasst alle wichtigen Funktionalitäten, Erweiterungen und vorgenommenen Fixes in einem Gesamtüberblick zusammen. Vom Marketplace über das Nachrichtensystem bis hin zum Admin-Dashboard und Passwort-Zurücksetzen stehen zahlreiche Werkzeuge bereit, um die Plattform effizient und nutzerfreundlich zu betreiben. Gleichzeitig sorgen Ban-Funktion und Duplikatskontrolle für einen reibungslosen Ablauf, während ein optionaler Bilderabgleich die Darstellung aufwertet.

Durch die Behebung des Response-Anzeigeproblems sind nun sämtliche Nachrichten vollständig sichtbar, sodass einem reibungslosen Dialog zwischen Anbietenden und Interessierten nichts mehr im Wege steht.
