import { createContext, useContext, useState, type ReactNode } from "react";
import type { Outcome } from "../types";

interface AppState {
  // Slider/toggle inputs — persisted across navigation
  sleep: number;
  setSleep: (v: number) => void;
  meetings: number;
  setMeetings: (v: number) => void;
  stress: number;
  setStress: (v: number) => void;
  weekends: boolean;
  setWeekends: (v: boolean) => void;
  // Last prediction result — shared so the tree page can highlight the path
  outcome: Outcome | null;
  setOutcome: (v: Outcome | null) => void;
  predictionPath: string[];
  setPredictionPath: (v: string[]) => void;
}

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [sleep, setSleep] = useState(7);
  const [meetings, setMeetings] = useState(5);
  const [stress, setStress] = useState(4);
  const [weekends, setWeekends] = useState(false);
  const [outcome, setOutcome] = useState<Outcome | null>(null);
  const [predictionPath, setPredictionPath] = useState<string[]>([]);

  return (
    <AppContext.Provider
      value={{
        sleep, setSleep,
        meetings, setMeetings,
        stress, setStress,
        weekends, setWeekends,
        outcome, setOutcome,
        predictionPath, setPredictionPath,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppState(): AppState {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppState must be used within AppProvider");
  return ctx;
}
