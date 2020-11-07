"""Routes for parent Flask app."""
from flask import *
from flask import current_app as app

import json
import api_config
import util
import pandas as pd

import inspect

@app.route("/")
def index():
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])
    return auth_init()
    #return render_template("index.html")
    
@app.route("/info")
def info():
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])
    return render_template("info.html")
    
@app.route("/auth/init")
def auth_init():
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])
    http = util.init_http_api(session)

    req = {
        "userHash": api_config.USERHASH,
        #'redirectUrl': 'http://localhost:5000/dashapp',
        "redirectUrl": "http://hedgy-app.herokuapp.com/dashapp",
        "language": "en",
    }

    j = http.post("v1/authentication/initialize", json=req).json()
    if "authUrl" not in j:
        session.errorMessage = "Authentication failed. Check you credentials in api_config.py"
        return render_template("error.html")
    return redirect(j["authUrl"])


@app.route("/auth/complete")
def auth_complete():
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])
    http = util.init_http_api(session)

    req = {
        "code": request.args.get("code")
    }

    j = http.post("v1/authentication/tokens", json=req).json()
    print(j)
    return complete_login(j)


@app.route("/auth/unattended", methods=["GET", "POST"])
def auth_unattended():
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])

    if request.method == "POST":
        http = util.init_http_api(session)

        req = {
            "userHash": api_config.USERHASH,
            "loginToken": request.form["loginToken"],
        }

        j = http.post("v1/authentication/unattended", json=req).json()
        return complete_login(j)

    return render_template("login_with_token.html")


@app.route("/auth/logout")
def auth_logout():
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])
    del session["accessToken"]
    return redirect(url_for("index"))


@app.route("/query/accounts")
def query_accounts():
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])
    http = util.init_http_api(session)
    j = http.get("v2/accounts").json()
    return jsonify(j)


@app.route("/query/accounts/<account_id>/transactions")
def query_transactions(account_id):
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])
    http = util.init_http_api(session)
    url = "v2/accounts/%s/transactions" % account_id
    
    query_params = {}

    if api_config.INCLUDE_TRANSACTION_DETAILS is True:
        query_params["withDetails"] = "true"

    pagingtoken = request.args.get('pagingToken')
    if pagingtoken is not None:
        query_params["pagingtoken"] = pagingtoken

    encoded_params = build_query_string(query_params)
    url = url + encoded_params
        
    j = http.get(url).json()
    
    '''
    with open('data.txt', 'w') as outfile:
        json.dump(j, outfile)
    '''
    print(parse_transactions(j, 'df'))
    

    df = parse_transactions(j, 'df')
    '''
    df.to_excel('./output/sample.xlsx')
    '''


    return jsonify(j)

def build_query_string(parameter_object):
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])
    query_parts = []

    for parameter_key in parameter_object: 
        formatted_param = "%s=%s" % (parameter_key, parameter_object[parameter_key])
        query_parts.append(formatted_param)

    query_string = "&".join(query_parts)

    if len(query_string) > 0:
        query_string = "?" + query_string
        
    return query_string

def parse_transactions(data, type='list_of_dicts'):  
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])
    d = []
    for t in data['transactions']:
        d.append({'id':t['id'],
                  'idSchema':t['idSchema'],
                  'date':t['date'],
                  'text':t['text'],
                  'originalText':t['originalText'],
    
                  'category':t['category'],
                  'amount':t['amount']['value'],
                  'currency':t['amount']['currency'],
                  'type':t['type']})
        
    if type == 'df':
        df = pd.DataFrame(d)
        df = df[['id','idSchema','type','date','category','text','originalText','amount','currency']]
        return df
    elif type == 'list_of_dicts':
        return d

def complete_login(j):
    print(inspect.stack()[0][3] + ' called by ' + inspect.stack()[1][3])
    # long lived access
    session["loginToken"] = j["login"]["loginToken"]
    session["label"] = j["login"]["label"]

    # short lived access
    session["accessToken"] = j["session"]["accessToken"]
    session["sessionExpires"] = j["session"]["expires"]

    return redirect(url_for("index"))