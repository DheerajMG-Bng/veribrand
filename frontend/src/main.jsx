import React, {
  useEffect,
  useState,
  useRef,
  createContext,
  useContext,
} from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  Routes,
  Route,
  NavLink,
  Link,
  useNavigate,
  useParams,
} from "react-router-dom";
import {
  ShieldCheck,
  LayoutDashboard,
  BookOpen,
  ArrowUpRight,
  ArrowLeft,
  Plus,
  Check,
  ChevronRight,
  FileText,
  Sparkles,
  Clock,
  MessageSquare,
  History,
  GitBranch,
  AlertTriangle,
  CheckCircle2,
  X,
  ArrowRight,
  Play,
  Search,
  ExternalLink,
} from "lucide-react";
import "./styles.css";

const Context = createContext();
const statuses = {
  draft: "Draft",
  in_review: "Manager review",
  changes_requested: "Changes requested",
  pending_reviewer: "Reviewer sign-off",
  approved: "Approved",
};
const date = (s) =>
  s
    ? new Date(
        s.endsWith("Z") || /[+-]\d\d:\d\d$/.test(s) ? s : s + "Z",
      ).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })
    : "—";
const label = (s) => s?.replaceAll("_", " ");
function Badge({ status, children }) {
  return (
    <span className={`badge ${status || ""}`}>
      {children || statuses[status] || label(status)}
    </span>
  );
}
function Empty({ title, children }) {
  return (
    <div className="empty">
      <FileText size={30} />
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}
function Modal({ title, onClose, children }) {
  const ref = useRef();
  useEffect(() => {
    ref.current.showModal();
  }, []);
  return (
    <dialog
      ref={ref}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === ref.current) onClose();
      }}
    >
      <div className="modal-head">
        <h2>{title}</h2>
        <button
          className="icon-button"
          onClick={onClose}
          aria-label="Close dialog"
        >
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}

