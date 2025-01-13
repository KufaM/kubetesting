from flask import Flask, render_template, request, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired, Regexp, NumberRange

app = Flask(__name__)

# Nastavení pro SQLite databázi
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Inicializace databáze a migrací
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Model pro řádky v databázi
class Row(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jmeno = db.Column(db.String(100), nullable=False)
    vek = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Row('{self.id}', '{self.jmeno}', '{self.vek}')"

class Uzivatele(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surename = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Uzivatele('{self.id}', '{self.name}', '{self.surename}')"

class FormFormular(FlaskForm):
    name = StringField('Name', validators=[
        InputRequired(message="You can't leave this empty"),
        Regexp('^[a-zA-Z]+$', message="Buď tak hodný a napiš sem reálné jméno")
    ])
    surename = StringField('Surename', validators=[
        InputRequired(message="You can't leave this empty"),
        Regexp('^[a-zA-Z]+$', message="Buď tak hodný a napiš sem reálné jméno")
    ])
    submit = SubmitField('Submit')

bp = Blueprint('bp', __name__)

@bp.route("/formular", methods=["GET", "POST"])
def formular():
    form = FormFormular()
    if form.validate_on_submit():
        new_user = Uzivatele(name=form.name.data, surename=form.surename.data)
        db.session.add(new_user)
        db.session.commit()
        return "Formular submitted"
    return render_template("formular.html", form=form)

@app.route('/')
def index():
    # Získání všech řádků z databáze
    rows = Row.query.all()
    return render_template('index.html', data=rows)

@app.route('/add', methods=['POST'])
def add_row():
    jmeno = request.form['jmeno']
    vek = request.form['vek']
    
    # Validace vstupů
    if not jmeno.isalpha():
        return "Name must contain letters only", 400
    if not vek.isdigit() or not (0 <= int(vek) <= 150):
        return "Age must be a number between 0 and 150", 400
    
    # Vytvoření nového řádku a uložení do databáze
    new_row = Row(jmeno=jmeno, vek=int(vek))
    db.session.add(new_row)
    db.session.commit()  # Uložení změn do databáze
    
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['GET'])
def delete_row(id):
    row = Row.query.get(id)  # Získání řádku podle ID
    if row:
        db.session.delete(row)  # Odstranění řádku
        db.session.commit()  # Uložení změn do databáze
    return redirect(url_for('index'))

app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)
