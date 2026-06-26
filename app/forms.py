from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    is_admin = BooleanField("Organisation Admin", default=True)


class ProgramForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=180)])
    subtitle = StringField("Subtitle", validators=[Optional(), Length(max=260)])
    banner_image = FileField("Banner Image", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"])])
    description = TextAreaField("Description", validators=[DataRequired()])
    dates = StringField("Dates", validators=[DataRequired(), Length(max=120)])
    deadline = StringField("Registration Deadline", validators=[Optional(), Length(max=120)])
    location = StringField("Location", validators=[DataRequired(), Length(max=180)])
    venue = StringField("Venue", validators=[Optional(), Length(max=180)])
    tags = StringField("Tags", description="Comma-separated e.g. Leadership, HR, Governance")


class ActivityForm(FlaskForm):
    day_schedule_id = SelectField("Day Schedule", coerce=int, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired(), Length(max=160)])
    time = StringField("Time", validators=[DataRequired(), Length(max=80)])
    details = TextAreaField("Details", validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=140)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    organisation = StringField("Organisation", validators=[Optional(), Length(max=160)])


class ParticipantForm(FlaskForm):
    participant_type = SelectField("Type", choices=[("individual", "Individual"), ("organisation", "Organisation")])
    name = StringField("Name", validators=[DataRequired(), Length(max=180)])
    email = StringField("Email", validators=[Optional(), Email()])
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    notes = TextAreaField("Notes", validators=[Optional()])


class HighlightForm(FlaskForm):
    details = TextAreaField("Highlight Details", validators=[DataRequired()])


class ProgramModelForm(FlaskForm):
    details = TextAreaField("Model Details", validators=[DataRequired()])


class PricingForm(FlaskForm):
    description = TextAreaField("Pricing Description", validators=[DataRequired()])


class PackageForm(FlaskForm):
    detail = StringField("Package Detail", validators=[DataRequired(), Length(max=255)])
    included = BooleanField("Included in package", default=False)


class DayScheduleForm(FlaskForm):
    title = StringField("Schedule Title", validators=[DataRequired(), Length(max=180)])
    date = StringField("Date", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[DataRequired()])


class ScheduleDetailForm(FlaskForm):
    title = StringField("Detail Title", validators=[DataRequired(), Length(max=180)])
    details = TextAreaField("Details", validators=[DataRequired()])


class AudienceForm(FlaskForm):
    detail = TextAreaField("Audience Detail", validators=[DataRequired()])
