# Occavue

![Django](https://img.shields.io/badge/Django-4.x-green?logo=django)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-CLI-38B2AC?logo=tailwind-css&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-blue?logo=postgresql)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render)

Occavue is a **Django-based event management platform** designed to simplify the creation, management, and participation in events. Built on the **Django MVT architecture**, it leverages **Django templates + Tailwind CSS (CLI)** for frontend rendering, **Django ORM** for database interactions, and **PostgreSQL** as the database engine. The app is deployed on **Render** for production use.

---

## ✨ Features

- **User Authentication & Authorization**

  - Secure signup/login system
  - Email activation for new accounts
  - Password reset and account management

- **Role-Based Access Control (RBAC)**

  - Different roles with varying permissions
  - Admins, Organizers, and Participants

- **Event Management**

  - Event categories (e.g., conferences, workshops, meetups)
  - Create, update, and delete events
  - RSVP system for participants
  - Team/organizer management for events

---

## 🛠️ Tech Stack

- **Backend Framework**: Django (MVT Pattern)
- **Frontend**: Django Templates + Tailwind CSS (CLI)
- **Database**: PostgreSQL
- **Authentication**: Django’s built-in auth system + custom email verification
- **Deployment**: [Render](https://render.com/)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/mMahnoor/Event_Management_System.git
cd Event_Management_System
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_NAME=occavue_db
DATABASE_USER=your-db-user
DATABASE_PASSWORD=your-db-password
DATABASE_HOST=localhost
DATABASE_PORT=5432
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
```

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Install Tailwind CLI

Make sure you have **Node.js** and **npm** installed. Then install Tailwind CLI:

```bash
npm install -D tailwindcss
npx tailwindcss init
```

### 7. Build Tailwind CSS

Run the following to generate your CSS:

```bash
npx tailwindcss -i ./static/CSS/tailwind.css -o ./static/css/output.css --watch
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

Visit: [https://occavue.onrender.com/](https://occavue.onrender.com/)

---

## 📂 Project Structure

```
occavue/
├── core/                  # Global views and templates
├── event_management/      # Main project settings
├── events/                # Event management app
├── users/                 # Authentication and roles
├── templates/             # Django templates (frontend)
├── static/                # Static files (CSS, JS, images)
│   └── Images/            # Tailwind input file (all images and svgs)
│   └── CSS/               # Tailwind input file (tailwind.css) and compiled output (output.css)
├── manage.py              # Django CLI entrypoint
└── requirements.txt       # Dependencies
```

---

## 🌐 Deployment (Render)

Occavue is deployed on **Render**.

- Python version: `3.x`
- Start command:

  ```bash
  gunicorn occavue.wsgi
  ```

- Collect static files before deployment:

  ```bash
  python manage.py collectstatic --noinput
  ```

- Environment variables should be configured in Render’s dashboard (same as `.env`).

---

## ✅ Future Enhancements

- Event ticketing & payment integration
- Calendar & notification system
- REST API endpoints for mobile integration
- Advanced analytics & reporting

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch (`feature/your-feature`)
3. Commit your changes
4. Submit a Pull Request

---

## 📧 Contact

For questions, suggestions, or support, reach out at:
**Mahnur Akther**
📩 [mahnurakther@gmail.com](mailto:mahnurakther@gmail.com)
