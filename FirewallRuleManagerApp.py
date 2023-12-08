from AzureFirewallRuleManager import FirewallRuleManager
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('Interface', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('Interface', filename)

@app.route('/test',methods=['GET','POST','PUT'])
def refreshRules():
    print(f'We detected a {request.method!a} request.')

    try:
        match request.method:
            case "GET":
                    resp = {'message':'Nothing to see here!'}
                    return jsonify(resp),200
            case "POST":
                    # data = request.get_json()
                    data = request.json
                    print(data)
                    # resp = {'message':f'looks good to me! this is what we received: {data}'}
                    resp = {'message':f'looks good to me! this is what we received: {data}'}
                    return jsonify(resp),200
            case "PUT":
                    data = request.get_json()
                    resp = {'message':f'looks good to me! this is what we received: {data}'}
                    return jsonify(resp),200            
    except Exception as e:
        return jsonify(e), 500

    
@app.route('/refreshFirewallRules',methods=['GET'])
def refresh_Firewall_Rules():
    try:
        AzFRM.load_firewall_rules()
        resp = {'message':'The '}
        return jsonify(resp),200
    except Exception as e:
        return jsonify(e), 500

if __name__ == '__main__':
    AzFRM = FirewallRuleManager()
    app.run(debug=True)