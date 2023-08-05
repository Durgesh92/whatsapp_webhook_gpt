from flask import Flask, request, jsonify
import json
from bs4 import BeautifulSoup
from urllib.parse import unquote
import os
import openai
import yaml
import requests
from txtai.embeddings import Embeddings
import uuid

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
openai.api_key = config['openai_key']
session_memory = {}
session_embeddings = {}
sessions_dir = "history"

# token = "EAAUpsrsFIS0BAHT9GiEjLli4XY7ZBZCAVtzViqIrcH7qrgqwch1xDQgJA0hO1vCYPH0VcNjuZCkmaXBkml0ZCNEHBjvFrjHPPXvKJZCdrhSLtHyV1ZA4LTBCTI9zZBH9zN9JsyIp89MWunH96Rjsm3L7zi2ZAyznxRSmki6hkysZApNuZAQRpPOe4VRWW9j9wTeAqJ2KvH0TDdFmaZAR6Vyvey07OHibuZAk5vlkOPrWriP3xQZDZD"
# number = '113472301814609'


token = "EABfI6y3lkH4BO165ZBSKLBmYzZBq6CkruWab01jhKlbIvquztUjZApMMWp7gYX2yOn0g4dlmZCeJS0VsbX4H4Wrc4Kx8UIxpdefFK3inqvhRqxoZAKHvLG6ZBeEZBhPFVCw1Nwgcl8ygYzgtfXFDqVGuLb5PkM8z7xG1odrl88RNX3kac80eiQX1FDu4Ph8zK9DiiGdbp16I66yb5FYZAiEWOTAv8M0Jybm3hHbB"
number = "110990108751639"
class Dialogue:
    user_content: str
    assistant_content: str

    def __init__(self, user_content: str, assistant_content: str):
        self.user_content = user_content
        self.assistant_content = assistant_content

    def raw(self):
        return [
            {'role': 'user', 'content': self.user_content},
            {'role': 'assistant', 'content': self.assistant_content}
        ]

app = Flask(__name__)

def get_baseline_prompt():
    with open("prompt.txt","r") as f1:
        file_contents = f1.read()
        return file_contents

def is_existing_session(session_id):
    file_path = sessions_dir + "/" + session_id
    if os.path.isfile(file_path):
        return True
    return False

def send_whatsapp_text(message,to):
    url = 'https://graph.facebook.com/v17.0/'+number+'/messages'
    access_token = token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(response.text)
        resp_js = json.loads(response.text)
        messages = resp_js["messages"]
        session_id = to
        dict1 = {}
        history = []
        t1 = []
        t1.append("hello")
        t1.append(message)
        history.append(t1)
        dict1["history"] = history
        opp = open(sessions_dir + "/" + session_id,"w")
        opp.write(json.dumps(dict1))
        opp.close()
        for msg in messages:
            id_ = msg["id"]
            if not os.path.isfile("messages_id_map.json"):
                op = open("messages_id_map.json","w")
                tmp_dict = {}
                tmp_dict["status"] = ""
                tmp_dict["id"] = id_
                tmp_dict_1 = {}
                tmp_dict_1["phone"] = to
                tmp_dict_1["data"] = [tmp_dict]
                tmp_list = []
                tmp_list.append(tmp_dict_1)
                op.write(json.dumps(tmp_list))
                op.close()
            else:
                data_ = json.load(open("messages_id_map.json","r"))
                tmp_list = []
                phone_exists = False
                for x in data_:
                    if x["phone"] == to:
                        data_list = x["data"]
                        tmp_dict = {}
                        tmp_dict["status"] = ""
                        tmp_dict["id"] = id_
                        data_list.append(tmp_dict)
                        x["data"] = data_list
                        phone_exists = True
                    tmp_list.append(x)
                if not phone_exists:
                    tmp_dict = {}
                    tmp_dict["status"] = ""
                    tmp_dict["id"] = id_
                    tmp_dict_1 = {}
                    tmp_dict_1["phone"] = to
                    tmp_dict_1["data"] = [tmp_dict]
                    tmp_list.append(tmp_dict_1)
                op = open("messages_id_map.json","w")
                # print("tmp_list 1 : ",tmp_list)
                op.write(json.dumps(tmp_list))
                op.close() 
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(response.text)

