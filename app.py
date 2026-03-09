"""
GymFitness Center - Flask Web Application
Uses Flask + built-in sqlite3 (no extra packages needed)
"""
from flask import Flask, render_template, redirect, url_for, request, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gymfitness-secret-key-2024'
DATABASE = os.path.join(os.path.dirname(__file__), 'gymfitness.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid

def init_db():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
        full_name TEXT, bio TEXT, goal TEXT, joined_date TEXT DEFAULT CURRENT_TIMESTAMP,
        attendance INTEGER DEFAULT 0, is_staff INTEGER DEFAULT 0)''')

    # migration support for existing databases (keep attendance and is_staff columns if missing)
    cursor.execute("PRAGMA table_info('users')")
    existing_cols = [row[1] for row in cursor.fetchall()]
    if 'attendance' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN attendance INTEGER DEFAULT 0")
    if 'is_staff' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_staff INTEGER DEFAULT 0")

    cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        description TEXT, category TEXT, duration TEXT, difficulty TEXT,
        image_url TEXT, is_featured INTEGER DEFAULT 0,
        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        body TEXT NOT NULL, created_date TEXT DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        category TEXT, proficiency INTEGER DEFAULT 50, description TEXT,
        icon TEXT DEFAULT 'bi-star',
        user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS technologies (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        category TEXT, description TEXT, quantity INTEGER DEFAULT 1,
        condition TEXT DEFAULT 'Excellent', icon TEXT DEFAULT 'bi-tools',
        user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id))''')
    # create a default staff account if none exist
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_staff=1")
    if cursor.fetchone()[0] == 0:
        # add admin/admin (you can change later via staff dashboard)
        pwd = generate_password_hash('admin123')
        try:
            cursor.execute("INSERT INTO users (username,email,password_hash,full_name,is_staff) VALUES (?,?,?,?,1)",
                           ['admin','admin@example.com', pwd, 'Administrator'])
            print('🔑 Default staff user created: admin/admin123')
        except sqlite3.IntegrityError:
            pass
    db.commit()
    db.close()

def is_logged_in():
    return 'user_id' in session

from datetime import datetime


