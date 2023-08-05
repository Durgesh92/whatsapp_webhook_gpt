from flask import Flask, request
from wa_me import Bot

bot = Bot()
bot.start(phone_id="113472301814609", token="EAAUpsrsFIS0BAHT9GiEjLli4XY7ZBZCAVtzViqIrcH7qrgqwch1xDQgJA0hO1vCYPH0VcNjuZCkmaXBkml0ZCNEHBjvFrjHPPXvKJZCdrhSLtHyV1ZA4LTBCTI9zZBH9zN9JsyIp89MWunH96Rjsm3L7zi2ZAyznxRSmki6hkysZApNuZAQRpPOe4VRWW9j9wTeAqJ2KvH0TDdFmaZAR6Vyvey07OHibuZAk5vlkOPrWriP3xQZDZD")

@app.get("/")
async def ping():
    if request.args.get("hub.verify_token") == "VERIFY_TOKEN":
        return request.args.get("hub.challenge")
    return "Invalid verify token"

@app.post("/")
def root():
    data = request.get_json()
    bot.handle(data)
    return "Success"