@app.route('/webhook', methods=['POST','GET','PUT'])
def handle_webhook():
    parameters = json.load(open("parmeters.json","r"))
    parameters = parameters["parameters"]
    html_data = request.get_data()
    # print("tilda webhook received : ",html_data)
    html_data_decoded = html_data.decode('utf-8')
    tmp_dict = {}
    p1 = html_data_decoded.split("&")
    for x in p1:
        x1 = x.split("=")
        normal_string = unquote(x1[1])
        tmp_dict[x1[0].lower()] = normal_string
    if "phone" in tmp_dict:
        send_whatsapp_text(config["init_msg"],tmp_dict["phone"].replace("+",""))
    return "ok"

@app.route('/verify_webhook_test', methods=['GET','PUT','POST'])
def webhook_verify2():
    print("verify_webhook_test")
    # token = request.args.get("hub.verify_token")
    # challenge = request.args.get("hub.challenge")
    # if token == "aqwsed":
    #     return challenge
    data = json.loads(request.data.decode('utf-8'))
    # print("whatsapp data : ")
    entry = data["entry"]
    for ent in entry:
        changes = ent["changes"]
        for chn in changes:
            display_phone_number = chn["value"]["metadata"]["display_phone_number"]
            if "messages" in chn["value"]:
                messages = chn["value"]["messages"]
                for msg in messages:
                    from_ = msg["from"]
                    if msg["type"] == "text":
                        session_id = from_
                        body = msg["text"]["body"]
                        user_message = body
                        if session_id not in session_memory:
                            embeddings = None
                            session_memory[session_id] = embeddings
                        prompts = get_baseline_prompt()
                        # if is_existing_session(session_id):
                        if os.path.exists(sessions_dir + "/" + session_id):
                            session_file_ = sessions_dir + "/" + session_id
                        else:
                            session_file_ = sessions_dir + "/+" + session_id
                        # print("session : ",sessions_dir + "/" + session_id)
                        session_file = json.load(open(session_file_,"r"))
                        history = session_file["history"]
                        if session_memory[session_id] == None:
                            embeddings = Embeddings(            {
                                    'path': config['vector_space_model'],
                                    'content': True
                                })
                            session_memory[session_id] = embeddings
                        messages = [{"role": "system", "content": prompts}]
                        last_message = history[-1][-1]
                        history = history + [[user_message, None]]
                        neighborhoods = []
                        results = session_memory[session_id].search(
                            "SELECT text, score, raw FROM txtai WHERE similar('{0}') limit {1}".format(history[-1][0], 5)
                        )                        
                        for r in results:
                            neighborhoods += eval(r['raw'])
                        neighborhoods = list(reversed(neighborhoods))
                        messages += neighborhoods
                        messages.append({"role": "user", "content": history[-1][0]})
                        model_name = "gpt-4"
                        chat = openai.ChatCompletion.create(
                            model=model_name,
                            messages=messages,
                            temperature=0.7,
                            max_tokens=256,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0
                        )
                        reply = chat.choices[0].message.content
                        reply = reply.replace("\n"," ")
                        dig = Dialogue(history[-1][0], reply)
                        dialogue_list = []
                        dialogue_list.append(dig)
                        session_memory[session_id].upsert(
                            (
                                str(uuid.uuid4()), {'text': dialogue.user_content, 'raw': dialogue.raw()}, None
                            ) for dialogue in dialogue_list
                        )
                        history[-1][1] = reply
                        op = open(session_file_,"w")
                        dict1 = {}
                        dict1["history"] = history
                        op.write(json.dumps(dict1))
                        op.close()
                        send_whatsapp_text(reply,from_)
            elif "statuses" in chn["value"]:
                print("whatsapp statuses : ",data)
                statuses = chn["value"]["statuses"]
                for st in statuses:
                    status = st["status"]
                    timestamp = st["timestamp"]
                    recipient_id = st["recipient_id"]
                    id_ = st["id"]
                    data_ = json.load(open("messages_id_map.json","r"))
                    tmp_list = []
                    for x in data_:
                        if x["phone"] == recipient_id:
                            data_list = x["data"]
                            nl = []
                            for dt_ in data_list:
                                if dt_["id"] == id_:
                                    dt_["status"] = status
                                    dt_["timestamp"] = timestamp
                                    if "errors" in st:
                                        dt_["errors"] = st["errors"][0]["title"]
                                nl.append(dt_)
                            x["data"] = nl
                        tmp_list.append(x)
                    # print("tmp_list 2 : ",tmp_list)
                    op = open("messages_id_map.json","w")
                    op.write(json.dumps(tmp_list))
                    op.close() 
    return "ok"

