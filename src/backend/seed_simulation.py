# ---- Simulation data seeder ----
# Creates three demo older adults with controlled score trajectories
# (stable / worsening / improving) plus one caregiver linked to all of
# them. These simulated trajectories are the reliability check for the
# trend-linked risk flag defined in the Unit 3 design: the flag must
# fire for the worsening and sustained-high patterns and must stay
# silent for stable and improving patterns.
#
# Usage:
#   cd src/backend
#   python seed_simulation.py
#
# Demo accounts (password for all: Passw0rd!demo):
#   tanaka  (older adult, stable)      sato (older adult, worsening)
#   suzuki  (older adult, improving)   kaigo (caregiver, linked to all)

from core import scoring, trend
from data import repository as repo
from modules import auth

PASSWORD = "Passw0rd!demo"

# Each answer triple maps to a score between 3 and 9.
TRAJECTORIES = {
    "tanaka": {
        "display_name": "Hanako Tanaka",
        "pattern": "stable",
        "answers": [(1, 1, 2), (1, 2, 1), (2, 1, 1), (1, 1, 2), (1, 2, 1)],
    },
    "sato": {
        "display_name": "Taro Sato",
        "pattern": "worsening",
        "answers": [(1, 1, 2), (2, 2, 1), (2, 2, 2), (3, 2, 2), (3, 3, 2)],
    },
    "suzuki": {
        "display_name": "Yoshiko Suzuki",
        "pattern": "improving",
        "answers": [(3, 3, 2), (3, 2, 2), (2, 2, 2), (2, 1, 2), (1, 2, 1)],
    },
}


def seed():
    conn = repo.get_connection()
    repo.init_db(conn)

    password_hash = auth.hash_password(PASSWORD)
    older_ids = {}

    for username, spec in TRAJECTORIES.items():
        if repo.find_user_by_username(conn, username):
            print(f"skip {username}: already exists")
            continue
        user_id = repo.create_user(
            conn, username, password_hash, "older_adult", spec["display_name"]
        )
        older_ids[username] = user_id
        repo.grant_consent(conn, user_id, "1.0")
        for answers in spec["answers"]:
            clean = scoring.validate_answers(
                {"q1": answers[0], "q2": answers[1], "q3": answers[2]}
            )
            score = scoring.compute_score(clean)
            repo.save_response(conn, user_id, clean, score)
            history = [r["score"] for r in repo.score_history(conn, user_id)]
            flag = trend.evaluate_flag(history)
            if flag["level"] != trend.FLAG_NONE:
                repo.save_flag(conn, user_id, flag["level"], flag["reason"])
        scores = [r["score"] for r in repo.score_history(conn, user_id)]
        final_flag = trend.evaluate_flag(scores)
        print(
            f"{username} ({spec['pattern']}): scores={scores} "
            f"flag={final_flag['level']}"
        )

    if not repo.find_user_by_username(conn, "kaigo"):
        caregiver_id = repo.create_user(
            conn, "kaigo", password_hash, "caregiver", "Kei Yamamoto"
        )
        for user_id in older_ids.values():
            repo.link_caregiver(conn, caregiver_id, user_id)
        print("kaigo (caregiver): linked to all seeded older adults")

    conn.close()
    print("done")


if __name__ == "__main__":
    seed()
