from functools import wraps
from flask_discord import DiscordOAuth2Session
from hello import app, oauth

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = oauth.fetch_user()

        if not str(user.id) in app.config["PERMISSIONS"]:
            return 'Доступ запрещен'
        return f(*args, **kwargs)
    return decorated_function