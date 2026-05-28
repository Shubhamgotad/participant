# PRAVAAH - Student Management System
## A Django + MySQL Student Portal

---

## 🚀 SETUP & RUN COMMANDS (Step by Step)

### STEP 1: Extract the ZIP
```bash
unzip pravaah.zip
cd pravaah
```

---

### STEP 2: Create Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

---

### STEP 3: Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note for Windows users:** If `mysqlclient` fails, try:
> ```bash
> pip install mysqlclient --only-binary=mysqlclient
> ```
> Or download the wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient

---

### STEP 4: Setup MySQL Database
Open MySQL command line or MySQL Workbench and run:
```sql
CREATE DATABASE pravaah_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### STEP 5: Configure Database in settings.py
Open `pravaah/settings.py` and update:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pravaah_db',
        'USER': 'root',             # ← your MySQL username
        'PASSWORD': 'your_password', # ← your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

---

### STEP 6: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### STEP 7: Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
Follow the prompts to set username, email, and password.

---

### STEP 8: (Optional) Populate Sample Data
```bash
python populate_data.py
```
This creates:
- Admin: `admin` / `admin@123`
- Student 1: `student1` / `student@123`
- Student 2: `student2` / `student@123`
- Sample attendance and result records

---

### STEP 9: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

---

### STEP 10: Run the Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 📌 URLS

| Page              | URL                              |
|-------------------|----------------------------------|
| Landing Page      | http://127.0.0.1:8000/           |
| Student Login     | http://127.0.0.1:8000/accounts/login/ |
| Student Register  | http://127.0.0.1:8000/accounts/register/ |
| Dashboard         | http://127.0.0.1:8000/dashboard/ |
| Profile           | http://127.0.0.1:8000/students/profile/ |
| Attendance        | http://127.0.0.1:8000/students/attendance/ |
| Results           | http://127.0.0.1:8000/students/results/ |
| Admin Panel       | http://127.0.0.1:8000/admin/     |

---

## 🏗️ PROJECT STRUCTURE

```
pravaah/
├── pravaah/           # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── views.py
├── accounts/          # Auth app (login, register, logout)
│   ├── forms.py
│   ├── views.py
│   └── urls.py
├── students/          # Student data (models, profile, attendance, results)
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── dashboard/         # Dashboard home
│   ├── views.py
│   └── urls.py
├── templates/         # All HTML templates
│   ├── base.html
│   ├── dashboard_base.html
│   ├── landing.html
│   ├── accounts/
│   ├── students/
│   └── dashboard/
├── static/
│   ├── css/style.css
│   └── js/main.js
├── media/             # Uploaded photos
├── manage.py
├── requirements.txt
├── setup_db.sql
└── populate_data.py
```

---

## 🔧 TECH STACK

- **Backend:** Django 4.2
- **Database:** MySQL (via mysqlclient)
- **Frontend:** Bootstrap 5, HTML, CSS, JavaScript
- **Auth:** Django built-in session authentication
- **File Upload:** Pillow (for student photos)

---

## 👤 ADMIN FEATURES

Via Django Admin (`/admin/`):
- Approve/reject student registrations
- Add/edit/delete students
- Manage attendance records
- Manage result records
- Post notifications

---

## ⚠️ IMPORTANT NOTES

1. **Student Approval:** After registration, students must be approved by admin before they can log in.
   - Go to `/admin/` → Students → Select student → Check "Is approved" → Save

2. **Media Files:** Ensure the `media/` directory is writable for photo uploads.

3. **Secret Key:** Change `SECRET_KEY` in `settings.py` before deploying to production.

4. **Debug Mode:** Set `DEBUG = False` and configure `ALLOWED_HOSTS` for production.
