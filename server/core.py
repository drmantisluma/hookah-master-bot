from flask import Flask, request, abort, jsonify
from server.scripts.tobacco_scripts import add_tobacco_to_database, get_tobacco_from_db, get_tobacco_from_db_by_mark

app = Flask(__name__)


@app.route("/api/tobacco/", methods=['GET', 'POST'])
def manage_tobacco():
    if request.method == 'POST':
        data = request.get_json()
        result = add_tobacco_to_database(data)

        if any(result):
            return jsonify({"warning": "Some warnings appeared", "data": result}), 207
        else:
            return jsonify({"message": "Tobacco successfully added"}), 201

    elif request.method == 'GET':
        result = get_tobacco_from_db()

        if not result:
            abort(404, description="No tobacco found in the database")

        return jsonify({"data": result})


@app.get("/api/tobacco/<string:mark>")
def get_by_mark(mark):
    result = get_tobacco_from_db_by_mark(mark)

    if not result:
        abort(404, description="Tobacco with the given mark not found")

    return jsonify({"data": result})
