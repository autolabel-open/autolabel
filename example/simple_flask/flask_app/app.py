import subprocess

from flask import Flask, jsonify, request
from loguru import logger

app = Flask(__name__)

logger.remove()
logger.add(
    "/app/logs/app.log",
    format="{time} {level} {message}",
    level="INFO",
    rotation="10 MB",
)


@app.route("/a", methods=["GET"])
def endpoint_a():
    logger.info("This is endpoint A")
    return jsonify({"message": "This is endpoint A"}), 200


@app.route("/b", methods=["GET"])
def endpoint_b():
    logger.info("This is endpoint B")
    return jsonify({"message": "This is endpoint B"}), 200


@app.route("/execute", methods=["POST"])
def execute_command():
    logger.info("Executing command")

    if not request.json or "command" not in request.json:
        return jsonify({"error": "Please provide a command to execute."}), 400

    command = request.json["command"]
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return jsonify({"output": result.stdout, "error": result.stderr}), 200
    except subprocess.CalledProcessError as e:
        return (
            jsonify(
                {"output": e.stdout, "error": e.stderr, "returncode": e.returncode}
            ),
            400,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
