import { useState, useRef, useEffect } from "react";
import {
  Settings, Plus, Send, X, Paperclip, Image, FileText,
  Copy, RotateCcw, Check
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { uploadDocument, sendQuery, getAnalytics } from "./api";
import "./App.css";

const LOADING_PHRASES = [
  "Reading your documents...",
  "Finding the best answer...",
  "Cross-checking sources...",
  "Almost there...",
];

function App() {
  const [messages, setMessages] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [input, setInput] = useState("");
  const [userRole, setUserRole] = useState("engineer");
  const [loading, setLoading] = useState(false);
  const [loadingPhraseIdx, setLoadingPhraseIdx] = useState(0);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [showAttachMenu, setShowAttachMenu] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [copiedIdx, setCopiedIdx] = useState(null);
  const bottomRef = useRef(null);
  const fileInputRef = useRef(null);
  const attachMenuRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (!loading) return;
    setLoadingPhraseIdx(0);
    const interval = setInterval(() => {
      setLoadingPhraseIdx((i) => (i + 1) % LOADING_PHRASES.length);
    }, 1600);
    return () => clearInterval(interval);
  }, [loading]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (attachMenuRef.current && !attachMenuRef.current.contains(e.target)) {
        setShowAttachMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) setFile(f);
    setShowAttachMenu(false);
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

  const runQuery = async (text) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);
    try {
      const data = await sendQuery(text, userRole);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          query: text,
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

  const handleSend = (overrideText) => {
    const text = (overrideText ?? input).trim();
    if (!text || loading) return;
    setInput("");
    runQuery(text);
  };

  const handleRegenerate = (query) => {
    if (loading) return;
    setMessages((prev) => prev.slice(0, -1));
    runQuery(query);
  };

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 1500);
  };

  const handleNewChat = () => {
    if (messages.length > 0) {
      const firstUserMsg = messages.find((m) => m.role === "user");
      const title = firstUserMsg ? firstUserMsg.content.slice(0, 30) + (firstUserMsg.content.length > 30 ? "..." : "") : "New chat";
      setChatHistory((prev) => [{ id: Date.now(), title, messages }, ...prev]);
    }
    setMessages([]);
    setInput("");
    setFile(null);
  };

  const handleLoadHistory = (entry) => {
    if (messages.length > 0) handleNewChat();
    setMessages(entry.messages);
    setChatHistory((prev) => prev.filter((c) => c.id !== entry.id));
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
  const lastAssistantIdx = [...messages].map((m, i) => ({ m, i })).reverse().find(({ m }) => m.role === "assistant")?.i;

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-top">
          <div className="sidebar-logo"></div>
          <button className="new-chat-sidebar-btn" onClick={handleNewChat}>
            <Plus size={16} /> New Chat
          </button>
        </div>

        <div className="chat-history-list">
          {chatHistory.length === 0 && <p className="history-empty">No past chats yet</p>}
          {chatHistory.map((entry) => (
            <button key={entry.id} className="history-item" onClick={() => handleLoadHistory(entry)}>
              {entry.title}
            </button>
          ))}
        </div>

        <div className="sidebar-bottom">
          <Settings className="sidebar-icon" size={20} onClick={handleAnalytics} title="Analytics" />
        </div>
      </div>

      {/* Main area */}
      <div className="main-area">
        <div className="topbar">
          <h1>NEXUS</h1>
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
          <div className="chat-column">
            {isEmpty && !loading && (
              <div className="center-content">
                <div className="orb"></div>
                <div className="headline">
                  <h2>Got something on your mind?</h2>
                  <h2 className="highlight">Let's chat with your documents.</h2>
                </div>
                <p className="subtext">Use the + icon beside the input to upload a document, then ask away.</p>
                <div className="suggestion-row">
                  {["Summarize this document", "What safety procedures are mentioned?", "Compare Task 2 and Task 5"].map((s, i) => (
                    <button key={i} className="suggestion-pill" onClick={() => handleSend(s)}>{s}</button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <ChatBubble
                key={i}
                msg={msg}
                isLastAssistant={i === lastAssistantIdx}
                onRegenerate={handleRegenerate}
                onCopy={() => handleCopy(msg.content, i)}
                copied={copiedIdx === i}
              />
            ))}

            {loading && (
              <div className="bubble assistant fade-in">
                <div className="loading-row">
                  <div className="typing-dots"><span></span><span></span><span></span></div>
                  <span className="loading-text">{LOADING_PHRASES[loadingPhraseIdx]}</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        <div className="input-bar-wrap">
          <div className="input-bar">
            <div className="attach-wrap" ref={attachMenuRef}>
              <button className="attach-btn" onClick={() => setShowAttachMenu(!showAttachMenu)}>
                <Plus size={18} />
              </button>
              {showAttachMenu && (
                <div className="attach-menu">
                  <button onClick={() => fileInputRef.current?.click()}>
                    <FileText size={15} /> Upload Document
                  </button>
                  <button disabled title="Coming soon">
                    <Image size={15} /> Photos
                  </button>
                  <button disabled title="Coming soon">
                    <Paperclip size={15} /> Other Files
                  </button>
                </div>
              )}
              <input ref={fileInputRef} type="file" hidden onChange={handleFileChange} />
            </div>

            <input
              type="text"
              className="query-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask about your documents..."
            />

            <select className="role-pill-select" value={userRole} onChange={(e) => setUserRole(e.target.value)}>
              <option value="technician">Technician</option>
              <option value="engineer">Engineer</option>
              <option value="manager">Manager</option>
            </select>

            <button className="ask-btn" onClick={() => handleSend()} disabled={loading}>
              <Send size={16} />
            </button>
          </div>
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

function ChatBubble({ msg, isLastAssistant, onRegenerate, onCopy, copied }) {
  const [showDetails, setShowDetails] = useState(false);

  if (msg.role === "system") {
    return <div className="system-msg fade-in">{msg.content}</div>;
  }
  if (msg.role === "user") {
    return <div className="bubble user fade-in">{msg.content}</div>;
  }

  return (
    <div className="bubble assistant fade-in">
      <div className="markdown-body">
        <ReactMarkdown>{msg.content}</ReactMarkdown>
      </div>

      <div className="assistant-actions">
        <button className="icon-action-btn" onClick={onCopy} title="Copy">
          {copied ? <Check size={13} /> : <Copy size={13} />}
        </button>
        {isLastAssistant && msg.query && (
          <button className="icon-action-btn" onClick={() => onRegenerate(msg.query)} title="Regenerate">
            <RotateCcw size={13} />
          </button>
        )}
        {msg.meta && (
          <button className="details-toggle" onClick={() => setShowDetails(!showDetails)}>
            {showDetails ? "Hide details ▲" : "Show details ▼"}
          </button>
        )}
      </div>

      {showDetails && msg.meta && (
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
    </div>
  );
}

export default App;