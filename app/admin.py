import os
from functools import wraps
from uuid import uuid4
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from . import db
from .models import (
    Program,
    Tag,
    Activity,
    Highlight,
    ProgramModel,
    Pricing,
    Package,
    DaySchedule,
    ScheduleDetail,
    Registration,
    Participant,
    User,
    Audience,
)
from .forms import (
    ProgramForm,
    ActivityForm,
    ParticipantForm,
    HighlightForm,
    ProgramModelForm,
    PricingForm,
    PackageForm,
    DayScheduleForm,
    ScheduleDetailForm,
    UserForm,
    AudienceForm,
)


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def save_image(file):
    if not file:
        return None
    filename = secure_filename(file.filename)
    if not filename:
        return None
    ext = filename.rsplit(".", 1)[-1].lower()
    stored = f"{uuid4().hex}.{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], stored)
    file.save(path)
    return stored


def sync_tags(program, tag_string):
    program.tags.clear()
    for raw in (tag_string or "").split(","):
        name = raw.strip().title()
        if not name:
            continue
        tag = Tag.query.filter_by(name=name).first() or Tag(name=name)
        db.session.add(tag)
        program.tags.append(tag)


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        program_count=Program.query.count(),
        registration_count=Registration.query.count(),
        participant_count=Participant.query.count(),
        user_count=User.query.count(),
    )


@admin_bp.route("/programs")
@login_required
@admin_required
def programs():
    programs = Program.query.order_by(Program.created_at.desc()).all()
    return render_template("admin/programs.html", programs=programs)


