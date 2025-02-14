---
layout: default
title: "App Structure"
parent: "AnimeMarketPlace"
nav_order: 3
---

## Ordner und Dateien

1. **`docs/`**  
   - Enthält Dokumentationen (z. B. technische Beschreibungen, Architekturdiagramme, UML, Handbücher).  
   - Kann Markdown-Dateien und Grafiken enthalten.

2. **`instance/`**  
   - Nutzt die Möglichkeit von Flask, eine separate Instanz-Konfiguration aufzubewahren (z. B. `config.py`, `config.json` oder `secrets.cfg`).  
   - Dieser Ordner sollte in `.gitignore` aufgeführt werden, falls sensible Daten (API-Keys, Passwörter) dort liegen.

3. **`migrations/`**  
   - Enthält automatisch generierte Migrationsskripte von **Flask-Migrate** (basierend auf **Alembic**).  
   - Wird erstellt, sobald man mit `flask db init` die Migrations-Umgebung initialisiert und dann `flask db migrate`, `flask db upgrade` ausführt.
   - (Migration hab ich nur benutzt, weil es mühselig war ganzezeit die Datenbank neu zu Initialisieren)

4. **`static/`**  
   - Fasst alle statischen Ressourcen wie **CSS**, **JavaScript** und Bilder.  
   - Standard-Ordner, auf den man in Flask über `url_for('static', filename='...')` zugreifen kann.

5. **`templates/`**  
   - Beinhaltet sämtliche HTML-Vorlagen, welche mit **Jinja2** (Standard bei Flask) gerendert werden können.  
   - Typischerweise liegen hier Seiten wie `login.html`, `register.html` und das Basis-Layout `base.html`.

6. **`venv/`**  
   - Die virtuelle Python-Umgebung, in der alle Dependencies installiert sind.  
   - Wird in der Regel **nicht** ins Versionskontrollsystem eingecheckt (daher in `.gitignore`).

7. **`.gitignore`**  
   - Regelt, welche Dateien und Ordner **nicht** ins Git-Repository übertragen werden sollen.  
   - Typischer Inhalt: `venv/`, `__pycache__/`, `instance/`, `*.pyc`, etc.

8. **`app.py`**  
   - Einstiegspunkt der Flask-Anwendung.  
   - Kann Routen, Konfiguration und das Erstellen des `app`-Objekts enthalten, oder auf Module verweisen.

9. **`db.py`**  
   - Beinhaltet die **SQLAlchemy**-Konfiguration und Datenbank-Modelle (z. B. `User`, `OfferList`, `AnimeList`).  
   - Häufig mit Hilfsfunktionen wie `add_initial_anime_data()` für Demodaten oder Migrations-Utility.

10. **`README.md`**  
    - Enthält eine **Projektbeschreibung**, Installations- und Nutzungshinweise, ggf. Beispiele für CLI-Befehle.  

11. **`requirements.txt`**  
    - Listet alle **Python-Abhängigkeiten** (Flask, SQLAlchemy, WTForms, requests etc.).  
    - Erleichtert das Installieren per `pip install -r requirements.txt`.

---

### Empfehlung zur Nutzung

- Mit dem Befehl `python -m venv venv` kann eine virtuelle Umgebung erstellt werden, welche dann via `venv\Scripts\activate` (Windows) oder `source venv/bin/activate` (Linux/Mac) aktiviert wird.  
- Anschließend installiert man die benötigten Pakete mittels `pip install -r requirements.txt`.  
- Starten kann man die Anwendung je nach Konfiguration mit `flask run` (unter Voraussetzung, dass `FLASK_APP=app.py` gesetzt ist) oder über einen Codeblock am Ende von `app.py`: