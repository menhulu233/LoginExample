# Internlink structure 
InternLink/
├── app.py                                 # Entrypoint: calls create_app() and runs the server :contentReference[oaicite:15]{index=15}
├── config.py                              # App configuration (DB creds, secret key, etc.)
├── requirements.txt                       # Python dependencies
│
├── app/                                   # Main application package :contentReference[oaicite:16]{index=16}
│   ├── __init__.py                        # create_app(): load Config, init_db, bcrypt, register blueprints
│   ├── db.py                              # init_db(app) & get_db_conn() :contentReference[oaicite:17]{index=17}
│   ├── utils.py                           # hash_password() & check_password() :contentReference[oaicite:18]{index=18}
│   ├── forms.py                           # Flask-WTF forms (LoginForm, RegisterForm, etc.) :contentReference[oaicite:19]{index=19}
│   │
│   └── views/                             # Blueprint modules
│       ├── user.py                        # /user: login, register, reset, logout, dashboard :contentReference[oaicite:20]{index=20}
│       ├── student.py                     # /student: profile, internships, applications :contentReference[oaicite:21]{index=21}
│       ├── employer.py                    # /employer: post internships, manage applications :contentReference[oaicite:22]{index=22}
│       └── admin.py                       # /admin: dashboards, user & stats management :contentReference[oaicite:23]{index=23}
│
├── templates/                             # Jinja2 templates
│   ├── base.html                          # Global layout :contentReference[oaicite:24]{index=24}
│   ├── home.html                          # Landing page :contentReference[oaicite:25]{index=25}
│   ├── user/                              # login.html, register.html, forgot_password.html
│   ├── student/                           # student_profile.html, applications.html, internships.html
│   ├── employer/                          # internship_form.html, internships.html, applications.html
│   └── admin/                             # admin_base.html, dashboard.html, user_management.html,
│                                            application_management.html, internship_management.html
│
└── static/                                # Static assets
    ├── css/bootstrap.min.css
    ├── js/bootstrap.bundle.min.js
    ├── js/jquery.min.js
    └── uploads/                           # user-uploaded files
        ├── avatars/
        └── resumes/