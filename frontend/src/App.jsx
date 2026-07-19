import { useState } from "react";
import { Home, Search, Briefcase, BookOpen, Folder, HelpCircle, Settings } from "lucide-react";
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
  const [showAnalytics, setShowAnalytics] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setUploadStatus("Uploading...");
    try {
      const data = await uploadDocument(file);
      setUploadStatus(`Uploaded: ${data.filename || data.doc_id} — ${data.status}`);
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
    if (showAnalytics) {
      setShowAnalytics(false);
      return;
    }
    const data = await getAnalytics();
    setAnalytics(data);
    setShowAnalytics(true);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleQuery();
  };

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-logo"></div>
        <Home className="sidebar-icon active" size={22} />
        <Search className="sidebar-icon" size={22} />
        <Briefcase className="sidebar-icon" size={22} />
        <BookOpen className="sidebar-icon" size={22} />
        <Folder className="sidebar-icon" size={22} />
        <HelpCircle className="sidebar-icon" size={22} />
        <Settings className="sidebar-icon" size={22} />
      </div>

      {/* Main area */}
      <div className="main-area">
        <div className="topbar">
          <h1>NEXUS</h1>
          <div className="topbar-actions">
            <button className="new-chat-btn" onClick={() => { setResult(null); setQuery(""); }}>
              + New Chat
            </button>
          </div>
        </div>

        <div className="center-content">
          <div className="orb"></div>

          <div className="headline">
            <h2>Got something on your mind?</h2>
            <h2 className="highlight">Let's chat with your documents.</h2>
          </div>

          <div className="chat-card">
            <div className="chat-card-header">
              <span>Upload a document to get started</span>
              <select
                className="role-select"
                value={userRole}
                onChange={(e) => setUserRole(e.target.value)}
              >
                <option value="technician">Technician</option>
                <option value="engineer">Engineer</option>
                <option value="manager">Manager</option>
              </select>
            </div>

            <div className="input-row">
              <input
                type="text"
                className="query-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about your documents..."
              />
              <button className="ask-btn" onClick={handleQuery} disabled={loading}>
                {loading ? "Thinking..." : "Ask"}
              </button>
            </div>

            <div className="upload-row">
              <input
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
                style={{ fontSize: "12px" }}
              />
              <button className="ask-btn" onClick={handleUpload}>
                Upload
              </button>
            </div>
            {uploadStatus && <p className="upload-status">{uploadStatus}</p>}
          </div>

          {result && (
            <div className="result-panel">
              <p className="result-answer">{result.answer}</p>
              <div className="result-meta">
                <span className="badge">{result.agent_used}</span>
                <span className="badge">{result.intent}</span>
                <span className="badge">{result.confidence}</span>
                <span className={`badge ${result.cached ? "cached" : ""}`}>
                  {result.cached ? "Cached" : "Fresh"}
                </span>
                <span className="badge">{result.processing_time_ms}ms</span>
              </div>
              {result.sources && result.sources.length > 0 && (
                <ul className="sources-list">
                  {result.sources.map((s, i) => (
                    <li key={i}>
                      [{s.index}] {s.title} — Page {s.page}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          <div className="analytics-toggle" onClick={handleAnalytics}>
            {showAnalytics ? "Hide Analytics" : "Show Analytics Dashboard"}
          </div>

          {showAnalytics && analytics && (
            <pre className="analytics-box">{JSON.stringify(analytics, null, 2)}</pre>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;