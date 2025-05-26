import json
from functools import wraps

from flask import Blueprint, request, jsonify, abort
from src.database.sql_manager import register_user, login_check, get_user_info, append_history, update_history, \
    query_user_recent_history
from src.global_data.response_temple import make_response_template
from src.algorithm.rule_engine import HandMajSet, FormData
import src.global_data.config as config
import jwt
import datetime


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth:
            abort(401)
        parts = auth.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            abort(401)
        token = parts[1]
        try:
            payload = jwt.decode(token, config.jwt_sec, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            abort(403)

        request.user = payload['username']
        request.exp = payload['exp']
        return f(*args, **kwargs)

    return decorated


blueprint = Blueprint('accountapi', __name__)


@blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify(make_response_template('Invalid input', '400001', {})), 400

    success = register_user(username, password, email)
    if success:
        return jsonify(make_response_template('Registration successful', '000000', {})), 200
    else:
        return jsonify(make_response_template('Username already exists', '400002', {})), 400


@blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(make_response_template('Invalid input', '400001', {})), 400

    if login_check(username, password):
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, config.jwt_sec, algorithm='HS256')
        return jsonify(make_response_template('Login successful', '000000', {'token': token})), 200
    else:
        return jsonify(make_response_template('Invalid username or password', '400003', {})), 401


@blueprint.route('/user_info', methods=['GET'])
def user_info():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify(make_response_template('Token is missing', '400004', {})), 401
    if not token.lower().startswith('bearer'):
        return jsonify(make_response_template('Invalid token format', '400004', {})), 401
    token = token.split()[1]
    try:
        decoded = jwt.decode(token, config.jwt_sec, algorithms=['HS256'])
        username = decoded.get('username')
        user_info = get_user_info(username)
        if user_info:
            return jsonify(make_response_template('User info retrieved', '000000', user_info)), 200
        else:
            return jsonify(make_response_template('User not found', '400005', {})), 404
    except jwt.ExpiredSignatureError:
        return jsonify(make_response_template('Token has expired', '400006', {})), 401
    except jwt.InvalidTokenError:
        return jsonify(make_response_template('Invalid token', '400007', {})), 401


@blueprint.route('/calc', methods=['POST'])
def calc():
    data = request.json
    if not data:
        return jsonify(make_response_template('Invalid input', '400001', {})), 400
    data = data['content']
    form_data = {
        'hand_tiles': data.get('handTiles', []),
        'outer_tiles': data.get('outerTiles', []),
        'game_type': data.get('gameType', ""),
        'north_pulls': data.get('northPulls', 0),
        'current_round': data.get('currentRound', ""),
        'self_round': data.get('selfRound', ""),
        'is_dealer': data.get('isDealer', False),
        'is_self_draw': data.get('isSelfDraw', False),
        'is_riichi': data.get('isRiichi', False),
        'is_double_riichi': data.get('isDoubleRiichi', False),
        'is_first_turn': data.get('isFirstTurn', False),
        'is_on_kang': data.get('isOnKang', False),
        'is_catch_kang': data.get('isCatchKang', False),
        'ready_indicators': data.get('readyIndicators', []),
        'dora_indicators': data.get('doraIndicators', []),
        'ura_dora_indicators': data.get('uraDoraIndicators', []),
        'is_river_or_sea': data.get('isRiverOrSea', False),
        'is_first_turn_win': data.get('isFirstTurnWin', False),
        'concealed_kangs': data.get('concealedKangs', 0),
    }
    print(form_data)
    maj_set = HandMajSet(FormData(**form_data))
    info = maj_set.get_score_info()
    auth = request.headers.get('Authorization')
    if auth is not None:
        parts = auth.split()
        if parts[0].lower() == 'bearer' and len(parts) == 2:
            token = parts[1]
            try:
                t_info = jwt.decode(token, config.jwt_sec, algorithms=['HS256'])
                user_name = t_info.get('username')
                if user_name is not None:
                    u_info = get_user_info(user_name)
                    uid = u_info['uid']
                    scan_id = data.get('scan_id')
                    if scan_id is None:
                        scan_id = append_history(uid, json.dumps(info))
                    else:
                        update_flag = update_history(scan_id, uid, json.dumps(info))
                        if not update_flag:
                            scan_id = append_history(uid, json.dumps(info))
                    info['scan_id'] = scan_id
            except jwt.ExpiredSignatureError:
                pass
    return jsonify(make_response_template('Calculation successful', '000000', info)), 200


@blueprint.route('/history', methods=['GET'])
@require_auth
def history():
    username = request.user
    u_info = get_user_info(username)
    if u_info:
        uid = u_info['uid']
        history_data = query_user_recent_history(uid, limit=10)
        return jsonify(make_response_template('History retrieved', '000000',  history_data)), 200
    else:
        return jsonify(make_response_template('User not found', '400005', {})), 404



