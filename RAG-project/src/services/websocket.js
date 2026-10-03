import { Client } from "@stomp/stompjs";
import { WS_URL, getAuthToken } from "./api";

export function createStompClient({ onConnect, onDisconnect, onError }) {
  const token = getAuthToken();

  const client = new Client({
    brokerURL: WS_URL,
    connectHeaders: token ? { Authorization: `Bearer ${token}` } : {},
    reconnectDelay: 4000,
    heartbeatIncoming: 10000,
    heartbeatOutgoing: 10000,
    onConnect: (frame) => {
      if (onConnect) onConnect(frame);
    },
    onDisconnect: (frame) => {
      if (onDisconnect) onDisconnect(frame);
    },
    onStompError: (frame) => {
      if (onError) onError(frame);
    },
    onWebSocketError: (event) => {
      if (onError) onError(event);
    },
  });

  return client;
}

export function subscribeToConversation(client, conversationId, onMessage) {
  if (!client || !client.connected || !conversationId) {
    return null;
  }

  const destination = `/topic/chat/${conversationId}`;
  return client.subscribe(destination, (stompMessage) => {
    try {
      const payload = JSON.parse(stompMessage.body);
      if (onMessage) onMessage(payload);
    } catch {
      if (onMessage) onMessage(stompMessage.body);
    }
  });
}

export function sendMessageViaStomp(client, conversationId, content) {
  if (!client || !client.connected) {
    throw new Error("ارتباط زنده برقرار نیست");
  }

  client.publish({
    destination: "/app/send.message",
    body: JSON.stringify({
      conversationId,
      content,
    }),
  });
}