@admin_bp.route("/programs/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_program():
    form = ProgramForm()
    if form.validate_on_submit():
        program = Program(
            title=form.title.data,
            subtitle=form.subtitle.data,
            description=form.description.data,
            dates=form.dates.data,
            deadline=form.deadline.data,
            location=form.location.data,
            venue=form.venue.data,
            banner_image=save_image(form.banner_image.data),
        )
        sync_tags(program, form.tags.data)
        db.session.add(program)
        db.session.commit()
        flash("Program created.", "success")
        return redirect(url_for("admin.programs"))
    return render_template("admin/program_form.html", form=form, title="New Program")


@admin_bp.route("/programs/<int:program_id>/", methods=["GET", "POST"])
@login_required
@admin_required
def program_details(program_id):
    program = Program.query.get_or_404(program_id)
    activity_form = ActivityForm()
    activity_form.day_schedule_id.choices = [(schedule.id, schedule.title) for schedule in program.day_schedules]
    participant_form = ParticipantForm()
    highlight_form = HighlightForm()
    model_form = ProgramModelForm()
    pricing_form = PricingForm()
    package_form = PackageForm()
    day_schedule_form = DayScheduleForm()
    schedule_detail_form = ScheduleDetailForm()
    audience_form = AudienceForm()
    return render_template(
        "admin/program_details.html",
        program=program,
        activity_form=activity_form,
        participant_form=participant_form,
        highlight_form=highlight_form,
        model_form=model_form,
        pricing_form=pricing_form,
        package_form=package_form,
        day_schedule_form=day_schedule_form,
        schedule_detail_form=schedule_detail_form,
        audience_form=audience_form,
    )



@admin_bp.route("/programs/<int:program_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_program(program_id):
    program = Program.query.get_or_404(program_id)
    form = ProgramForm(obj=program)
    if not form.is_submitted():
        form.tags.data = ", ".join(tag.name for tag in program.tags)
    if form.validate_on_submit():
        program.title = form.title.data
        program.subtitle = form.subtitle.data
        program.description = form.description.data
        program.dates = form.dates.data
        program.deadline = form.deadline.data
        program.location = form.location.data
        program.venue = form.venue.data
        image = None
        if form.banner_image.data:
            image = save_image(form.banner_image.data)
        if image:
            program.banner_image = image
        sync_tags(program, form.tags.data)
        db.session.commit()
        flash("Program updated.", "success")
        return redirect(url_for("admin.programs"))
    return render_template("admin/program_form.html", form=form, title="Edit Program")


@admin_bp.route("/programs/<int:program_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_program(program_id):
    program = Program.query.get_or_404(program_id)
    db.session.delete(program)
    db.session.commit()
    flash("Program deleted.", "success")
    return redirect(url_for("admin.programs"))


@admin_bp.route("/programs/<int:program_id>/activities/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_activity(program_id):
    program = Program.query.get_or_404(program_id)
    if not program.day_schedules:
        flash("Please add a day schedule before adding activities.", "error")
        return redirect(url_for("admin.program_details", program_id=program.id))

    form = ActivityForm()
    form.day_schedule_id.choices = [(schedule.id, schedule.title) for schedule in program.day_schedules]
    if form.validate_on_submit():
        schedule = DaySchedule.query.get(form.day_schedule_id.data)
        if not schedule or schedule.program_id != program.id:
            flash("Invalid schedule selected.", "error")
            return redirect(url_for("admin.program_details", program_id=program.id))
        activity = Activity(
            program=program,
            day_schedule=schedule,
            day=schedule.title,
            title=form.title.data,
            time=form.time.data,
            details=form.details.data,
        )
        db.session.add(activity)
        db.session.commit()
        flash("Activity added.", "success")
        return redirect(url_for("admin.program_details", program_id=program.id))
    return render_template("admin/activity_form.html", form=form, program=program)


@admin_bp.route("/programs/<int:program_id>/participants/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_participant(program_id):
    program = Program.query.get_or_404(program_id)
    form = ParticipantForm()
    if form.validate_on_submit():
        participant = Participant(program=program, participant_type=form.participant_type.data, name=form.name.data, email=form.email.data, phone=form.phone.data, notes=form.notes.data)
        db.session.add(participant)
        db.session.commit()
        flash("Participant added.", "success")
        return redirect(url_for("admin.program_details", program_id=program.id))
    return render_template("admin/participant_form.html", form=form, program=program)


@admin_bp.route("/programs/<int:program_id>/highlights/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_highlight(program_id):
    program = Program.query.get_or_404(program_id)
    form = HighlightForm()
    if form.validate_on_submit():
        highlight = Highlight(program=program, details=form.details.data)
        db.session.add(highlight)
        db.session.commit()
        flash("Highlight added.", "success")
        return redirect(url_for("admin.program_details", program_id=program.id))
    return render_template("admin/highlight_form.html", form=form, program=program)


@admin_bp.route("/highlights/<int:highlight_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_highlight(highlight_id):
    highlight = Highlight.query.get_or_404(highlight_id)
    form = HighlightForm()
    if form.validate_on_submit():
        highlight.details = form.details.data
        db.session.commit()
        flash("Highlight updated.", "success")
        return redirect(url_for("admin.program_details", program_id=highlight.program_id))
    elif request.method == "GET":
        form.details.data = highlight.details
    return render_template("admin/highlight_form.html", form=form, highlight=highlight)


@admin_bp.route("/highlights/<int:highlight_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_highlight(highlight_id):
    highlight = Highlight.query.get_or_404(highlight_id)
    program_id = highlight.program_id
    db.session.delete(highlight)
    db.session.commit()
    flash("Highlight deleted.", "success")
    return redirect(url_for("admin.program_details", program_id=program_id))


@admin_bp.route("/programs/<int:program_id>/audience/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_audience(program_id):
    program = Program.query.get_or_404(program_id)
    form = AudienceForm()
    if form.validate_on_submit():
        audience = Audience(program=program, detail=form.detail.data)
        db.session.add(audience)
        db.session.commit()
        flash("Audience detail added.", "success")
        return redirect(url_for("admin.program_details", program_id=program.id))
    return render_template("admin/audience_form.html", form=form, program=program)


@admin_bp.route("/audience/<int:audience_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_audience(audience_id):
    audience = Audience.query.get_or_404(audience_id)
    form = AudienceForm()
    if form.validate_on_submit():
        audience.detail = form.detail.data
        db.session.commit()
        flash("Audience detail updated.", "success")
        return redirect(url_for("admin.program_details", program_id=audience.program_id))
    elif request.method == "GET":
        form.detail.data = audience.detail
    return render_template("admin/audience_form.html", form=form, audience=audience)


@admin_bp.route("/audience/<int:audience_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_audience(audience_id):
    audience = Audience.query.get_or_404(audience_id)
    program_id = audience.program_id
    db.session.delete(audience)
    db.session.commit()
    flash("Audience detail deleted.", "success")
    return redirect(url_for("admin.program_details", program_id=program_id))


@admin_bp.route("/programs/<int:program_id>/models/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_program_model(program_id):
    program = Program.query.get_or_404(program_id)
    form = ProgramModelForm()
    if form.validate_on_submit():
        program_model = ProgramModel(program=program, details=form.details.data)
        db.session.add(program_model)
        db.session.commit()
        flash("Model detail added.", "success")
        return redirect(url_for("admin.program_details", program_id=program.id))
    return render_template("admin/model_form.html", form=form, program=program)


@admin_bp.route("/activities/<int:activity_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    form = ActivityForm()
    program = activity.program
    form.day_schedule_id.choices = [(schedule.id, schedule.title) for schedule in program.day_schedules]
    if form.validate_on_submit():
        schedule = DaySchedule.query.get(form.day_schedule_id.data)
        if schedule and schedule.program_id == program.id:
            activity.day_schedule = schedule
            activity.day = schedule.title
        activity.title = form.title.data
        activity.time = form.time.data
        activity.details = form.details.data
        db.session.commit()
        flash("Activity updated.", "success")
        return redirect(url_for("admin.program_details", program_id=activity.program_id))
    elif request.method == "GET":
        form.day_schedule_id.data = activity.day_schedule_id if activity.day_schedule_id else None
        form.title.data = activity.title
        form.time.data = activity.time
        form.details.data = activity.details
    return render_template("admin/activity_form.html", form=form, activity=activity, program=activity.program)


@admin_bp.route("/activities/<int:activity_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    program_id = activity.program_id
    db.session.delete(activity)
    db.session.commit()
    flash("Activity deleted.", "success")
    return redirect(url_for("admin.program_details", program_id=program_id))


@admin_bp.route("/participants/<int:participant_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    form = ParticipantForm()
    if form.validate_on_submit():
        participant.participant_type = form.participant_type.data
        participant.name = form.name.data
        participant.email = form.email.data
        participant.phone = form.phone.data
        participant.notes = form.notes.data
        db.session.commit()
        flash("Participant updated.", "success")
        return redirect(url_for("admin.program_details", program_id=participant.program_id))
    elif request.method == "GET":
        form.participant_type.data = participant.participant_type
        form.name.data = participant.name
        form.email.data = participant.email
        form.phone.data = participant.phone
        form.notes.data = participant.notes
    return render_template("admin/participant_form.html", form=form, participant=participant)


@admin_bp.route("/participants/<int:participant_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    program_id = participant.program_id
    db.session.delete(participant)
    db.session.commit()
    flash("Participant deleted.", "success")
    return redirect(url_for("admin.program_details", program_id=program_id))


@admin_bp.route("/pricing/<int:pricing_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_pricing(pricing_id):
    pricing = Pricing.query.get_or_404(pricing_id)
    form = PricingForm()
    if form.validate_on_submit():
        pricing.description = form.description.data
        db.session.commit()
        flash("Pricing updated.", "success")
        return redirect(url_for("admin.program_details", program_id=pricing.program_id))
    elif request.method == "GET":
        form.description.data = pricing.description
    return render_template("admin/pricing_form.html", form=form, pricing=pricing)


@admin_bp.route("/pricing/<int:pricing_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_pricing(pricing_id):
    pricing = Pricing.query.get_or_404(pricing_id)
    program_id = pricing.program_id
    db.session.delete(pricing)
    db.session.commit()
    flash("Pricing deleted.", "success")
    return redirect(url_for("admin.program_details", program_id=program_id))


@admin_bp.route("/packages/<int:package_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_package(package_id):
    package = Package.query.get_or_404(package_id)
    form = PackageForm()
    if form.validate_on_submit():
        package.detail = form.detail.data
        package.included = form.included.data
        db.session.commit()
        flash("Package item updated.", "success")
        return redirect(url_for("admin.program_details", program_id=package.pricing.program_id))
    elif request.method == "GET":
        form.detail.data = package.detail
        form.included.data = package.included
    return render_template("admin/package_form.html", form=form, package=package)


@admin_bp.route("/packages/<int:package_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_package(package_id):
    package = Package.query.get_or_404(package_id)
    program_id = package.pricing.program_id
    db.session.delete(package)
    db.session.commit()
    flash("Package item deleted.", "success")
    return redirect(url_for("admin.program_details", program_id=program_id))


@admin_bp.route("/day-schedules/<int:schedule_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_day_schedule(schedule_id):
    schedule = DaySchedule.query.get_or_404(schedule_id)
    form = DayScheduleForm()
    if form.validate_on_submit():
        schedule.title = form.title.data
        schedule.date = form.date.data
        schedule.description = form.description.data
        db.session.commit()
        flash("Day schedule updated.", "success")
        return redirect(url_for("admin.program_details", program_id=schedule.program_id))
    elif request.method == "GET":
        form.title.data = schedule.title
        form.date.data = schedule.date
        form.description.data = schedule.description
    return render_template("admin/day_schedule_form.html", form=form, schedule=schedule)


@admin_bp.route("/day-schedules/<int:schedule_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_day_schedule(schedule_id):
    schedule = DaySchedule.query.get_or_404(schedule_id)
    program_id = schedule.program_id
    db.session.delete(schedule)
    db.session.commit()
    flash("Day schedule deleted.", "success")
    return redirect(url_for("admin.program_details", program_id=program_id))


@admin_bp.route("/schedule-details/<int:detail_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_schedule_detail(detail_id):
    detail = ScheduleDetail.query.get_or_404(detail_id)
    form = ScheduleDetailForm()
    if form.validate_on_submit():
        detail.title = form.title.data
        detail.details = form.details.data
        db.session.commit()
        flash("Schedule detail updated.", "success")
        return redirect(url_for("admin.program_details", program_id=detail.day_schedule.program_id))
    elif request.method == "GET":
        form.title.data = detail.title
        form.details.data = detail.details
    return render_template("admin/schedule_detail_form.html", form=form, detail=detail)


@admin_bp.route("/schedule-details/<int:detail_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_schedule_detail(detail_id):
    detail = ScheduleDetail.query.get_or_404(detail_id)
    program_id = detail.day_schedule.program_id
    db.session.delete(detail)
    db.session.commit()
    flash("Schedule detail deleted.", "success")
    return redirect(url_for("admin.program_details", program_id=program_id))


@admin_bp.route("/programs/<int:program_id>/pricing/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_pricing(program_id):
    program = Program.query.get_or_404(program_id)
    form = PricingForm()
    if form.validate_on_submit():
        pricing = Pricing(program=program, description=form.description.data)
        db.session.add(pricing)
        db.session.commit()
        flash("Pricing plan added.", "success")
        return redirect(url_for("admin.program_details", program_id=program.id))
    return render_template("admin/pricing_form.html", form=form, program=program)


@admin_bp.route("/pricing/<int:pricing_id>/packages/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_package(pricing_id):
    pricing = Pricing.query.get_or_404(pricing_id)
    form = PackageForm()
    if form.validate_on_submit():
        package = Package(pricing=pricing, detail=form.detail.data, included=form.included.data)
        db.session.add(package)
        db.session.commit()
        flash("Package item added.", "success")
        return redirect(url_for("admin.program_details", program_id=pricing.program.id))
    return render_template("admin/package_form.html", form=form, pricing=pricing)


@admin_bp.route("/programs/<int:program_id>/schedules/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_day_schedule(program_id):
    program = Program.query.get_or_404(program_id)
    form = DayScheduleForm()
    if form.validate_on_submit():
        schedule = DaySchedule(program=program, title=form.title.data, date=form.date.data, description=form.description.data)
        db.session.add(schedule)
        db.session.commit()
        flash("Day schedule added.", "success")
        return redirect(url_for("admin.program_details", program_id=program.id))
    return render_template("admin/day_schedule_form.html", form=form, program=program)


@admin_bp.route("/schedules/<int:schedule_id>/details/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_schedule_detail(schedule_id):
    schedule = DaySchedule.query.get_or_404(schedule_id)
    form = ScheduleDetailForm()
    if form.validate_on_submit():
        detail = ScheduleDetail(day_schedule=schedule, title=form.title.data, details=form.details.data)
        db.session.add(detail)
        db.session.commit()
        flash("Schedule detail added.", "success")
        return redirect(url_for("admin.program_details", program_id=schedule.program.id))
    return render_template("admin/schedule_detail_form.html", form=form, schedule=schedule)


@admin_bp.route("/registrations")
@login_required
@admin_required
def registrations():
    registrations = Registration.query.order_by(Registration.created_at.desc()).all()
    return render_template("admin/registrations.html", registrations=registrations)


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data.lower(), password_hash=generate_password_hash(form.password.data), is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash("Admin user added.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form)
