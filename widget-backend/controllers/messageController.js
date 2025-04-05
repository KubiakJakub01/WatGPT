const axios = require("axios");
const Message = require("../models/Message");
const { v4: uuidv4 } = require("uuid");

const sendMessage = async (req, res) => {
  const { widgetId, messageId, text, sender } = req.body;

  if (!widgetId || !messageId || !text || !sender) {
    return res.status(400).json({ error: "Missing fields in request body" });
  }

  try {
    const userMessage = new Message({ widgetId, messageId, text, sender });
    await userMessage.save();

    const botRes = await axios.get("http://localhost:8000/chat", {
      params: { text },
    });

    const botText = botRes.data?.text || "Brak odpowiedzi";

    const botMessage = new Message({
      widgetId,
      messageId: uuidv4(),
      text: botText,
      sender: "bot",
    });

    await botMessage.save();

    res.json({
      success: true,
      message:  {
        widgetId,
        messageId: botMessage.messageId,
        text: botText,
        sender: "bot",
    },
    });
  } catch (error) {
    console.error("❌ Error processing message:", error.message);
    res.status(500).json({ error: "Error processing message" });
  }
};

const getMessagesByWidgetId = async (req, res) => {
    const { widgetId } = req.params;
  
    try {
      const messages = await Message.find({ widgetId }).sort({ timestamp: 1 });
      res.json({ success: true, messages });
    } catch (error) {
      console.error("❌ Error fetching messages:", error.message);
      res.status(500).json({ error: "Error fetching messages" });
    }
  };

module.exports = { sendMessage, getMessagesByWidgetId };
