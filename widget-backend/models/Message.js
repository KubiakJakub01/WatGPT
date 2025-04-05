const mongoose = require('mongoose');

const messageSchema = new mongoose.Schema({
  widgetId: { type: String, required: true },
  messageId: { type: String, required: true },
  text: { type: String, required: true },
  sender: { type: String, enum: ['user', 'bot'], required: true },
  timestamp: { type: Date, default: Date.now },
});

module.exports = mongoose.model('Message', messageSchema);
