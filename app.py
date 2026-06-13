from functools import wraps
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'unischedule_secret_2026'
base_dir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(base_dir, 'instance')
os.makedirs(instance_dir, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_dir, 'unischedule.db').replace('\\', '/')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Please login to access the requested page.', 'warning')
    return redirect(url_for('login'))

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
PERIODS = 8

ROLE_ADMIN = 'ADMIN'
ROLE_STUDENT = 'STUDENT'
DAY_RANGE = {6: DAYS, 5: DAYS[:5], 4: DAYS[:4], 3: DAYS[:3]}

section_subject = db.Table(
    'section_subject',
    db.Column('section_id', db.Integer, db.ForeignKey('section.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

student_subject = db.Table(
    'student_subject',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

def admin_only():
    return current_user.is_authenticated and current_user.role == ROLE_ADMIN


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not admin_only():
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('dashboard'))
        return view(*args, **kwargs)
    return wrapped_view


def get_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings(days_per_week=5, periods_per_day=8, free_hours_per_week=3)
        db.session.add(settings)
        db.session.commit()
        return settings

    changed = False
    if settings.days_per_week is None:
        settings.days_per_week = 5
        changed = True
    if settings.periods_per_day is None:
        settings.periods_per_day = 8
        changed = True
    if settings.free_hours_per_week is None:
        settings.free_hours_per_week = 3
        changed = True
    if changed:
        db.session.commit()
    return settings


def ensure_database_columns():
    with db.engine.connect() as conn:
        def has_column(table_name, column_name):
            rows = conn.execute(text(f"PRAGMA table_info({table_name})")).mappings().all()
            return column_name in [row['name'] for row in rows]

        if not has_column('subject', 'code'):
            try:
                conn.execute(text('ALTER TABLE subject ADD COLUMN code VARCHAR(50)'))
            except Exception:
                pass
        if not has_column('subject', 'credits'):
            try:
                conn.execute(text('ALTER TABLE subject ADD COLUMN credits INTEGER DEFAULT 0'))
            except Exception:
                pass


def build_section_grid(section_id, settings):
    return {day: {period: None for period in range(1, settings.periods_per_day + 1)} for day in DAYS[:settings.days_per_week]}

@dataclass
class ClusterSetup:
    name: str
    section_count: int
    section_names: List[str] = field(default_factory=list)

@dataclass
class SubjectSetup:
    code: str
    name: str
    faculty_name: str
    hours_per_week: int
    cluster_name: str
    restricted_section_names: List[str] = field(default_factory=list)


def parse_cluster_setup(form):
    clusters = []
    names = form.getlist('cluster_name[]')
    counts = form.getlist('cluster_sections[]')
    for name, count in zip(names, counts):
        trimmed = name.strip()
        if not trimmed:
            continue
        try:
            section_count = int(count or 0)
        except ValueError:
            section_count = 0
        clusters.append(ClusterSetup(name=trimmed, section_count=section_count))
    return clusters


def parse_subject_setup(form):
    subjects = []
    codes = form.getlist('subject_code[]')
    names = form.getlist('subject_name[]')
    faculties = form.getlist('faculty_name[]')
    hours = form.getlist('subject_hours[]')
    clusters = form.getlist('subject_cluster[]')
    restricted = form.getlist('restricted_sections[]')
    for code, name, faculty, hour, cluster_name, restricted_list in zip(codes, names, faculties, hours, clusters, restricted):
        trimmed_code = code.strip()
        trimmed_name = name.strip()
        if not trimmed_code or not trimmed_name:
            continue
        try:
            hours_per_week = int(hour or 0)
        except ValueError:
            hours_per_week = 0
        restricted_section_names = [x.strip() for x in restricted_list.split(',') if x.strip()]
        subjects.append(SubjectSetup(
            code=trimmed_code,
            name=trimmed_name,
            faculty_name=faculty.strip(),
            hours_per_week=hours_per_week,
            cluster_name=cluster_name.strip(),
            restricted_section_names=restricted_section_names
        ))
    return subjects


def validate_timetable_setup(clusters: List[ClusterSetup], subjects: List[SubjectSetup]) -> List[str]:
    errors = []
    if not clusters:
        errors.append('At least one cluster must be defined.')
    seen = set()
    for cluster in clusters:
        if cluster.section_count < 1:
            errors.append(f'Cluster {cluster.name} must have at least one section.')
        if cluster.name in seen:
            errors.append(f'Duplicate cluster name found: {cluster.name}')
        seen.add(cluster.name)
    if not subjects:
        errors.append('At least one subject must be defined.')
    subject_codes = set()
    for subject in subjects:
        if subject.code in subject_codes:
            errors.append(f'Duplicate subject code: {subject.code}')
        subject_codes.add(subject.code)
        if subject.hours_per_week < 1:
            errors.append(f'Subject {subject.code} must have at least 1 weekly period.')
        if not subject.faculty_name:
            errors.append(f'Subject {subject.code} must include a faculty name.')
        if not subject.cluster_name:
            errors.append(f'Subject {subject.code} must be assigned to a cluster.')
        if subject.cluster_name not in [c.name for c in clusters] and not Cluster.query.filter_by(name=subject.cluster_name).first():
            errors.append(f'Cluster {subject.cluster_name} for subject {subject.code} does not exist.')
    return errors


def apply_timetable_setup(clusters: List[ClusterSetup], subjects: List[SubjectSetup]):
    cluster_map = {}
    for cluster_def in clusters:
        cluster = Cluster.query.filter_by(name=cluster_def.name).first()
        if not cluster:
            cluster = Cluster(name=cluster_def.name)
            db.session.add(cluster)
            db.session.commit()
        existing = len(cluster.sections)
        for index in range(existing + 1, cluster_def.section_count + 1):
            section_name = f'{cluster.name}{index}'
            section = Section(name=section_name, cluster_id=cluster.id)
            db.session.add(section)
        db.session.commit()
        cluster_map[cluster.name] = cluster
    for subject_def in subjects:
        subject = Subject.query.filter_by(code=subject_def.code).first()
        if not subject:
            subject = Subject(code=subject_def.code, name=subject_def.name)
            db.session.add(subject)
        subject.name = subject_def.name
        subject.hours_per_week = subject_def.hours_per_week
        cluster = Cluster.query.filter_by(name=subject_def.cluster_name).first()
        faculty = Faculty.query.filter_by(name=subject_def.faculty_name).first()
        if not faculty:
            faculty = Faculty(name=subject_def.faculty_name)
            db.session.add(faculty)
            db.session.commit()
        subject.faculty = faculty
        eligible_sections = cluster.sections
        if subject_def.restricted_section_names:
            eligible_sections = [s for s in cluster.sections if s.name in subject_def.restricted_section_names]
        subject.sections = eligible_sections
        db.session.commit()


def build_schedule_for_sections(settings):
    timetable = []
    faculty_assignments = {(f.id, day, period): None for f in Faculty.query.all() for day in DAYS[:settings.days_per_week] for period in range(1, settings.periods_per_day + 1)}
    for cluster in Cluster.query.order_by(Cluster.name).all():
        cluster_data = {'name': cluster.name, 'sections': []}
        for section in cluster.sections:
            grid = build_section_grid(section.id, settings)
            if not section.subjects:
                continue
            lessons = []
            for subject in section.subjects:
                if not subject.faculty:
                    raise ValueError(f'Subject {subject.name} has no faculty assigned.')
                lessons.append({
                    'subject': subject,
                    'remaining': subject.hours_per_week,
                    'placed_days': set(),
                    'placed_periods': 0
                })
            for day in DAYS[:settings.days_per_week]:
                for period in range(1, settings.periods_per_day + 1):
                    candidate = None
                    best_score = -999
                    previous_subject = None
                    if period > 1:
                        prev = grid[day][period - 1]
                        previous_subject = prev.subject.name if prev else None
                    for lesson in lessons:
                        if lesson['remaining'] <= 0:
                            continue
                        subject = lesson['subject']
                        key = (subject.faculty_id, day, period)
                        if faculty_assignments.get(key) is not None:
                            continue
                        if subject.name == previous_subject:
                            continue
                        score = lesson['remaining'] * 10
                        if day not in lesson['placed_days']:
                            score += 5
                        if lesson['placed_periods'] > 0:
                            score += 1
                        if score > best_score:
                            best_score = score
                            candidate = lesson
                    if not candidate:
                        for lesson in lessons:
                            if lesson['remaining'] <= 0:
                                continue
                            subject = lesson['subject']
                            key = (subject.faculty_id, day, period)
                            if faculty_assignments.get(key) is None:
                                candidate = lesson
                                break
                    if not candidate:
                        continue
                    subject = candidate['subject']
                    grid[day][period] = {'subject': subject, 'faculty': subject.faculty}
                    faculty_assignments[(subject.faculty_id, day, period)] = section.id
                    candidate['remaining'] -= 1
                    candidate['placed_days'].add(day)
                    candidate['placed_periods'] += 1
            section_data = {
                'name': section.name,
                'grid': grid,
                'cluster': cluster.name
            }
            cluster_data['sections'].append(section_data)
        timetable.append(cluster_data)
    return timetable

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Cluster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    sections = db.relationship('Section', backref='cluster', cascade='all, delete-orphan')

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'))
    subjects = db.relationship('Subject', secondary=section_subject, back_populates='sections')
    students = db.relationship('Student', back_populates='section', lazy=True)

    def cluster_name(self):
        return self.cluster.name if self.cluster else 'N/A'

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    prefer_morning = db.Column(db.Boolean, default=False)
    prefer_afternoon = db.Column(db.Boolean, default=False)
    avoid_first_period = db.Column(db.Boolean, default=False)
    avoid_last_period = db.Column(db.Boolean, default=False)
    avoid_friday = db.Column(db.Boolean, default=False)
    max_classes_per_day = db.Column(db.Integer, default=4)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    hours_per_week = db.Column(db.Integer, default=3)
    credits = db.Column(db.Integer, default=0, nullable=False)
    is_lab = db.Column(db.Boolean, default=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'))
    faculty = db.relationship('Faculty')
    sections = db.relationship('Section', secondary=section_subject, back_populates='subjects')
    students = db.relationship('Student', secondary=student_subject, back_populates='subjects')

    def type_label(self):
        return 'Lab' if self.is_lab else 'Theory'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(120), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    section = db.relationship('Section', back_populates='students')
    subjects = db.relationship('Subject', secondary=student_subject, back_populates='students')

    def section_name(self):
        return self.section.name if self.section else 'N/A'

    def cluster_name(self):
        return self.section.cluster.name if self.section and self.section.cluster else 'N/A'

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    days_per_week = db.Column(db.Integer, default=5)
    periods_per_day = db.Column(db.Integer, default=8)
    free_hours_per_week = db.Column(db.Integer, default=3)

class TimetableEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    section = db.relationship('Section')
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship('Subject')
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'))
    faculty = db.relationship('Faculty')
    day = db.Column(db.String(20))
    period = db.Column(db.Integer)
    is_free = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user_roles():
    return {
        'role_admin': ROLE_ADMIN,
        'role_student': ROLE_STUDENT
    }

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password) and user.role == role:
            login_user(user)
            return redirect(url_for('dashboard'))
        if user and check_password_hash(user.password, password) and user.role != role:
            flash(f'Please select the correct role for {username}.', 'danger')
        else:
            flash('Invalid username, password, or role.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        if role == ROLE_ADMIN:
            flash('Admin registration is not allowed.', 'danger')
            return render_template('register.html')
        if not username or not password or not role:
            flash('All fields are required.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        else:
            user = User(username=username, password=generate_password_hash(password), role=ROLE_STUDENT)
            db.session.add(user)
            db.session.commit()
            student = Student(roll_number=f'{username}_roll', name=username)
            db.session.add(student)
            db.session.commit()
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/users')
@login_required
def manage_users():
    if not admin_only():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    users = User.query.order_by(User.role, User.username).all()
    return render_template('users.html', users=users)

@app.route('/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if not admin_only():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('The primary admin account cannot be deleted.', 'danger')
        return redirect(url_for('manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User account removed successfully.', 'success')
    return redirect(url_for('manage_users'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == ROLE_STUDENT:
        return redirect(url_for('student_portal'))
    settings = Settings.query.first() or Settings()
    unassigned_students = Student.query.filter_by(section_id=None).count()
    sections_without_subjects = Section.query.filter(~Section.subjects.any()).count()
    subjects_unassigned = Subject.query.filter(Subject.faculty_id == None).count()
    return render_template('dashboard.html', stats={
        'clusters': Cluster.query.count(),
        'sections': Section.query.count(),
        'faculty': Faculty.query.count(),
        'subjects': Subject.query.count(),
        'students': Student.query.count(),
        'timetables': TimetableEntry.query.count()
    }, pending={
        'unassigned_students': unassigned_students,
        'sections_without_subjects': sections_without_subjects,
        'subjects_unassigned': subjects_unassigned
    }, settings=settings)

@app.route('/clusters', methods=['GET', 'POST'])
@login_required
def manage_clusters():
    if not admin_only():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name').strip()
        sections_count = int(request.form.get('sections_count') or 0)
        if not name or sections_count < 1:
            flash('Cluster name and section count are required.', 'danger')
        elif Cluster.query.filter_by(name=name).first():
            flash('Cluster name already exists.', 'danger')
        else:
            cluster = Cluster(name=name)
            db.session.add(cluster)
            db.session.commit()
            for index in range(1, sections_count + 1):
                section_name = f'{name}{index}'
                section = Section(name=section_name, cluster_id=cluster.id)
                db.session.add(section)
            db.session.commit()
            flash(f'Cluster {name} created with {sections_count} sections.', 'success')
            return redirect(url_for('manage_clusters'))
    clusters = Cluster.query.order_by(Cluster.name).all()
    return render_template('clusters.html', clusters=clusters)

@app.route('/clusters/delete/<int:cluster_id>')
@login_required
def delete_cluster(cluster_id):
    if current_user.role != 'ADMIN':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    cluster = Cluster.query.get_or_404(cluster_id)
    db.session.delete(cluster)
    db.session.commit()
    flash('Cluster removed.', 'success')
    return redirect(url_for('manage_clusters'))

@app.route('/faculty', methods=['GET', 'POST'])
@login_required
def manage_faculty():
    if not admin_only():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name')
        faculty = Faculty(
            name=name,
            prefer_morning=bool(request.form.get('prefer_morning')),
            prefer_afternoon=bool(request.form.get('prefer_afternoon')),
            avoid_first_period=bool(request.form.get('avoid_first_period')),
            avoid_last_period=bool(request.form.get('avoid_last_period')),
            avoid_friday=bool(request.form.get('avoid_friday')),
            max_classes_per_day=int(request.form.get('max_classes_per_day') or 4)
        )
        if not name:
            flash('Faculty name is required.', 'danger')
        else:
            db.session.add(faculty)
            db.session.commit()
            flash('Faculty saved successfully.', 'success')
            return redirect(url_for('manage_faculty'))
    faculty_list = Faculty.query.order_by(Faculty.name).all()
    return render_template('faculty.html', faculty_list=faculty_list)

@app.route('/faculty/delete/<int:faculty_id>')
@login_required
def delete_faculty(faculty_id):
    if current_user.role != 'ADMIN':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    faculty = Faculty.query.get_or_404(faculty_id)
    db.session.delete(faculty)
    db.session.commit()
    flash('Faculty removed.', 'success')
    return redirect(url_for('manage_faculty'))

@app.route('/subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    if not admin_only():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    faculties = Faculty.query.order_by(Faculty.name).all()
    sections = Section.query.order_by(Section.name).all()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'assign_sections':
            subject_id = int(request.form.get('subject_id') or 0)
            selected_section_ids = [int(sid) for sid in request.form.getlist('section_ids') if sid.isdigit()]
            if subject_id == 0:
                flash('Subject selection is required.', 'danger')
            else:
                subject = Subject.query.get_or_404(subject_id)
                subject.sections = Section.query.filter(Section.id.in_(selected_section_ids)).all()
                db.session.commit()
                flash('Section assignments updated for subject.', 'success')
                return redirect(url_for('manage_subjects'))
        else:
            code = request.form.get('code')
            name = request.form.get('name')
            hours = int(request.form.get('hours') or 1)
            credits = int(request.form.get('credits') or 0)
            is_lab = bool(request.form.get('is_lab'))
            faculty_id = int(request.form.get('faculty_id') or 0)
            if not code or not name:
                flash('Subject code and name are required.', 'danger')
            elif Subject.query.filter_by(code=code).first():
                flash('Subject code already exists.', 'danger')
            else:
                subject = Subject(code=code, name=name, hours_per_week=hours, credits=credits, is_lab=is_lab, faculty_id=faculty_id if faculty_id != 0 else None)
                db.session.add(subject)
                db.session.commit()
                flash('Subject added.', 'success')
                return redirect(url_for('manage_subjects'))
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('subjects.html', subjects=subjects, faculties=faculties, sections=sections)

@app.route('/subjects/delete/<int:subject_id>')
@login_required
def delete_subject(subject_id):
    if current_user.role != 'ADMIN':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject removed.', 'success')
    return redirect(url_for('manage_subjects'))

@app.route('/students', methods=['GET', 'POST'])
@login_required
def manage_students():
    if not admin_only():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    sections = Section.query.order_by(Section.name).all()
    if request.method == 'POST':
        roll = request.form.get('roll')
        name = request.form.get('name')
        section_id = int(request.form.get('section_id') or 0)
        if not roll or not name or section_id == 0:
            flash('All student details are required.', 'danger')
        else:
            student = Student(roll_number=roll, name=name, section_id=section_id)
            db.session.add(student)
            db.session.commit()
            flash('Student added.', 'success')
            return redirect(url_for('manage_students'))
    students = Student.query.order_by(Student.name).all()
    return render_template('students.html', students=students, sections=sections)

@app.route('/sections', methods=['GET', 'POST'])
@login_required
def manage_sections():
    if not admin_only():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    sections = Section.query.order_by(Section.name).all()
    clusters = Cluster.query.order_by(Cluster.name).all()
    subjects = Subject.query.order_by(Subject.name).all()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create_section':
            section_name = request.form.get('section_name')
            cluster_id = int(request.form.get('cluster_id') or 0)
            if not section_name or cluster_id == 0:
                flash('Section name and cluster are required.', 'danger')
            elif Section.query.filter_by(name=section_name).first():
                flash('Section name already exists.', 'danger')
            else:
                section = Section(name=section_name, cluster_id=cluster_id)
                db.session.add(section)
                db.session.commit()
                flash(f'Section {section_name} created successfully.', 'success')
                return redirect(url_for('manage_sections'))
        elif action == 'move_section':
            section_id = int(request.form.get('section_id') or 0)
            cluster_id = int(request.form.get('cluster_id') or 0)
            if section_id == 0 or cluster_id == 0:
                flash('Section and target cluster are required for moving.', 'danger')
            else:
                section = Section.query.get_or_404(section_id)
                section.cluster_id = cluster_id
                db.session.commit()
                flash(f'Section {section.name} moved successfully.', 'success')
                return redirect(url_for('manage_sections'))
        elif action == 'assign_subjects':
            section_id = int(request.form.get('section_id') or 0)
            selected_subject_ids = request.form.getlist('subject_ids')
            if section_id == 0:
                flash('Section selection is required.', 'danger')
            else:
                section = Section.query.get_or_404(section_id)
                section.subjects = Subject.query.filter(Subject.id.in_(selected_subject_ids)).all()
                db.session.commit()
                flash('Section subjects updated successfully.', 'success')
                return redirect(url_for('manage_sections'))
    return render_template('sections.html', sections=sections, clusters=clusters, subjects=subjects)

@app.route('/students/delete/<int:student_id>')
@login_required
def delete_student(student_id):
    if current_user.role != 'ADMIN':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student removed.', 'success')
    return redirect(url_for('manage_students'))

@app.route('/student/portal')
@login_required
def student_portal():
    if current_user.role != ROLE_STUDENT:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    student = Student.query.filter_by(name=current_user.username).first()
    selected_subjects = student.subjects if student else []
    return render_template('student_dashboard.html', student=student, selected_subjects=selected_subjects)

@app.route('/student/choose_section', methods=['GET', 'POST'])
@login_required
def choose_section():
    if current_user.role != ROLE_STUDENT:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    student = Student.query.filter_by(name=current_user.username).first()
    if not student:
        flash('Student profile not found. Please ask the admin to create it.', 'warning')
        return redirect(url_for('dashboard'))
    clusters = Cluster.query.order_by(Cluster.name).all()
    if request.method == 'POST':
        cluster_id = int(request.form.get('cluster_id') or 0)
        section_id = int(request.form.get('section_id') or 0)
        if cluster_id == 0 or section_id == 0:
            flash('Please select a cluster and section.', 'danger')
        else:
            section = Section.query.get(section_id)
            if not section or section.cluster_id != cluster_id:
                flash('Selected section does not belong to the chosen cluster.', 'danger')
            else:
                student.section_id = section_id
                db.session.commit()
                flash('Section selected successfully.', 'success')
                return redirect(url_for('student_portal'))
    return render_template('choose_section.html', student=student, clusters=clusters)

@app.route('/student/choose_subjects', methods=['GET', 'POST'])
@login_required
def choose_subjects():
    if current_user.role != ROLE_STUDENT:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    student = Student.query.filter_by(name=current_user.username).first()
    if not student:
        flash('Student profile not found. Please ask the admin to create it.', 'warning')
        return redirect(url_for('dashboard'))
    if not student.section:
        flash('Please select a section first before choosing subjects.', 'warning')
        return redirect(url_for('choose_section'))

    section_subjects = student.section.subjects
    if section_subjects:
        subject_choices = section_subjects
        fallback_message = 'These subjects are preassigned to your section.'
    else:
        subject_choices = Subject.query.order_by(Subject.name).all()
        fallback_message = 'No section-specific subjects are assigned. All subjects are available by default.'

    selected_ids = [s.id for s in student.subjects]
    if request.method == 'POST':
        subject_ids = [int(sid) for sid in request.form.getlist('subject_ids') if sid.isdigit()]
        student.subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
        db.session.commit()
        flash('Subject preferences saved.', 'success')
        return redirect(url_for('student_portal'))
    return render_template('choose_subjects.html', student=student, subject_choices=subject_choices, selected_ids=selected_ids, fallback_message=fallback_message)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
    if not admin_only():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    if request.method == 'POST':
        settings.days_per_week = int(request.form.get('days_per_week') or 5)
        settings.periods_per_day = int(request.form.get('periods_per_day') or 8)
        settings.free_hours_per_week = int(request.form.get('free_hours_per_week') or 3)
        db.session.commit()
        flash('Settings saved successfully.', 'success')
        return redirect(url_for('settings_page'))
    return render_template('settings.html', settings=settings)

def validate_required_data():
    if Cluster.query.count() == 0:
        return 'At least one cluster must exist.'
    if Section.query.count() == 0:
        return 'At least one section must exist.'
    if Faculty.query.count() == 0:
        return 'At least one faculty member must exist.'
    if Subject.query.count() == 0:
        return 'At least one subject must exist.'
    return None

@app.route('/timetables/clear', methods=['POST'])
@login_required
def clear_timetables():
    if not admin_only():
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    TimetableEntry.query.delete()
    db.session.commit()
    flash('All timetable entries were cleared.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/generate', methods=['POST'])
@login_required
def generate_timetable():
    if current_user.role != 'ADMIN':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))

    shuffle = request.form.get('shuffle') == '1'
    error = validate_required_data()
    if error:
        flash(error, 'danger')
        return redirect(url_for('dashboard'))

    settings = get_settings()
    sections = Section.query.all()
    subjects = Subject.query.all()
    faculty_list = {f.id: f for f in Faculty.query.all()}
    if shuffle:
        random.shuffle(sections)

    days_per_week = int(settings.days_per_week or 5)
    periods_per_day = int(settings.periods_per_day or 8)
    free_hours_per_section = int(settings.free_hours_per_week or 3)

    available_slots = [(day, period) for day in DAYS[:days_per_week] for period in range(1, periods_per_day + 1)]
    class_slots_per_section = len(available_slots) - free_hours_per_section

    for section in sections:
        effective_subjects = section.subjects if section.subjects else subjects
        section_hours = sum(subject.hours_per_week for subject in effective_subjects)
        if section_hours > class_slots_per_section:
            flash(f'Section {section.name} needs {section_hours} slots but only {class_slots_per_section} are available after free hours.', 'danger')
            return redirect(url_for('dashboard'))

    global_assignments = {}
    daily_faculty_counts = {f.id: {day: 0 for day in DAYS[:settings.days_per_week]} for f in faculty_list.values()}
    TimetableEntry.query.delete()
    db.session.commit()

    def faculty_available(faculty_id, day, period, section_id):
        return (faculty_id, day, period) not in global_assignments

    def add_entry(section_id, subject, day, period, is_free=False):
        entry = TimetableEntry(section_id=section_id, subject_id=subject.id if subject else None,
                               faculty_id=subject.faculty_id if subject else None,
                               day=day, period=period, is_free=is_free)
        db.session.add(entry)
        if subject:
            global_assignments[(subject.faculty_id, day, period)] = section_id
            daily_faculty_counts[subject.faculty_id][day] += 1

    def score_slot(faculty, day, period):
        score = 0
        if faculty.prefer_morning and period <= 3:
            score += 5
        if faculty.prefer_afternoon and period >= max(4, settings.periods_per_day // 2 + 1):
            score += 5
        if faculty.avoid_first_period and period == 1:
            score -= 10
        if faculty.avoid_last_period and period == settings.periods_per_day:
            score -= 10
        if faculty.avoid_friday and day == 'Friday':
            score -= 8
        return score

    for section in sections:
        section_slots = [(day, period) for day in DAYS[:settings.days_per_week] for period in range(1, settings.periods_per_day + 1)]
        assigned = []
        free_assigned = 0

        # Build the pool of candidate free slots
        free_slot_pool = list(section_slots)
        if shuffle:
            # Randomly pick free slots from anywhere in the week
            random.shuffle(free_slot_pool)
        else:
            # Deterministic: spread one free slot per day at the start of the day
            ordered_free = []
            for day in DAYS[:settings.days_per_week]:
                daily_count = (settings.free_hours_per_week // settings.days_per_week) + (
                    1 if free_assigned < settings.free_hours_per_week % settings.days_per_week else 0
                )
                for period_offset in range(daily_count):
                    period = 1 + period_offset
                    if period <= settings.periods_per_day:
                        ordered_free.append((day, period))
            free_slot_pool = ordered_free + [s for s in section_slots if s not in ordered_free]

        for day_period in free_slot_pool:
            if free_assigned >= settings.free_hours_per_week:
                break
            day, period = day_period
            if (day, period) in assigned:
                continue
            add_entry(section.id, None, day, period, is_free=True)
            assigned.append((day, period))
            free_assigned += 1

        effective_subjects = section.subjects if section.subjects else subjects
        subject_schedule = list(effective_subjects)
        if shuffle:
            lab_subjects = [s for s in subject_schedule if s.is_lab]
            theory_subjects = [s for s in subject_schedule if not s.is_lab]
            random.shuffle(lab_subjects)
            random.shuffle(theory_subjects)
            subject_schedule = lab_subjects + theory_subjects
        else:
            subject_schedule.sort(key=lambda s: (not s.is_lab, -s.hours_per_week))
        for subject in subject_schedule:
            faculty = faculty_list.get(subject.faculty_id)
            if not faculty:
                flash(f'Subject {subject.name} in section {section.name} has no faculty assigned.', 'danger')
                return redirect(url_for('dashboard'))
            hours_remaining = subject.hours_per_week
            if subject.is_lab:
                while hours_remaining > 0:
                    placed = False
                    for day in DAYS[:settings.days_per_week]:
                        for period in range(1, settings.periods_per_day):
                            if any((day, p) in assigned for p in [period, period + 1]):
                                continue
                            if not faculty_available(faculty.id, day, period, section.id):
                                continue
                            if not faculty_available(faculty.id, day, period + 1, section.id):
                                continue
                            if daily_faculty_counts[faculty.id][day] + 2 > faculty.max_classes_per_day:
                                continue
                            if faculty.avoid_first_period and period == 1:
                                continue
                            if faculty.avoid_last_period and period + 1 == settings.periods_per_day:
                                continue
                            add_entry(section.id, subject, day, period)
                            add_entry(section.id, subject, day, period + 1)
                            assigned.extend([(day, period), (day, period + 1)])
                            hours_remaining -= 2
                            placed = True
                            break
                        if placed:
                            break
                    if not placed:
                        flash(f'Could not place lab subject {subject.name} for section {section.name}.', 'danger')
                        return redirect(url_for('dashboard'))
            else:
                while hours_remaining > 0:
                    best = None
                    best_score = -999
                    for day, period in section_slots:
                        if (day, period) in assigned:
                            continue
                        if not faculty_available(faculty.id, day, period, section.id):
                            continue
                        if daily_faculty_counts[faculty.id][day] + 1 > faculty.max_classes_per_day:
                            continue
                        score = score_slot(faculty, day, period)
                        if score > best_score:
                            best_score = score
                            best = (day, period)
                    if not best:
                        flash(f'Unable to place theory subject {subject.name} for {section.name}.', 'danger')
                        return redirect(url_for('dashboard'))
                    day, period = best
                    add_entry(section.id, subject, day, period)
                    assigned.append((day, period))
                    hours_remaining -= 1

    db.session.commit()
    flash('Timetables generated successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/timetables')
@login_required
def view_timetables():
    sections = Section.query.order_by(Section.name).all()
    return render_template('timetables.html', sections=sections)

@app.route('/timetable/<int:section_id>')
@login_required
def view_timetable(section_id):
    section = Section.query.get_or_404(section_id)
    settings = get_settings()
    days_per_week = int(settings.days_per_week or 5)
    periods_per_day = int(settings.periods_per_day or 8)
    grid = {day: {period: None for period in range(1, periods_per_day + 1)} for day in DAYS[:days_per_week]}
    entries = TimetableEntry.query.filter_by(section_id=section_id).all()
    for entry in entries:
        grid[entry.day][entry.period] = entry
    return render_template('timetable_view.html', section=section, grid=grid, settings=settings)

@app.route('/create_admin')
def create_admin():
    if User.query.filter_by(username='admin').first():
        return 'Admin exists'
    user = User(username='admin', password=generate_password_hash('admin123'), role='ADMIN')
    db.session.add(user)
    db.session.commit()
    return 'Admin created'

def initialize_database():
    db.create_all()
    ensure_database_columns()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='ADMIN')
        db.session.add(admin)
        db.session.commit()

with app.app_context():
    initialize_database()

if __name__ == '__main__':
    app.run(debug=True)
