from flask import Blueprint, render_template, redirect, url_for, flash
from .models import Program
from .forms import RegistrationForm
from . import db


public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    programs = Program.query.order_by(Program.created_at.desc()).limit(3).all()
    return render_template("/public/home.html", programs=programs)


@public_bp.route("/programs")
def programs():
    programs = Program.query.order_by(Program.created_at.desc()).all()
    return render_template("public/programs.html", programs=programs)


@public_bp.route("/programs/<int:program_id>", methods=["GET", "POST"])
def program_detail(program_id):
    program = Program.query.get_or_404(program_id)
    form = RegistrationForm()
    if form.validate_on_submit():
        registration = form.populate_obj(type("RegistrationObj", (), {})())
        from .models import Registration
        registration = Registration(
            program=program,
            full_name=form.full_name.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            organisation=form.organisation.data,
        )
        db.session.add(registration)
        db.session.commit()
        flash("Registration submitted successfully.", "success")
        return redirect(url_for("public.program_detail", program_id=program.id))
    return render_template("public/program_detail.html", program=program, form=form)


@public_bp.route("/about")
def about():
    return render_template("public/about.html")

@public_bp.route("/services")
def services():
    return render_template("public/services.html")


@public_bp.route("/portfolio")
def portfolio():
    return render_template("public/portfolio.html")


@public_bp.route("/contact")
def contact():
    return render_template("public/contact.html")
