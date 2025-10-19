import frappe
from smartai_chatbot.smart_ai_chatbot.doctype.chat_session.chat_sessionation import ChatSessionation
from smartai_chatbot.smart_ai_chatbot.doctype.chat_message.chat_messageation import ChatMessageation

@frappe.whitelist()
def send_chat_message(message, session_id=None):
    user = frappe.session.user

    if not session_id:
        session = frappe.get_doc({
            "doctype": "Chat Sessionation",
            "user": user,
            "title": f"Chat with {user}"
        })
        session.insert(ignore_permissions=True)
        session_id = session.name
    else:
        session = frappe.get_doc("Chat Sessionation", session_id)

    # Save user message
    ChatMessageation({
        "doctype": "Chat Messageation",
        "chat_session": session_id,
        "role": "user",
        "content": message
    }).insert(ignore_permissions=True)

    # AI reply (dummy for now)
    ai_reply = "I'm here to help! (AI integration pending)"

    # Save AI message
    ChatMessageation({
        "doctype": "Chat Messageation",
        "chat_session": session_id,
        "role": "assistant",
        "content": ai_reply
    }).insert(ignore_permissions=True)

    return {
        "session_id": session_id,
        "reply": ai_reply
    }
