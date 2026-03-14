from flask import render_template, request, redirect, url_for, flash, session
from models import db, Cliente, Pedido, DetallePedido, Pizza
from forms import PedidoForm
import datetime
from . import pedidos


@pedidos.route("/", methods=["GET", "POST"])
def index():
    form = PedidoForm()
    if "carrito" not in session:
        session["carrito"] = []

    if request.method == "GET" and "cliente" in session:
        form.nombre.data = session["cliente"]["nombre"]
        form.direccion.data = session["cliente"]["direccion"]
        form.telefono.data = session["cliente"]["telefono"]
        if "fecha" in session["cliente"]:
            form.fecha.data = datetime.datetime.strptime(
                session["cliente"]["fecha"], "%Y-%m-%d"
            ).date()

    if request.method == "POST":
        if "btn_agregar" in request.form and form.validate():
            session["cliente"] = {
                "nombre": form.nombre.data,
                "direccion": form.direccion.data,
                "telefono": form.telefono.data,
                "fecha": form.fecha.data.strftime("%Y-%m-%d"),
            }

            tamano = form.tamano.data
            ingredientes = form.ingredientes.data
            num_pizzas = form.num_pizzas.data

            precios_tamano = {"Chica": 40, "Mediana": 80, "Grande": 120}
            precio_base = precios_tamano.get(tamano, 0)
            extra_ingredientes = len(ingredientes) * 10
            subtotal = (precio_base + extra_ingredientes) * num_pizzas

            item = {
                "id_temp": len(session["carrito"]) + 1,
                "tamano": tamano,
                "ingredientes": ", ".join(ingredientes)
                if ingredientes
                else "Sin extras",
                "num_pizzas": num_pizzas,
                "subtotal": float(subtotal),
            }

            carrito_actual = session["carrito"]
            carrito_actual.append(item)
            session["carrito"] = carrito_actual
            session.modified = True

            flash("Pizza agregada al pedido temporal", "success")
            return redirect(url_for("pedidos.index"))

        elif "btn_terminar" in request.form:
            if not session.get("carrito"):
                flash("No hay pizzas en el carrito para terminar el pedido", "error")
                return redirect(url_for("pedidos.index"))

            datos_cliente = session.get("cliente")

            if not datos_cliente:
                flash(
                    "Faltan los datos del cliente. Agrega al menos una pizza primero.",
                    "error",
                )
                return redirect(url_for("pedidos.index"))

            cliente = Cliente.query.filter_by(
                telefono=datos_cliente["telefono"]
            ).first()
            if not cliente:
                cliente = Cliente(
                    nombre=datos_cliente["nombre"],
                    direccion=datos_cliente["direccion"],
                    telefono=datos_cliente["telefono"],
                )
                db.session.add(cliente)
                db.session.commit()
            else:
                cliente.direccion = datos_cliente["direccion"]
                cliente.nombre = datos_cliente["nombre"]
                db.session.commit()

            fecha_str = datos_cliente.get(
                "fecha", datetime.date.today().strftime("%Y-%m-%d")
            )
            fecha_obj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()

            total_pedido = sum(item["subtotal"] for item in session["carrito"])
            nuevo_pedido = Pedido(
                id_cliente=cliente.id_cliente, fecha=fecha_obj, total=total_pedido
            )
            db.session.add(nuevo_pedido)
            db.session.commit()

            for item in session["carrito"]:
                precio_unitario = item["subtotal"] / item["num_pizzas"]

                nueva_pizza = Pizza(
                    tamano=item["tamano"],
                    ingredientes=item["ingredientes"],
                    precio=precio_unitario,
                )
                db.session.add(nueva_pizza)
                db.session.commit()

                detalle = DetallePedido(
                    id_pedido=nuevo_pedido.id_pedido,
                    id_pizza=nueva_pizza.id_pizza,
                    cantidad=item["num_pizzas"],
                    subtotal=item["subtotal"],
                )
                db.session.add(detalle)

            db.session.commit()

            session.pop("carrito", None)
            session.pop("cliente", None)

            flash("¡Pedido registrado exitosamente en la base de datos!", "success")
            return redirect(url_for("pedidos.index"))

    total_carrito = sum(item["subtotal"] for item in session.get("carrito", []))

    return render_template(
        "pedidos/index.html",
        form=form,
        carrito=session.get("carrito", []),
        total_carrito=total_carrito,
    )


@pedidos.route("/quitar/<int:id_temp>")
def quitar(id_temp):
    if "carrito" in session:
        carrito = session["carrito"]
        carrito = [item for item in carrito if item["id_temp"] != id_temp]
        session["carrito"] = carrito
        session.modified = True
        flash("Pizza removida del pedido temporal", "warning")
    return redirect(url_for("pedidos.index"))


@pedidos.route("/ventas", methods=["GET"])
def ventas():
    fecha_exacta = request.args.get("fecha_exacta")
    mes = request.args.get("mes")
    anio = request.args.get("anio")

    query = Pedido.query.join(Cliente).order_by(Pedido.fecha.desc())
    ventas_filtradas = query.all()

    if fecha_exacta and fecha_exacta != "":
        ventas_filtradas = [
            v for v in ventas_filtradas if v.fecha.strftime("%Y-%m-%d") == fecha_exacta
        ]

    if mes and mes != "":
        ventas_filtradas = [v for v in ventas_filtradas if str(v.fecha.month) == mes]

    if anio and anio != "":
        ventas_filtradas = [v for v in ventas_filtradas if str(v.fecha.year) == anio]

    total_acumulado = sum(v.total for v in ventas_filtradas)

    return render_template(
        "pedidos/ventas.html", ventas=ventas_filtradas, total_acumulado=total_acumulado
    )


@pedidos.route("/venta/detalle/<int:id_pedido>")
def detalle_venta(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)

    detalles = DetallePedido.query.filter_by(id_pedido=id_pedido).all()

    return render_template("pedidos/detalle.html", pedido=pedido, detalles=detalles)
