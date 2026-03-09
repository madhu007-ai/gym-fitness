# 🏋️ GymFitness Center

A complete gym fitness management web application built with **Flask** and **Bootstrap 5** for a college web development assignment.

---

## 📋 Features

- ✅ User Registration & Login (with password hashing)
- ✅ Session management
- ✅ User Dashboard with full CRUD operations
- ✅ Attendance tracking per user
- ✅ Simple blogging system: logged-in users can publish posts via `/blog/add` (stored in SQLite)
- ✅ Staff/worker role support – a boolean flag on users allows certain members to access a staff dashboard where they can promote or demote other users
- ✅ Static pages: About Us and Blog
- ✅ 4 database tables (Users, Projects, Skills, Technologies)
- ✅ Responsive design (mobile/tablet/desktop)
- ✅ Client and server-side form validation
- ✅ 8+ pages: Home, Register, Login, Dashboard, Add Program, Edit, Gym Center, About, Blog
- ✅ Dark fitness-themed UI with animations
- ✅ Bootstrap 5 + Bootstrap Icons

---

## 📂 Project Structure

```
gymfitness/
├── app.py                    # Main Flask application & all routes
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── gymfitness.db             # SQLite database (auto-created on first run)
│
├── templates/                # HTML templates (Jinja2)
│   ├── base.html             # Base layout (navbar, footer, flash messages)
│   ├── home.html             # Landing page
│   ├── register.html         # Registration page
│   ├── login.html            # Login page
│   ├── dashboard.html        # User dashboard
│   ├── add_project.html      # Add fitness program
│   ├── edit_project.html     # Edit fitness program
│   ├── edit_skill.html       # Edit skill
│   ├── edit_technology.html  # Edit equipment
│   ├── update_profile.html   # Update profile
│   ├── about.html            # Static about us page
│   ├── blog.html             # Blog listing page
│   ├── add_blog.html         # Form to create new blog posts
│   ├── blog_post.html        # Individual post view
│   ├── gym_center.html       # Full gym center info page
│   └── 404.html              # Error page
│
└── static/
    ├── css/
    │   └── style.css         # All custom styles
    └── js/
        └── main.js           # JavaScript (animations, validation)
```

---

## 🗃️ Database Tables

| Table | Description |
|-------|-------------|
| `users` | Member accounts (username, email, hashed password, bio, goal, attendance) |
| `projects` | Fitness programs (title, category, difficulty, duration) |
| `skills` | Skills/certifications (name, category, proficiency %) |
| `technologies` | Gym equipment (name, category, quantity, condition) |

---

## 🚀 Setup & Run

### 1. Install Python (3.8+)

Download from [python.org](https://python.org)

### 2. Create a virtual environment (recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies

> A default staff account (`admin` / `admin123`) is automatically created on first run if the database contains no staff users. Use these credentials to log in initially and then promote other users from the Staff dashboard.


```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

### 5. Open in browser

Visit: **http://localhost:5000**

---

## 📖 How to Use

1. **Register** a new account at `/register` (new users are clients by default)
2. **Log in** at `/login`
3. Go to your **Dashboard** to add fitness programs, skills, and equipment
4. Visit the **About Us** page at `/about` or check the **Blog** at `/blog`
5. If you have been granted staff privileges you will see a **Staff** link in the
   navigation; click it to access the staff dashboard where you can promote or
   demote other users.
6. Visit the **Gym Center** page for full facility info

---

## 🔐 Security Features

- Passwords are hashed using `werkzeug.security` (PBKDF2-SHA256) — never stored in plain text
- Session management with Flask sessions
- Server-side ownership checks before editing/deleting records
- CSRF protection via form validation

---

## 🎨 Tech Stack

| Technology | Purpose |
|-----------|---------|
| Flask | Python web framework |
| SQLAlchemy | Database ORM |
| SQLite | Database (file-based) |
| Bootstrap 5 | Responsive CSS framework |
| Bootstrap Icons | Icon library |
| Google Fonts | Typography (Bebas Neue, Barlow) |
| JavaScript | Animations, form validation |

---

## 👨‍💻 For Beginners

Every file has detailed comments explaining what each line does. Start by reading:
1. `app.py` — understand routes and database models
2. `templates/base.html` — understand the layout
3. `templates/home.html` — understand Jinja2 templating
4. `static/css/style.css` — understand the styling

---

*Built for Web Development Course Assignment | 2024*
