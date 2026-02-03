import { useEffect, useMemo, useState } from "react";
import { asyncProcess, connectWs, createTransaction, listTransactions } from "./api.js";

function makeIdempotencyKey() {
  return `idemp_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

export default function App() {
  const [type, setType] = useState("credit");
  const [amount, setAmount] = useState("100.00");
  const [idempotencyKey, setIdempotencyKey] = useState("");
  const [transactions, setTransactions] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [error, setError] = useState("");
  const [notifications, setNotifications] = useState([]);

  const computedKey = useMemo(() => (idempotencyKey.trim() ? idempotencyKey.trim() : makeIdempotencyKey()), [idempotencyKey]);

  useEffect(() => {
    listTransactions().then(setTransactions).catch(() => {});
    // Single WS connection for live updates; keep it simple for the demo.
    const socket = connectWs((msg) => {
      if (msg.event === "transaction.updated") {
        setTransactions((prev) => {
          const updated = prev.map((t) => (t.id === msg.data.id ? msg.data : t));
          const exists = updated.some((t) => t.id === msg.data.id);
          return exists ? updated : [msg.data, ...updated];
        });
        // Push a lightweight toast; we cap rendering below to avoid unbounded growth.
        setNotifications((prev) => [
          {
            id: `${msg.data.id}_${msg.data.status}_${Date.now()}`,
            message: `Transaction ${msg.data.id.slice(0, 8)} is now ${msg.data.status}`,
            status: msg.data.status,
          },
          ...prev,
        ]);
      }
    });
    return () => socket.close();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    try {
      // If no key is provided, generate one so the backend always gets idempotency.
      const tx = await createTransaction({ type, amount, idempotencyKey: computedKey });
      if (tx?.detail) {
        setError(tx.detail);
        return;
      }
      setTransactions((prev) => [tx, ...prev.filter((t) => t.id !== tx.id)]);
      setSelectedId(tx.id);
      if (!idempotencyKey.trim()) {
        setIdempotencyKey(computedKey);
      }
    } catch (err) {
      setError("Failed to create transaction");
    }
  }

  async function handleAsyncProcess() {
    if (!selectedId) return;
    // Fire-and-forget; status changes come back through WebSocket.
    await asyncProcess(selectedId);
  }

  return (
    <div className="min-h-screen bg-background text-secondary">
      <div className="mx-auto max-w-4xl px-4 py-10">
        <h1 className="text-4xl font-semibold tracking-tight">Transactions</h1>

        <form className="mt-6 rounded-2xl border border-border bg-surface p-6 shadow-sm" onSubmit={handleCreate}>
          <div className="grid gap-6 md:grid-cols-2">
            <label className="flex flex-col gap-2 text-sm font-medium">
              Type
              <select
                className="rounded-lg border border-border px-3 py-2"
                value={type}
                onChange={(e) => setType(e.target.value)}
              >
                <option value="credit">credit</option>
                <option value="debit">debit</option>
              </select>
            </label>
            <label className="flex flex-col gap-2 text-sm font-medium">
              Amount
              <input
                className="rounded-lg border border-border px-3 py-2"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </label>
          </div>
          <label className="mt-4 flex flex-col gap-2 text-sm font-medium">
            Idempotency-Key (optional)
            <input
            className="rounded-lg border border-border px-3 py-2"
              value={idempotencyKey}
              onChange={(e) => setIdempotencyKey(e.target.value)}
            />
          </label>
          {error ? <div className="mt-3 text-sm text-red-600">{error}</div> : null}
          <button className="mt-5 rounded-lg bg-primary px-5 py-2 text-white" type="submit">
            Create transaction
          </button>
        </form>

        <div className="mt-6 rounded-2xl border border-border bg-surface p-6 shadow-sm">
          <div className="grid gap-4 md:grid-cols-[1fr_auto] md:items-end">
            <label className="flex flex-col gap-2 text-sm font-medium">
              Transaction ID
              <input
                className="rounded-lg border border-border px-3 py-2"
                placeholder="Select from list or paste"
                value={selectedId}
                onChange={(e) => setSelectedId(e.target.value)}
              />
            </label>
            <button className="rounded-lg bg-secondary px-5 py-2 text-white" onClick={handleAsyncProcess}>
              Async process
            </button>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-border bg-surface p-6 shadow-sm">
          <h2 className="text-lg font-semibold">Recent</h2>
          <ul className="mt-4 divide-y divide-border">
            {transactions.map((t) => (
              <li
                key={t.id}
                onClick={() => setSelectedId(t.id)}
                className="cursor-pointer py-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
                  <span className="font-mono text-xs text-gray-600">{t.id}</span>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${
                      t.status === "processed"
                        ? "bg-emerald-100 text-emerald-700"
                        : t.status === "failed"
                        ? "bg-rose-100 text-rose-700"
                        : t.status === "created"
                        ? "bg-gray-200 text-gray-700"
                        : "bg-amber-100 text-amber-700"
                    }`}
                  >
                    {t.status}
                  </span>
                </div>
                <div className="mt-2 flex items-center justify-between text-sm">
                  <span className="capitalize">{t.type}</span>
                  <span className="font-semibold">${t.amount}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="fixed right-4 top-4 z-50 flex w-80 flex-col gap-2">
        {/* Status toasts */}
        {notifications.slice(0, 5).map((note) => (
          <div
            key={note.id}
            className={`rounded-lg border px-4 py-3 text-sm shadow-sm ${
              note.status === "processed"
                ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                : note.status === "failed"
                ? "border-rose-200 bg-rose-50 text-rose-800"
                : note.status === "created"
                ? "border-gray-200 bg-gray-50 text-gray-800"
                : "border-amber-200 bg-amber-50 text-amber-800"
            }`}
          >
            {note.message}
          </div>
        ))}
      </div>
    </div>
  );
}
