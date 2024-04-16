import flask
from flask import jsonify, request, make_response
from datetime import datetime
from . import db_session
from .tickets import Ticket

blueprint = flask.Blueprint(
    'tickets_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/all_tickets/<int:status_id>', methods=['GET'])
def get_tickets_with_one_status(status_id):
    db_sess = db_session.create_session()
    tickets = db_sess.query(Ticket).filter(Ticket.status == status_id).all()
    return jsonify(
        {
            'tickets': [item.to_dict() for item in tickets]
        }
    )


@blueprint.route('/api/add_ticket', methods=['POST'])
def add_ticket_api():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['name', 'email', 'product_name', 'problem_name', 'problem_full', 'is_finished', 'worker', 'chat_id', 'last_id']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    ticket = Ticket(
        name=request.json['name'],
        email=request.json['email'],
        product_name=request.json['product_name'],
        problem_name=request.json['problem_name'],
        problem_full=request.json['problem_full'],
        is_finished=request.json['is_finished'],
        worker=request.json['worker'],
        chat_id=request.json['chat_id'],
        status=0,
        created_at=datetime.now(),
        last_id=request.json['last_id']
    )
    db_sess.add(ticket)
    db_sess.commit()
    return jsonify({'id': ticket.id})