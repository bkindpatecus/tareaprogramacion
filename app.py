import os
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

archivo = "gastos.csv"
mi_link = "https://link.mercadopago.cl/appgastos"

os.makedirs("static", exist_ok=True)

if not os.path.exists(archivo):
    df = pd.DataFrame(columns=["fecha", "categoria", "monto"])
    df.to_csv(archivo, index=False)


pagina = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mis Gastos</title>
    <style>

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', sans-serif;
        }

        body {
            background-color: #0f172a;
            color: #f8fafc;
            padding: 40px 20px;
            line-height: 1.6;
        }

        .contenedor {
            max-width: 700px;
            margin: 0 auto;
        }

        h1 {
            font-size: 2.2rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #06b6d4, #f43f5e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: uppercase;
        }

        h2 {
            font-size: 1.4rem;
            color: #06b6d4;
            margin: 35px 0 15px 0;
            border-bottom: 2px solid #06b6d4;
            padding-bottom: 5px;
            display: inline-block;
        }

        form {
            background-color: #1e293b;
            padding: 25px;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        input {
            background-color: #0f172a;
            border: 1px solid #334155;
            color: white;
            padding: 11px;
            border-radius: 6px;
            font-size: 1rem;
            outline: none;
        }

        input:focus {
            border-color: #06b6d4;
        }

        button[type="submit"] {
            background: linear-gradient(135deg, #06b6d4, #0891b2);
            color: white;
            border: none;
            padding: 12px;
            font-size: 1rem;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            text-transform: uppercase;
        }

        button[type="submit"]:hover {
            opacity: 0.85;
        }

        .botones {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }

        .btn-grafico {
            flex: 1;
            display: inline-block;
            background: linear-gradient(135deg, #f43f5e, #e11d48);
            color: white;
            text-decoration: none;
            padding: 12px;
            font-weight: bold;
            border-radius: 50px;
            text-transform: uppercase;
            font-size: 0.85rem;
            text-align: center;
        }

        .btn-mp {
            flex: 1;
            display: inline-block;
            background: linear-gradient(135deg, #00b1ea, #009ee3);
            color: white;
            text-decoration: none;
            padding: 12px;
            font-weight: bold;
            border-radius: 50px;
            text-transform: uppercase;
            font-size: 0.85rem;
            text-align: center;
        }

        .btn-grafico:hover, .btn-mp:hover {
            opacity: 0.9;
            transform: scale(1.01);
        }

        .lista-gastos {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .item-gasto {
            background-color: #1e293b;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #f43f5e;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .item-gasto .fecha {
            color: #94a3b8;
            font-size: 0.85rem;
        }

        .item-gasto .categoria {
            font-weight: bold;
        }

        .item-gasto .monto {
            font-size: 1.1rem;
            font-weight: bold;
            color: #06b6d4;
        }

        .vacio {
            color: #94a3b8;
            text-align: center;
            font-style: italic;
        }

    </style>
</head>
<body>
    <div class="contenedor">

        <h1>Mis Gastos</h1>

        <form action="/agregar" method="POST">
            <input type="date" name="fecha" required>
            <input type="text" name="categoria" placeholder="Categoría (ej. Comida, Uber...)" required>
            <input type="number" name="monto" placeholder="Monto en pesos" required>
            <button type="submit">Añadir gasto</button>
        </form>

        <div class="botones">
            <a href="/grafico" class="btn-grafico">Ver gráfico</a>
            <a href="{{ mi_link }}" target="_blank" class="btn-mp">Pagar con Mercado Pago</a>
        </div>

        <h2>Historial</h2>

        <div class="lista-gastos">
            {% if gastos %}
                {% for g in gastos %}
                <div class="item-gasto">
                    <div>
                        <span class="categoria">{{ g.categoria }}</span><br>
                        <span class="fecha">{{ g.fecha }}</span>
                    </div>
                    <div class="monto">${{ g.monto }}</div>
                </div>
                {% endfor %}
            {% else %}
                <p class="vacio">Todavía no hay gastos cargados.</p>
            {% endif %}
        </div>

    </div>
</body>
</html>
"""


@app.route("/")
def index():
    df = pd.read_csv(archivo)
    return render_template_string(pagina, gastos=df.to_dict(orient="records"), mi_link=mi_link)


@app.route("/agregar", methods=["POST"])
def agregar():
    fecha = request.form["fecha"]
    categoria = request.form["categoria"]
    monto = request.form["monto"]

    df = pd.read_csv(archivo)
    nuevo = pd.DataFrame([[fecha, categoria, monto]], columns=["fecha", "categoria", "monto"])
    df = pd.concat([df, nuevo], ignore_index=True)
    df.to_csv(archivo, index=False)

    return redirect(url_for("index"))


@app.route("/grafico")
def grafico():
    df = pd.read_csv(archivo)

    if df.empty:
        return "No hay datos todavía"

    df["monto"] = pd.to_numeric(df["monto"])
    agrupado = df.groupby("fecha")["monto"].sum()

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7, 4))
    agrupado.plot(kind="bar", color="#06b6d4", ax=ax)

    plt.title("Gastos por día", fontsize=13, color="#f8fafc", pad=15)
    plt.xlabel("Fecha", color="#94a3b8")
    plt.ylabel("Monto ($)", color="#94a3b8")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#334155')
    ax.spines['bottom'].set_color('#334155')

    plt.tight_layout()
    plt.savefig("static/grafico.png", facecolor='#1e293b')
    plt.close()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Gráfico</title>
        <style>
            body {{ background-color: #0f172a; color: white; font-family: sans-serif; text-align: center; padding: 40px 20px; }}
            h1 {{ color: #06b6d4; margin-bottom: 20px; font-size: 1.6rem; }}
            img {{ max-width: 100%; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); margin-bottom: 25px; }}
            .btn {{ display: inline-block; background: #f43f5e; color: white; text-decoration: none; padding: 12px 30px; font-weight: bold; border-radius: 50px; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <h1>Gastos por día</h1>
        <img src="/static/grafico.png">
        <br>
        <a href="/" class="btn">Volver</a>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)