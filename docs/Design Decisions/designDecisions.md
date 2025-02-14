---
layout: default
title: "Design Decisions"
parent: "Documentation"
nav_order: 2
---
# **Designentscheidungen für die App**

## **1. Frontend: Tailwind CSS**
### **Begründung:**
- Tailwind ist **Utility-First**, was bedeutet, dass wir direkt in den HTML-Dateien Klassen definieren können, anstatt eigene CSS-Dateien mit vielen spezifischen Stilen zu schreiben.
- Es ist **modular und flexibel**, ähnlich zu Bootstrap, aber erlaubt uns, spezifischer und feiner zu stylen.
- **Ömer nutzt es auf der Arbeit**, also gibt es bereits Erfahrung damit, was die Entwicklung effizienter macht.
- **Dark Mode und Responsiveness** sind von Haus aus einfach zu integrieren.

### **Alternative:**
- Bootstrap: Bekannt und weit verbreitet, aber weniger flexibel als Tailwind.
- Pure CSS mit SCSS: Erfordert mehr manuelle Anpassungen, bietet aber volle Kontrolle.

---

## **2. API-Integration: IMDb API**
### **Begründung:**
- Wir können **Filmdaten und Bilder direkt abrufen**, anstatt alles manuell einzupflegen.
- IMDb bietet eine **große Datenbank** mit Bildern, Beschreibungen und weiteren Metadaten.
- Spart **viel Zeit bei der Content-Erstellung**, da Bilder und Beschreibungen automatisch geladen werden können.

### **Alternative:**
- TMDb API: Bietet ähnliche Funktionen, könnte aber andere Limits haben.
- Manuelle Dateneingabe: Viel zu aufwendig und fehleranfällig.

---

## **3. Datenbank: SQLAlchemy**
### **Begründung:**
- SQLAlchemy ist **ein ORM (Object-Relational Mapping)**, das wir bereits im Unterricht gelernt haben.
- Es ermöglicht eine **einfache Handhabung der Datenbank**, ohne direkt SQL schreiben zu müssen.
- Unterstützt **verschiedene Datenbanken** wie SQLite, PostgreSQL oder MySQL.
- **Model-Definitionen sind Python-basiert**, wodurch die Integration mit Flask einfach ist.


---

## **5. Admin-Accounts und Benutzerverwaltung**
### **Begründung:**
- **Flask-Login** und **Flask-Security** ermöglichen eine einfache Implementierung von Benutzerrollen.
- Admin-Accounts können direkt über die **SQLAlchemy-Datenbank** erstellt werden oder über eine Flask-Admin-Schnittstelle.
- Passwort-Hashing mit **Flask-Bcrypt** oder **Werkzeug** für Sicherheit.

