import { useState, useEffect, useRef } from "react";
import { useAuth } from "../context/AuthContext";
import { useChat } from "../context/ChatContext";
import "./ChatWidget.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function ChatWidget() {
  const { isAuthed, user, token } = useAuth();
  const { session, messages, unread, isTyping, connected, startChat, sendMessage, sendTyping, markRead, closeSession } = useChat();

  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [lang, setLang] = useState("he");
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [historySession, setHistorySession] = useState(null);
  const [historyMessages, setHistoryMessages] = useState([]);

  const messagesEndRef = useRef(null);
  const isAdmin = String(user?.role ?? "").trim().toLowerCase() === "admin";

  // ── Hooks must come before any conditional return ──────────────────────────
  useEffect(() => {
    if (open) messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open, isTyping]);

  useEffect(() => {
    if (open && unread > 0) markRead();
  }, [open]);

  if (!isAuthed || isAdmin) return null;

  const handleOpen = async () => {
    setOpen(true);
    if (!session) await startChat();
    markRead();
  };

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || !session) return;
    sendMessage(trimmed);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e) => {
    setInput(e.target.value);
    sendTyping();
  };

  const handleCloseSession = async () => {
    if (!confirm("Close this conversation? It will be saved in your history.")) return;
    await closeSession();
  };

  const loadHistory = async () => {
    const res = await fetch(`${API_URL}/chat/history`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    setHistory(data.sessions || []);
    setShowHistory(true);
    setHistorySession(null);
    setHistoryMessages([]);
  };

  const loadHistorySession = async (s) => {
    const res = await fetch(`${API_URL}/chat/messages/${s.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    setHistorySession(s);
    setHistoryMessages(data.messages || []);
  };

  const handleNewChat = async () => {
    await startChat();
  };

  return (
    <>
      {/* Floating button */}
      <button
        className={`chat-fab ${open ? "open" : ""}`}
        onClick={open ? () => setOpen(false) : handleOpen}
        aria-label="Open chat"
      >
        {open ? <CloseIcon /> : <ChatIcon />}
        {!open && unread > 0 && <span className="chat-fab-badge">{unread > 9 ? "9+" : unread}</span>}
      </button>

      {/* Chat window */}
      {open && (
        <div className="chat-window">
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-info">
              <div className="chat-header-avatar">S</div>
              <div>
                <div className="chat-header-name">Support</div>
                <div className={`chat-header-status ${connected ? "online" : "offline"}`}>
                  {connected ? "Online" : "Connecting..."}
                </div>
              </div>
            </div>
            <div className="chat-header-actions">
              <div className="chat-lang-toggle">
                <button className={lang === "he" ? "active" : ""} onClick={() => setLang("he")}>HE</button>
                <button className={lang === "en" ? "active" : ""} onClick={() => setLang("en")}>EN</button>
              </div>
              {session?.status === "active" && (
                <>
                  <button className="chat-btn-icon" onClick={loadHistory} title="Chat history">
                    <HistoryIcon />
                  </button>
                  <button className="chat-btn-icon danger" onClick={handleCloseSession} title="End conversation">
                    <EndIcon />
                  </button>
                </>
              )}
              <button className="chat-btn-icon" onClick={() => setOpen(false)} title="Minimize">
                <MinimizeIcon />
              </button>
            </div>
          </div>

          {/* Body */}
          <div className="chat-body">
            {showHistory ? (
              <div className="chat-history-panel">
                <button
                  className="chat-history-back"
                  onClick={() => { setShowHistory(false); setHistorySession(null); setHistoryMessages([]); }}
                >
                  ← Back to chat
                </button>

                {historySession ? (
                  <>
                    <div className="chat-history-title">
                      {new Date(historySession.closed_at).toLocaleString()}
                      <span className="chat-history-by"> — closed by {historySession.closed_by}</span>
                    </div>
                    <div className="chat-messages chat-messages-history">
                      {historyMessages.length === 0 && (
                        <div className="chat-empty">No messages in this conversation</div>
                      )}
                      {historyMessages.map((m) => (
                        <MessageBubble key={m.id} msg={m} />
                      ))}
                    </div>
                    <button
                      className="chat-history-back"
                      style={{ marginTop: "0.5rem" }}
                      onClick={() => { setHistorySession(null); setHistoryMessages([]); }}
                    >
                      ← Back to history
                    </button>
                  </>
                ) : history.length === 0 ? (
                  <div className="chat-empty">No past conversations</div>
                ) : (
                  <div className="chat-history-list">
                    {history.map((s) => (
                      <button key={s.id} className="chat-history-item" onClick={() => loadHistorySession(s)}>
                        <div className="chat-history-item-date">
                          {new Date(s.closed_at).toLocaleDateString()} · closed by {s.closed_by}
                        </div>
                        <div className="chat-history-item-msg">{s.last_message || "(no messages)"}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="chat-messages">
                {session?.status === "active" && (
                  <div className="chat-msg theirs chat-greeting">
                    <div className="chat-msg-bubble">
                      {lang === "he" ? (
                        <>היי {user?.name ? user.name.split(" ")[0] : ""}! 👋<br />ברוכים הבאים לתמיכה של DocuGuard.<br />במה נוכל לעזור לך היום?</>
                      ) : (
                        <>Hey {user?.name ? user.name.split(" ")[0] : ""}! 👋<br />Welcome to DocuGuard Support.<br />How can we help you today?</>
                      )}
                    </div>
                    <div className="chat-msg-time">Support</div>
                  </div>
                )}
                {messages.map((m) => (
                  <MessageBubble key={m.id} msg={m} />
                ))}
                {isTyping && (
                  <div className="chat-typing">
                    <span /><span /><span />
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Footer */}
          {!showHistory && session?.status === "active" && (
            <div className="chat-footer">
              <textarea
                className="chat-input"
                placeholder="Type a message..."
                value={input}
                onChange={handleInput}
                onKeyDown={handleKeyDown}
                rows={1}
              />
              <button className="chat-send-btn" onClick={handleSend} disabled={!input.trim()}>
                <SendIcon />
              </button>
            </div>
          )}

          {!showHistory && (!session || session?.status === "closed") && (
            <div className="chat-closed-notice">
              {session?.status === "closed"
                ? <>Conversation closed. <button onClick={handleNewChat}>Start new chat</button></>
                : <>Start a conversation with support.</>
              }
            </div>
          )}
        </div>
      )}
    </>
  );
}

function MessageBubble({ msg }) {
  const isMe = msg.sender_role === "user";
  const time = msg.timestamp
    ? new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "";
  return (
    <div className={`chat-msg ${isMe ? "mine" : "theirs"}`}>
      <div className="chat-msg-bubble">{msg.content}</div>
      <div className="chat-msg-time">{time}</div>
    </div>
  );
}

function ChatIcon() {
  return (
    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}
function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2.5">
      <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
function MinimizeIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5">
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  );
}
function EndIcon() {
  return (
    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14H6L5 6" />
      <path d="M10 11v6" /><path d="M14 11v6" />
    </svg>
  );
}
function HistoryIcon() {
  return (
    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="1 4 1 10 7 10" />
      <path d="M3.51 15a9 9 0 1 0 .49-4.5" />
    </svg>
  );
}
function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}
