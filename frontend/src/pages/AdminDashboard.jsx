import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { adminApi } from "../lib/api";
import "./AdminDashboard.css";

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("overview");
  const [expandedUser, setExpandedUser] = useState(null);

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

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, [fetchData]);

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
            <h1>{tab === "overview" ? "Dashboard Overview" : "User Management"}</h1>
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

      {/* ── Mobile bottom nav ── */}
      <div className="admin-bottom-nav">
        <button className={tab === "overview" ? "active" : ""} onClick={() => setTab("overview")}><GridIcon /><span>Overview</span></button>
        <button className={tab === "users" ? "active" : ""} onClick={() => setTab("users")}><UsersIcon /><span>Users</span></button>
        <button onClick={() => navigate("/")}><HomeIcon /><span>Home</span></button>
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
function UsersIcon() { return <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>; }
function SearchIcon() { return <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>; }
function HomeIcon() { return <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>; }