def _parse_user_row(row):
    """Convert a sqlite Row to a dict and parse the joined_date field to a
    :class:`datetime.datetime` object so templates can call ``strftime``.
    If parsing fails we leave the original string in place.
    """
    if not row:
        return None
    # convert sqlite3.Row to plain dict for easier mutation
    user = dict(row)
    jd = user.get('joined_date')
    if jd:
        if isinstance(jd, str):
            try:
                # ISO format inserted by default, but older records may include
                # a time component
                user['joined_date'] = datetime.fromisoformat(jd)
            except ValueError:
                try:
                    user['joined_date'] = datetime.strptime(jd, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
    return user


def get_current_user():
    if is_logged_in():
        row = query_db('SELECT * FROM users WHERE id = ?', [session['user_id']], one=True)
        user = _parse_user_row(row)
        # ensure boolean-like value
        if user:
            user['is_staff'] = bool(user.get('is_staff'))
        return user
    return None

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_logged_in():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def staff_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_logged_in():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        user = get_current_user()
        if not user or not user.get('is_staff'):
            flash('Staff access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    featured_projects = query_db('SELECT p.*, u.username, u.full_name FROM projects p JOIN users u ON p.user_id = u.id WHERE p.is_featured = 1 LIMIT 6')
    total_members = query_db('SELECT COUNT(*) as count FROM users', one=True)['count']
    total_programs = query_db('SELECT COUNT(*) as count FROM projects', one=True)['count']
    return render_template('home.html', featured_projects=featured_projects, total_members=total_members, total_programs=total_programs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Valid email required.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if query_db('SELECT id FROM users WHERE username = ?', [username], one=True):
            errors.append('Username already taken.')
        if query_db('SELECT id FROM users WHERE email = ?', [email], one=True):
            errors.append('Email already registered.')
        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html')
        execute_db('INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)',
                   [username, email, generate_password_hash(password), full_name or username])
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if user and check_password_hash(user['password_hash'], password):
            # convert sqlite Row to dict just for session flags
            usr = dict(user)
            session['user_id'] = usr['id']
            session['username'] = usr['username']
            session['is_staff'] = bool(usr.get('is_staff', 0))
            flash(f"Welcome back, {usr.get('full_name') or usr['username']}! 💪", 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')


# specialized login page for staff users only
@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    # if already logged in as staff redirect to dashboard
    if is_logged_in() and session.get('is_staff'):
        return redirect(url_for('staff_dashboard'))
    # otherwise show form or attempt login
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        # sqlite3.Row doesn't support get(), so index directly or convert to dict
        if user and user['is_staff'] and check_password_hash(user['password_hash'], password):
            usr = dict(user)
            session['user_id'] = usr['id']
            session['username'] = usr['username']
            session['is_staff'] = True
            flash(f"Welcome staff member {usr.get('full_name') or usr['username']}!", 'success')
            return redirect(url_for('staff_dashboard'))
        flash('Invalid staff credentials.', 'danger')
    return render_template('staff_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    projects = query_db('SELECT * FROM projects WHERE user_id = ? ORDER BY created_date DESC', [user['id']])
    skills = query_db('SELECT * FROM skills WHERE user_id = ?', [user['id']])
    technologies = query_db('SELECT * FROM technologies WHERE user_id = ?', [user['id']])
    featured_count = sum(1 for p in projects if p['is_featured'])
    return render_template('dashboard.html', user=user, projects=projects, skills=skills, technologies=technologies, featured_count=featured_count)

# portfolio route removed per request - location page was replaced by blog/about pages


@app.route('/profile/update', methods=['GET', 'POST'])
@login_required
def update_profile():
    user = get_current_user()
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        existing = query_db('SELECT id FROM users WHERE email = ? AND id != ?', [email, user['id']], one=True)
        if existing:
            flash('Email already in use.', 'danger')
            return render_template('update_profile.html', user=user)
        execute_db('UPDATE users SET full_name=?, bio=?, goal=?, email=? WHERE id=?',
                   [request.form.get('full_name',''), request.form.get('bio',''),
                    request.form.get('goal',''), email, user['id']])
        flash('Profile updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('update_profile.html', user=user)

@app.route('/project/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        if not title:
            flash('Title required!', 'danger')
            return render_template('add_project.html')
        execute_db('INSERT INTO projects (title,description,category,duration,difficulty,image_url,is_featured,user_id) VALUES (?,?,?,?,?,?,?,?)',
                   [title, request.form.get('description',''), request.form.get('category',''),
                    request.form.get('duration',''), request.form.get('difficulty',''),
                    request.form.get('image_url',''), 1 if request.form.get('is_featured')=='on' else 0,
                    session['user_id']])
        flash('Program added! 🎯', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_project.html')

@app.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = query_db('SELECT * FROM projects WHERE id = ?', [project_id], one=True)
    if not project or project['user_id'] != session['user_id']:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        execute_db('UPDATE projects SET title=?,description=?,category=?,duration=?,difficulty=?,image_url=?,is_featured=? WHERE id=?',
                   [request.form.get('title',''), request.form.get('description',''),
                    request.form.get('category',''), request.form.get('duration',''),
                    request.form.get('difficulty',''), request.form.get('image_url',''),
                    1 if request.form.get('is_featured')=='on' else 0, project_id])
        flash('Program updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_project.html', project=project)

@app.route('/project/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = query_db('SELECT * FROM projects WHERE id = ?', [project_id], one=True)
    if project and project['user_id'] == session['user_id']:
        execute_db('DELETE FROM projects WHERE id = ?', [project_id])
        flash('Program deleted.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/skill/add', methods=['POST'])
@login_required
def add_skill():
    name = request.form.get('name','').strip()
    if not name:
        flash('Skill name required!', 'danger')
        return redirect(url_for('dashboard'))
    execute_db('INSERT INTO skills (name,category,proficiency,description,icon,user_id) VALUES (?,?,?,?,?,?)',
               [name, request.form.get('category',''), int(request.form.get('proficiency',50)),
                request.form.get('description',''), request.form.get('icon','bi-star'), session['user_id']])
    flash(f'Skill "{name}" added!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/skill/edit/<int:skill_id>', methods=['GET', 'POST'])
@login_required
def edit_skill(skill_id):
    skill = query_db('SELECT * FROM skills WHERE id = ?', [skill_id], one=True)
    if not skill or skill['user_id'] != session['user_id']:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        execute_db('UPDATE skills SET name=?,category=?,proficiency=?,description=?,icon=? WHERE id=?',
                   [request.form.get('name',''), request.form.get('category',''),
                    int(request.form.get('proficiency',50)), request.form.get('description',''),
                    request.form.get('icon','bi-star'), skill_id])
        flash('Skill updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_skill.html', skill=skill)

@app.route('/skill/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    skill = query_db('SELECT * FROM skills WHERE id = ?', [skill_id], one=True)
    if skill and skill['user_id'] == session['user_id']:
        execute_db('DELETE FROM skills WHERE id = ?', [skill_id])
        flash('Skill deleted.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/technology/add', methods=['POST'])
@login_required
def add_technology():
    name = request.form.get('name','').strip()
    if not name:
        flash('Equipment name required!', 'danger')
        return redirect(url_for('dashboard'))
    execute_db('INSERT INTO technologies (name,category,description,quantity,condition,icon,user_id) VALUES (?,?,?,?,?,?,?)',
               [name, request.form.get('category',''), request.form.get('description',''),
                int(request.form.get('quantity',1)), request.form.get('condition','Excellent'),
                request.form.get('icon','bi-tools'), session['user_id']])
    flash(f'Equipment "{name}" added!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/technology/edit/<int:tech_id>', methods=['GET', 'POST'])
@login_required
def edit_technology(tech_id):
    tech = query_db('SELECT * FROM technologies WHERE id = ?', [tech_id], one=True)
    if not tech or tech['user_id'] != session['user_id']:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        execute_db('UPDATE technologies SET name=?,category=?,description=?,quantity=?,condition=?,icon=? WHERE id=?',
                   [request.form.get('name',''), request.form.get('category',''),
                    request.form.get('description',''), int(request.form.get('quantity',1)),
                    request.form.get('condition','Excellent'), request.form.get('icon','bi-tools'), tech_id])
        flash('Equipment updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_technology.html', tech=tech)

@app.route('/technology/delete/<int:tech_id>', methods=['POST'])
@login_required
def delete_technology(tech_id):
    tech = query_db('SELECT * FROM technologies WHERE id = ?', [tech_id], one=True)
    if tech and tech['user_id'] == session['user_id']:
        execute_db('DELETE FROM technologies WHERE id = ?', [tech_id])
        flash('Equipment deleted.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/gym-center')
def gym_center():
    return render_template('gym_center.html')

# ------------------ staff management ------------------
@app.route('/staff')
@staff_required
def staff_dashboard():
    # show all users and basic metrics
    users = query_db('SELECT id, username, full_name, email, is_staff FROM users')
    total = len(users)
    staff_count = sum(1 for u in users if u['is_staff'])
    return render_template('staff.html', users=users, total=total, staff_count=staff_count)

@app.route('/staff/toggle/<int:user_id>', methods=['POST'])
@staff_required
def toggle_staff(user_id):
    # flip is_staff flag
    user = query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    if user:
        newval = 0 if user['is_staff'] else 1
        execute_db('UPDATE users SET is_staff = ? WHERE id = ?', [newval, user_id])
        flash('User role updated.', 'success')
    return redirect(url_for('staff_dashboard'))

# previous location functionality removed; replacing with blog and about pages

@app.route('/about')
def about():
    # simple static about page
    return render_template('about.html')

@app.route('/blog')
def blog():
    # show list of posts
    posts = query_db('''SELECT p.*, u.username FROM posts p
                        LEFT JOIN users u ON p.user_id = u.id
                        ORDER BY created_date DESC''')
    return render_template('blog.html', posts=posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = query_db('''SELECT p.*, u.username FROM posts p
                       LEFT JOIN users u ON p.user_id = u.id
                       WHERE p.id = ?''', [post_id], one=True)
    if not post:
        flash('Post not found.', 'warning')
        return redirect(url_for('blog'))
    return render_template('blog_post.html', post=post)

@app.route('/blog/add', methods=['GET', 'POST'])
@login_required
def add_blog():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        if not title or not body:
            flash('Title and content are required.', 'danger')
            return render_template('add_blog.html')
        execute_db('INSERT INTO posts (title, body, user_id) VALUES (?,?,?)',
                   [title, body, session['user_id']])
        flash('Post published!', 'success')
        return redirect(url_for('blog'))
    return render_template('add_blog.html')

@app.route('/attendance/check', methods=['POST'])
@login_required
def check_attendance():
    user = get_current_user()
    execute_db('UPDATE users SET attendance = attendance + 1 WHERE id = ?', [user['id']])
    flash('Attendance recorded. Keep it up!', 'success')
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    init_db()
    print("🏋️  GymFitness Center starting at http://localhost:5000")
    app.run(debug=True, port=5000)
