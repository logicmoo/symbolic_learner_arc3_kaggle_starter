import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

// A workbench-wide task registry: any page's long-running action registers
// itself via startBusy(label) when it starts and stopBusy(id) when it stops,
// instead of each page keeping its own private "busy" boolean. Rendered
// persistently near the breadcrumb trail (see TaskStatusBar) so switching
// views mid-task (e.g. navigating away from Play while an import runs)
// doesn't hide that something is still running, or lose the report of what
// it did and how long it took once it finishes. A task that never calls
// stopBusy stays visibly stuck with a live elapsed time -- the signal that
// something is wrong.

export type BusyTask = { id: string; label: string; startedAt: number };
export type FinishedTask = BusyTask & {
  endedAt: number;
  status: "done" | "error";
  detail?: string;
};

type TaskRegistry = {
  activeTasks: BusyTask[];
  taskLog: FinishedTask[];
  startBusy: (label: string) => string;
  stopBusy: (id: string, status: "done" | "error", detail?: string) => void;
  perform: (work: () => Promise<string | void>, label?: string) => Promise<string | void>;
};

const TaskRegistryContext = createContext<TaskRegistry | null>(null);

export function TaskRegistryProvider({ children }: { children: ReactNode }) {
  const [activeTasks, setActiveTasks] = useState<BusyTask[]>([]);
  const [taskLog, setTaskLog] = useState<FinishedTask[]>([]);

  const startBusy = useCallback((label: string): string => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    setActiveTasks((current) => [...current, { id, label, startedAt: Date.now() }]);
    return id;
  }, []);

  const stopBusy = useCallback((id: string, status: "done" | "error", detail?: string) => {
    setActiveTasks((current) => {
      const task = current.find((entry) => entry.id === id);
      if (task) {
        setTaskLog((log) => [{ ...task, endedAt: Date.now(), status, detail }, ...log].slice(0, 8));
      }
      return current.filter((entry) => entry.id !== id);
    });
  }, []);

  const perform = useCallback(
    async (work: () => Promise<string | void>, label?: string): Promise<string | void> => {
      const taskId = startBusy(label || "action");
      try {
        const detail = await work();
        stopBusy(taskId, "done", typeof detail === "string" ? detail : undefined);
        return detail;
      } catch (reason) {
        const message = reason instanceof Error ? reason.message : String(reason);
        stopBusy(taskId, "error", message);
        throw reason;
      }
    },
    [startBusy, stopBusy],
  );

  return (
    <TaskRegistryContext.Provider value={{ activeTasks, taskLog, startBusy, stopBusy, perform }}>
      {children}
    </TaskRegistryContext.Provider>
  );
}

export function useTaskRegistry(): TaskRegistry {
  const context = useContext(TaskRegistryContext);
  if (!context) {
    throw new Error("useTaskRegistry must be used within a TaskRegistryProvider");
  }
  return context;
}

export function formatElapsed(ms: number): string {
  const clamped = Math.max(0, ms);
  if (clamped < 1000) return `${Math.round(clamped)}ms`;
  const totalSeconds = Math.round(clamped / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
}

/** Persistent, workbench-wide status strip -- render once near the
 * breadcrumb trail. Shows every currently active task (with a live-ticking
 * elapsed time) and, once nothing is running, the most recently finished
 * task's outcome (what it did, how long it ran, and whether it errored). */
export function TaskStatusBar() {
  const { activeTasks, taskLog } = useTaskRegistry();
  const [nowTick, setNowTick] = useState(() => Date.now());

  useEffect(() => {
    if (!activeTasks.length) return;
    const timer = window.setInterval(() => setNowTick(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [activeTasks.length]);

  const lastFinished = taskLog[0];
  if (!activeTasks.length && !lastFinished) return null;

  return (
    <div className="workbench-task-status" aria-live="polite">
      {activeTasks.map((task) => (
        <div
          key={task.id}
          className="workbench-task-active"
          title={`started ${new Date(task.startedAt).toLocaleTimeString()}`}
        >
          Working: {task.label} ({formatElapsed(nowTick - task.startedAt)})
        </div>
      ))}
      {!activeTasks.length && lastFinished && (
        <div className={`workbench-task-done ${lastFinished.status === "error" ? "failed" : ""}`}>
          {lastFinished.label} — {lastFinished.status === "error" ? "stopped (error)" : "finished"} at{" "}
          {new Date(lastFinished.endedAt).toLocaleTimeString()} (ran for{" "}
          {formatElapsed(lastFinished.endedAt - lastFinished.startedAt)})
          {lastFinished.detail ? ` — ${lastFinished.detail}` : ""}
        </div>
      )}
    </div>
  );
}
