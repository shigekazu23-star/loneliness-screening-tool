# ---- Application / Logic layer: Flask REST API (controller + routing) ----
# Wires the modules defined in the Unit 3 design: M1 auth, M2 consent,
# M3 input validation, M4 scoring, M5 repository, M6 trend and risk flag,
# M7 visualization data. Core logic (M4, M6) stays in core/ with no Flask
# or SQLite imports, following the onion/clean separation.
#
# Run (development):
#   cd src/backend
#   pip install -r requirements.txt
#   flask --app app run --port 5000

from flask import Flask, g, jsonify, request
from flask_cors import CORS

from core import scoring, trend
from data import repository as repo
from modules import auth

CONSENT_VERSION = "1.0"


def create_app(db_path: str = None) -> Flask:
    app = Flask(__name__)
    CORS(app)

    def db():
        if "db" not in g:
            g.db = repo.get_connection(db_path)
        return g.db

    @app.teardown_appcontext
    def close_db(exc):
        conn = g.pop("db", None)
        if conn is not None:
            conn.close()

    with app.app_context():
        conn = repo.get_connection(db_path)
        repo.init_db(conn)
        conn.close()

    # ---- M1: registration and login ----

    @app.post("/api/register")
    def register():
        body = request.get_json(silent=True) or {}
        username = (body.get("username") or "").strip()
        password = body.get("password") or ""
        role = body.get("role") or ""
        display_name = (body.get("display_name") or username).strip()
        if not username or len(password) < 8:
            return jsonify(
                {"error": "username required and password of 8+ characters"}
            ), 400
        if role not in auth.ROLES:
            return jsonify({"error": "role must be older_adult or caregiver"}), 400
        if repo.find_user_by_username(db(), username):
            return jsonify({"error": "username already exists"}), 409
        user_id = repo.create_user(
            db(), username, auth.hash_password(password), role, display_name
        )
        return jsonify({"id": user_id, "username": username, "role": role}), 201

    @app.post("/api/login")
    def login():
        body = request.get_json(silent=True) or {}
        user = repo.find_user_by_username(db(), body.get("username") or "")
        if not user or not auth.verify_password(
            body.get("password") or "", user["password_hash"]
        ):
            return jsonify({"error": "invalid credentials"}), 401
        token = auth.issue_token(user["id"], user["role"])
        return jsonify(
            {
                "token": token,
                "role": user["role"],
                "display_name": user["display_name"],
            }
        )

    # ---- M2: consent (explicit, versioned, revocable) ----

    @app.get("/api/consent")
    @auth.require_auth("older_adult")
    def consent_status():
        active = repo.active_consent(db(), g.user_id)
        return jsonify(
            {
                "active": active is not None,
                "version": active["version"] if active else None,
                "granted_at": active["granted_at"] if active else None,
            }
        )

    @app.post("/api/consent")
    @auth.require_auth("older_adult")
    def grant_consent():
        if repo.active_consent(db(), g.user_id):
            return jsonify({"error": "consent already active"}), 409
        repo.grant_consent(db(), g.user_id, CONSENT_VERSION)
        return jsonify({"active": True, "version": CONSENT_VERSION}), 201

    @app.delete("/api/consent")
    @auth.require_auth("older_adult")
    def revoke_consent():
        repo.revoke_consent(db(), g.user_id)
        return jsonify({"active": False})

    # ---- M3 + M4 + M5 + M6: submit a questionnaire response ----

    @app.post("/api/responses")
    @auth.require_auth("older_adult")
    def submit_response():
        if not repo.active_consent(db(), g.user_id):
            return jsonify({"error": "active consent required"}), 403
        body = request.get_json(silent=True) or {}
        try:
            answers = scoring.validate_answers(body)  # M3
        except scoring.InvalidResponseError as err:
            return jsonify({"error": str(err)}), 400
        score = scoring.compute_score(answers)  # M4
        repo.save_response(db(), g.user_id, answers, score)  # M5
        history = [row["score"] for row in repo.score_history(db(), g.user_id)]
        flag = trend.evaluate_flag(history)  # M6
        if flag["level"] != trend.FLAG_NONE:
            repo.save_flag(db(), g.user_id, flag["level"], flag["reason"])
        return jsonify({"score": score, "flag": flag}), 201

    # ---- M7: visualization data for the dashboard ----

    @app.get("/api/responses")
    @auth.require_auth("older_adult")
    def my_history():
        history = repo.score_history(db(), g.user_id)
        scores = [row["score"] for row in history]
        return jsonify(
            {
                "history": history,
                "trend": trend.trend_direction(scores),
                "flag": trend.evaluate_flag(scores),
            }
        )

    # ---- caregiver view (RBAC + consent gate) ----

    @app.post("/api/caregiver/link")
    @auth.require_auth("caregiver")
    def link_older_adult():
        body = request.get_json(silent=True) or {}
        target = repo.find_user_by_username(db(), body.get("username") or "")
        if not target or target["role"] != "older_adult":
            return jsonify({"error": "older adult not found"}), 404
        if not repo.active_consent(db(), target["id"]):
            return jsonify({"error": "this person has not given consent"}), 403
        repo.link_caregiver(db(), g.user_id, target["id"])
        return jsonify({"linked": target["username"]}), 201

    @app.get("/api/caregiver/overview")
    @auth.require_auth("caregiver")
    def caregiver_overview():
        people = []
        for person in repo.linked_older_adults(db(), g.user_id):
            # Consent is re-checked on every read so that revocation
            # takes effect immediately (M2 design decision).
            if not repo.active_consent(db(), person["id"]):
                continue
            history = repo.score_history(db(), person["id"])
            scores = [row["score"] for row in history]
            people.append(
                {
                    "display_name": person["display_name"],
                    "username": person["username"],
                    "latest_score": scores[-1] if scores else None,
                    "trend": trend.trend_direction(scores),
                    "flag": trend.evaluate_flag(scores),
                    "history": history,
                }
            )
        return jsonify({"people": people})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5000, debug=True)
