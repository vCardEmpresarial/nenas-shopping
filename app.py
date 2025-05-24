from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from io import BytesIO
import requests
import os

app = Flask(__name__)
app.secret_key = "clave-secreta-segura"

URL_EXCEL = "https://docs.google.com/spreadsheets/d/1D1txp7lKGItuMAa14neECoZKXMB3jRy-/export?format=xlsx"

def obtener_dataframe():
    response = requests.get(URL_EXCEL)
    if response.status_code == 200:
        df = pd.read_excel(BytesIO(response.content))
        df.columns = df.columns.str.strip().str.lower()
        return df
    else:
        raise Exception("No se pudo descargar el archivo desde Google Sheets.")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        clave = request.form["clave"].strip().lower()
        password = request.form["password"].strip()

        df = obtener_dataframe()
        df["clave"] = df["clave"].astype(str).str.strip().str.lower()
        df["contraseña"] = df["contraseña"].astype(str).str.strip()

        user_data = df[(df["clave"] == clave) & (df["contraseña"] == password)]

        if not user_data.empty:
            session["clave"] = clave
            return redirect(url_for("compras"))

        return render_template("login.html", error="Clave o contraseña incorrecta.")

    return render_template("login.html")

@app.route("/compras")
def compras():
    if "clave" not in session:
        return redirect(url_for("login"))

    clave = session["clave"]
    df = obtener_dataframe()
    df["clave"] = df["clave"].astype(str).str.strip().str.lower()
    user_data = df[df["clave"] == clave]

    compras = user_data[["fecha", "hora de conf", "articulo", "precio"]].copy()
    compras["precio"] = compras["precio"].replace('[\$,]', '', regex=True).replace(',', '', regex=False).astype(float)
    compras["precio"] = compras["precio"].apply(lambda x: "${:,.0f}".format(x))

    total = user_data["precio"].replace('[\$,]', '', regex=True).replace(',', '', regex=False).astype(float).sum()
    total = "${:,.0f}".format(total)

    nombre = user_data.iloc[0]["clienta"]

    return render_template("compras.html", nombre=nombre, compras=compras.to_dict(orient="records"), total=total)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