function App() {
  const [role, setRole] = useState(
    localStorage.getItem("veribrand-role") || "creator",
  );
  const [ai, setAi] = useState(null),
    [error, setError] = useState(""),
    [toast, setToast] = useState("");
  const [kb, setKb] = useState([]),
    [samples, setSamples] = useState([]);
  async function api(path, body, method) {
    const response = await fetch("/api" + path, {
      method: method || (body === undefined ? "GET" : "POST"),
      headers: { "Content-Type": "application/json", "X-Role": role },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    });
    const data = await response.json();
    if (!response.ok)
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : "The request could not be completed. Please try again.",
      );
    return data;
  }
  const refreshAi = () =>
    api("/ai/status")
      .then(setAi)
      .catch(() => setAi({ state: "unavailable" }));
  const refreshKb = () => api("/knowledge").then(setKb);
  useEffect(() => {
    refreshAi();
    refreshKb().catch((e) => setError(e.message));
    api("/samples")
      .then(setSamples)
      .catch((e) => setError(e.message));
    const id = setInterval(refreshAi, 30000);
    return () => clearInterval(id);
  }, []);
  useEffect(() => {
    localStorage.setItem("veribrand-role", role);
  }, [role]);
  useEffect(() => {
    if (toast) {
      const id = setTimeout(() => setToast(""), 5000);
      return () => clearTimeout(id);
    }
  }, [toast]);
  return (
    <Context.Provider
      value={{
        role,
        setRole,
        ai,
        api,
        kb,
        samples,
        setError,
        setToast,
        refreshAi,
        refreshKb,
      }}
    >
      <a className="skip" href="#main">
        Skip to content
      </a>
      <header className="header">
        <div className="header-inner">
          <Link className="brand" to="/" aria-label="VeriBrand home">
            <span className="brand-icon">
              <ShieldCheck size={24} />
            </span>
            Veri<span>Brand</span>
            <span className="demo-tag">DEMO</span>
          </Link>
          <nav aria-label="Main navigation">
            <NavLink to="/" end>
              <LayoutDashboard size={17} />
              Dashboard
            </NavLink>
            <NavLink to="/knowledge">
              <BookOpen size={17} />
              Knowledge Base
            </NavLink>
          </nav>
          <div className="header-right">
            <span className={`ai-chip ${ai?.state === "ok" ? "online" : ""}`}>
              <span />
              {ai?.state === "ok"
                ? "AI available"
                : ai?.state === "busy"
                  ? "AI busy"
                  : ai?.state === "exhausted"
                    ? "AI limit reached"
                    : "Rules available"}
            </span>
            <label className="role-label">
              Demo role
              <select
                aria-label="Demo role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              >
                {["creator", "manager", "reviewer", "admin"].map((r) => (
                  <option key={r} value={r}>
                    {r[0].toUpperCase() + r.slice(1)}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
      </header>
      {error && (
        <div className="global-error" role="alert">
          <AlertTriangle size={18} />
          <span>{error}</span>
          <button onClick={() => setError("")} aria-label="Dismiss error">
            <X size={18} />
          </button>
        </div>
      )}
      {toast && (
        <div className="toast" role="status">
          <CheckCircle2 size={18} />
          {toast}
        </div>
      )}
      <main id="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/contents/:id" element={<ContentPage />} />
          <Route path="/knowledge" element={<Knowledge />} />
          <Route
            path="*"
            element={
              <Empty title="Page not found">
                <Link to="/">Back to dashboard</Link>
              </Empty>
            }
          />
        </Routes>
      </main>
      <footer>
        <span className="footer-brand">
          <ShieldCheck size={16} /> VeriBrand <span>· Team 27</span>
        </span>
        <p>
          Fictional brand data · Simulated roles, no authentication · Do not
          enter confidential content.
          <br />
          With AI on, drafts are sent to Groq for analysis.
        </p>
        <span className="human-note">
          <CheckCircle2 size={15} /> AI proposes. Humans decide.
        </span>
      </footer>
    </Context.Provider>
  );
}

function Dashboard() {
  const { api, role, setRole, samples, setError, setToast } =
      useContext(Context),
    navigate = useNavigate();
  const [items, setItems] = useState(null),
    [showForm, setShowForm] = useState(false),
    [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ title: "", channel: "social", text: "" }),
    [filter, setFilter] = useState("all"),
    [search, setSearch] = useState("");
  const [guide, setGuide] = useState(
    localStorage.getItem("veribrand-guide") !== "dismissed",
  );
  const load = () =>
    api("/contents")
      .then(setItems)
      .catch((e) => setError(e.message));
  useEffect(() => {
    load();
  }, []);
  async function create(e) {
    e?.preventDefault();
    setSaving(true);
    try {
      const data = await api("/contents", form);
      navigate("/contents/" + data.id);
      setToast("Draft created. Run a review to get started.");
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }
  async function guided() {
    setRole("creator");
    setSaving(true);
    try {
      // This explicit header also covers a role switch in the same React event.
      const s = samples[0];
      if (!s) throw new Error("Samples are still loading. Please try again.");
      const response = await fetch("/api/contents", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Role": "creator" },
        body: JSON.stringify({
          title: "Guided demo · Launch campaign",
          channel: s.channel,
          text: s.text,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail);
      sessionStorage.setItem("veribrand-guided", String(data.id));
      navigate("/contents/" + data.id);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }
  const visible = (items || []).filter(
    (i) =>
      (filter === "all" || i.status === filter) &&
      i.title.toLowerCase().includes(search.toLowerCase()),
  );
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">YOUR BRAND. EVERY WORD.</div>
          <h1>Content workspace</h1>
          <p>From first draft to final sign-off, with confidence.</p>
        </div>
        <button
          className="primary"
          onClick={() => setShowForm(true)}
          disabled={role !== "creator"}
        >
          <Plus size={18} />
          New draft
        </button>
      </div>
      {guide && (
        <section className="guide-banner">
          <div className="guide-symbol">
            <Play size={22} />
          </div>
          <div>
            <div className="eyebrow">NEW TO VERIBRAND?</div>
            <h2>A good draft starts with a second look.</h2>
            <p>
              Start here: 1) Load sample draft #1, 2) Run review, 3) Fix
              findings, 4) Submit,
              <br className="desktop" /> 5) Switch role to Manager, then
              Reviewer for any retained high-risk claim.
            </p>
            <div className="guide-bottom">
              <button
                className="primary"
                onClick={guided}
                disabled={saving || !samples.length}
              >
                Try the guided demo <ArrowRight size={16} />
              </button>
              <span>About 3 minutes · No setup needed</span>
            </div>
          </div>
          <button
            className="icon-button dismiss"
            aria-label="Dismiss guide"
            onClick={() => {
              setGuide(false);
              localStorage.setItem("veribrand-guide", "dismissed");
            }}
          >
            <X size={18} />
          </button>
          <div className="guide-art" aria-hidden="true">
            <ShieldCheck size={86} />
            <span className="art-check">
              <Check size={18} />
            </span>
            <i />
            <b />
          </div>
        </section>
      )}
      <div className="stats">
        {[
          {
            title: "Total content",
            value: items?.length,
            icon: FileText,
            desc: "All drafts in your workspace",
          },
          {
            title: "Needs attention",
            value: items?.filter((i) =>
              ["draft", "changes_requested"].includes(i.status),
            ).length,
            icon: GitBranch,
            desc: "Ready for a creator’s next step",
          },
          {
            title: "Awaiting approval",
            value: items?.filter((i) =>
              ["in_review", "pending_reviewer"].includes(i.status),
            ).length,
            icon: Clock,
            desc: "With a manager or reviewer",
          },
          {
            title: "Approved",
            value: items?.filter((i) => i.status === "approved").length,
            icon: ShieldCheck,
            desc: "Signed off by a human",
          },
        ].map(({ title, value, icon: Icon, desc }) => (
          <div className="stat" key={title}>
            <div className="stat-title">
              {title}
              <Icon size={18} />
            </div>
            <strong>{value ?? "—"}</strong>
            <p>{desc}</p>
          </div>
        ))}
      </div>
      <section className="panel content-list">
        <div className="section-heading">
          <div>
            <h2>
              Your content <span className="count">{items?.length || 0}</span>
            </h2>
            <p>One place for every draft, decision, and approval.</p>
          </div>
          <label className="search">
            <Search size={16} />
            <input
              aria-label="Search content"
              placeholder="Search content…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
        </div>
        <div className="list-toolbar">
          <div className="filter-tabs" aria-label="Filter content">
            {[
              ["all", "All content"],
              ["draft", "Drafts"],
              ["in_review", "In review"],
              ["approved", "Approved"],
            ].map(([v, t]) => (
              <button
                key={v}
                className={filter === v ? "active" : ""}
                onClick={() => setFilter(v)}
              >
                {t}
              </button>
            ))}
          </div>
          <label className="sample-select">
            Load a sample
            <select
              aria-label="Load a sample"
              value=""
              disabled={role !== "creator"}
              onChange={(e) => {
                const s = samples.find((s) => s.id === Number(e.target.value));
                if (s) {
                  setForm({
                    title: `Sample ${s.id} · Brand review`,
                    channel: s.channel,
                    text: s.text,
                  });
                  setShowForm(true);
                }
              }}
            >
              <option value="">Choose a draft</option>
              {samples.map((s) => (
                <option key={s.id} value={s.id}>
                  #{s.id} ·{" "}
                  {s.id === 2
                    ? "Clean pack announcement"
                    : s.id === 11
                      ? "Unsupported endorsement"
                      : s.text.slice(0, 42) + "…"}
                </option>
              ))}
            </select>
          </label>
        </div>
        {items === null ? (
          <div className="empty" role="status">
            Loading workspace…
          </div>
        ) : visible.length === 0 ? (
          <Empty title="No drafts here yet">
            Create a draft or try a sample to see your review workflow.
          </Empty>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>CONTENT</th>
                  <th>CHANNEL</th>
                  <th>STATUS</th>
                  <th>LAST UPDATED</th>
                  <th>
                    <span className="sr-only">Open</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {visible.map((i) => (
                  <tr key={i.id}>
                    <td>
                      <Link className="content-title" to={"/contents/" + i.id}>
                        <span className="document-icon">
                          <FileText size={19} />
                        </span>
                        <span>
                          {i.title}
                          <small>
                            Acme Hydrate · #{String(i.id).padStart(3, "0")}
                          </small>
                        </span>
                      </Link>
                    </td>
                    <td>
                      <span className="channel">{i.channel}</span>
                    </td>
                    <td>
                      <Badge status={i.status} />
                    </td>
                    <td className="muted">{date(i.updated_at)}</td>
                    <td>
                      <Link
                        className="icon-button"
                        to={"/contents/" + i.id}
                        aria-label={"Open " + i.title}
                      >
                        <ArrowUpRight size={19} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="list-footer">
          <span>
            {visible.length} content {visible.length === 1 ? "item" : "items"}
          </span>
          <span>
            <ShieldCheck size={14} /> Every decision leaves a trail.
          </span>
        </div>
      </section>
      <div className="workspace-note">
        <BookOpen size={20} />
        <div>
          <strong>Grounded in your brand. Backed by sources.</strong>
          <p>
            Every verified finding links to your approved knowledge base.
            Unsupported claims stay with a human.
          </p>
        </div>
        <Link to="/knowledge">
          Explore knowledge base <ArrowUpRight size={16} />
        </Link>
      </div>
      {showForm && (
        <Modal title="Create a new draft" onClose={() => setShowForm(false)}>
          <form onSubmit={create}>
            <label>
              Draft title
              <input
                required
                maxLength={200}
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                placeholder="e.g. Classic range launch"
              />
            </label>
            <label>
              Channel
              <select
                value={form.channel}
                onChange={(e) => setForm({ ...form, channel: e.target.value })}
              >
                {["social", "influencer", "ad", "email"].map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </label>
            <label>
              Draft text
              <textarea
                required
                maxLength={5000}
                rows={8}
                value={form.text}
                onChange={(e) => setForm({ ...form, text: e.target.value })}
                placeholder="Write or paste the content you want to review…"
              />
            </label>
            <div className="form-help">
              {form.text.length.toLocaleString()} / 5,000 characters · Text only
            </div>
            <div className="modal-actions">
              <button type="button" onClick={() => setShowForm(false)}>
                Cancel
              </button>
              <button
                className="primary"
                disabled={saving || !form.text.trim()}
              >
                {saving ? "Creating…" : "Create draft"}
                <ArrowRight size={16} />
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

function ContentPage() {
  const { id } = useParams(),
    { api, role, setRole, kb, setError, setToast, refreshAi } =
      useContext(Context);
  const [data, setData] = useState(null),
    [audit, setAudit] = useState([]),
    [tab, setTab] = useState("Findings"),
    [useAi, setUseAi] = useState(true),
    [busy, setBusy] = useState(""),
    [result, setResult] = useState(null),
    [selected, setSelected] = useState(null),
    [dialog, setDialog] = useState(null),
    [input, setInput] = useState(""),
    [cite, setCite] = useState(null),
    [diff, setDiff] = useState(null),
    [from, setFrom] = useState(1),
    [to, setTo] = useState(1),
    [comment, setComment] = useState("");
  const guided = sessionStorage.getItem("veribrand-guided") === id;
  async function load() {
    const [d, a] = await Promise.all([
      api("/contents/" + id),
      api("/contents/" + id + "/audit"),
    ]);
    setData(d);
    setAudit(a);
    setTo(d.versions[0].version_no);
    setFrom(Math.max(1, d.versions[0].version_no - 1));
  }
  useEffect(() => {
    setData(null);
    setResult(null);
    load().catch((e) => setError(e.message));
  }, [id]);
  async function act(action, body = {}, message) {
    setBusy(action);
    try {
      let r = await api("/contents/" + id + "/" + action, body);
      if (action === "review") setResult(r);
      if (["apply", "versions"].includes(action)) setResult(null);
      await load();
      refreshAi();
      if (message) setToast(message);
      return true;
    } catch (e) {
      setError(e.message);
      return false;
    } finally {
      setBusy("");
    }
  }
  async function decide(f, decision, edited_text, reason) {
    setBusy("decision");
    try {
      await api("/findings/" + f.id + "/decision", {
        decision,
        edited_text,
        reason,
      });
      await load();
      setToast(
        "Decision saved. Your draft text stays unchanged until you apply fixes.",
      );
      return true;
    } catch (e) {
      setError(e.message);
      return false;
    } finally {
      setBusy("");
    }
  }
  function openDialog(type, f) {
    setDialog({ type, f });
    setInput(
      type === "editFinding"
        ? (f.edited_text ?? f.replacement ?? f.quote)
        : type === "version"
          ? data.versions[0].text
          : "",
    );
  }
  async function dialogSubmit(e) {
    e.preventDefault();
    let ok = false;
    if (dialog.type === "editFinding")
      ok = await decide(dialog.f, "edited", input);
    if (dialog.type === "reject")
      ok = await decide(dialog.f, "rejected", undefined, input);
    if (dialog.type === "return")
      ok = await act(
        "return",
        { comment: input },
        "Returned to the creator with your comment.",
      );
    if (dialog.type === "signoff")
      ok = await act(
        "reviewer-signoff",
        { reason: input },
        "Reviewer sign-off recorded. Content approved.",
      );
    if (dialog.type === "version")
      ok = await act(
        "versions",
        { text: input },
        "New version created. Review it before submitting.",
      );
    if (ok) setDialog(null);
  }
  if (!data)
    return (
      <div className="page">
        <div className="empty" role="status">
          Loading draft…
        </div>
      </div>
    );
  const v = data.versions[0],
    findings = data.findings,
    editable = ["draft", "changes_requested"].includes(data.status),
    creator = role === "creator" && editable;
  const fixes = findings.filter((f) =>
    ["accepted", "edited"].includes(f.decision),
  ).length;
  const pendingHigh = findings.filter(
    (f) => f.severity === "high" && f.decision === "pending",
  ).length;
  const latestReview = [...audit]
    .reverse()
    .find(
      (a) =>
        a.action === "review_completed" && a.detail.version === v.version_no,
    );
  let cursor = 0;
  const parts = [];
  const draftSlice = (start, end) =>
    Array.from(v.text).slice(start, end).join("");
  for (const f of findings) {
    parts.push(draftSlice(cursor, f.start));
    parts.push(
      <button
        key={f.id}
        className={`text-highlight ${f.severity} ${selected === f.id ? "selected" : ""}`}
        aria-label={`Finding: ${f.quote}, ${f.severity} severity`}
        onClick={() => {
          setTab("Findings");
          setSelected(f.id);
          setTimeout(
            () =>
              document
                .getElementById("finding-" + f.id)
                ?.scrollIntoView({ behavior: "smooth", block: "center" }),
            50,
          );
        }}
      >
        {draftSlice(f.start, f.end)}
      </button>,
    );
    cursor = f.end;
  }
  parts.push(draftSlice(cursor));
  const stages = ["Draft", "Review", "Manager", "Reviewer", "Approved"];
  const stage =
    data.status === "approved"
      ? 4
      : data.status === "pending_reviewer"
        ? 3
        : data.status === "in_review"
          ? 2
          : v.reviewed_at
            ? 1
            : 0;
  return (
    <div className="page">
      <Link className="back-link" to="/">
        <ArrowLeft size={16} />
        Workspace
      </Link>
      <div className="page-heading detail-heading">
        <div>
          <div className="eyebrow">
            ACME HYDRATE · {data.channel.toUpperCase()} · CONTENT #{id}
          </div>
          <h1>{data.title}</h1>
          <p>
            Version {v.version_no} · Updated {date(data.updated_at)}
          </p>
        </div>
        <Badge status={data.status} />
      </div>
      <ol className="stepper" aria-label="Approval progress">
        {stages.map((s, i) => (
          <li className={stage >= i ? "complete" : ""} key={s}>
            <span>{stage > i ? <Check size={14} /> : i + 1}</span>
            {s}
            {i < 4 && <i />}
          </li>
        ))}
      </ol>
      {guided && (
        <div className="inline-guide">
          <Play size={18} />
          <div>
            <strong>Your guided demo</strong>
            <p>
              {data.status === "approved"
                ? "Complete! Open the audit trail to see every decision."
                : data.status === "pending_reviewer"
                  ? "Switch to Reviewer and sign off with a reason, or return the content."
                  : data.status === "in_review"
                    ? "Switch to Manager to approve or return this draft. Retained medical claims route to Reviewer."
                    : !v.reviewed_at
                      ? "Run review to check this version against Acme Hydrate’s approved knowledge."
                      : "Accept a suggestion, edit a phrase, or reject with a reason. Apply accepted/edited fixes, then re-check. You can also edit the whole draft. Retained high-risk claims require Reviewer sign-off."}
            </p>
          </div>
          {data.status === "in_review" && role !== "manager" && (
            <button onClick={() => setRole("manager")}>
              Switch to Manager
            </button>
          )}
          {data.status === "pending_reviewer" && role !== "reviewer" && (
            <button onClick={() => setRole("reviewer")}>
              Switch to Reviewer
            </button>
          )}
        </div>
      )}
      {data.status === "changes_requested" && (
        <div className="notice warning">
          <MessageSquare size={18} />
          <span>
            Changes requested. Read the comments, create a new version, and
            review it before resubmitting.
          </span>
        </div>
      )}
      <div className="detail-grid">
        <div>
          <section className="panel draft-panel">
            <div className="section-heading">
              <h2>
                <FileText size={18} />
                Draft preview
              </h2>
              <span className="muted small">
                v{v.version_no} · {v.text.length} characters
              </span>
            </div>
            <div className="draft-text">{parts}</div>
            <div className="draft-bottom">
              <span>
                {v.reviewed_at ? (
                  <>
                    <CheckCircle2 size={15} /> Reviewed {date(v.reviewed_at)}
                  </>
                ) : (
                  <>
                    <Clock size={15} /> This version has not been reviewed
                  </>
                )}
              </span>
              {creator && (
                <button onClick={() => openDialog("version")}>
                  Edit draft
                  <GitBranch size={15} />
                </button>
              )}
            </div>
          </section>
          <section className="panel workflow-panel">
            <h2>Next step</h2>
            {creator ? (
              <>
                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={useAi}
                    onChange={(e) => setUseAi(e.target.checked)}
                    disabled={!!busy}
                  />
                  <span>Use AI analysis</span>
                  <span className="muted small">Draft sent to Groq</span>
                </label>
                <div className="action-stack">
                  <button
                    className="primary"
                    disabled={
                      !!busy || findings.some((f) => f.decision !== "pending")
                    }
                    onClick={() => act("review", { use_ai: useAi })}
                  >
                    <Sparkles size={17} />
                    {busy === "review"
                      ? "Reviewing your draft…"
                      : v.reviewed_at
                        ? "Re-check this version"
                        : "Run review"}
                  </button>
                  {fixes > 0 && (
                    <button
                      disabled={!!busy}
                      onClick={() =>
                        act(
                          "apply",
                          {},
                          "Decisions applied to a new version. Re-check before submitting.",
                        )
                      }
                    >
                      <GitBranch size={17} />
                      Apply {fixes} {fixes === 1 ? "fix" : "fixes"} → new
                      version
                    </button>
                  )}
                  <button
                    disabled={
                      !!busy || !v.reviewed_at || pendingHigh > 0 || fixes > 0
                    }
                    onClick={() =>
                      act(
                        "submit",
                        {},
                        "Submitted for manager review. Switch your demo role to Manager.",
                      )
                    }
                  >
                    <ArrowUpRight size={17} />
                    Submit for approval
                  </button>
                </div>
                <p className="small muted">
                  {pendingHigh
                    ? `${pendingHigh} high-severity findings need a decision.`
                    : fixes
                      ? "Apply your fixes, then review the new version."
                      : !v.reviewed_at
                        ? "Run a review before submitting."
                        : "Ready to submit. Pending low/medium findings remain visible to approvers."}
                </p>
                {findings.some((f) => f.decision !== "pending") &&
                  fixes === 0 && (
                    <p className="small muted">
                      Decisions saved. To change the draft, use Edit draft to
                      create a new version.
                    </p>
                  )}
              </>
            ) : (
              <>
                <p className="muted">
                  {data.status === "approved"
                    ? "This content has been approved."
                    : "Current stage: " + statuses[data.status] + "."}
                </p>
                {role === "manager" && data.status === "in_review" && (
                  <button
                    className="primary"
                    disabled={!!busy}
                    onClick={() =>
                      act(
                        "approve",
                        {},
                        "Manager approval recorded. Check the next workflow stage.",
                      )
                    }
                  >
                    <ShieldCheck size={17} />
                    Approve as Manager
                  </button>
                )}
                {role === "reviewer" && data.status === "pending_reviewer" && (
                  <button
                    className="primary"
                    onClick={() => openDialog("signoff")}
                    disabled={!!busy}
                  >
                    <ShieldCheck size={17} />
                    Reviewer sign-off
                  </button>
                )}
                {((role === "manager" &&
                  ["in_review", "approved"].includes(data.status)) ||
                  (role === "reviewer" &&
                    ["pending_reviewer", "approved"].includes(
                      data.status,
                    ))) && (
                  <button
                    className="return-button"
                    disabled={!!busy}
                    onClick={() => openDialog("return")}
                  >
                    Return with a comment
                  </button>
                )}
                {editable && role !== "creator" && (
                  <p className="small">
                    Switch to <strong>Creator</strong> to edit and review this
                    draft.
                  </p>
                )}
                {data.status === "in_review" && role !== "manager" && (
                  <p className="small">
                    Switch to <strong>Manager</strong> for the next approval.
                  </p>
                )}
                {data.status === "pending_reviewer" && role !== "reviewer" && (
                  <p className="small">
                    Switch to <strong>Reviewer</strong> for the required
                    sign-off.
                  </p>
                )}
              </>
            )}
          </section>
          <div className="human-card">
            <ShieldCheck size={21} />
            <div>
              <strong>You're in control.</strong>
              <p>
                Suggestions never change your draft automatically. Human
                decisions and approvals are recorded.
              </p>
            </div>
          </div>
        </div>
        <section className="panel review-panel">
          <div
            className="detail-tabs"
            role="tablist"
            aria-label="Content details"
          >
            {[
              ["Findings", Sparkles],
              ["Versions and diff", GitBranch],
              ["Comments", MessageSquare],
              ["Audit trail", History],
            ].map(([t, Icon]) => (
              <button
                role="tab"
                aria-selected={tab === t}
                key={t}
                className={tab === t ? "active" : ""}
                onClick={() => setTab(t)}
              >
                <Icon size={15} />
                {t}
                {t === "Findings" && (
                  <span className="count">{findings.length}</span>
                )}
              </button>
            ))}
          </div>
          <div className="tab-content" role="tabpanel" aria-label={tab}>
            {tab === "Findings" && (
              <>
                {busy === "review" && (
                  <div className="review-progress" role="status">
                    <span className="spinner" />
                    <div>
                      <strong>
                        Checking rules and grounding AI suggestions…
                      </strong>
                      <p>
                        Model fallback can take a little longer. You can
                        continue with rules if AI is unavailable.
                      </p>
                    </div>
                  </div>
                )}
                {(result || latestReview) && (
                  <div
                    className={`notice ${(result?.ai_status || latestReview?.detail.ai_status) === "ok" ? "success" : ""}`}
                  >
                    <Sparkles size={17} />
                    <div>
                      {result?.note ||
                        (latestReview.detail.ai_status === "ok"
                          ? "AI suggestions checked against the knowledge base."
                          : "Rule-based review completed.")}
                      <small>
                        {(result?.model_used || latestReview?.detail.model) &&
                          `Model: ${result?.model_used || latestReview?.detail.model}`}
                        {result?.precomputed_at
                          ? ` · Precomputed with ${result.model_used} on ${date(result.precomputed_at)}`
                          : result?.cached || latestReview?.detail.cached
                            ? " · Cached result"
                            : ""}
                      </small>
                    </div>
                  </div>
                )}
                {!v.reviewed_at ? (
                  <Empty title="Ready for a second look">
                    Run a review to find guideline, terminology, and claim
                    issues, with citations to the knowledge base.
                  </Empty>
                ) : findings.length === 0 ? (
                  <div className="clean-state">
                    <div>
                      <ShieldCheck size={34} />
                    </div>
                    <h2>Looking good.</h2>
                    <p>
                      No findings in this review. A human still makes the final
                      call.
                    </p>
                    <Badge status="approved">Ready for approval</Badge>
                  </div>
                ) : (
                  <>
                    <div className="findings-summary">
                      <h2>
                        {findings.length}{" "}
                        {findings.length === 1 ? "finding" : "findings"} to
                        consider
                      </h2>
                      <span>
                        {
                          findings.filter((f) => f.decision !== "pending")
                            .length
                        }{" "}
                        decided
                      </span>
                    </div>
                    {findings.map((f) => (
                      <article
                        id={"finding-" + f.id}
                        key={f.id}
                        className={`finding ${f.severity} ${selected === f.id ? "selected" : ""}`}
                      >
                        <div className="finding-top">
                          <Badge status={f.severity}>
                            {f.severity[0].toUpperCase() + f.severity.slice(1)}{" "}
                            severity
                          </Badge>
                          <span className="origin">
                            {f.origin === "rule"
                              ? "Rule-based"
                              : "AI-suggested"}{" "}
                            · {Math.round(f.confidence * 100)}% confidence
                          </span>
                          {f.decision !== "pending" && (
                            <Badge status={f.decision}>
                              {label(f.decision)}
                            </Badge>
                          )}
                        </div>
                        <button
                          className="quote"
                          onClick={() => setSelected(f.id)}
                        >
                          “{f.quote}”
                        </button>
                        <p className="finding-reason">{f.reason}</p>
                        <div className="citations">
                          {[f.source_code, ...f.also_cites]
                            .filter(Boolean)
                            .map((c) => (
                              <button
                                key={c}
                                onClick={() =>
                                  setCite(
                                    kb.find((k) => k.code === c) || {
                                      code: c,
                                      title: "Historical citation",
                                      text: "This item has since been removed from the active knowledge base.",
                                    },
                                  )
                                }
                              >
                                <BookOpen size={12} />
                                {c}
                                <ExternalLink size={11} />
                              </button>
                            ))}
                          <span
                            className={
                              f.verification === "unverified"
                                ? "unverified"
                                : "verified"
                            }
                          >
                            {f.verification === "unverified" ? (
                              <AlertTriangle size={13} />
                            ) : (
                              <ShieldCheck size={13} />
                            )}{" "}
                            {f.verification === "unverified"
                              ? "Unverified, needs a human"
                              : "Verified citation"}
                          </span>
                          {f.requires_reviewer && (
                            <span className="reviewer-required">
                              Reviewer sign-off required if retained
                            </span>
                          )}
                        </div>
                        {f.replacement !== null ? (
                          <div className="replacement">
                            <span>{f.replacement_hint?.startsWith('AI-suggested') ? 'AI-SUGGESTED WORDING' : 'SUGGESTED WORDING'}</span>
                            <p>
                              {f.replacement === "" ? (
                                <em>Remove this phrase</em>
                              ) : (
                                f.replacement
                              )}
                            </p>
                          </div>
                        ) : (
                          <p className="replacement-hint">
                            {f.replacement_hint ||
                              "No safe automatic replacement. Edit this phrase or reject with a reason."}
                          </p>
                        )}
                        {f.decision === "edited" && (
                          <div className="replacement">
                            <span>YOUR EDIT</span>
                            <p>
                              {f.edited_text || <em>Remove this phrase</em>}
                            </p>
                          </div>
                        )}
                        {f.decision_reason && (
                          <p className="decision-reason">
                            Override reason: {f.decision_reason}
                          </p>
                        )}
                        {creator && (
                          <div className="finding-actions">
                            <button
                              disabled={
                                !!busy ||
                                f.replacement === null ||
                                f.verification === "unverified"
                              }
                              onClick={() => decide(f, "accepted")}
                            >
                              <Check size={14} />
                              Accept
                            </button>
                            <button
                              disabled={!!busy}
                              onClick={() => openDialog("editFinding", f)}
                            >
                              Edit
                            </button>
                            <button
                              disabled={!!busy}
                              onClick={() => openDialog("reject", f)}
                            >
                              Reject with reason
                            </button>
                          </div>
                        )}
                      </article>
                    ))}
                  </>
                )}
              </>
            )}
            {tab === "Versions and diff" && (
              <>
                <div className="versions-list">
                  {data.versions.map((ver) => (
                    <div className="version-row" key={ver.id}>
                      <GitBranch size={17} />
                      <div>
                        <strong>Version {ver.version_no}</strong>
                        <small>
                          {label(ver.source)} · {ver.created_by_role} ·{" "}
                          {date(ver.created_at)}
                        </small>
                      </div>
                      {ver.reviewed_at && (
                        <Badge status="approved">Reviewed</Badge>
                      )}
                    </div>
                  ))}
                </div>
                <h3>Compare versions</h3>
                <form
                  className="diff-controls"
                  onSubmit={async (e) => {
                    e.preventDefault();
                    try {
                      setDiff(
                        await api(`/contents/${id}/diff?from=${from}&to=${to}`),
                      );
                    } catch (e) {
                      setError(e.message);
                    }
                  }}
                >
                  <label>
                    From
                    <select
                      value={from}
                      onChange={(e) => setFrom(Number(e.target.value))}
                    >
                      {data.versions.map((v) => (
                        <option key={v.id} value={v.version_no}>
                          Version {v.version_no}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    To
                    <select
                      value={to}
                      onChange={(e) => setTo(Number(e.target.value))}
                    >
                      {data.versions.map((v) => (
                        <option key={v.id} value={v.version_no}>
                          Version {v.version_no}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button>Compare</button>
                </form>
                {diff && (
                  <div className="diff-result">
                    <h4>Before · Version {diff.from}</h4>
                    <pre>{diff.before}</pre>
                    <h4>After · Version {diff.to}</h4>
                    <pre>{diff.after}</pre>
                  </div>
                )}
              </>
            )}
            {tab === "Comments" && (
              <>
                {data.comments.length === 0 && (
                  <Empty title="Keep the conversation here">
                    Questions, return notes, and context stay attached to this
                    draft.
                  </Empty>
                )}
                {data.comments.map((c) => (
                  <div className="comment" key={c.id}>
                    <div>
                      <strong>{c.role}</strong>
                      <time>{date(c.created_at)}</time>
                    </div>
                    <p>{c.text}</p>
                  </div>
                ))}
                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    if (
                      await act("comments", { text: comment }, "Comment added.")
                    )
                      setComment("");
                  }}
                >
                  <label>
                    Add a comment
                    <textarea
                      required
                      maxLength={2000}
                      rows={3}
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                    />
                  </label>
                  <button
                    className="primary"
                    disabled={!!busy || !comment.trim()}
                  >
                    Post comment
                  </button>
                </form>
              </>
            )}
            {tab === "Audit trail" && (
              <>
                <div className="section-intro">
                  <h2>Every action, accounted for.</h2>
                  <p>
                    The trail records demo roles, decisions, and when AI was
                    involved.
                  </p>
                </div>
                <ol className="audit-list">
                  {[...audit].reverse().map((a) => (
                    <li key={a.id}>
                      <span className="audit-dot" />
                      <div>
                        <div className="audit-title">
                          <strong>{label(a.action)}</strong>
                          {a.ai_involved && (
                            <Badge status="ai">AI involved</Badge>
                          )}
                        </div>
                        <small>
                          {a.role} · {date(a.created_at)}
                        </small>
                        <pre>{JSON.stringify(a.detail, null, 2)}</pre>
                      </div>
                    </li>
                  ))}
                </ol>
              </>
            )}
          </div>
        </section>
      </div>
      {dialog && (
        <Modal
          title={
            {
              editFinding: "Edit this phrase",
              reject: "Reject finding with a reason",
              return: "Return to creator",
              signoff: "Authorised Reviewer sign-off",
              version: "Create a new draft version",
            }[dialog.type]
          }
          onClose={() => setDialog(null)}
        >
          <form onSubmit={dialogSubmit}>
            {dialog.f && <blockquote>{dialog.f.quote}</blockquote>}
            {dialog.type === "signoff" && (
              <p className="notice warning">
                Retained high-risk wording remains in the draft. Record your
                review decision and reasoning.
              </p>
            )}
            <label>
              {["editFinding", "version"].includes(dialog.type)
                ? "Replacement text"
                : "Reason"}
              <textarea
                rows={dialog.type === "version" ? 9 : 4}
                maxLength={
                  ["editFinding", "version"].includes(dialog.type) ? 5000 : 2000
                }
                required={dialog.type !== "editFinding"}
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />
            </label>
            {dialog.type === "editFinding" && (
              <p className="small muted">
                Leave blank to remove the phrase. Your edit is applied only when
                you choose Apply fixes; the new version must be reviewed.
              </p>
            )}
            <div className="modal-actions">
              <button type="button" onClick={() => setDialog(null)}>
                Cancel
              </button>
              <button
                className="primary"
                disabled={
                  !!busy || (dialog.type !== "editFinding" && !input.trim())
                }
              >
                {busy ? "Saving…" : "Save decision"}
              </button>
            </div>
          </form>
        </Modal>
      )}
      {cite && (
        <Modal
          title={`${cite.code} · ${cite.title}`}
          onClose={() => setCite(null)}
        >
          <Badge status="draft">{label(cite.kind)}</Badge>
          <p className="citation-text">{cite.text}</p>
          {cite.valid_until && <p>Valid until: {cite.valid_until}</p>}
          <p className="small muted">
            Source: organisation-approved knowledge base · Fictional Acme
            Hydrate
          </p>
        </Modal>
      )}
    </div>
  );
}

function Knowledge() {
  const { kb, api, role, refreshKb, setError, setToast } = useContext(Context),
    [search, setSearch] = useState(""),
    [editing, setEditing] = useState(null),
    [form, setForm] = useState({}),
    [busy, setBusy] = useState(false),
    [deleting, setDeleting] = useState(null),
    [resetting, setResetting] = useState(false);
  function edit(item) {
    setEditing(item || {});
    setForm(
      item
        ? {
            ...item,
            meta: JSON.stringify(item.meta, null, 2),
            valid_until: item.valid_until || "",
          }
        : {
            code: "",
            kind: "guideline",
            title: "",
            text: "",
            meta: "{}",
            valid_until: "",
          },
    );
  }
  async function save(e) {
    e.preventDefault();
    setBusy(true);
    try {
      const body = {
        ...form,
        meta: JSON.parse(form.meta),
        valid_until: form.valid_until || null,
      };
      delete body.id;
      await api(
        "/knowledge" + (editing.id ? "/" + editing.id : ""),
        body,
        editing.id ? "PUT" : "POST",
      );
      await refreshKb();
      setEditing(null);
      setToast("Knowledge base saved. Future reviews use the updated rules.");
    } catch (e) {
      setError(
        e instanceof SyntaxError ? "Metadata must be valid JSON." : e.message,
      );
    } finally {
      setBusy(false);
    }
  }
  const filtered = kb.filter((k) =>
    (k.code + " " + k.title + " " + k.text)
      .toLowerCase()
      .includes(search.toLowerCase()),
  );
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">THE SOURCE OF TRUTH</div>
          <h1>Brand knowledge base</h1>
          <p>
            Approved guidelines, facts, and claims. Every finding starts here.
          </p>
        </div>
        {role === "admin" && (
          <button className="primary" onClick={() => edit()}>
            <Plus size={17} />
            Add knowledge
          </button>
        )}
      </div>
      <div className="kb-intro">
        <BookOpen size={24} />
        <div>
          <strong>Acme Hydrate</strong>
          <p>{kb.length} approved knowledge items · Fictional demo brand</p>
        </div>
        <label className="search">
          <Search size={16} />
          <input
            placeholder="Search knowledge…"
            aria-label="Search knowledge"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </label>
      </div>
      {[
        ["guideline", "Brand guidelines", "How we sound and show up."],
        ["term", "Terminology", "The right words for our brand."],
        ["fact", "Approved facts", "What we can confidently say."],
        ["claim_rule", "Claims register", "The boundaries that protect trust."],
      ].map(([kind, title, desc]) => (
        <section className="kb-group" key={kind}>
          <div className="kb-section-heading">
            <h2>
              {title}
              <span className="count">
                {filtered.filter((k) => k.kind === kind).length}
              </span>
            </h2>
            <p>{desc}</p>
          </div>
          <div className="kb-grid">
            {filtered
              .filter((k) => k.kind === kind)
              .map((k) => (
                <article className="panel kb-item" key={k.id}>
                  <div>
                    <span className="kb-code">{k.code}</span>
                    {k.valid_until && (
                      <span
                        className={`small ${k.valid_until < new Date().toISOString().slice(0, 10) ? "expired" : "muted"}`}
                      >
                        {k.valid_until < new Date().toISOString().slice(0, 10)
                          ? "Expired"
                          : "Valid until"}{" "}
                        {k.valid_until}
                      </span>
                    )}
                  </div>
                  <h3>{k.title}</h3>
                  <p>{k.text}</p>
                  <div className="kb-item-footer">
                    <span>
                      {k.meta.check
                        ? "Deterministic check"
                        : "AI judgement / reference"}
                      {k.meta.requires_reviewer ? " · Reviewer required" : ""}
                    </span>
                    {role === "admin" && (
                      <div>
                        <button onClick={() => edit(k)}>Edit</button>
                        <button onClick={() => setDeleting(k)}>Delete</button>
                      </div>
                    )}
                  </div>
                </article>
              ))}
          </div>
        </section>
      ))}
      {role === "admin" && (
        <div className="admin-tools">
          <h3>Demo tools</h3>
          <p>
            Reset shared demo contents and restore the original knowledge base.
            AI usage counters are preserved.
          </p>
          <button onClick={() => setResetting(true)}>Reset demo data</button>
        </div>
      )}
      {editing && (
        <Modal
          title={editing.id ? "Edit knowledge item" : "Add knowledge item"}
          onClose={() => setEditing(null)}
        >
          <form onSubmit={save}>
            <div className="form-columns">
              <label>
                Code
                <input
                  required
                  pattern="[A-Z]-[0-9]{2,3}"
                  value={form.code}
                  onChange={(e) => setForm({ ...form, code: e.target.value })}
                />
              </label>
              <label>
                Kind
                <select
                  value={form.kind}
                  onChange={(e) => setForm({ ...form, kind: e.target.value })}
                >
                  {["guideline", "term", "fact", "claim_rule"].map((k) => (
                    <option key={k} value={k}>
                      {label(k)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <label>
              Title
              <input
                required
                maxLength={200}
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
            </label>
            <label>
              Approved text
              <textarea
                required
                maxLength={2000}
                rows={3}
                value={form.text}
                onChange={(e) => setForm({ ...form, text: e.target.value })}
              />
            </label>
            <label>
              Valid until (optional)
              <input
                type="date"
                value={form.valid_until}
                onChange={(e) =>
                  setForm({ ...form, valid_until: e.target.value })
                }
              />
            </label>
            <label>
              Rule metadata (JSON)
              <textarea
                className="code-input"
                rows={6}
                value={form.meta}
                onChange={(e) => setForm({ ...form, meta: e.target.value })}
              />
            </label>
            <div className="modal-actions">
              <button type="button" onClick={() => setEditing(null)}>
                Cancel
              </button>
              <button className="primary" disabled={busy}>
                {busy ? "Saving…" : "Save knowledge"}
              </button>
            </div>
          </form>
        </Modal>
      )}
      {(deleting || resetting) && (
        <Modal
          title={
            deleting
              ? "Delete " + deleting.code + "?"
              : "Reset shared demo data?"
          }
          onClose={() => {
            setDeleting(null);
            setResetting(false);
          }}
        >
          <p>
            {deleting
              ? "Future reviews will no longer use this knowledge item. Existing findings retain historical citations."
              : "This removes all content, findings, comments and audit history and creates three seeded demo drafts."}
          </p>
          <div className="modal-actions">
            <button
              onClick={() => {
                setDeleting(null);
                setResetting(false);
              }}
            >
              Cancel
            </button>
            <button
              className="danger"
              disabled={busy}
              onClick={async () => {
                setBusy(true);
                try {
                  await api(
                    deleting ? "/knowledge/" + deleting.id : "/demo/reset",
                    {},
                    deleting ? "DELETE" : "POST",
                  );
                  await refreshKb();
                  setToast(
                    deleting ? "Knowledge item deleted." : "Demo data reset.",
                  );
                  setDeleting(null);
                  setResetting(false);
                } catch (e) {
                  setError(e.message);
                } finally {
                  setBusy(false);
                }
              }}
            >
              {busy ? "Working…" : deleting ? "Delete item" : "Reset demo"}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
);
