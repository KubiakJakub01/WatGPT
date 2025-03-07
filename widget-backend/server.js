require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 5000;
const targetUrl = process.env.TARGET_URL || 'http://localhost:8000/';

app.use(express.json());

app.use(cors());
app.use(express.json());

app.post('/send-message', async (req, res) => {
    const { message } = req.body;

    if (!message) {
        return res.status(400).json({ error: 'No message in request' });
    }

    try {
        // const response = await axios.post(targetUrl, { message });
        // res.json({ success: true, response: response.data });
        res.json({success: true, response: { message: 'xd' } })
    } catch (error) {
        console.error("error sending message:", error.message);
        res.status(500).json({ error: 'error sending message' });
    }
});

app.listen(port, () => {
    console.log(`Server listen on port: ${port}`);
});
