from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, RadioField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from app.services.data_loader import get_career_field_map
from app.services.scoring import DEFAULT_WEIGHTS


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
    partner1_career = IntegerField("Partner 1 – Career priority", default=DEFAULT_WEIGHTS["career"], validators=[NumberRange(min=0, max=10)])
    partner1_housing = IntegerField("Partner 1 – Housing priority", default=DEFAULT_WEIGHTS["housing"], validators=[NumberRange(min=0, max=10)])
    partner1_col = IntegerField("Partner 1 – Cost of living priority", default=DEFAULT_WEIGHTS["col"], validators=[NumberRange(min=0, max=10)])
    partner1_commute = IntegerField("Partner 1 – Commute priority", default=DEFAULT_WEIGHTS["commute"], validators=[NumberRange(min=0, max=10)])
    partner1_childcare = IntegerField("Partner 1 – Childcare priority", default=DEFAULT_WEIGHTS["childcare"], validators=[NumberRange(min=0, max=10)])
    partner2_career = IntegerField("Partner 2 – Career priority", default=DEFAULT_WEIGHTS["career"], validators=[NumberRange(min=0, max=10)])
    partner2_housing = IntegerField("Partner 2 – Housing priority", default=DEFAULT_WEIGHTS["housing"], validators=[NumberRange(min=0, max=10)])
    partner2_col = IntegerField("Partner 2 – Cost of living priority", default=DEFAULT_WEIGHTS["col"], validators=[NumberRange(min=0, max=10)])
    partner2_commute = IntegerField("Partner 2 – Commute priority", default=DEFAULT_WEIGHTS["commute"], validators=[NumberRange(min=0, max=10)])
    partner2_childcare = IntegerField("Partner 2 – Childcare priority", default=DEFAULT_WEIGHTS["childcare"], validators=[NumberRange(min=0, max=10)])
    submit = SubmitField("See ranked locations")


def init_partner_form(form: PartnerForm) -> None:
    form.career_field.choices = career_choices()
