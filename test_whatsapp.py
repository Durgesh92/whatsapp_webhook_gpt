import requests

def send_facebook_message():
    url = 'https://graph.facebook.com/v17.0/113472301814609/messages'
    access_token = 'EAAUpsrsFIS0BAHT9GiEjLli4XY7ZBZCAVtzViqIrcH7qrgqwch1xDQgJA0hO1vCYPH0VcNjuZCkmaXBkml0ZCNEHBjvFrjHPPXvKJZCdrhSLtHyV1ZA4LTBCTI9zZBH9zN9JsyIp89MWunH96Rjsm3L7zi2ZAyznxRSmki6hkysZApNuZAQRpPOe4VRWW9j9wTeAqJ2KvH0TDdFmaZAR6Vyvey07OHibuZAk5vlkOPrWriP3xQZDZD'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "+919033179470",
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "Hey! \nIts Mike You recently filled out the form in my link in bio. \nYou are interested in business and social media growth \nIs it true?"
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(response.text)

# Call the function to send the message
send_facebook_message()

