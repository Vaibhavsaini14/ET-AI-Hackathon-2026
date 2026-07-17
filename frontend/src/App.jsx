import { useState } from "react";
import { uploadDocument, sendQuery, getAnalytics } from "./api";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [userRole, setUserRole] = useState("engineer");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [analytics, setAnalytics] = useState(null);

  const handleUpload = async () => {
    if (!file) return;
    setUploadStatus("Uploading...");
    try {
      const data = await uploadDocument(file);
      setUploadStatus(`Uploaded: ${data.title || data.doc_id} — status: ${data.status}`);
    } catch (err) {
      setUploadStatus("Upload failed: " + err.message);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await sendQuery(query, userRole);
      setResult(data);
    } catch (err) {
      setResult({ answer: "Error: " + err.message, sources: [] });
    }
    setLoading(false);
  };

  const handleAnalytics = async () => {
    const data = await getAnalytics();
    setAnalytics(data);
  };

  return (
    <div className="app">
      <h1>NEXUS — Industrial Knowledge Intelligence</h1>

      <section className="panel">
        <h2>1. Upload Document</h2>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload}>Upload</button>
        <p>{uploadStatus}</p>
      </section>

      <section className="panel">
        <h2>2. Ask a Question</h2>
        <select value={userRole} onChange={(e) => setUserRole(e.target.value)}>
          <option value="technician">Technician</option>
          <option value="engineer">Engineer</option>
          <option value="manager">Manager</option>
        </select>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about your documents..."
          style={{ width: "60%", marginLeft: "8px" }}
        />
        <button onClick={handleQuery} disabled={loading}>
          {loading ? "Thinking..." : "Ask"}
        </button>

        {result && (
          <div className="result">
            <p><strong>Answer:</strong> {result.answer}</p>
            <p>
              <strong>Agent:</strong> {result.agent_used} |{" "}
              <strong>Intent:</strong> {result.intent} |{" "}
              <strong>Confidence:</strong> {result.confidence} |{" "}
              <strong>Cached:</strong> {String(result.cached)} |{" "}
              <strong>Time:</strong> {result.processing_time_ms}ms
            </p>
            <h4>Sources:</h4>
            <ul>
              {result.sources?.map((s, i) => (
                <li key={i}>
                  [{s.index}] {s.title} — Page {s.page}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="panel">
        <h2>3. Analytics</h2>
        <button onClick={handleAnalytics}>Refresh Dashboard</button>
        {analytics && (
          <pre style={{ textAlign: "left", background: "#111", color: "#0f0", padding: "10px" }}>
            {JSON.stringify(analytics, null, 2)}
          </pre>
        )}
      </section>
    </div>
  );
}

export default App;