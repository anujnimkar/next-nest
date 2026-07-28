from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, RadioField, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange

from app.services.data_loader import get_career_field_map
def career_choices():
    return [(field["id"], field["label"]) for field in sorted(get_career_field_map().values(), key=lambda item: item["label"])]


class PartnerForm(FlaskForm):
    career_field = SelectField("Career field (next 5–7 years)", choices=[], validators=[DataRequired()])
    max_commute = IntegerField(
        "Maximum one-way commute (minutes)",
        default=35,
        validators=[DataRequired(), NumberRange(min=10, max=90)],
    )
    submit = SubmitField("Continue")


class PreferencesForm(FlaskForm):
    has_kids = RadioField(
        "Do you have kids or plan to?",
        choices=[("yes", "Yes"), ("no", "No")],
        default="no",
        validators=[DataRequired()],
    )
    partner1_career_importance = IntegerField(
        "Partner 1 – Career importance",
        default=5,
        validators=[InputRequired(), NumberRange(min=0, max=10)],
    )
    partner1_salary = IntegerField(
        "Partner 1 – Monthly salary preference",
        default=10000,
        validators=[InputRequired(), NumberRange(min=0, max=100000)],
    )
    partner1_housing = IntegerField(
        "Partner 1 – Monthly housing budget",
        default=3000,
        validators=[InputRequired(), NumberRange(min=0, max=10000)],
    )
    partner1_col = IntegerField(
        "Partner 1 – Monthly cost of living budget",
        default=1500,
        validators=[InputRequired(), NumberRange(min=0, max=10000)],
    )
    partner1_childcare = IntegerField(
        "Partner 1 – Monthly childcare budget",
        default=2000,
        validators=[InputRequired(), NumberRange(min=0, max=10000)],
    )
    partner2_career_importance = IntegerField(
        "Partner 2 – Career importance",
        default=5,
        validators=[InputRequired(), NumberRange(min=0, max=10)],
    )
    partner2_salary = IntegerField(
        "Partner 2 – Monthly salary preference",
        default=10000,
        validators=[InputRequired(), NumberRange(min=0, max=100000)],
    )
    partner2_housing = IntegerField(
        "Partner 2 – Monthly housing budget",
        default=3000,
        validators=[InputRequired(), NumberRange(min=0, max=10000)],
    )
    partner2_col = IntegerField(
        "Partner 2 – Monthly cost of living budget",
        default=1500,
        validators=[InputRequired(), NumberRange(min=0, max=10000)],
    )
    partner2_childcare = IntegerField(
        "Partner 2 – Monthly childcare budget",
        default=2000,
        validators=[InputRequired(), NumberRange(min=0, max=10000)],
    )
    submit = SubmitField("See ranked locations")


def init_partner_form(form: PartnerForm) -> None:
    form.career_field.choices = career_choices()
