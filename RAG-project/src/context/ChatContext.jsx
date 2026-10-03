import { useEffect, useRef, useState, useCallback } from "react";
import { chatApi } from "../services/api";
import { createStompClient, subscribeToConversation, sendMessageViaStomp } from "../services/websocket";
import { useAuth } from "./useAuth";
import { ChatContext } from "./chat-context-def";
import toast from "react-hot-toast";

export function ChatProvider({ children }) {
  const { isAuthenticated, token } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const stompClientRef = useRef(null);
  const subscriptionRef = useRef(null);
  const activeIdRef = useRef(null);
  const isSendingRef = useRef(false);

  useEffect(() => {
    activeIdRef.current = activeConversationId;
  }, [activeConversationId]);

  const handleIncomingMessage = useCallback((msg) => {
    if (!msg) return;

    setMessages((prev) => {
      const existsIndex = prev.findIndex(
        (m) =>
          (m.messageId && m.messageId === msg.messageId) ||
          (m.tempId && m.tempId === msg.messageId)
      );

      if (existsIndex !== -1) {
        const next = [...prev];
        next[existsIndex] = { ...next[existsIndex], ...msg };
        return next;
      }

      if (!msg.botMessage) {
        const pendingIndex = prev.findIndex(
          (m) =>
            !m.botMessage &&
            (m.tempId === msg.messageId ||
              (m.tempId && m.content === msg.content))
        );
        if (pendingIndex !== -1) {
          const next = [...prev];
          next[pendingIndex] = { ...next[pendingIndex], ...msg, tempId: undefined };
          return next;
        }

        const duplicateIndex = prev.findIndex(
          (m) => !m.botMessage && m.content === msg.content
        );
        if (duplicateIndex !== -1) {
          const next = [...prev];
          next[duplicateIndex] = { ...next[duplicateIndex], ...msg };
          return next;
        }
      }

      if (msg.botMessage) {
        isSendingRef.current = false;
        setIsSending(false);
        const updated = prev.map((m) =>
          m.status === "PROCESSING" ? { ...m, status: "NONE" } : m
        );
        return [...updated, msg];
      }

      return [...prev, msg];
    });

    if (msg.botMessage) {
      isSendingRef.current = false;
      setIsSending(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated || !token) {
      return;
    }

    const client = createStompClient({
      onConnect: () => {
        setWsConnected(true);
      },
      onDisconnect: () => {
        setWsConnected(false);
      },
      onError: (err) => {
        console.error(err);
        setWsConnected(false);
      },
    });

    client.activate();
    stompClientRef.current = client;

    return () => {
      if (subscriptionRef.current) {
        subscriptionRef.current.unsubscribe();
        subscriptionRef.current = null;
      }
      client.deactivate();
      stompClientRef.current = null;
      setWsConnected(false);
    };
  }, [isAuthenticated, token, handleIncomingMessage]);

  useEffect(() => {
    if (!stompClientRef.current || !wsConnected || !activeConversationId) {
      return;
    }

    if (subscriptionRef.current) {
      subscriptionRef.current.unsubscribe();
      subscriptionRef.current = null;
    }

    subscriptionRef.current = subscribeToConversation(
      stompClientRef.current,
      activeConversationId,
      handleIncomingMessage
    );

    return () => {
      if (subscriptionRef.current) {
        subscriptionRef.current.unsubscribe();
        subscriptionRef.current = null;
      }
    };
  }, [activeConversationId, wsConnected, handleIncomingMessage]);

  const loadMessages = useCallback(async (conversationId) => {
    if (!conversationId) return;
    setIsLoadingMessages(true);
    try {
      const data = await chatApi.getMessages(conversationId);
      if (Array.isArray(data)) {
        const seen = new Set();
        const unique = [];
        for (let i = 0; i < data.length; i++) {
          const item = data[i];
          const key =
            item.messageId ||
            `${item.botMessage}-${item.content}-${item.createdAt || item.sendTime}`;
          if (!seen.has(key)) {
            seen.add(key);
            let processedItem = item;
            if (item.status === "PROCESSING") {
              const hasNextBot = data
                .slice(i + 1)
                .some((other) => other.botMessage);
              if (hasNextBot || !isSendingRef.current) {
                processedItem = { ...item, status: "NONE" };
              }
            }
            unique.push(processedItem);
          }
        }
        setMessages(unique);
      } else {
        setMessages([]);
      }
    } catch (error) {
      console.error(error);
      toast.error("خطا در بارگذاری پیام‌ها");
    } finally {
      setIsLoadingMessages(false);
    }
  }, []);

  const selectConversation = useCallback(
    (id) => {
      if (id === activeConversationId) return;
      isSendingRef.current = false;
      setIsSending(false);
      setActiveConversationId(id);
      loadMessages(id);
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      }
    },
    [activeConversationId, loadMessages]
  );

  const createConversation = useCallback(async () => {
    try {
      const newChat = await chatApi.createConversation();
      if (newChat && newChat.conversationId) {
        setConversations((prev) => [newChat, ...prev]);
        setActiveConversationId(newChat.conversationId);
        setMessages([]);
        toast.success("گفتگوی جدید ایجاد شد");
        if (window.innerWidth < 768) {
          setSidebarOpen(false);
        }
        return newChat;
      }
    } catch (error) {
      console.error(error);
      toast.error("خطا در ایجاد گفتگوی جدید");
    }
    return null;
  }, []);

  const deleteConversation = useCallback(
    async (chatId) => {
      try {
        await chatApi.deleteConversation(chatId);
        setConversations((prev) => {
          const filtered = prev.filter(
            (c) => (c.conversationId || c.id) !== chatId
          );
          if (activeConversationId === chatId) {
            if (filtered.length > 0) {
              const nextId = filtered[0].conversationId || filtered[0].id;
              setActiveConversationId(nextId);
              loadMessages(nextId);
            } else {
              setActiveConversationId(null);
              setMessages([]);
            }
          }
          return filtered;
        });
        toast.success("گفتگو حذف شد");
      } catch (error) {
        console.error(error);
        toast.error("خطا در حذف گفتگو");
      }
    },
    [activeConversationId, loadMessages]
  );

  const loadConversations = useCallback(async () => {
    if (!isAuthenticated) return;
    setIsLoadingConversations(true);
    try {
      const list = await chatApi.getConversations();
      const validList = Array.isArray(list) ? list : [];
      setConversations(validList);

      if (validList.length > 0 && !activeConversationId) {
        const firstId = validList[0].conversationId || validList[0].id;
        if (firstId) {
          setActiveConversationId(firstId);
          loadMessages(firstId);
        }
      }
    } catch (error) {
      console.error(error);
      toast.error("خطا در دریافت لیست گفتگوها");
    } finally {
      setIsLoadingConversations(false);
    }
  }, [isAuthenticated, activeConversationId, loadMessages]);

  useEffect(() => {
    if (!isAuthenticated) return;
    let isSubscribed = true;

    async function fetchInitialChats() {
      setIsLoadingConversations(true);
      try {
        const list = await chatApi.getConversations();
        if (!isSubscribed) return;
        const validList = Array.isArray(list) ? list : [];
        setConversations(validList);

        if (validList.length > 0) {
          const firstId = validList[0].conversationId || validList[0].id;
          if (firstId) {
            setActiveConversationId(firstId);
            const data = await chatApi.getMessages(firstId);
            if (isSubscribed) {
              const raw = Array.isArray(data) ? data : [];
              const seen = new Set();
              const unique = [];
              for (let i = 0; i < raw.length; i++) {
                const item = raw[i];
                const key =
                  item.messageId ||
                  `${item.botMessage}-${item.content}-${item.createdAt || item.sendTime}`;
                if (!seen.has(key)) {
                  seen.add(key);
                  let processedItem = item;
                  if (item.status === "PROCESSING") {
                    const hasNextBot = raw
                      .slice(i + 1)
                      .some((other) => other.botMessage);
                    if (hasNextBot || !isSendingRef.current) {
                      processedItem = { ...item, status: "NONE" };
                    }
                  }
                  unique.push(processedItem);
                }
              }
              setMessages(unique);
            }
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        if (isSubscribed) {
          setIsLoadingConversations(false);
        }
      }
    }

    fetchInitialChats();

    return () => {
      isSubscribed = false;
    };
  }, [isAuthenticated]);

  const sendMessage = useCallback(
    async (content) => {
      const trimmed = content?.trim();
      if (!trimmed || isSendingRef.current) return;

      let targetConversationId = activeConversationId;

      if (!targetConversationId) {
        const newChat = await createConversation();
        if (newChat?.conversationId) {
          targetConversationId = newChat.conversationId;
        } else {
          toast.error("ابتدا یک گفتگو ایجاد کنید");
          return;
        }
      }

      const tempId = `temp-${Date.now()}`;
      const optimisticMessage = {
        tempId,
        messageId: tempId,
        conversationId: targetConversationId,
        content: trimmed,
        sendTime: new Date().toISOString(),
        status: "PROCESSING",
        botMessage: false,
      };

      setMessages((prev) => [...prev, optimisticMessage]);
      isSendingRef.current = true;
      setIsSending(true);

      try {
        if (!stompClientRef.current || !stompClientRef.current.connected) {
          throw new Error("ارتباط زنده برقرار نیست");
        }
        sendMessageViaStomp(
          stompClientRef.current,
          targetConversationId,
          trimmed
        );
      } catch (error) {
        console.error(error);
        toast.error("خطا در ارسال پیام");
        setMessages((prev) =>
          prev.map((m) =>
            m.tempId === tempId ? { ...m, status: "FAILED" } : m
          )
        );
        isSendingRef.current = false;
        setIsSending(false);
      }
    },
    [activeConversationId, createConversation]
  );

  const activeConversation = conversations.find(
    (c) => (c.conversationId || c.id) === activeConversationId
  );

  const value = {
    conversations,
    activeConversationId,
    activeConversation,
    messages,
    isLoadingConversations,
    isLoadingMessages,
    isSending,
    wsConnected,
    sidebarOpen,
    setSidebarOpen,
    loadConversations,
    selectConversation,
    createConversation,
    deleteConversation,
    sendMessage,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}
