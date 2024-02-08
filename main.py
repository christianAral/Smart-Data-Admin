from SmartData import SmartDataAdmin
from CheckVersion import CheckVersion
from flask import Flask, jsonify, request, send_from_directory
import webbrowser
from threading import Timer

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('Interface', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('Interface', filename)
    
@app.route('/checkVersion',methods=['GET'])
def check_version():
    try:
        return jsonify(CheckVersion()),200
    except Exception as e:
        return jsonify(e), 500    
    
@app.route('/testFirewallChecksum',methods=['GET'])
def test_Firewall_Checksum():
    try:
        resp = SDAdmin.firewallMGR.test_firewall_checksum()
        return jsonify(resp),200
    except Exception as e:
        return jsonify(e), 500

@app.route('/refreshFirewallRules',methods=['GET'])
def refresh_Firewall_Rules():
    try:
        param1 = request.args.get('refresh',True)
        rules = SDAdmin.firewallMGR.get_firewall_rules(refresh=param1)
        rules = [{
                'name':r.name,
                'start':r.start_ip_address,
                'end':r.end_ip_address
                } for r in rules]
        return jsonify(rules),200
    except Exception as e:
        return jsonify(e), 500
    
@app.route('/updateFirewallRules',methods=['POST'])
def update_Firewall_Rules():
    try:
        data = request.json
        resp = SDAdmin.firewallMGR.update_rules(data)
        return jsonify(resp),200
    except Exception as e:
        return jsonify(e), 500
    
@app.route('/logs',methods=['GET'])
def get_logs():
    try:
        resp = SDAdmin.logger.list_log_file_names()
        return jsonify(resp),200
    except Exception as e:
        return jsonify(e), 500
    
@app.route('/logs/<logName>',methods=['GET'])
def get_log(logName):
    try:
        resp = SDAdmin.logger.get_log_file(logName)
        return jsonify(resp),200
    except Exception as e:
        return jsonify(e), 500
    
@app.route('/sftpmgr',methods=['GET'])
def get_sftp_users():
    try:
        resp = SDAdmin.sftpMGR.get_sftp_user_info()
        return jsonify(resp),200
    except Exception as e:
        return jsonify(e), 500
    
@app.route('/sftpmgr/secret',methods=['POST'])
def get_sftp_user_password():
    try:
        data = request.json
        resp = SDAdmin.sftpMGR.get_sftp_user_password(
            ARN=data['ARN_b64'],
            b64=True,
            asLink=True,
            passphrase=data['passphrase']
        )
        return jsonify(resp),200
    except Exception as e:
        return jsonify(e), 500
    
def open_browser():
    webbrowser.open_new('http://localhost:5000/')

if __name__ == '__main__':
    SDAdmin = SmartDataAdmin()
    Timer(1, open_browser).start()
    app.run(debug=False)