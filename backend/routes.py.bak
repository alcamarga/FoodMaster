from flask import jsonify
from database import db_session
from flask_jwt_extended import jwt_required

@app.route('/pagar_subcuenta/<int:subcuenta_id>', methods=['POST'])
@jwt_required()
def pagar_subcuenta(subcuenta_id):
    subcuenta = Subcuenta.query.get(subcuenta_id)
    if not subcuenta:
        return jsonify({'error': 'No existe'}), 404
    if subcuenta.estado == 'PENDIENTE':
        subcuenta.estado = 'SALDADA'
        mesa = subcuenta.mesa
        if not any(subc.estado == 'PENDIENTE' for subc in mesa.subcuentas):
            mesa.estado = 'LIBRE'
        db_session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Subcuenta ya pagada'}), 400

@app.route('/liberar_mesa/<int:mesa_id>', methods=['POST'])
@jwt_required()
def liberar_mesa(mesa_id):
    mesa = Mesa.query.get(mesa_id)
    if not mesa:
        return jsonify({'error': 'Mesa no encontrada'}), 404
    if all(sub.estado == 'SALDADA' for sub in mesa.subcuentas):
        mesa.estado = 'LIBRE'
        db_session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Algunas subcuentas no están pagadas'}), 400