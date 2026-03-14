from flask_wtf import FlaskForm 
from wtforms import StringField, IntegerField, RadioField, SelectMultipleField, DateField
from wtforms import validators
from wtforms.widgets import ListWidget, CheckboxInput
import datetime

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class PedidoForm(FlaskForm):
    nombre = StringField("Nombre", [
        validators.DataRequired(message="El nombre es requerido"),
        validators.Length(min=3, max=100, message="Requiere mínimo 3 caracteres") 
    ])
    direccion = StringField("Dirección", [
        validators.DataRequired(message="La dirección es requerida")
    ])
    telefono = StringField("Teléfono", [
        validators.DataRequired(message="El teléfono es requerido")
    ])
    fecha = DateField("Fecha de Compra", format='%Y-%m-%d', default=datetime.date.today, validators=[
        validators.DataRequired(message="La fecha es requerida")
    ])

    tamano = RadioField("Tamaño Pizza", 
        choices=[('Chica', 'Chica $40'), ('Mediana', 'Mediana $80'), ('Grande', 'Grande $120')],
        validators=[validators.DataRequired(message="Selecciona un tamaño")]
    )
    
    ingredientes = MultiCheckboxField("Ingredientes Extra",
        choices=[('Jamon', 'Jamón $10'), ('Piña', 'Piña $10'), ('Champinones', 'Champiñones $10')]
    )
    
    num_pizzas = IntegerField("Num. de Pizzas", [
        validators.DataRequired(message="Ingresa la cantidad"),
        validators.NumberRange(min=1, message="Mínimo 1 pizza")
    ])