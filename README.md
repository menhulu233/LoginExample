InternLink/
├── app.py                                 # Entrypoint: calls create_app() and runs the server
├── config.py                              # App configuration (DB creds, secret key, etc.)
├── requirements.txt                       # Python dependencies
│
├── app/                                   # Main application package
│   ├── __init__.py                        # create_app(): load Config, init_db, bcrypt, register blueprints
│   ├── db.py                              # init_db(app) & get_db_conn()
│   ├── utils.py                           # hash_password() & check_password()
│   ├── forms.py                           # Flask-WTF forms (LoginForm, RegisterForm, etc.)
│   │
│   └── views/                             # Blueprint modules
│       ├── user.py                        # /user: login, register, reset, logout, dashboard
│       ├── student.py                     # /student: profile, internships, applications
│       ├── employer.py                    # /employer: post internships, manage applications
│       └── admin.py                       # /admin: dashboards, user & stats management
│
├── templates/                             # Jinja2 templates
│   ├── base.html                          # Global layout
│   ├── home.html                          # Landing page
│   ├── user/                              # login.html, register.html, forgot_password.html
│   ├── student/                           # student_profile.html, applications.html, internships.html
│   ├── employer/                          # internship_form.html, internships.html, applications.html
│   └── admin/                             # admin_base.html, dashboard.html, user_management.html,
│                                          # application_management.html, internship_management.html
│
└── static/                                # Static assets
    ├── css/bootstrap.min.css
    ├── js/bootstrap.bundle.min.js
    ├── js/jquery.min.js
    └── uploads/                           # user-uploaded files
        ├── avatars/
        └── resumes/
