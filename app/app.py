from flask import Flask, jsonify, render_template, request
import logging

# --- OpenTelemetry core ---
from opentelemetry import trace

# --- Instrumentation ---
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from utils.dynamodb import DynamoDB
from utils.observability import Observability
from opentelemetry.trace.status import Status, StatusCode

# ------------------------------------------
# Flask App + Instrumentation
# ------------------------------------------
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

ob: Observability = Observability()


@app.route("/")
def index():
    logging.info("Hello!!")
    return render_template("index.html")

@app.route("/api/support_msg", methods=["POST"])
def post_support_msg():
    with ob.tracer.start_as_current_span("msg_recive") as span:
        data = request.get_json()
        msg = data.get("msg")

        if msg == "":
            return jsonify({"message": "メッセージを入力してください"}), 400

    with ob.tracer.start_as_current_span("post_dynamodb") as span:
        raise Exception("DynamoDBへ接続失敗しました。")
        db = DynamoDB()
        db.put_support_msg(msg)
        return jsonify({"message": "メッセージありがとうございました！"}), 200

@app.route("/api/support_msg", methods=["GET"])
def get_support_msg():
    with ob.tracer.start_as_current_span("fetch_dynamodb") as span:
        db = DynamoDB()
        msgs = db.fetch_all_support_msg()
        return jsonify({"messages": msgs}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    span = trace.get_current_span()
    span.record_exception(e)
    span.set_status(trace.status.Status(trace.status.StatusCode.ERROR))
    logging.error("Exception occurred", exc_info=True)
    return jsonify({"error": str(e)}), 500

# ------------------------------------------
# Main
# ------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)