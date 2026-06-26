from datetime import datetime
from flask_login import UserMixin
from . import db

program_tags = db.Table(
    "program_tags",
    db.Column("program_id", db.Integer, db.ForeignKey("program.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    subtitle = db.Column(db.String(260))
    banner_image = db.Column(db.String(255))
    description = db.Column(db.Text, nullable=False)
    dates = db.Column(db.String(120), nullable=False)
    deadline = db.Column(db.String(120))
    location = db.Column(db.String(180), nullable=False)
    venue = db.Column(db.String(180))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tags = db.relationship("Tag", secondary=program_tags, backref="programs")
    highlights = db.relationship("Highlight", backref="program", cascade="all, delete-orphan")
    models = db.relationship("ProgramModel", backref="program", cascade="all, delete-orphan")
    pricings = db.relationship("Pricing", backref="program", cascade="all, delete-orphan")
    day_schedules = db.relationship("DaySchedule", backref="program", cascade="all, delete-orphan")
    activities = db.relationship("Activity", backref="program", cascade="all, delete-orphan")
    registrations = db.relationship("Registration", backref="program", cascade="all, delete-orphan")
    participants = db.relationship("Participant", backref="program", cascade="all, delete-orphan")
    audience = db.relationship("Audience", backref="program", cascade="all, delete-orphan")

class Audience(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    detail = db.Column(db.String(120), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False) 
    
class Highlight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False)
    details = db.Column(db.Text, nullable=False)


class ProgramModel(db.Model):
    __tablename__ = "model"
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False)
    details = db.Column(db.Text, nullable=False)


class Pricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)
    packages = db.relationship("Package", backref="pricing", cascade="all, delete-orphan")


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pricing_id = db.Column(db.Integer, db.ForeignKey("pricing.id"), nullable=False)
    detail = db.Column(db.String(255), nullable=False)
    included = db.Column(db.Boolean, default=False)



class DaySchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    date = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    schedule_details = db.relationship("ScheduleDetail", backref="day_schedule", cascade="all, delete-orphan")


class ScheduleDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_schedule_id = db.Column(db.Integer, db.ForeignKey("day_schedule.id"), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    details = db.Column(db.Text, nullable=False)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False)
    day_schedule_id = db.Column(db.Integer, db.ForeignKey("day_schedule.id"), nullable=True)
    day = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text, nullable=False)
    day_schedule = db.relationship("DaySchedule", backref="activities")


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False)
    full_name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(40))
    organisation = db.Column(db.String(160))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False)
    participant_type = db.Column(db.String(40), nullable=False)  # individual/organisation
    name = db.Column(db.String(180), nullable=False)
    email = db.Column(db.String(150))
    phone = db.Column(db.String(40))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
