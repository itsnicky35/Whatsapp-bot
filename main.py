import os
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from fuzzywuzzy import fuzz

app = Flask(__name__)

TWILIO_ACCOUNT_SID = "ACd8946de20bbdeaecac5b3ddc9bd956ba"
TWILIO_AUTH_TOKEN = "0a9755806d8592e27bc0b4b315e59da4"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
user_sessions = {}

pizza_menu = {
    "1": "Veg Pizza",
    "2": "Non-Veg Pizza",
    "3": "Cheese Burst Pizza"
}

size_menu = {
    "1": "Small",
    "2": "Medium",
    "3": "Large"
}

def reset_session(user_id):
    user_sessions[user_id] = {
        "step": "greeted",
        "pizza": None,
        "size": None,
        "address": None
    }


def handle_user_message(user_id, msg):
    msg = msg.strip().lower()
    session = user_sessions.get(user_id, {})
    step = session.get("step")

    if not session:
        reset_session(user_id)
        return "Welcome to Pizza Planet! Type 'menu' to see our pizza options."

    if step == "greeted":
        if "menu" in msg:
            session["step"] = "waiting_for_pizza"
            return "Pizza Menu:\n1. Veg Pizza\n2. Non-Veg Pizza\n3. Cheese Burst Pizza\n\nType the number to select."
        elif fuzz.partial_ratio(msg, "bye") > 70:
            reset_session(user_id)
            return "Goodbye! Come back soon for more pizza!"
        else:
            return "Please type 'menu' to begin your order."

    elif step == "waiting_for_pizza":
        if msg in pizza_menu:
            session["pizza"] = pizza_menu[msg]
            session["step"] = "waiting_for_size"
            return f"You chose {pizza_menu[msg]}. Now select a size:\n1. Small\n2. Medium\n3. Large"
        else:
            return "Invalid choice. Type 1, 2, or 3 to choose a pizza."

    elif step == "waiting_for_size":
        if msg in size_menu:
            session["size"] = size_menu[msg]
            session["step"] = "waiting_for_address"
            return f"{size_menu[msg]} size selected.\nPlease enter your delivery address."
        else:
            return "Invalid size. Type 1, 2, or 3 to select size."

    elif step == "waiting_for_address":
        session["address"] = msg
        session["step"] = "order_confirmed"
        return (f"Your order is confirmed!\n\n"
                f"Order Summary:\n"
                f"Pizza: {session['pizza']}\n"
                f"Size: {session['size']}\n"
                f"Address: {session['address']}\n\n"
                f"Your pizza will arrive in 30 minutes.\n\n"
                f"Type 'menu' to place another order or 'bye' to exit.")

    elif step == "order_confirmed":
        if "menu" in msg:
            reset_session(user_id)
            return "Pizza Menu:\n1. Veg Pizza\n2. Non-Veg Pizza\n3. Cheese Burst Pizza\n\nType the number to select."
        elif "bye" in msg:
            reset_session(user_id)
            return "Goodbye! Enjoy your pizza!"
        else:
            return "Want another order? Type 'menu' or 'bye' to end."

    else:
        reset_session(user_id)
        return "Let's start over. Type 'menu' to begin your order."


@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "")
    sender = request.values.get("From", "")
    print(f"Message from {sender}: {incoming_msg}")

    reply = handle_user_message(sender, incoming_msg)

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "running",
        "message": "Pizza bot is online and ready to serve!"
    }), 200


if __name__ == "__main__":
    print("Pizza Bot is running on http://localhost:5001")
    app.run(port=5001, debug=True)
