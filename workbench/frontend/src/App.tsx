import { FilesystemWorkbenchPage } from "./pages/FilesystemWorkbenchPage";
import { TaskRegistryProvider } from "./taskRegistry";

export function App() {
  return (
    <TaskRegistryProvider>
      <FilesystemWorkbenchPage />
    </TaskRegistryProvider>
  );
}
