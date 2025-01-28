import React, { useState } from "react";
import axios from "axios";

function App() {
  const [selectedAudio, setSelectedAudio] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  const audioFiles = [
    {
      label: "Audio File 1",
      url: "s3://dax-health-transcribe/Sample_data.mp3",
    },
    {
      label: "Audio File 2",
      url: "s3://dax-health-transcribe/Sample_data.mp3",
    },
    {
      label: "Audio File 3",
      url: "s3://dax-health-transcribe/Sample_data.mp3",
    },
  ];

  const handleTranscription = async () => {
    if (!selectedAudio) {
      alert("Please select an audio file.");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/start-transcription", {
        audioUrl: selectedAudio,
      });
      setSummary(response.data);
    } catch (error) {
      console.error("Error starting transcription:", error);
      alert("Failed to process the audio file.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionAnswer = async () => {
    if (!summary || !question) {
      alert("Please complete transcription and enter a question.");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/question-ans", {
        question,
      });
      setAnswer(response.data.answer);
    } catch (error) {
      console.error("Error fetching answer:", error);
      alert("Failed to fetch the answer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">AWS HealthScribe Transcription</h1>

      <div className="mb-4">
        <h2 className="font-bold">Select an Audio File:</h2>
        {audioFiles.map((file) => (
          <label key={file.url} className="block">
            <input
              type="radio"
              name="audio"
              value={file.url}
              onChange={() => setSelectedAudio(file.url)}
            />
            {file.label}
          </label>
        ))}
      </div>

      <button
        onClick={handleTranscription}
        disabled={!selectedAudio || loading}
        className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        Start Transcription
      </button>

      {summary && (
        <div className="mt-4">
          <h2 className="font-bold">Summary:</h2>
          <pre className="bg-gray-100 p-2 rounded">{JSON.stringify(summary, null, 2)}</pre>
        </div>
      )}

      <div className="mt-4">
        <h2 className="font-bold">Ask a Question:</h2>
        <input
          type="text"
          placeholder="Enter your question here"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="border p-2 w-full rounded mb-2"
        />
        <button
          onClick={handleQuestionAnswer}
          disabled={!question || loading}
          className="px-4 py-2 bg-green-500 text-white rounded disabled:opacity-50"
        >
          Get Answer
        </button>
      </div>

      {answer && (
        <div className="mt-4">
          <h2 className="font-bold">Answer:</h2>
          <p className="bg-gray-100 p-2 rounded">{answer}</p>
        </div>
      )}

      {loading && <p className="text-blue-500 mt-4">Processing...</p>}
    </div>
  );
}

export default App;
