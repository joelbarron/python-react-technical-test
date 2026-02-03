const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export async function createTransaction({ type, amount, idempotencyKey }) {
  const res = await fetch(`${BASE_URL}/transactions/create`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(idempotencyKey ? { "Idempotency-Key": idempotencyKey } : {}),
    },
    body: JSON.stringify({ type, amount }),
  });
  return res.json();
}

export async function asyncProcess(transactionId) {
  const res = await fetch(`${BASE_URL}/transactions/async-process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transaction_id: transactionId }),
  });
  return res.json();
}

export async function listTransactions() {
  const res = await fetch(`${BASE_URL}/transactions/`);
  return res.json();
}

export function connectWs(onMessage) {
  const wsBase = (BASE_URL || "").replace(/^http/, "ws");
  // Keep a single socket; caller handles reconnection if desired.
  const socket = new WebSocket(`${wsBase}/ws/transactions/`);
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  return socket;
}
