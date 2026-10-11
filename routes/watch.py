import sqlite3

from flask import Blueprint, g, jsonify, request
from services.watch_auth import watch_token_required
from services.watch_push import PushError, submit

watch_blueprint = Blueprint('watch', __name__)


@watch_blueprint.route('/watch/results', methods=['POST'])
@watch_token_required('footyapp:push')
def watch_results():
    if request.content_length is None or request.content_length > 16384:
        return jsonify(error='invalid_submission', message='A small JSON request body is required.'), 400
    try:
        receipt = submit(request.get_json(silent=True), g.watch_claims['sub'])
        return jsonify(receipt)
    except PushError as error:
        return jsonify(error=error.code, message=error.message), error.status
    except (sqlite3.Error, OSError):
        return jsonify(error='push_unavailable', message='The upload journal is unavailable. Do not retry until it is checked.'), 503
