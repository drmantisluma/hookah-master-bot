from flask import Flask, request, abort, jsonify, render_template
from src.hookah_master_helper.server.scripts.tobacco_scripts import *

app = Flask(__name__, template_folder='../client/')


@app.route('/', methods=['GET'])
def initial():
    return render_template('index.html')


@app.route("/api/tobacco/", methods=['GET', 'POST'])
def manage_tobacco():
    if request.method == 'POST':
        data = request.get_json()
        result = add_tobacco_to_database(data)

        if result:
            return jsonify({"warning": "Some warnings appeared", "data": result}), 207
        else:
            return jsonify("Tobacco successfully added"), 201

    elif request.method == 'GET':
        result = get_tobacco_from_db()

        if not result:
            abort(404, description="No tobacco found in the database")

        return jsonify(result)




@app.get("/api/tobacco/brands")
def get_all_brands_from_db():
    result = get_all_brands()

    if not result:
        abort(404, description="Empty table 'BRANDS'")

    return jsonify(result)