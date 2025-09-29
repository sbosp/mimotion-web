from app import create_app
from flask_login import LoginManager
from app.models import User

app = create_app()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5003)
