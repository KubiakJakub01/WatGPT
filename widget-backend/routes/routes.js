const express = require('express');
const router = express.Router();
const { sendMessage, getMessagesByWidgetId } = require('../controllers/messageController');

router.post('/', sendMessage);
router.get('/:widgetId', getMessagesByWidgetId);

module.exports = router;
