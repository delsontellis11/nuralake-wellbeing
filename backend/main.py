import os
import sys
import httpx
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

from agent.graph import run_agent

app = FastAPI(title="Well Beings WhatsApp Agent")

conversation_history = {}

def send_whatsapp_message(phone_number: str, message: str):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    response = httpx.post(url, json=payload, headers=headers)
    print(f"WhatsApp API response: {response.status_code} - {response.text}")
    return response

@app.get("/")
async def root():
    return {"status": "Well Beings Agent is running"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode == "subscribe" and token == os.getenv("VERIFY_TOKEN"):
        print("Webhook verified!")
        return PlainTextResponse(content=challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def receive_message(request: Request):
    try:
        body = await request.json()
        print(f"Incoming webhook: {body}")

        entry = body.get("entry", [])
        if not entry:
            return {"status": "no entry"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "no changes"}

        value = changes[0].get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return {"status": "no messages"}

        message = messages[0]
        phone_number = message.get("from")
        msg_type = message.get("type")

        if msg_type != "text":
            return {"status": "non-text message ignored"}

        text = message["text"]["body"]
        print(f"Message from {phone_number}: {text}")

        history = conversation_history.get(phone_number, [])
        response = run_agent(text, phone_number, history)

        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": response})
        conversation_history[phone_number] = history[-10:]

        send_whatsapp_message(phone_number, response)
        return {"status": "ok"}

    except Exception as e:
        print(f"Error processing message: {e}")
        return {"status": "error", "detail": str(e)}