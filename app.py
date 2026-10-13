
from flask import Flask, jsonify, render_template, request

from compiler_pipeline import analyze_program

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/analyze")
def analyze():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON request."}), 400

    source_code = data.get("source_code")

    if not isinstance(source_code, str):
        return jsonify({"error": "Source code must be text."}), 400

    if not source_code.strip():
        return jsonify({"error": "Please enter some source code."}), 400

    if len(source_code) > 50000:
        return jsonify({
            "error": "Source code exceeds the 50,000-character limit."
        }), 413

    try:
        pipeline = analyze_program(source_code)

        # Keep existing summary and findings available at the top level.
        report = pipeline["report"]

        response = {
            **report,
            "pipeline": {
                "tokens": pipeline["tokens"],
                "ast": pipeline["ast"],
                "ir": pipeline["ir"],
                "cfg": pipeline["cfg"],
                "call_graph": pipeline["call_graph"],
            },
        }

        return jsonify(response)

    except Exception:
        app.logger.exception("Source analysis failed")
        return jsonify({
            "error": (
                "Analysis failed. Check that your source uses "
                "the supported language syntax."
            )
        }), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
