import React, { useState } from 'react';
import axios from 'axios';

export default function App() {
    const [file, setFile] = useState(null);
    const [columnIndex1A, setColumnIndex1A] = useState('');
    const [columnIndex2A, setColumnIndex2A] = useState('');
    const [columnIndex1B, setColumnIndex1B] = useState('');
    const [columnIndex2B, setColumnIndex2B] = useState('');
    const [manualEntry1, setManualEntry1] = useState('');
    const [manualEntry2, setManualEntry2] = useState('');
    const [useCSV1, setUseCSV1] = useState(true);
    const [useCSV2, setUseCSV2] = useState(true);
    const [response, setResponse] = useState('');

    const handleFileUpload = async (e) => {
        const formData = new FormData();
        formData.append('file', e.target.files[0]);

        try {
            const res = await axios.post('http://localhost:8000/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setFile(res.data.filePath);
        } catch (error) {
            console.error('Error uploading file:', error);
        }
    };

    // Handle the execution of the logic and call the Python script
    const execute = async () => {
        const data = {
            file: file,
            columnIndex1A: columnIndex1A,
            columnIndex2A: columnIndex2A,
            columnIndex1B: columnIndex1B,
            columnIndex2B: columnIndex2B,
            manualEntry1: manualEntry1,
            manualEntry2: manualEntry2,
            useCSV1: useCSV1,
            useCSV2: useCSV2,
        };

        try {
            const res = await axios.post('http://localhost:8000/execute', data);
            setResponse(res.data.response);  // Display the response from Python script
        } catch (error) {
            console.error('Error executing Python script:', error);
        }
    };

    return (
        <div style={{ padding: 20 }}>
            <h1>CSV Processor</h1>
            <input type="file" onChange={handleFileUpload} />
            <p>Uploaded File: {file}</p>

            <h2>Array 1</h2>
            <label>
                <input type="checkbox" checked={useCSV1} onChange={() => setUseCSV1(!useCSV1)} /> Use CSV
            </label>
            {useCSV1 ? (
                <>
                    <input
                        type="text"
                        placeholder="Column Index 1"
                        value={columnIndex1A}
                        onChange={(e) => setColumnIndex1A(e.target.value)}
                    />
                    <input
                        type="text"
                        placeholder="Column Index 2"
                        value={columnIndex2A}
                        onChange={(e) => setColumnIndex2A(e.target.value)}
                    />
                </>
            ) : (
                <>
                    <p>Enter data manually in the format: "[[lat,lon],[lat,lon]...]"</p>
                    <input
                        type="text"
                        placeholder="Comma-separated values"
                        value={manualEntry1}
                        onChange={(e) => setManualEntry1(e.target.value)}
                    />
                </>
                
            )}

            <h2>Array 2</h2>
            <label>
                <input type="checkbox" checked={useCSV2} onChange={() => setUseCSV2(!useCSV2)} /> Use CSV
            </label>
            {useCSV2 ? (
                <>
                    <input
                        type="text"
                        placeholder="Column Index 1"
                        value={columnIndex1B}
                        onChange={(e) => setColumnIndex1B(e.target.value)}
                    />
                    <input
                        type="text"
                        placeholder="Column Index 2"
                        value={columnIndex2B}
                        onChange={(e) => setColumnIndex2B(e.target.value)}
                    />
                </>
            ) : (
                <>
                    <p>Enter data manually in the format: "[[lat,lon],[lat,lon]...]"</p>
                    <input
                        type="text"
                        placeholder="Comma-separated values"
                        value={manualEntry2}
                        onChange={(e) => setManualEntry2(e.target.value)}
                    />
                </>
            )}

            {/* Move the Execute button to a new line */}
            <div style={{ marginTop: 20 }}>
                <button onClick={execute}>Execute</button>
            </div>

            {response && (
                <div>
                    <h3>Result:</h3>
                    <pre>{response}</pre>
                </div>
            )}
        </div>
    );
}


