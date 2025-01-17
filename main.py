import os
import threading
import webbrowser
import pandas as pd
from templates.controller import housePredict
from templates.controller import createJsonPrep
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Carregar o CSV
df = pd.read_csv('static/dataset/Bin_1.csv')

@app.route('/NEIGHBORHOOD', methods=['GET'])
def get_bairros():
    zona = request.args.get('ZONE')
    bairros = df[df['ZONE'] == zona]['NEIGHBORHOOD'].unique().tolist()
    return jsonify(bairros)


@app.route('/STREET', methods=['GET'])
def get_ruas():
    zona = request.args.get('ZONE')
    bairro = request.args.get('NEIGHBORHOOD')
    ruas = df[(df['ZONE'] == zona) & (df['NEIGHBORHOOD'] == bairro)]['STREET'].unique()
    ruas_filtradas = sorted([rua for rua in ruas if isinstance(rua, str) and rua.strip()])
    return jsonify(ruas_filtradas)


@app.route("/")
@app.route("/index")
def index():
    zonas = df['ZONE'].unique()
    return render_template('view/main.html', zonas=zonas)

@app.route('/submit', methods=['POST'])
def submit():
    prediction = housePredict.HousePredict()

    form_data = request.form.to_dict()

    cjp = createJsonPrep.CreateJsonPreparation(form_dict=form_data)

    if not cjp.get_data("itemZONE", expected_type=str):
        return render_template('view/error_price.html')

    else:
        s = cjp.structure()
        price, max_price, min_price = prediction.predict(s)

        predict = {
            "price": round(float(price[0][0]), 2),
            "max_price": round(float(max_price[0][0]), 2),
            "min_price": round(float(min_price[0][0]), 2)
        }

        return render_template('view/submit.html', predict=predict)


    # if (cjp.get_data("itemZONE", expected_type=str) == "") or (
    #         cjp.get_data("itemNEIGHBORHOOD", expected_type=str) == "") or (
    #         cjp.get_data("itemSTREET", expected_type=str) == ""):
    #     return render_template('view/submit.html', predict=predict)
    #
    # else:

def abrir_navegador():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=abrir_navegador).start()
    app.run(debug=True)