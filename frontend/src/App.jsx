import { useState, useRef, useEffect } from "react";
import { Home, Search, Briefcase, BookOpen, Folder, HelpCircle, Settings, Paperclip, Plus, Send, X } from "lucide-react";
import { uploadDocument, sendQuery, getAnalytics } from "./api";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [userRole, setUserRole] = useState("engineer");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const bottomRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) setFile(f);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setMessages((prev) => [...prev, { role: "system", content: `Uploading "${file.name}"...` }]);
    try {
      const data = await uploadDocument(file);
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { role: "system", content: `Indexed "${data.title || file.name}" — ${data.chunk_count || 0} chunks ready.` },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { role: "system", content: "Upload failed: " + (err.response?.data?.detail || err.message) },
      ]);
    }
    setUploading(false);
    setFile(null);
  };

  const handleSend = async (overrideText) => {
    const text = (overrideText ?? input).trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendQuery(text, userRole);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          meta: {
            agent: data.agent_used,
            intent: data.intent,
            confidence: data.confidence,
            cached: data.cached,
            time: data.processing_time_ms,
            sources: data.sources,
          },
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: " + (err.response?.data?.detail || err.message), meta: null },
      ]);
    }
    setLoading(false);
  };

  const handleNewChat = () => {
    setMessages([]);
    setInput("");
    setFile(null);
  };

  const handleAnalytics = async () => {
    if (showAnalytics) {
      setShowAnalytics(false);
      return;
    }
    try {
      const data = await getAnalytics();
      setAnalytics(data);
      setShowAnalytics(true);
    } catch (err) {
      setAnalytics({ error: err.message });
      setShowAnalytics(true);
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-logo"></div>
        <Home className="sidebar-icon active" size={22} onClick={handleNewChat} title="Home / New chat" />
        <Search className="sidebar-icon" size={22} title="Search (coming soon)" />
        <Briefcase className="sidebar-icon" size={22} title="Workspace (coming soon)" />
        <BookOpen className="sidebar-icon" size={22} title="Library (coming soon)" />
        <label title="Upload document">
          <Folder className="sidebar-icon" size={22} />
          <input ref={fileInputRef} type="file" hidden onChange={handleFileChange} />
        </label>
        <HelpCircle className="sidebar-icon" size={22} title="Help (coming soon)" />
        <Settings className="sidebar-icon" size={22} onClick={handleAnalytics} title="Analytics" />
      </div>

      {/* Main area */}
      <div className="main-area">
        <div className="topbar">
          <h1>NEXUS</h1>
          <div className="topbar-actions">
            <select className="role-select" value={userRole} onChange={(e) => setUserRole(e.target.value)}>
              <option value="technician">Technician</option>
              <option value="engineer">Engineer</option>
              <option value="manager">Manager</option>
            </select>
            <button className="new-chat-btn" onClick={handleNewChat}>+ New Chat</button>
          </div>
        </div>

        {file && (
          <div className="pending-file-bar">
            <Paperclip size={14} />
            <span>{file.name}</span>
            <button className="upload-confirm-btn" onClick={handleUpload} disabled={uploading}>
              {uploading ? "Uploading..." : "Upload"}
            </button>
            <button className="upload-cancel-btn" onClick={() => setFile(null)}>
              <X size={14} />
            </button>
          </div>
        )}

        <div className="chat-scroll">
          {isEmpty && !loading && (
            <div className="center-content">
              <div className="orb"></div>
              <div className="headline">
                <h2>Got something on your mind?</h2>
                <h2 className="highlight">Let's chat with your documents.</h2>
              </div>
              <p className="subtext">Click the folder icon in the sidebar to upload a document, then ask away.</p>
              <div className="suggestion-row">
                {["Summarize this document", "What safety procedures are mentioned?", "Compare Task 2 and Task 5"].map((s, i) => (
                  <button key={i} className="suggestion-pill" onClick={() => handleSend(s)}>{s}</button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatBubble key={i} msg={msg} />
          ))}

          {loading && (
            <div className="bubble assistant">
              <div className="typing-dots"><span></span><span></span><span></span></div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="input-bar">
          <input
            type="text"
            className="query-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about your documents..."
          />
          <button className="ask-btn" onClick={() => handleSend()} disabled={loading}>
            <Send size={16} />
          </button>
        </div>
      </div>

      {showAnalytics && (
        <div className="modal-overlay" onClick={() => setShowAnalytics(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Analytics Dashboard</h3>
              <button onClick={() => setShowAnalytics(false)}><X size={16} /></button>
            </div>
            {analytics ? (
              <>
                <div className="stats-grid">
                  <div className="stat-tile"><span>Total Queries</span><strong>{analytics.total_queries ?? "—"}</strong></div>
                  <div className="stat-tile"><span>Avg Response</span><strong>{analytics.avg_processing_time_ms ?? "—"} ms</strong></div>
                  <div className="stat-tile"><span>Entities</span><strong>{analytics.knowledge_graph?.total_entities ?? "—"}</strong></div>
                  <div className="stat-tile"><span>Cache Size</span><strong>{analytics.cache?.exact_cache_size ?? "—"}</strong></div>
                </div>
                <pre className="analytics-box">{JSON.stringify(analytics, null, 2)}</pre>
              </>
            ) : <p>Loading...</p>}
          </div>
        </div>
      )}
    </div>
  );
}

function ChatBubble({ msg }) {
  const [showDetails, setShowDetails] = useState(false);

  if (msg.role === "system") {
    return <div className="system-msg">{msg.content}</div>;
  }
  if (msg.role === "user") {
    return <div className="bubble user">{msg.content}</div>;
  }

  return (
    <div className="bubble assistant">
      <p className="result-answer">{msg.content}</p>
      {msg.meta && (
        <>
          <button className="details-toggle" onClick={() => setShowDetails(!showDetails)}>
            {showDetails ? "Hide details ▲" : "Show details ▼"}
          </button>
          {showDetails && (
            <div className="details-panel">
              <div className="result-meta">
                {msg.meta.agent && <span className="badge">{msg.meta.agent}</span>}
                {msg.meta.intent && <span className="badge">{msg.meta.intent}</span>}
                {msg.meta.confidence && <span className="badge">{msg.meta.confidence}</span>}
                <span className={`badge ${msg.meta.cached ? "cached" : ""}`}>
                  {msg.meta.cached ? "Cached" : "Fresh"}
                </span>
                <span className="badge">{msg.meta.time}ms</span>
              </div>
              {msg.meta.sources?.length > 0 && (
                <ul className="sources-list">
                  {msg.meta.sources.map((s, i) => (
                    <li key={i}>[{s.index}] {s.title} — Page {s.page}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;