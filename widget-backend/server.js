require('dotenv').config();
const express = require('express');
const cors = require('cors');
const connectDB = require('./config/db');
const { sendMessage, getMessagesByWidgetId } = require('../controllers/messageController');


const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Routes
router.post('/', sendMessage);
router.get('/:widgetId', getMessagesByWidgetId);

connectDB().then(() => {
  app.listen(port, () => {
    console.log(`✅ Server listening on port ${port}`);
  });
});
