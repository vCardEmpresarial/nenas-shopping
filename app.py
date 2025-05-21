
from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "clave-secreta-segura"
EXCEL_URL = "https://docs.google.com/spreadsheets/d/1D1txp7lKGItuMAa14neECoZKXMB3jRy-/edit?usp=sharing&ouid=104857370499470822424&rtpof=true&sd=true"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        clave = request.form["clave"].strip().lower()
        password = request.form["password"].strip()

        df = pd.read_excel(EXCEL_URL)
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

    df = pd.read_excel(EXCEL_URL)
    df["clave"] = df["clave"].astype(str).str.strip().str.lower()
    user_data = df[df["clave"] == clave]

    compras = user_data[["FECHA", "Articulo", "PRECIO"]]
    total = compras["PRECIO"].sum()
    nombre = user_data.iloc[0]["clienta"]

    return render_template("compras.html", nombre=nombre, compras=compras.to_dict(orient="records"), total=total)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

