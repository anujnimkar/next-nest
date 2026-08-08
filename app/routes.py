from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.forms import PartnerForm, PreferencesForm, init_partner_form
from app.services.scoring import rank_metros

bp = Blueprint("main", __name__)

SESSION_KEY = "relocation_preferences"


def _partner_preferences(prefix: str, form: PreferencesForm) -> dict[str, int]:
    return {
        "career_importance": getattr(form, f"{prefix}_career_importance").data,
        "salary": getattr(form, f"{prefix}_salary").data,
        "housing": getattr(form, f"{prefix}_housing").data,
        "col": getattr(form, f"{prefix}_col").data,
        "childcare": getattr(form, f"{prefix}_childcare").data,
    }


@bp.route("/", methods=["GET", "POST"])
def index():
    step = request.args.get("step", "1")
    if step == "1":
        return _partner_step("partner1", 1, 2)
    if step == "2":
        if "partner1" not in session.get(SESSION_KEY, {}):
            return redirect(url_for("main.index", step=1))
        return _partner_step("partner2", 2, 3)
    if step == "3":
        data = session.get(SESSION_KEY, {})
        if "partner1" not in data or "partner2" not in data:
            return redirect(url_for("main.index", step=1))
        return _preferences_step()
    return redirect(url_for("main.index", step=1))


def _partner_step(partner_key: str, current_step: int, next_step: int):
    form = PartnerForm()
    init_partner_form(form)
    saved_partner = session.get(SESSION_KEY, {}).get(partner_key)
    if request.method == "GET" and saved_partner:
        form.process(
            data={
                "career_field": saved_partner["field"],
                "max_commute": saved_partner["commute"],
            }
        )
    if form.validate_on_submit():
        session.setdefault(SESSION_KEY, {})
        session[SESSION_KEY][partner_key] = {
            "field": form.career_field.data,
            "commute": form.max_commute.data,
        }
        session.modified = True
        return redirect(url_for("main.index", step=next_step))
    return render_template(
        "index.html",
        form=form,
        step=current_step,
        partner_label="Partner 1" if partner_key == "partner1" else "Partner 2",
    )


def _preferences_step():
    form = PreferencesForm()
    saved_preferences = session.get(SESSION_KEY, {}).get("preferences")
    if request.method == "GET" and saved_preferences:
        partner1 = saved_preferences["partner1_preferences"]
        partner2 = saved_preferences["partner2_preferences"]
        form.process(
            data={
                "has_kids": "yes" if saved_preferences["has_kids"] else "no",
                **{f"partner1_{key}": value for key, value in partner1.items()},
                **{f"partner2_{key}": value for key, value in partner2.items()},
            }
        )
    if form.validate_on_submit():
        data = session.get(SESSION_KEY, {})
        preferences = {
            "partner1_field": data["partner1"]["field"],
            "partner1_commute": data["partner1"]["commute"],
            "partner2_field": data["partner2"]["field"],
            "partner2_commute": data["partner2"]["commute"],
            "has_kids": form.has_kids.data == "yes",
            "partner1_preferences": _partner_preferences("partner1", form),
            "partner2_preferences": _partner_preferences("partner2", form),
        }
        session[SESSION_KEY]["preferences"] = preferences
        session.modified = True
        return redirect(url_for("main.results"))
    return render_template("index.html", form=form, step=3, partner_label="Household")


@bp.route("/results")
def results():
    data = session.get(SESSION_KEY, {})
    preferences = data.get("preferences")
    if not preferences:
        flash("Please complete the questionnaire first.", "warning")
        return redirect(url_for("main.index", step=1))

    ranked = rank_metros(preferences)
    return render_template(
        "results.html",
        ranked=ranked,
        preferences=preferences,
        has_kids=preferences["has_kids"],
    )


@bp.route("/reset")
def reset():
    session.pop(SESSION_KEY, None)
    return redirect(url_for("main.index", step=1))
