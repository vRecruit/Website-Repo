from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from vrecruit import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    your_name = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(120), nullable=False)
    new_acc = db.Column(db.Boolean, default=True)
    contact_number = db.Column(db.Integer, nullable=False)
    posts = db.relationship('PostJob', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.email}', '{self.your_name}', '{self.contact_number}', '{self.user_type}')"

class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(120), nullable=True)
    designation = db.Column(db.String(120), nullable=True)
    company_website = db.Column(db.String(120), nullable=True)
    company_address = db.Column(db.Text, nullable=True)
   #  company_logo = db.Column(db.String(100), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Employer('{self.company_name}', '{self.designation}', '{self.company_website}', '{self.company_address}')"

class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
   #  profile_picture = db.Column(db.String(100), nullable=False, default='default.jpg')
   #  resume = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Applicant('{self.college_name}')"

class PostJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(100), nullable=False)
    no_of_openings = db.Column(db.Integer, nullable=False)
    job_profile = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    job_stipend = db.Column(db.Integer, nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    skills_required = db.Column(db.Text, nullable=False)
    job_experience = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"PostJob(('{self.job_type}', '{self.no_of_openings}', '{self.job_profile}', '{self.date_posted}', '{self.job_stipend}', '{self.job_description}', '{self.skills_required}', '{self.job_experience}')"
