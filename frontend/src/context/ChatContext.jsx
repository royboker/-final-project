import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";

const ChatContext = createContext(null);

import { API_URL, WS_URL } from "../config.js";

export function ChatProvider({ children }) {
  const { token, user, isAuthed } = useAuth();
  const isAdmin = String(user?.role ?? "").trim().toLowerCase() === "admin";

  // ── User state ─────────────────────────────────────────────────────────────
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [unread, setUnread] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const [connected, setConnected] = useState(false);

  // ── Admin state ────────────────────────────────────────────────────────────
  const [adminUnread, setAdminUnread] = useState(0);

  const wsRef = useRef(null);
  const typingTimerRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const adminPollRef = useRef(null);

  // ── User WebSocket ─────────────────────────────────────────────────────────
  const connect = useCallback(() => {
    if (!token || !isAuthed || isAdmin) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(`${WS_URL}/ws/user/${token}`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);

    ws.onclose = () => {
      setConnected(false);
      reconnectTimerRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => ws.close();

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);

        if (data.type === "message") {
          const msg = data.message;
          setMessages((prev) => {
            if (prev.find((m) => m.id === msg.id)) return prev;
            return [...prev, msg];
          });
          if (msg.sender_role === "admin") {
            setUnread((prev) => prev + 1);
          }
        }

        if (data.type === "typing") {
          setIsTyping(true);
          clearTimeout(typingTimerRef.current);
          typingTimerRef.current = setTimeout(() => setIsTyping(false), 2000);
        }

        if (data.type === "session_closed") {
          setSession((prev) => (prev ? { ...prev, status: "closed" } : null));
        }
      } catch (_) {}
    };
  }, [token, isAuthed, isAdmin]);

  // Connect/disconnect based on auth state
  useEffect(() => {
    if (isAuthed && !isAdmin) {
      connect();
      // Load active session
      fetch(`${API_URL}/chat/session`, { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => r.json())
        .then((data) => {
          if (data.session) {
            setSession(data.session);
            setUnread(data.session.unread_user || 0);
            return fetch(`${API_URL}/chat/messages/${data.session.id}`, {
              headers: { Authorization: `Bearer ${token}` },
            })
              .then((r) => r.json())
              .then((d) => setMessages(d.messages || []));
          }
        })
        .catch(() => {});
    } else {
      clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
      wsRef.current = null;
      setConnected(false);
      setSession(null);
      setMessages([]);
      setUnread(0);
    }

    return () => {
      clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [isAuthed, isAdmin, token]);

  // ── Admin unread polling ───────────────────────────────────────────────────
  useEffect(() => {
    if (!isAdmin || !isAuthed || !token) {
      clearInterval(adminPollRef.current);
      setAdminUnread(0);
      return;
    }

    const poll = () => {
      fetch(`${API_URL}/chat/sessions`, { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => r.json())
        .then((data) => {
          const total = (data.sessions || []).reduce((sum, s) => sum + (s.unread_admin || 0), 0);
          setAdminUnread(total);
        })
        .catch(() => {});
    };

    poll();
    adminPollRef.current = setInterval(poll, 15000);

    return () => clearInterval(adminPollRef.current);
  }, [isAdmin, isAuthed, token]);

  // ── User actions ───────────────────────────────────────────────────────────
  const startChat = useCallback(async () => {
    if (!token) return;
    const res = await fetch(`${API_URL}/chat/session`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    setSession(data.session);
    setUnread(0);
    const msgRes = await fetch(`${API_URL}/chat/messages/${data.session.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const msgData = await msgRes.json();
    setMessages(msgData.messages || []);
  }, [token]);

  const sendMessage = useCallback(
    (content) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN || !session) return;
      wsRef.current.send(JSON.stringify({ type: "message", session_id: session.id, content }));
    },
    [session]
  );

  const sendTyping = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN || !session) return;
    wsRef.current.send(JSON.stringify({ type: "typing", session_id: session.id }));
  }, [session]);

  const markRead = useCallback(() => {
    setUnread(0);
    if (wsRef.current?.readyState === WebSocket.OPEN && session) {
      wsRef.current.send(JSON.stringify({ type: "read", session_id: session.id }));
    }
  }, [session]);

  const closeSession = useCallback(async () => {
    if (!session || !token) return;
    await fetch(`${API_URL}/chat/close/${session.id}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    setSession(null);
    setMessages([]);
    setUnread(0);
  }, [session, token]);

  const clearAdminUnread = useCallback(() => setAdminUnread(0), []);

  const value = {
    session,
    messages,
    unread,
    adminUnread,
    isTyping,
    connected,
    startChat,
    sendMessage,
    sendTyping,
    markRead,
    closeSession,
    setMessages,
    clearAdminUnread,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChat must be used within <ChatProvider>");
  return ctx;
}
