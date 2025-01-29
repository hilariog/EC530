const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const bodyParser = require('body-parser');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(cors());
app.use(express.json());
app.use(bodyParser.json());
app.use(express.static('uploads'));

// Endpoint for file upload
app.post('/upload', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ message: 'No file uploaded' });
    }
    const newPath = path.join(__dirname, 'uploads', req.file.originalname);
    fs.renameSync(req.file.path, newPath);
    res.json({ filePath: `/uploads/${req.file.originalname}` });
});

// Endpoint to execute Python script
app.post('/execute', (req, res) => {
    const { file, columnIndex1A, columnIndex2A, columnIndex1B, columnIndex2B, manualEntry1, manualEntry2, useCSV1, useCSV2 } = req.body;

    // Ensure file is passed correctly and resolve the full path
    const absoluteFilePath = path.join(__dirname, file); // Using path.join instead of path.resolve
    console.log("Resolved absolute file path being passed to Python:", absoluteFilePath);

    const command = `python3 ./scripts/process_data.py "${absoluteFilePath}" "${columnIndex1A}" "${columnIndex2A}" "${columnIndex1B}" "${columnIndex2B}" "${manualEntry1}" "${manualEntry2}" ${useCSV1} ${useCSV2}`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            return res.status(500).send({ response: `Error executing Python script: ${error.message}` });
        }

        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return res.status(500).send({ response: stderr });
        }

        res.json({ response: stdout });
    });
});

app.listen(8000, () => {
    console.log('Server running on port http://localhost:8000');
});
