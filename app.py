from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from models import db
from flask_migrate import Migrate

from pedidos import pedidos

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

app.register_blueprint(pedidos)

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect()

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == '__main__':
    csrf.init_app(app)
    with app.app_context():
        db.create_all()

    app.run(debug=True)