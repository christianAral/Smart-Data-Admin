from AzureFirewallRuleManager import FirewallRuleManager
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
    
@app.route('/refreshFirewallRules',methods=['GET'])
def refresh_Firewall_Rules():
    try:
        param1 = request.args.get('refresh',True)
        rules = AzFRM.get_firewall_rules(refresh=param1)
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
        # Placeholder for a function that will handle processing all requested rules
        resp = AzFRM.update_rules(data)
        return jsonify(resp),200
    except Exception as e:
        return jsonify(e), 500
    
def open_browser():
    webbrowser.open_new('http://localhost:5000/')

if __name__ == '__main__':
    AzFRM = FirewallRuleManager()
    Timer(1, open_browser).start()
    app.run(debug=False)