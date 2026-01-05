from db.mongo import users_collection, login_logs_collection
from datetime import datetime
from collections import defaultdict

def get_user_profile(email):
    user = users_collection.find_one(
        {"email": email},
        {"_id": 0, "password": 0, "face_embedding": 0}
    )

    if not user:
        return None

    login_count = login_logs_collection.count_documents({"email": email})

    user["total_logins"] = login_count

    return user
def get_login_statistics(email):
    total = login_logs_collection.count_documents({"email": email})
    success = login_logs_collection.count_documents({
        "email": email,
        "status": "success"
    })
    failed = total - success

    success_rate = 0
    if total > 0:
        success_rate = round((success / total) * 100, 2)

    return {
        "total_logins": total,
        "successful_logins": success,
        "failed_logins": failed,
        "success_rate": success_rate
    }
def get_security_score(success_rate):
    if success_rate >= 90:
        return "HIGH"
    elif success_rate >= 60:
        return "MEDIUM"
    else:
        return "LOW"
def get_dashboard(email):
    profile = get_user_profile(email)
    if not profile:
        return None

    stats = get_login_statistics(email)
    security = get_security_score(stats["success_rate"])
    trends = get_monthly_login_trends(email)

    dashboard_data = {
        "profile": profile,
        "statistics": stats,
        "security_score": security,
        "monthly_trends": trends
    }

    return dashboard_data

    return dashboard_data
def get_monthly_login_trends(email):
    logs = login_logs_collection.find({"email": email})
    monthly_counts = defaultdict(int)

    for log in logs:
        month_year = log["timestamp"].strftime("%Y-%m")
        monthly_counts[month_year] += 1

    # Sort by month
    sorted_trends = dict(sorted(monthly_counts.items()))
    return sorted_trends