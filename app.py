from flask import Flask, request
from Models import db, GameServers, StreamList, datetime
from requests import get, post

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@127.0.0.1:3306/jaredwu0805"

db.init_app(app)


@app.route('/')
def index():
    return "Manager listening"


# Register game server
@app.route('/register')
def register():
    g_server_ip = request.remote_addr
    print('register', g_server_ip)
    get_register(g_server_ip)
    return g_server_ip + ' game server registered'


@app.route('/game', methods=['POST'])
def playing_game():
    data = request.form
    game_id = data.get('gameid')
    response = {
        'msg': 'Please specify the gameID',
        'game server ready': 'False',
    }
    if not game_id:
        return response

    game_server_info = GameServers.query.filter_by(is_available=True).first()
    # If cannot query any game server
    if not game_server_info:
        response['msg'] = 'Currently no available game server'
        return response

    game_server_ip = game_server_info.ip
    game_server_res = get('http://{0}:5000/connection?type=gaming'.format(game_server_ip)).json()
    if game_server_res['launch success']:
        game_server_info.is_available = False
        db.session.commit()
        save_stream_source(game_server_ip, request.remote_addr, game_id)

        response['msg'] = 'Successfully launch game server'
        response['game server ip'] = game_server_ip
        response['game server ready'] = True

        return response
    else:
        response['msg'] = 'Error when launching game server'
        return response


@app.route('/streaming', methods=['POST'])
def streaming():
    data = request.form
    stream_info = StreamList.query.filter_by(id=data.get('streamid')).first()
    stream_info.num_of_audience += 1
    db.session.commit()
    print(stream_info.server_ip)
    return {'server ip': stream_info.server_ip,
            'game_title': stream_info.game_title}


# Disconnection signal from game server
@app.route('/disconnection')
def disconnection():
    g_server_ip = request.remote_addr
    print('disconnect', g_server_ip)
    query = GameServers.query.filter_by(ip=g_server_ip).first()
    if query:
        query.is_available = False
        db.session.commit()

    return g_server_ip + ' disconnected'


def save_stream_source(game_server_ip, gamer_ip, game_id):
    new_stream = StreamList(server_ip=game_server_ip, client_ip=gamer_ip, game_title=game_id)
    db.session.add(new_stream)
    db.session.commit()
    print('Stream created')


def get_register(g_server_ip):
    query = GameServers.query.filter_by(ip=g_server_ip).first()
    # If game server registered before, update its is_available and last_connection_at
    if query:
        query.is_available = True
        query.last_connection_at = datetime.utcnow()
        db.session.commit()
    # Create new server entity
    else:
        new_server = GameServers(ip=g_server_ip, last_connection_at=datetime.utcnow())
        db.session.add(new_server)
        db.session.commit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run()
