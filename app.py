from flask import Flask, request, Response, jsonify
from Models import db, GameServers, StreamList, datetime, WaitingList
from requests import get, post
import logging

app = Flask(__name__)

# MySql database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@127.0.0.1:3306/jaredwu0805"

db.init_app(app)

# cloudXR_client_cmd = "C:\Program Files\Nvidia Corporation\CloudXR\Client\CLoudXRClient.exe -w"


@app.route('/')
def index():
    db.create_all()
    return "ok"


# Register game server
@app.route('/registration')
def register_game_server():
    g_server_ip = request.remote_addr
    print('register', g_server_ip)
    get_register(g_server_ip)
    return g_server_ip + ' game server registered'


# Disconnection signal from game server
@app.route('/cancellation')
def unregister_game_server():
    g_server_ip = request.remote_addr
    print('disconnect', g_server_ip)
    query = GameServers.query.filter_by(server_ip=g_server_ip).first()

    if query:
        query.is_available = False
        StreamList.query.filter_by(server_ip=g_server_ip).delete()
        db.session.commit()

    return g_server_ip + ' disconnected'


@app.route('/games')
def game_list():
    # TBD
    data = {"status": True,
            "ip": "123"}
    resp = jsonify(data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/games/<string:game_id>/launch', methods=['GET'])
def playing_game(game_id):
    response = {
        'msg': '',
        'status': False
    }
    player_ip = request.remote_addr
    is_client_awaiting = WaitingList.query.filter_by(client_ip=player_ip).first()

    if is_client_awaiting:
        processing_server_ip = is_client_awaiting.server_ip
        processing_server_res = get('http://{0}:5000/game-connection'.format(processing_server_ip)).json()
        print(processing_server_res)
        if processing_server_res['status']:
            response['status'] = True
            response['msg'] = 'Successfully launch game server and game title.'
            response['game_server_ip'] = processing_server_ip
            # delete waiting list
            # is_client_awaiting.delete()
            # db.session.commit()
        else:
            response['msg'] = 'Processing... Game server is allocating resources to launch game...'
    else:
        game_server_info = GameServers.query.filter_by(is_available=True).first()
        # If cannot query any game server
        if not game_server_info:
            response['msg'] = 'Currently no available game server'
        else:
            game_server_ip = game_server_info.server_ip
            req_data = {
                "player_ip": player_ip,
                "game_title": game_id,
                "game_id": game_id
            }
            game_server_res = post('http://{0}:5000/game-connection'.format(game_server_ip), data=req_data).json()

            # if game_server_res['launch success']:
                # Client's gaming status also needs to update, TBD
            game_server_info.is_available = False
            db.session.commit()
            # update_waiting_list(player_ip, game_server_ip)
            # save_stream_source(game_server_ip, player_ip, game_id)

            response['status'] = True
            response['msg'] = 'Connecting... Now launching game title...'
            response['game_server_ip'] = game_server_ip
            # else:
            #     response['msg'] = 'Error when launching game server'

    resp = jsonify(response)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/streaming', methods=['POST'])
def streaming():
    data = request.form
    stream_info = StreamList.query.filter_by(id=data.get('streamid')).first()
    # Pre-add the audience
    stream_info.num_of_audience += 1
    db.session.commit()
    print(stream_info.server_ip)
    return {'server ip': stream_info.server_ip,
            'game_title': stream_info.game_title}


@app.route('/clean')
def clean_streams():
    StreamList.query.delete()
    WaitingList.query.delete()
    db.session.commit()
    return 'table cleaned'


def save_stream_source(game_server_ip, gamer_ip, game_id):
    new_stream = StreamList(server_ip=game_server_ip, client_ip=gamer_ip, game_title=game_id)
    db.session.add(new_stream)
    db.session.commit()
    print('Stream created')


def get_register(g_server_ip):
    query = GameServers.query.filter_by(server_ip=g_server_ip).first()
    # If game server registered before, update its is_available and last_connection_at
    if query:
        query.is_available = True
        query.last_connection_at = datetime.utcnow()
        db.session.commit()
    # Create new server entity
    else:
        new_server = GameServers(server_ip=g_server_ip, last_connection_at=datetime.utcnow())
        db.session.add(new_server)
        db.session.commit()


def update_waiting_list(client_ip, server_ip):
    new_client = WaitingList(client_ip=client_ip, server_ip=server_ip)
    db.session.add(new_client)
    db.session.commit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run()
