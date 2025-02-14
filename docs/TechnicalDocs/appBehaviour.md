---
layout: default
title: "App Behaviour"
parent: "AnimeMarketPlace"
nav_order: 3
---

# App Behaviour

## 1. Registration and Login

- When registering, a new User is created (`User` model in `db.py`).
- The password is hashed using Bcrypt (`app.py`).
- After successful registration, the user is redirected to the login page (`register.html`).
- During login, credentials are validated, and if correct, the user is logged in (`login.html`).
- If the password is incorrect, an error message is displayed.


## 2. Dashboard

- Provides an overview of all platform features (`dashboard.html` is referenced in `app.py` but not provided).
- Users can directly access:
    - AnimeList (`AnimeList.html`)
    - Marketplace (`marketplace.html`)
    - Bookmarks (`my_bookmarks.html`)
    - Inbox (`inbox.html`)


## 3. Anime List

- Anime data is stored in the database (`AnimeList` model in `db.py`).
- Users can sort anime by rating, title, and release date (`AnimeList.html`).
- A search function and genre filtering are available (`animelist` route in `app.py`).


## 4. Marketplace

- Users can buy/sell anime items (`marketplace.html`).
- ffers are stored in the OfferList table (`OfferList` model in `db.py`).
- When adding an offer:
    - Users provide anime title, price, and offer type(`marketplace_entry` in `app.py`).
    - The offer is added to the database.
    - Only logged-in users can create or purchase offers.


## 5. Chat & Transactions (Inbox)

- Users can communicate with sellers via the Inbox (`inbox.html`).
- Requests (`Request` model in `db.py`) store purchase inquiries.
- Responses (`Response`model in `db.py`) enable chat threads.
- Each entry is linked to an offer (`offer_id`).
- The system displays active conversations (`inbox.html`).


## 6. Bookmarks

- Users can bookmark anime for later (`my_bookmarks.html`).
- The Bookmarks table stores which anime a user has saved (`Bookmark` model in `db.py`).


## 7. Password Reset

- Users can change their password via the Reset Password page (`reset_password.html`).
- The old password is verified before allowing changes (`reset_password` route in `app.py`).
- The **new password** is hashed and stored securely.


## 8. Admin Functionality

- Admins can:
    - Ban/unban users (`admin_users.html`).
    - Reset passwords.
- The `is_admin` flag in the `User` table (`db.py`) determines admin acces