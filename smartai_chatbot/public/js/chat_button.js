frappe.provide("smartai_chatbot");

frappe.ui.ChatButton = class {
    constructor() {
        this.make_button();
    }

    make_button() {
        if (!frappe.user.has_role("Chat User")) return;

        const $btn = $(`
            <button class="btn btn-primary btn-sm" id="smartai-chat-btn" style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
                💬 Chat
            </button>
        `);

        $("body").append($btn);

        $btn.on("click", () => {
            this.show_chat_modal();
        });
    }

    show_chat_modal() {
        const d = new frappe.ui.Dialog({
            title: "💬 SmartAI Chat",
            fields: [
                {
                    fieldname: "messages",
                    fieldtype: "HTML",
                    options: `<div id="chat-messages" style="height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background: #f9f9f9;"></div>`
                },
                {
                    fieldname: "message",
                    label: "Your Message",
                    fieldtype: "Text",
                    reqd: 1
                }
            ],
            primary_action_label: "Send",
            primary_action: () => {
                const msg = d.get_value("message");
                if (!msg.trim()) return;
                this.send_message(msg);
                d.set_value("message", "");
            }
        });

        d.show();
        this.dialog = d;
        this.messages = [];
    }

    send_message(message) {
        this.append_message("You", message);

        frappe.call({
            method: "smartai_chatbot.api.send_chat_message",
            args: {
                message: message,
                session_id: this.session_id || null
            },
            callback: (r) => {
                if (r.message) {
                    this.session_id = r.message.session_id;
                    this.append_message("AI", r.message.reply);
                }
            }
        });
    }

    append_message(sender, text) {
        const $box = this.dialog.fields_dict.messages.$wrapper.find("#chat-messages");
        const $msg = $(`<div><b>${sender}:</b> ${text}</div>`);
        $box.append($msg);
        $box.scrollTop($box[0].scrollHeight);
    }
};

$(document).ready(() => {
    new frappe.ui.ChatButton();
});
