import { useState } from "react";
import { Link } from "react-router-dom";
import { predict } from "../services/api";
import { useAppState } from "../context/AppContext";

const OUTCOME_CSS_CLASS = {
  Healthy: "outcome-Healthy",
  "Risk of burnout": "outcome-Risk",
  "Vacation required": "outcome-Vacation",
  "Critical condition": "outcome-Critical",
} as const;

function validateSleep(v: number): { error: string | null; warning: string | null } {
  if (!Number.isFinite(v)) return { error: "Please enter a valid number.", warning: null };
  if (v < 0) return { error: "Sleep hours must be bigger than 0", warning: null };
  if (v > 24) return { error: "Sleep hours can't exceed 24.", warning: null };
  if (v > 12) return { error: null, warning: "High value — most people sleep less than 12 h." };
  return { error: null, warning: null };
}

function validateMeetings(v: number): string | null {
  if (!Number.isFinite(v)) return "Please enter a valid number.";
  if (v < 0) return "Meetings can't be negative.";
  if (!Number.isInteger(v)) return "Meetings must be a whole number.";
  return null;
}

function validateStress(v: number): string | null {
  if (!Number.isFinite(v)) return "Please enter a valid number.";
  if (v < 1 || v > 10) return "Stress must be between 1 and 10.";
  return null;
}

export default function Dashboard() {
  const {
    sleep, setSleep,
    meetings, setMeetings,
    stress, setStress,
    weekends, setWeekends,
    outcome, setOutcome,
    setPredictionPath,
  } = useAppState();

  const [sleepRaw, setSleepRaw] = useState(Number.isFinite(sleep) ? String(sleep) : "");
  const [meetingsRaw, setMeetingsRaw] = useState(Number.isFinite(meetings) ? String(meetings) : "");
  const [stressRaw, setStressRaw] = useState(Number.isFinite(stress) ? String(stress) : "");

  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isStale, setIsStale] = useState(true);

  // Derived validation — runs on every render using the context numbers (kept in sync
  // with the raw strings via parseFloat in each onChange handler)
  const sleepValidation = validateSleep(sleep);
  const meetingsError = validateMeetings(meetings);
  const stressError = validateStress(stress);
  const hasError = !!(sleepValidation.error || meetingsError || stressError);

  // Called by every input onChange — clears old result, no API call
  function markStale() {
    setIsStale(true);
    setApiError(null);
  }

  // The only place predict() is ever called — explicit button click only
  async function handlePredictClick() {
    setLoading(true);
    setApiError(null);
    try {
      const res = await predict({ sleep, meetings, weekends: weekends ? "Yes" : "No", stress });
      setOutcome(res.outcome);
      setPredictionPath(res.path);
      setIsStale(false);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setApiError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="predict-page">
      <div className="card">
        <h2>Predict Your Burnout Risk</h2>

        {/* Sleep */}
        <div className="field">
          <div className="field-header">
            <label htmlFor="sleep">Sleep (hours/night)</label>
          </div>
          <input
            id="sleep"
            type="number"
            min={1}
            max={24}
            step={0.5}
            value={sleepRaw}
            onChange={(e) => {
              setSleepRaw(e.target.value);
              setSleep(parseFloat(e.target.value));
              markStale();
            }}
          />
          {sleepValidation.error && <p className="field-error">{sleepValidation.error}</p>}
          {!sleepValidation.error && sleepValidation.warning && (
            <p className="field-warning">{sleepValidation.warning}</p>
          )}
        </div>

        {/* Meetings */}
        <div className="field">
          <div className="field-header">
            <label htmlFor="meetings">Meetings per day</label>
          </div>
          <input
            id="meetings"
            type="number"
            min={0}
            step={1}
            value={meetingsRaw}
            onChange={(e) => {
              setMeetingsRaw(e.target.value);
              setMeetings(parseFloat(e.target.value));
              markStale();
            }}
          />
          {meetingsError && <p className="field-error">{meetingsError}</p>}
        </div>

        {/* Stress */}
        <div className="field">
          <div className="field-header">
            <label htmlFor="stress">Stress level (1–10)</label>
          </div>
          <input
            id="stress"
            type="number"
            min={1}
            max={10}
            step={0.5}
            value={stressRaw}
            onChange={(e) => {
              setStressRaw(e.target.value);
              setStress(parseFloat(e.target.value));
              markStale();
            }}
          />
          {stressError && <p className="field-error">{stressError}</p>}
        </div>

        {/* Weekends */}
        <div className="toggle-row">
          <label>Working weekends</label>
          <div className="weekends-group">
            <button
              type="button"
              className={`btn-seg${weekends ? " btn-seg-active" : ""}`}
              onClick={() => { setWeekends(true); markStale(); }}
            >
              Yes
            </button>
            <button
              type="button"
              className={`btn-seg${!weekends ? " btn-seg-active" : ""}`}
              onClick={() => { setWeekends(false); markStale(); }}
            >
              No
            </button>
          </div>
        </div>

        {/* Predict button */}
        <button
          className="btn btn-primary"
          style={{ width: "100%", marginTop: 4 }}
          onClick={handlePredictClick}
          disabled={loading || hasError}
        >
          {loading ? "Predicting…" : "Predict"}
        </button>

        {/* Result — directly below the button, same card */}
        <div className="result-area">
          {loading && <span className="loading-msg">Calculating…</span>}
          {!loading && apiError && <span className="error-msg">{apiError}</span>}
          {!loading && !apiError && isStale && (
            <p className="result-placeholder">Click Predict to see your result.</p>
          )}
          {!loading && !apiError && !isStale && outcome && (
            <div className="result-row">
              <span className={`outcome-badge ${OUTCOME_CSS_CLASS[outcome]}`}>
                {outcome}
              </span>
              <Link to="/tree" className="see-tree-link">
                Explore the full tree 
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
