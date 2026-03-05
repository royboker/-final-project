import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useChat } from "../context/ChatContext";
import { adminApi } from "../lib/api";
import "./AdminDashboard.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const WS_URL = API_URL.replace(/^http/, "ws");

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const { adminUnread, clearAdminUnread } = useChat();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("overview");
  const [expandedUser, setExpandedUser] = useState(null);
  const [scans, setScans] = useState([]);
  const [scansLoading, setScansLoading] = useState(false);
  const [scanSearch, setScanSearch] = useState("");
  const [expandedScan, setExpandedScan] = useState(null);
  const [viewScansUser, setViewScansUser] = useState(null);
  const [viewScanDetail, setViewScanDetail] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, usersRes] = await Promise.all([
        adminApi.getStats(token),
        adminApi.getUsers(token),
      ]);
      setStats(statsRes);
      setUsers(usersRes.users);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  const fetchScans = useCallback(async () => {
    setScansLoading(true);
    try {
      const res = await adminApi.getScans(token);
      setScans(res.scans || []);
    } catch (err) {
      console.error(err);
    } finally {
      setScansLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, [fetchData]);

  useEffect(() => {
    if (tab === "scans") fetchScans();
  }, [tab, fetchScans]);

  function openUserScans(u) {
    setViewScansUser(u);
    setViewScanDetail(null);
    if (scans.length === 0 && !scansLoading) fetchScans();
  }

  async function handleDelete(userId, userName) {
    if (!confirm(`Delete user "${userName}"? This cannot be undone.`)) return;
    await adminApi.deleteUser(token, userId);
    setUsers(u => u.filter(x => x.id !== userId));
  }

  async function handleRoleChange(userId, currentRole) {
    const newRole = currentRole === "admin" ? "user" : "admin";
    await adminApi.changeRole(token, userId, newRole);
    setUsers(u => u.map(x => x.id === userId ? { ...x, role: newRole } : x));
  }

  const filtered = users.filter(u =>
    u.name.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  const maxLogins = stats ? Math.max(...stats.chart.map(d => d.logins), 1) : 1;

  if (loading) return (
    <div className="admin-loading">
      <div className="admin-spinner" />
      <p>Loading dashboard...</p>
    </div>
  );

  return (
    <div className="admin-layout">
      {/* ── Sidebar ── */}
      <aside className="admin-sidebar">
        <a className="admin-logo" href="/">
          <LogoIcon />
          <span>Docu<em>Guard</em></span>
        </a>
        <nav className="admin-nav">
          <button className={tab === "overview" ? "active" : ""} onClick={() => setTab("overview")}>
            <GridIcon /> Overview
          </button>
          <button className={tab === "users" ? "active" : ""} onClick={() => setTab("users")}>
            <UsersIcon /> Users
          </button>
          <button className={tab === "scans" ? "active" : ""} onClick={() => setTab("scans")}>
            <ScanIcon /> Scans
          </button>
          <button className={tab === "messages" ? "active" : ""} onClick={() => { setTab("messages"); clearAdminUnread(); }}>
            <ChatIcon /> Messages
            {adminUnread > 0 && <span className="admin-nav-badge">{adminUnread > 9 ? "9+" : adminUnread}</span>}
          </button>
        </nav>
        <div className="admin-sidebar-footer">
          <div className="admin-me">
            <div className="admin-me-avatar">{user?.name?.[0]?.toUpperCase()}</div>
            <div>
              <div className="admin-me-name">{user?.name}</div>
              <div className="admin-me-role">Administrator</div>
            </div>
          </div>
          <button className="admin-back-btn" onClick={() => navigate("/")}>← Home</button>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="admin-main">
        <div className="admin-topbar">
          <div>
            <h1>{tab === "overview" ? "Dashboard Overview" : tab === "users" ? "User Management" : tab === "messages" ? "Messages" : "All Scans"}</h1>
            <p>Last updated: {new Date().toLocaleTimeString()} · Auto-refreshes every 15s</p>
          </div>
          <div className="admin-live">
            <span className="admin-live-dot" />
            LIVE
          </div>
        </div>

        {tab === "overview" && stats && (
          <>
            <div className="admin-stats-grid">
              <StatCard label="Total Users" value={stats.total_users} icon="👥" color="lime" />
              <StatCard label="New Today" value={stats.new_today} icon="✨" color="blue" />
              <StatCard label="Active Today" value={stats.active_today} icon="🟢" color="green" />
              <StatCard label="Active This Week" value={stats.active_week} icon="📅" color="orange" />
              <StatCard label="Total Scans" value={stats.total_scans} icon="🔍" color="purple" />
              <StatCard label="Forged Detected" value={stats.forged_scans} icon="⚠️" color="red" />
            </div>
            <div className="admin-chart-card">
              <h3>Login Activity — Last 7 Days</h3>
              <div className="admin-chart">
                {stats.chart.map((d, i) => (
                  <div className="admin-chart-col" key={i}>
                    <div className="admin-chart-bar-wrap">
                      <div className="admin-chart-bar" style={{ height: `${(d.logins / maxLogins) * 100}%` }}>
                        <span className="admin-chart-val">{d.logins}</span>
                      </div>
                    </div>
                    <div className="admin-chart-label">{d.date}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {tab === "messages" && (
          <AdminMessagesTab token={token} />
        )}

        {tab === "scans" && (
          <ScansTab
            scans={scans}
            users={users}
            loading={scansLoading}
            search={scanSearch}
            onSearch={setScanSearch}
            expandedScan={expandedScan}
            setExpandedScan={setExpandedScan}
            onRefresh={fetchScans}
          />
        )}

        {tab === "users" && (
          <>
            <div className="admin-toolbar">
              <div className="admin-search-wrap">
                <SearchIcon />
                <input
                  type="text"
                  placeholder="Search by name or email..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
              </div>
              <span className="admin-count">{filtered.length} users</span>
            </div>

            {/* Desktop table */}
            <div className="admin-table-wrap desktop-only">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Auth</th>
                    <th>Role</th>
                    <th>Verified</th>
                    <th>Joined</th>
                    <th>Last Login</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(u => (
                    <tr key={u.id}>
                      <td>
                        <div className="admin-user-cell">
                          <div className="admin-avatar">{u.name?.[0]?.toUpperCase()}</div>
                          <div>
                            <div className="admin-user-name">{u.name}</div>
                            <div className="admin-user-email">{u.email}</div>
                          </div>
                        </div>
                      </td>
                      <td><span className={`admin-badge ${u.auth_method}`}>{u.auth_method === "google" ? "🔵 Google" : "📧 Email"}</span></td>
                      <td><span className={`admin-badge role-${u.role}`}>{u.role}</span></td>
                      <td><span className={`admin-badge ${u.is_verified ? "verified" : "unverified"}`}>{u.is_verified ? "✓ Yes" : "✕ No"}</span></td>
                      <td className="admin-date">{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
                      <td className="admin-date">{u.last_login ? new Date(u.last_login).toLocaleDateString() : "Never"}</td>
                      <td>
                        <div className="admin-actions">
                          <button className="admin-btn-scans" onClick={() => openUserScans(u)}>🔍 Scans</button>
                          <button className="admin-btn-role" onClick={() => handleRoleChange(u.id, u.role)} disabled={u.id === user?.id} style={u.id === user?.id ? { opacity: 0.3, cursor: "not-allowed" } : {}}>
                            {u.role === "admin" ? "⬇ Demote" : "⬆ Promote"}
                          </button>
                          <button className="admin-btn-delete" onClick={() => handleDelete(u.id, u.name)} disabled={u.id === user?.id} style={u.id === user?.id ? { opacity: 0.3, cursor: "not-allowed" } : {}}>🗑</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr><td colSpan={7} style={{ textAlign: "center", color: "#52525b", padding: "2rem" }}>No users found</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Mobile accordion cards */}
            <div className="admin-cards mobile-only">
              {filtered.map(u => (
                <div key={u.id} className={`admin-card ${expandedUser === u.id ? "expanded" : ""}`}>
                  <button className="admin-card-header" onClick={() => setExpandedUser(expandedUser === u.id ? null : u.id)}>
                    <div className="admin-user-cell">
                      <div className="admin-avatar">{u.name?.[0]?.toUpperCase()}</div>
                      <div>
                        <div className="admin-user-name">{u.name}</div>
                        <div className="admin-user-email">{u.email}</div>
                      </div>
                    </div>
                    <div className="admin-card-chevron">{expandedUser === u.id ? "▲" : "▼"}</div>
                  </button>

                  {expandedUser === u.id && (
                    <div className="admin-card-body">
                      <div className="admin-card-row">
                        <span className="admin-card-label">Auth</span>
                        <span className={`admin-badge ${u.auth_method}`}>{u.auth_method === "google" ? "🔵 Google" : "📧 Email"}</span>
                      </div>
                      <div className="admin-card-row">
                        <span className="admin-card-label">Role</span>
                        <span className={`admin-badge role-${u.role}`}>{u.role}</span>
                      </div>
                      <div className="admin-card-row">
                        <span className="admin-card-label">Verified</span>
                        <span className={`admin-badge ${u.is_verified ? "verified" : "unverified"}`}>{u.is_verified ? "✓ Yes" : "✕ No"}</span>
                      </div>
                      <div className="admin-card-row">
                        <span className="admin-card-label">Joined</span>
                        <span>{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</span>
                      </div>
                      <div className="admin-card-row">
                        <span className="admin-card-label">Last Login</span>
                        <span>{u.last_login ? new Date(u.last_login).toLocaleDateString() : "Never"}</span>
                      </div>
                      <div className="admin-card-actions">
                        <button className="admin-btn-scans" onClick={() => openUserScans(u)}>🔍 Scans</button>
                        <button className="admin-btn-role" onClick={() => handleRoleChange(u.id, u.role)} disabled={u.id === user?.id} style={u.id === user?.id ? { opacity: 0.3, cursor: "not-allowed" } : {}}>
                          {u.role === "admin" ? "⬇ Demote" : "⬆ Promote"}
                        </button>
                        <button className="admin-btn-delete" onClick={() => handleDelete(u.id, u.name)} disabled={u.id === user?.id} style={u.id === user?.id ? { opacity: 0.3, cursor: "not-allowed" } : {}}>🗑</button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {filtered.length === 0 && (
                <div style={{ textAlign: "center", color: "#52525b", padding: "2rem" }}>No users found</div>
              )}
            </div>
          </>
        )}
      </main>

      {/* ── User Scans Modal ── */}
      {viewScansUser && (
        <UserScansModal
          user={viewScansUser}
          scans={scans.filter(s => s.user_id === viewScansUser.id)}
          loading={scansLoading}
          selectedScan={viewScanDetail}
          onSelectScan={setViewScanDetail}
          onBack={() => setViewScanDetail(null)}
          onClose={() => { setViewScansUser(null); setViewScanDetail(null); }}
        />
      )}

      {/* ── Mobile bottom nav ── */}
      <div className="admin-bottom-nav">
        <button className={tab === "overview" ? "active" : ""} onClick={() => setTab("overview")}><GridIcon /><span>Overview</span></button>
        <button className={tab === "users" ? "active" : ""} onClick={() => setTab("users")}><UsersIcon /><span>Users</span></button>
        <button className={tab === "scans" ? "active" : ""} onClick={() => setTab("scans")}><ScanIcon /><span>Scans</span></button>
        <button className={tab === "messages" ? "active" : ""} onClick={() => { setTab("messages"); clearAdminUnread(); }} style={{ position: "relative" }}>
          <ChatIcon /><span>Messages</span>
          {adminUnread > 0 && <span className="admin-nav-badge">{adminUnread > 9 ? "9+" : adminUnread}</span>}
        </button>
        <button onClick={() => navigate("/")}><HomeIcon /><span>Home</span></button>
      </div>
    </div>
  );
}

// ── Admin Messages Tab ─────────────────────────────────────────────────────────
function AdminMessagesTab({ token }) {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [historySession, setHistorySession] = useState(null);
  const wsRef = useRef(null);
  const activeSessionRef = useRef(null);
  const typingRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Load active sessions
  const fetchSessions = useCallback(async () => {
    const res = await fetch(`${API_URL}/chat/sessions`, { headers: { Authorization: `Bearer ${token}` } });
    const data = await res.json();
    setSessions(data.sessions || []);
  }, [token]);

  useEffect(() => { fetchSessions(); }, [fetchSessions]);

  // Connect admin WebSocket
  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/ws/admin/${token}`);
    wsRef.current = ws;

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);

        if (data.type === "new_session") {
          setSessions((prev) => [data.session, ...prev]);
        }

        if (data.type === "message") {
          const msg = data.message;
          setSessions((prev) =>
            prev.map((s) =>
              s.id === msg.session_id
                ? { ...s, last_message: msg.content, unread_admin: msg.sender_role === "user" ? (s.unread_admin || 0) + 1 : s.unread_admin }
                : s
            )
          );
          if (activeSessionRef.current?.id === msg.session_id) {
            setMessages((prev) => {
              if (prev.find((m) => m.id === msg.id)) return prev;
              return [...prev, msg];
            });
            // Mark as read since we're viewing
            if (msg.sender_role === "user") {
              setSessions((prev) => prev.map((s) => s.id === msg.session_id ? { ...s, unread_admin: 0 } : s));
              ws.send(JSON.stringify({ type: "read", session_id: msg.session_id }));
            }
          }
        }

        if (data.type === "typing") {
          if (activeSessionRef.current?.id === data.session_id) {
            setIsTyping(true);
            clearTimeout(typingRef.current);
            typingRef.current = setTimeout(() => setIsTyping(false), 2000);
          }
        }

        if (data.type === "session_closed") {
          setSessions((prev) => prev.filter((s) => s.id !== data.session_id));
          if (activeSessionRef.current?.id === data.session_id) {
            setActiveSession(null);
            activeSessionRef.current = null;
            setMessages([]);
          }
        }
      } catch (_) {}
    };

    return () => ws.close();
  }, [token]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const openSession = async (s) => {
    setActiveSession(s);
    activeSessionRef.current = s;
    setShowHistory(false);
    setInput("");
    setIsTyping(false);
    // Load messages
    const res = await fetch(`${API_URL}/chat/messages/${s.id}`, { headers: { Authorization: `Bearer ${token}` } });
    const data = await res.json();
    setMessages(data.messages || []);
    // Mark read
    setSessions((prev) => prev.map((x) => x.id === s.id ? { ...x, unread_admin: 0 } : x));
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "read", session_id: s.id }));
    }
  };

  const sendReply = () => {
    const trimmed = input.trim();
    if (!trimmed || !activeSession || wsRef.current?.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(JSON.stringify({ type: "message", session_id: activeSession.id, content: trimmed }));
    setInput("");
  };

  const sendAdminTyping = () => {
    if (!activeSession || wsRef.current?.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(JSON.stringify({ type: "typing", session_id: activeSession.id }));
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendReply(); }
  };

  const closeSession = async (sessionId) => {
    if (!confirm("Close this conversation?")) return;
    await fetch(`${API_URL}/chat/close/${sessionId}`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
    setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    if (activeSession?.id === sessionId) { setActiveSession(null); activeSessionRef.current = null; setMessages([]); }
  };

  const loadHistory = async () => {
    const res = await fetch(`${API_URL}/chat/history/all`, { headers: { Authorization: `Bearer ${token}` } });
    const data = await res.json();
    setHistory(data.sessions || []);
    setShowHistory(true);
    setHistorySession(null);
    setActiveSession(null);
    activeSessionRef.current = null;
    setMessages([]);
  };

  const openHistorySession = async (s) => {
    const res = await fetch(`${API_URL}/chat/messages/${s.id}`, { headers: { Authorization: `Bearer ${token}` } });
    const data = await res.json();
    setHistorySession(s);
    setMessages(data.messages || []);
  };

  return (
    <div className="admin-chat-layout">
      {/* Session list */}
      <div className="admin-chat-sidebar">
        <div className="admin-chat-sidebar-header">
          <span>Active Conversations</span>
          <button className="admin-chat-hist-btn" onClick={loadHistory} title="View history">History</button>
        </div>

        {showHistory ? (
          <>
            <button className="admin-chat-back-btn" onClick={() => { setShowHistory(false); setHistorySession(null); setMessages([]); }}>
              ← Active chats
            </button>
            <div className="admin-chat-sidebar-sub">Past conversations</div>
            {history.length === 0 && <div className="admin-chat-empty">No history yet</div>}
            {history.map((s) => (
              <button
                key={s.id}
                className={`admin-chat-session-item ${historySession?.id === s.id ? "selected" : ""}`}
                onClick={() => openHistorySession(s)}
              >
                <div className="admin-chat-session-name">{s.user_name || s.user_email}</div>
                <div className="admin-chat-session-msg">{s.last_message || "(no messages)"}</div>
                <div className="admin-chat-session-date">{s.closed_at ? new Date(s.closed_at).toLocaleDateString() : ""}</div>
              </button>
            ))}
          </>
        ) : (
          <>
            {sessions.length === 0 && <div className="admin-chat-empty">No active conversations</div>}
            {sessions.map((s) => (
              <button
                key={s.id}
                className={`admin-chat-session-item ${activeSession?.id === s.id ? "selected" : ""}`}
                onClick={() => openSession(s)}
              >
                <div className="admin-chat-session-top">
                  <span className="admin-chat-session-name">{s.user_name || s.user_email}</span>
                  {s.unread_admin > 0 && <span className="admin-chat-unread">{s.unread_admin}</span>}
                </div>
                <div className="admin-chat-session-msg">{s.last_message || "No messages yet"}</div>
              </button>
            ))}
          </>
        )}
      </div>

      {/* Chat area */}
      <div className="admin-chat-main">
        {showHistory && historySession ? (
          <>
            <div className="admin-chat-topbar">
              <div>
                <div className="admin-chat-user-name">{historySession.user_name || historySession.user_email}</div>
                <div className="admin-chat-user-email">
                  Closed {historySession.closed_at ? new Date(historySession.closed_at).toLocaleString() : ""}
                  {historySession.closed_by ? ` · by ${historySession.closed_by}` : ""}
                </div>
              </div>
            </div>
            <div className="admin-chat-messages">
              {messages.length === 0 && (
                <div className="admin-chat-empty" style={{ marginTop: "2rem" }}>No messages in this conversation</div>
              )}
              {messages.map((m) => (
                <div key={m.id} className={`admin-chat-msg ${m.sender_role === "admin" ? "mine" : "theirs"}`}>
                  <div className="admin-chat-bubble">{m.content}</div>
                  <div className="admin-chat-time">
                    {m.sender_role === "admin" ? "You" : historySession.user_name} ·{" "}
                    {m.timestamp ? new Date(m.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <div className="admin-chat-closed">This conversation is closed (read-only)</div>
          </>
        ) : !activeSession ? (
          <div className="admin-chat-placeholder">
            <span>💬</span>
            <p>{showHistory ? "Select a past conversation" : "Select a conversation to view messages"}</p>
          </div>
        ) : (
          <>
            <div className="admin-chat-topbar">
              <div>
                <div className="admin-chat-user-name">{activeSession.user_name || activeSession.user_email}</div>
                <div className="admin-chat-user-email">{activeSession.user_email}</div>
              </div>
              {activeSession.status === "active" && (
                <button className="admin-btn-delete" onClick={() => closeSession(activeSession.id)} title="Close conversation">
                  Close chat
                </button>
              )}
            </div>

            <div className="admin-chat-messages">
              {messages.length === 0 && (
                <div className="admin-chat-empty" style={{ marginTop: "2rem" }}>No messages yet</div>
              )}
              {messages.map((m) => (
                <div key={m.id} className={`admin-chat-msg ${m.sender_role === "admin" ? "mine" : "theirs"}`}>
                  <div className="admin-chat-bubble">{m.content}</div>
                  <div className="admin-chat-time">
                    {m.sender_role === "admin" ? "You" : activeSession.user_name} ·{" "}
                    {m.timestamp ? new Date(m.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="admin-chat-msg theirs">
                  <div className="admin-chat-bubble admin-chat-typing">
                    <span /><span /><span />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {activeSession.status === "active" && (
              <div className="admin-chat-footer">
                <textarea
                  className="admin-chat-input"
                  placeholder={`Reply to ${activeSession.user_name || "user"}...`}
                  value={input}
                  onChange={(e) => { setInput(e.target.value); sendAdminTyping(); }}
                  onKeyDown={handleKeyDown}
                  rows={1}
                />
                <button className="admin-chat-send" onClick={sendReply} disabled={!input.trim()}>Send</button>
              </div>
            )}
            {activeSession.status === "closed" && (
              <div className="admin-chat-closed">This conversation has been closed.</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, color }) {
  return (
    <div className={`admin-stat-card color-${color}`}>
      <div className="admin-stat-icon">{icon}</div>
      <div className="admin-stat-value">{value}</div>
      <div className="admin-stat-label">{label}</div>
    </div>
  );
}

function LogoIcon() {
  return (
    <svg width="26" height="26" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="8" fill="#a3e635"/>
      <rect x="8" y="6" width="13" height="17" rx="2" fill="#09090f"/>
      <path d="M17 6 L21 10 H17 Z" fill="#a3e635"/>
      <rect x="10.5" y="13" width="8" height="1.2" rx="0.6" fill="#a3e635" opacity="0.9"/>
      <rect x="10.5" y="16" width="6" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6"/>
      <rect x="10.5" y="19" width="7" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6"/>
      <circle cx="22" cy="22" r="5" fill="#a3e635"/>
      <path d="M19.5 22 L21.2 23.8 L24.5 20.5" stroke="#09090f" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}
function GridIcon() { return <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>; }
function ChatIcon() { return <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>; }
function UsersIcon() { return <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>; }
function SearchIcon() { return <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>; }
function HomeIcon() { return <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>; }
function ScanIcon() { return <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><line x1="7" y1="12" x2="17" y2="12"/></svg>; }

function ConfBar({ value }) {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 80 ? "#a3e635" : pct >= 50 ? "#fb923c" : "#f87171";
  return (
    <div className="admin-conf-bar">
      <div><div className="admin-conf-fill" style={{ width: `${pct}%`, background: color }} /></div>
      <span>{pct}%</span>
    </div>
  );
}

function UserScansModal({ user, scans, loading, selectedScan, onSelectScan, onBack, onClose }) {
  return (
    <div className="usm-overlay" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="usm-panel">
        {/* Header */}
        <div className="usm-header">
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            {selectedScan && (
              <button className="usm-back-btn" onClick={onBack}>← Back</button>
            )}
            <div>
              <div style={{ fontWeight: 600, color: "#fff", fontSize: "0.95rem" }}>{user.name}</div>
              <div style={{ fontSize: "0.73rem", color: "#52525b" }}>
                {selectedScan ? "Scan Details" : `${scans.length} scan${scans.length !== 1 ? "s" : ""}`}
              </div>
            </div>
          </div>
          <button className="usm-close-btn" onClick={onClose}>✕</button>
        </div>

        {/* Body */}
        <div className="usm-body">
          {loading ? (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 180, gap: "0.75rem", color: "#71717a" }}>
              <div className="admin-spinner" style={{ width: 26, height: 26, borderWidth: 2 }} />
              Loading scans...
            </div>
          ) : selectedScan ? (
            /* ── Detail view ── */
            <ScanDetail scan={selectedScan} />
          ) : scans.length === 0 ? (
            <div style={{ textAlign: "center", color: "#52525b", padding: "3rem 0", fontSize: "0.875rem" }}>
              No scans found for this user.
            </div>
          ) : (
            /* ── List view ── */
            <div className="usm-scan-list">
              {scans.map(s => (
                <button key={s.id} className="usm-scan-item" onClick={() => onSelectScan(s)}>
                  <div className="usm-scan-thumb-wrap">
                    {s.image_data
                      ? <img src={`data:image/jpeg;base64,${s.image_data}`} alt="scan" className="usm-thumb" />
                      : <div className="usm-thumb usm-thumb-placeholder">📄</div>
                    }
                  </div>
                  <div className="usm-scan-info">
                    <div className="usm-scan-type">{s.doc_type ?? "Unknown"}</div>
                    <div className="usm-scan-meta">{s.file_name}</div>
                    <div className="usm-scan-meta">{s.model_used} · {Math.round((s.confidence || 0) * 100)}% confidence</div>
                    <div className="usm-scan-date">{s.scanned_at ? new Date(s.scanned_at).toLocaleString() : "—"}</div>
                  </div>
                  <div className="usm-scan-conf">
                    <ConfBar value={s.confidence} />
                  </div>
                  <div className="usm-scan-chevron">›</div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ScansTab({ scans, users, loading, search, onSearch, expandedScan, setExpandedScan, onRefresh }) {
  const userMap = Object.fromEntries(users.map(u => [u.id, u]));

  const filtered = scans.filter(s => {
    const q = search.toLowerCase();
    if (!q) return true;
    const u = userMap[s.user_id];
    return (
      s.file_name?.toLowerCase().includes(q) ||
      s.doc_type?.toLowerCase().includes(q) ||
      s.model_used?.toLowerCase().includes(q) ||
      u?.name?.toLowerCase().includes(q) ||
      u?.email?.toLowerCase().includes(q)
    );
  });

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "200px", gap: "0.75rem", color: "#71717a" }}>
      <div className="admin-spinner" style={{ width: 28, height: 28, borderWidth: 2 }} />
      Loading scans...
    </div>
  );

  return (
    <>
      <div className="admin-toolbar">
        <div className="admin-search-wrap">
          <SearchIcon />
          <input
            type="text"
            placeholder="Search by user, filename, doc type..."
            value={search}
            onChange={e => onSearch(e.target.value)}
          />
        </div>
        <span className="admin-count">{filtered.length} scans</span>
        <button className="admin-btn-role" onClick={onRefresh} style={{ whiteSpace: "nowrap" }}>⟳ Refresh</button>
      </div>

      {/* Desktop table */}
      <div className="admin-table-wrap desktop-only">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Image</th>
              <th>User</th>
              <th>File</th>
              <th>Doc Type</th>
              <th>Model</th>
              <th>Confidence</th>
              <th>Date</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(s => {
              const u = userMap[s.user_id];
              const isOpen = expandedScan === s.id;
              return (
                <>
                  <tr key={s.id} style={{ cursor: "pointer" }} onClick={() => setExpandedScan(isOpen ? null : s.id)}>
                    <td>
                      {s.image_data
                        ? <img className="admin-scan-thumb" src={`data:image/jpeg;base64,${s.image_data}`} alt="scan" />
                        : <div className="admin-scan-thumb" style={{ background: "rgba(255,255,255,0.05)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.2rem" }}>📄</div>
                      }
                    </td>
                    <td>
                      <div className="admin-user-cell">
                        <div className="admin-avatar">{u?.name?.[0]?.toUpperCase() ?? "?"}</div>
                        <div>
                          <div className="admin-user-name">{u?.name ?? "Unknown"}</div>
                          <div className="admin-user-email">{u?.email ?? s.user_id}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.file_name}</td>
                    <td><span className="admin-badge email">{s.doc_type ?? "—"}</span></td>
                    <td><span className="admin-badge role-user" style={{ textTransform: "uppercase", letterSpacing: "0.04em" }}>{s.model_used}</span></td>
                    <td><ConfBar value={s.confidence} /></td>
                    <td className="admin-date">{s.scanned_at ? new Date(s.scanned_at).toLocaleString() : "—"}</td>
                    <td style={{ color: "#52525b", fontSize: "0.7rem" }}>{isOpen ? "▲" : "▼"}</td>
                  </tr>
                  {isOpen && (
                    <tr key={`${s.id}-detail`} style={{ background: "rgba(163,230,53,0.03)" }}>
                      <td colSpan={8} style={{ padding: "1.25rem 1.5rem", borderBottom: "1px solid rgba(163,230,53,0.15)" }}>
                        <ScanDetail scan={s} />
                      </td>
                    </tr>
                  )}
                </>
              );
            })}
            {filtered.length === 0 && (
              <tr><td colSpan={8} style={{ textAlign: "center", color: "#52525b", padding: "2rem" }}>No scans found</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile accordion cards */}
      <div className="admin-cards mobile-only">
        {filtered.map(s => {
          const u = userMap[s.user_id];
          const isOpen = expandedScan === s.id;
          return (
            <div key={s.id} className={`admin-card ${isOpen ? "expanded" : ""}`}>
              <button className="admin-card-header" onClick={() => setExpandedScan(isOpen ? null : s.id)}>
                <div className="admin-user-cell">
                  {s.image_data
                    ? <img className="admin-scan-thumb" src={`data:image/jpeg;base64,${s.image_data}`} alt="scan" />
                    : <div className="admin-avatar">📄</div>
                  }
                  <div>
                    <div className="admin-user-name">{s.doc_type ?? s.file_name}</div>
                    <div className="admin-user-email">{u?.name ?? "Unknown"} · {s.model_used}</div>
                  </div>
                </div>
                <div className="admin-card-chevron">{isOpen ? "▲" : "▼"}</div>
              </button>
              {isOpen && (
                <div className="admin-card-body">
                  <ScanDetail scan={s} />
                </div>
              )}
            </div>
          );
        })}
        {filtered.length === 0 && (
          <div style={{ textAlign: "center", color: "#52525b", padding: "2rem" }}>No scans found</div>
        )}
      </div>
    </>
  );
}

function ScanDetail({ scan }) {
  const probs = scan.probabilities || {};
  return (
    <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap", alignItems: "flex-start" }}>
      {scan.image_data && (
        <img
          src={`data:image/jpeg;base64,${scan.image_data}`}
          alt="scan"
          style={{ width: 220, height: 138, objectFit: "cover", borderRadius: 12, border: "1px solid rgba(255,255,255,0.12)", flexShrink: 0, boxShadow: "0 8px 24px rgba(0,0,0,0.4)" }}
        />
      )}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.6rem", fontSize: "0.82rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: "0.5rem" }}>
          <DetailRow label="File" value={scan.file_name} />
          <DetailRow label="Doc Type" value={scan.doc_type} />
          <DetailRow label="Model" value={scan.model_used} />
          <DetailRow label="Confidence" value={`${Math.round((scan.confidence || 0) * 100)}%`} />
          <DetailRow label="Scanned At" value={scan.scanned_at ? new Date(scan.scanned_at).toLocaleString() : "—"} />
          {scan.demo && <DetailRow label="Mode" value="Demo (no model file)" />}
        </div>
        {Object.keys(probs).length > 0 && (
          <div style={{ marginTop: "0.5rem" }}>
            <div style={{ fontSize: "0.68rem", color: "#52525b", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>Probabilities</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
              {Object.entries(probs).sort((a, b) => b[1] - a[1]).map(([label, val]) => (
                <div key={label} style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                  <span style={{ width: 120, color: "#a1a1aa", fontSize: "0.78rem" }}>{label}</span>
                  <div style={{ flex: 1, height: 5, background: "rgba(255,255,255,0.07)", borderRadius: 99 }}>
                    <div style={{ width: `${Math.round(val * 100)}%`, height: "100%", background: label === scan.doc_type ? "#a3e635" : "rgba(163,230,53,0.3)", borderRadius: 99, transition: "width 0.3s" }} />
                  </div>
                  <span style={{ fontSize: "0.72rem", color: "#a1a1aa", width: 40, textAlign: "right" }}>{Math.round(val * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function DetailRow({ label, value }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.15rem" }}>
      <span style={{ fontSize: "0.65rem", color: "#52525b", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>{label}</span>
      <span style={{ color: "#e4e4e7" }}>{value ?? "—"}</span>
    </div>
  );
}