@app.route('/verify_webhook', methods=['GET','PUT','POST'])
def webhook_verify():
    data = json.loads(request.data.decode('utf-8'))
    # print("whatsapp data : ")
    entry = data["entry"]
    for ent in entry:
        changes = ent["changes"]
        for chn in changes:
            display_phone_number = chn["value"]["metadata"]["display_phone_number"]
            if "messages" in chn["value"]:
                messages = chn["value"]["messages"]
                for msg in messages:
                    from_ = msg["from"]
                    if msg["type"] == "text":
                        session_id = from_
                        body = msg["text"]["body"]
                        user_message = body
                        if session_id not in session_memory:
                            embeddings = None
                            session_memory[session_id] = embeddings
                        prompts = get_baseline_prompt()
                        # if is_existing_session(session_id):
                        if os.path.exists(sessions_dir + "/" + session_id):
                            session_file_ = sessions_dir + "/" + session_id
                        else:
                            session_file_ = sessions_dir + "/+" + session_id
                        # print("session : ",sessions_dir + "/" + session_id)
                        session_file = json.load(open(session_file_,"r"))
                        history = session_file["history"]
                        if session_memory[session_id] == None:
                            embeddings = Embeddings(            {
                                    'path': config['vector_space_model'],
                                    'content': True
                                })
                            session_memory[session_id] = embeddings
                        messages = [{"role": "system", "content": prompts}]
                        last_message = history[-1][-1]
                        history = history + [[user_message, None]]
                        neighborhoods = []
                        results = session_memory[session_id].search(
                            "SELECT text, score, raw FROM txtai WHERE similar('{0}') limit {1}".format(history[-1][0], 5)
                        )                        
                        for r in results:
                            neighborhoods += eval(r['raw'])
                        neighborhoods = list(reversed(neighborhoods))
                        messages += neighborhoods
                        messages.append({"role": "user", "content": history[-1][0]})
                        model_name = "gpt-4"
                        chat = openai.ChatCompletion.create(
                            model=model_name,
                            messages=messages,
                            temperature=0.7,
                            max_tokens=256,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0
                        )
                        reply = chat.choices[0].message.content
                        reply = reply.replace("\n"," ")
                        dig = Dialogue(history[-1][0], reply)
                        dialogue_list = []
                        dialogue_list.append(dig)
                        session_memory[session_id].upsert(
                            (
                                str(uuid.uuid4()), {'text': dialogue.user_content, 'raw': dialogue.raw()}, None
                            ) for dialogue in dialogue_list
                        )
                        history[-1][1] = reply
                        op = open(session_file_,"w")
                        dict1 = {}
                        dict1["history"] = history
                        op.write(json.dumps(dict1))
                        op.close()
                        send_whatsapp_text(reply,from_)
            elif "statuses" in chn["value"]:
                print("whatsapp statuses : ",data)
                statuses = chn["value"]["statuses"]
                for st in statuses:
                    status = st["status"]
                    timestamp = st["timestamp"]
                    recipient_id = st["recipient_id"]
                    id_ = st["id"]
                    data_ = json.load(open("messages_id_map.json","r"))
                    tmp_list = []
                    for x in data_:
                        if x["phone"] == recipient_id:
                            data_list = x["data"]
                            nl = []
                            for dt_ in data_list:
                                if dt_["id"] == id_:
                                    dt_["status"] = status
                                    dt_["timestamp"] = timestamp
                                    if "errors" in st:
                                        dt_["errors"] = st["errors"][0]["title"]
                                nl.append(dt_)
                            x["data"] = nl
                        tmp_list.append(x)
                    # print("tmp_list 2 : ",tmp_list)
                    op = open("messages_id_map.json","w")
                    op.write(json.dumps(tmp_list))
                    op.close() 
    return "ok"

if __name__ == "__main__":
    ssl_context = ('playground/certificate.crt', 'playground/playground.avatarintern.ai.key')
    app.run(
            host="0.0.0.0",
            port=7619,
            ssl_context=ssl_context,
            threaded=True
            )
