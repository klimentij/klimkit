const stateUrl = "./api/state";
const uiVersionUrl = "./api/ui-version";
const streamUrl = "./api/stream";
const archiveUrl = "./api/workspaces/archive";
const archiveBatchUrl = "./api/workspaces/archive-batch";
const acknowledgeUrl = "./api/workspaces/acknowledge";
const localWorkspaceBootstrapUrl = "./api/local-workspaces/bootstrap";

const tabStrip = document.querySelector("#tab-strip");
const frameDeck = document.querySelector("#frame-deck");
const tabTemplate = document.querySelector("#tab-template");
const panelTemplate = document.querySelector("#panel-template");
const separatorTemplate = document.querySelector("#separator-template");

const catalogToggle = document.querySelector("#catalog-toggle");
const catalogCount = document.querySelector("#catalog-count");
const drawer = document.querySelector("#workspace-drawer");
const drawerTitle = document.querySelector("#drawer-title");
const drawerEyebrow = document.querySelector("#drawer-eyebrow");
const drawerClose = document.querySelector("#drawer-close");
const catalogView = document.querySelector("#catalog-view");
const catalogSearch = document.querySelector("#catalog-search");
const catalogMachineFilter = document.querySelector("#catalog-machine-filter");
const catalogStatusFilter = document.querySelector("#catalog-status-filter");
const catalogShowArchived = document.querySelector("#catalog-show-archived");
const catalogBatchBar = document.querySelector("#catalog-batch-bar");
const catalogSelectionCount = document.querySelector("#catalog-selection-count");
const catalogSelectVisible = document.querySelector("#catalog-select-visible");
const catalogClearSelection = document.querySelector("#catalog-clear-selection");
const catalogArchiveSelected = document.querySelector("#catalog-archive-selected");
const catalogUnarchiveSelected = document.querySelector("#catalog-unarchive-selected");
const catalogSelectAll = document.querySelector("#catalog-select-all");
const catalogBody = document.querySelector("#catalog-body");
const catalogTableShell = document.querySelector(".catalog-table-shell");
const newWorkspaceForm = document.querySelector("#new-workspace-form");
const newWorkspaceMachine = document.querySelector("#new-workspace-machine");
const newWorkspaceFolder = document.querySelector("#new-workspace-folder");
const newWorkspaceHint = document.querySelector("#new-workspace-hint");
const newWorkspaceFolderOptions = document.querySelector("#new-workspace-folder-options");

const LOCAL_WORKSPACES_KEY = "switchboard-local-workspaces";
const LOCAL_WORKSPACE_SEQUENCE_KEY = "switchboard-local-workspace-sequence";
const CATALOG_FILTERS_KEY = "switchboard-catalog-filters";
const TAB_RENDER_BATCH = 20;
const MAX_LOADED_FRAMES = 3;
const POLL_INTERVAL_MS = 10000;
const UI_VERSION_POLL_INTERVAL_MS = 3000;
const FOLDER_SUGGESTION_LIMIT = 10;
const HOT_FRAME_STATES = new Set(["new", "starting", "planning", "working", "needs_input", "awaiting_approval"]);
const CODEX_LAUNCH_FLAGS = "-c check_for_update_on_startup=false --dangerously-bypass-approvals-and-sandbox";
const APP_INSTANCE_KEY = "__switchboardAppInstance";
const APP_GENERATION_KEY = "__switchboardAppGeneration";
const APP_POLL_TIMER_KEY = "__switchboardPollTimer";
const APP_POLL_SEQUENCE_KEY = "__switchboardPollSequence";
const APP_STREAM_KEY = "__switchboard2EventSource";
const APP_UI_VERSION_TIMER_KEY = "__switchboard2UiVersionTimer";

const ui = {
  activeId: loadJson("switchboard-active-id", null),
  serverWorkspaces: [],
  localWorkspaces: sanitizeLocalWorkspaces(loadJson(LOCAL_WORKSPACES_KEY, [])),
  machines: [],
  workspaces: [],
  orderedWorkspaceIds: [],
  items: new Map(),
  panels: new Map(),
  loadedFrames: new Set(),
  hintMode: false,
  notificationMemory: loadJson("switchboard-notification-memory", {}),
  acknowledgedEvents: loadJson("switchboard-acknowledged-events", {}),
  notificationPrompted: false,
  archiveRequests: new Set(),
  archiveSeparator: null,
  drawerOpen: false,
  visibleTabCount: TAB_RENDER_BATCH,
  catalogFilters: {
    search: "",
    machine: "",
    status: "",
    showArchived: false,
    ...loadJson(CATALOG_FILTERS_KEY, {}),
  },
  selectedWorkspaceIds: new Set(),
};

let pollTimer = null;
let refreshPromise = null;
let appGeneration = 0;
let stream = null;
let uiVersionPollTimer = null;
let currentUiVersion = "";
const folderPicker = {
  activeIndex: -1,
  items: [],
  open: false,
};

function loadJson(key, fallback) {
  try {
    return JSON.parse(window.localStorage.getItem(key) || JSON.stringify(fallback));
  } catch {
    return fallback;
  }
}

function saveJson(key, value) {
  window.localStorage.setItem(key, JSON.stringify(value));
}

function saveActiveId(id) {
  ui.activeId = id;
  saveJson("switchboard-active-id", id);
}

function saveLocalWorkspaces() {
  saveJson(LOCAL_WORKSPACES_KEY, ui.localWorkspaces);
}

function saveCatalogFilters() {
  saveJson(CATALOG_FILTERS_KEY, ui.catalogFilters);
}

function restoreTabStripScroll() {
  const saved = Number.parseInt(window.localStorage.getItem("switchboard-tab-strip-scroll-left") || "0", 10);
  if (!Number.isFinite(saved) || saved <= 0) {
    return;
  }
  tabStrip.scrollLeft = saved;
}

function sanitizeLocalWorkspaces(entries) {
  if (!Array.isArray(entries)) {
    return [];
  }
  return entries
    .filter((entry) => entry && typeof entry === "object")
    .map((entry) => {
      const machine = String(entry.machine || "").trim();
      const cwd = String(entry.cwd || "").trim();
      const machineDns = String(entry.machine_dns || "").trim();
      const title = String(entry.title || entry.folder_name || "").trim();
      const folderName = String(entry.folder_name || folderNameFromPath(cwd) || "workspace").trim();
      const createdAt = String(entry.created_at || isoNow()).trim();
      return {
        id: String(entry.id || legacyLocalWorkspaceId(machine, cwd)).trim(),
        session_id: "",
        machine,
        machine_dns: machineDns,
        cwd,
        folder_name: folderName,
        code_server_url: String(entry.code_server_url || buildWorkspaceCodeServerUrl(machineDns, cwd)).trim(),
        same_origin_helper_url: "",
        title: title || folderName,
        latest_user_message: "",
        branch: String(entry.branch || "workspace").trim(),
        detail: String(entry.detail || "Ad hoc workspace tab opened from Switchboard.").trim(),
        activity_state: "idle",
        local_status: "new",
        archived: false,
        archived_at: "",
        created_at: createdAt,
        updated_at: String(entry.updated_at || createdAt).trim(),
        latest_event_id: "",
        latest_event_status: "",
        latest_event_message: "",
        latest_event_created_at: "",
        is_local: true,
      };
    })
    .filter((entry) => entry.id && entry.machine && entry.cwd && entry.code_server_url);
}

function isoNow() {
  return new Date().toISOString();
}

function folderNameFromPath(cwd) {
  const normalized = String(cwd || "").replace(/\/+$/, "");
  if (!normalized) {
    return "";
  }
  const parts = normalized.split("/");
  return parts[parts.length - 1] || normalized;
}

function normalizePath(path) {
  return String(path || "").trim().replace(/\/+$/, "") || "/";
}

function isAbsolutePath(path) {
  return String(path || "").startsWith("/");
}

function machineFolderKey(machine, cwd) {
  return `${String(machine || "").trim().toLowerCase()}::${normalizePath(cwd)}`;
}

function legacyLocalWorkspaceId(machine, cwd) {
  return `local:${machineFolderKey(machine, cwd)}`;
}

function nextLocalWorkspaceSequence() {
  const current = Number.parseInt(window.localStorage.getItem(LOCAL_WORKSPACE_SEQUENCE_KEY) || "0", 10);
  const next = Number.isFinite(current) && current > 0 ? current + 1 : 1;
  window.localStorage.setItem(LOCAL_WORKSPACE_SEQUENCE_KEY, String(next));
  return next;
}

function createLocalWorkspaceId(machine, cwd) {
  return `local:${nextLocalWorkspaceSequence()}:${machineFolderKey(machine, cwd)}`;
}

function buildCodeServerUrl(machineDns, cwd) {
  if (!machineDns || !cwd) {
    return "";
  }
  const url = new URL(`https://${machineDns}/`);
  url.searchParams.set("folder", cwd);
  return url.toString();
}

function isLoopbackHostname(hostname) {
  const host = String(hostname || "").toLowerCase();
  return host === "localhost" || host === "::1" || host === "[::1]" || host.startsWith("127.");
}

function buildLocalCodeServerUrl(cwd) {
  if (!cwd) {
    return "";
  }
  const hostname = window.location.hostname || "127.0.0.1";
  const escapedHost = hostname.includes(":") && !hostname.startsWith("[") ? `[${hostname}]` : hostname;
  const localPort = isLoopbackHostname(hostname) ? ":8080" : "";
  const protocol = isLoopbackHostname(hostname) ? "http:" : window.location.protocol || "https:";
  const url = new URL(`${protocol}//${escapedHost}${localPort}/`);
  url.searchParams.set("folder", cwd);
  return url.toString();
}

function buildWorkspaceCodeServerUrl(machineDns, cwd) {
  return buildCodeServerUrl(machineDns, cwd) || buildLocalCodeServerUrl(cwd);
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\"'\"'`)}'`;
}

function codexResumeCommand(workspace) {
  const sessionId = String(workspace?.session_id || "").trim();
  return sessionId
    ? `codex ${CODEX_LAUNCH_FLAGS} resume ${shellQuote(sessionId)}`
    : "";
}

function codexLaunchCommand(workspace) {
  const cwd = String(workspace?.cwd || "").trim();
  return cwd
    ? `codex ${CODEX_LAUNCH_FLAGS} -C ${shellQuote(cwd)}`
    : `codex ${CODEX_LAUNCH_FLAGS}`;
}

function codexCommand(workspace) {
  return codexResumeCommand(workspace) || codexLaunchCommand(workspace);
}

async function bootstrapLocalWorkspace(workspace) {
  if (!workspace?.is_local || !workspace.cwd) {
    return;
  }
  try {
    const response = await fetch(localWorkspaceBootstrapUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cwd: workspace.cwd,
      }),
    });
    if (!response.ok) {
      throw new Error(`bootstrap failed with HTTP ${response.status}`);
    }
  } catch (error) {
    console.warn("Failed to prepare local code-server workspace", error);
  }
}

async function copyTextToClipboard(text) {
  const copyValue = String(text || "");
  if (!copyValue) {
    return false;
  }
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(copyValue);
      return true;
    } catch {
      // Fall through to DOM-based copy for browsers that block async clipboard writes.
    }
  }
  const textarea = document.createElement("textarea");
  textarea.value = copyValue;
  textarea.setAttribute("readonly", "readonly");
  textarea.style.position = "fixed";
  textarea.style.top = "-9999px";
  textarea.style.left = "-9999px";
  document.body.append(textarea);
  textarea.select();
  textarea.setSelectionRange(0, textarea.value.length);
  let copied = false;
  try {
    copied = document.execCommand("copy");
  } catch {
    copied = false;
  }
  textarea.remove();
  return copied;
}

function getWorkspaceById(id) {
  return ui.workspaces.find((workspace) => workspace.id === id) || null;
}

function workspaceSessionGroupKey(workspace) {
  const sessionId = String(workspace?.session_id || "").trim();
  if (sessionId) {
    return `session:${sessionId}`;
  }
  return `folder:${machineFolderKey(workspace?.machine, workspace?.cwd)}`;
}

function workspacesMatchNotificationTarget(candidate, source) {
  if (!candidate || !source) {
    return false;
  }
  if (workspaceSessionGroupKey(candidate) === workspaceSessionGroupKey(source)) {
    return true;
  }
  return machineFolderKey(candidate.machine, candidate.cwd) === machineFolderKey(source.machine, source.cwd);
}

function compareNotificationTargets(left, right, source) {
  if (Boolean(left.archived) !== Boolean(right.archived)) {
    return left.archived ? 1 : -1;
  }
  const sourceEventId = String(source?.latest_event_id || "").trim();
  const leftMatchesEvent = sourceEventId && String(left.latest_event_id || "").trim() === sourceEventId;
  const rightMatchesEvent = sourceEventId && String(right.latest_event_id || "").trim() === sourceEventId;
  if (leftMatchesEvent !== rightMatchesEvent) {
    return leftMatchesEvent ? -1 : 1;
  }
  const leftActive = left.id === ui.activeId;
  const rightActive = right.id === ui.activeId;
  if (leftActive !== rightActive) {
    return leftActive ? -1 : 1;
  }
  const leftStamp = workspaceSortStamp(left);
  const rightStamp = workspaceSortStamp(right);
  if (leftStamp !== rightStamp) {
    return rightStamp.localeCompare(leftStamp);
  }
  if (Boolean(left.is_local) !== Boolean(right.is_local)) {
    return left.is_local ? 1 : -1;
  }
  return String(left.id).localeCompare(String(right.id));
}

function resolveNotificationTargetWorkspace(source) {
  const candidates = ui.workspaces
    .filter((workspace) => workspacesMatchNotificationTarget(workspace, source))
    .sort((left, right) => compareNotificationTargets(left, right, source));
  return candidates[0] || source;
}

async function fetchState() {
  const response = await fetch(stateUrl, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch switchboard state: ${response.status}`);
  }
  return response.json();
}

async function fetchUiVersion() {
  const response = await fetch(uiVersionUrl, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch UI version: ${response.status}`);
  }
  const payload = await response.json();
  return String(payload.version || "").trim();
}

async function setArchiveState(sessionId, archived) {
  const response = await fetch(archiveUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ session_id: sessionId, archived }),
  });
  if (!response.ok) {
    throw new Error(`Failed to update archive state: ${response.status}`);
  }
  return response.json();
}

async function setArchiveStates(sessionIds, archived) {
  const response = await fetch(archiveBatchUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ session_ids: sessionIds, archived }),
  });
  if (!response.ok) {
    throw new Error(`Failed to update archive state: ${response.status}`);
  }
  return response.json();
}

async function acknowledgeWorkspace(sessionId, eventId) {
  const response = await fetch(acknowledgeUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ session_id: sessionId, event_id: eventId }),
  });
  if (!response.ok) {
    throw new Error(`Failed to acknowledge workspace state: ${response.status}`);
  }
  return response.json();
}

function sortWorkspaces(workspaces) {
  return [...workspaces].sort((left, right) => {
    if (Boolean(left.archived) !== Boolean(right.archived)) {
      return left.archived ? 1 : -1;
    }
    const leftStamp = workspaceCreatedSortStamp(left);
    const rightStamp = workspaceCreatedSortStamp(right);
    if (leftStamp !== rightStamp) {
      return rightStamp.localeCompare(leftStamp);
    }
    return String(left.id).localeCompare(String(right.id));
  });
}

function workspaceSortStamp(workspace) {
  return String(
    workspace.latest_event_created_at ||
      workspace.updated_at ||
      workspace.created_at ||
      workspace.reported_at ||
      "",
  );
}

function workspaceCreatedSortStamp(workspace) {
  return String(
    workspace.created_at ||
      workspace.reported_at ||
      workspace.updated_at ||
      workspace.latest_event_created_at ||
      "",
  );
}

function findServerWorkspaceForLocal(localWorkspace, serverWorkspaces, claimedServerIds) {
  const localCreatedAt = String(localWorkspace?.created_at || "").trim();
  const localKey = machineFolderKey(localWorkspace?.machine, localWorkspace?.cwd);
  return serverWorkspaces
    .filter((workspace) => {
      if (!workspace || claimedServerIds.has(workspace.id) || workspace.archived) {
        return false;
      }
      if (machineFolderKey(workspace.machine, workspace.cwd) !== localKey) {
        return false;
      }
      const serverStamp = workspaceSortStamp(workspace);
      return Boolean(serverStamp) && (!localCreatedAt || serverStamp >= localCreatedAt);
    })
    .sort((left, right) => workspaceSortStamp(left).localeCompare(workspaceSortStamp(right)))[0] || null;
}

function reconcileLocalWorkspaces(serverWorkspaces) {
  const claimedServerIds = new Set();
  const adoptedWorkspaceIds = new Map();
  const nextLocalWorkspaces = [];

  for (const localWorkspace of ui.localWorkspaces) {
    const adoptedServerWorkspace = findServerWorkspaceForLocal(localWorkspace, serverWorkspaces, claimedServerIds);
    if (!adoptedServerWorkspace) {
      nextLocalWorkspaces.push(localWorkspace);
      continue;
    }
    claimedServerIds.add(adoptedServerWorkspace.id);
    adoptedWorkspaceIds.set(localWorkspace.id, adoptedServerWorkspace.id);
  }

  if (nextLocalWorkspaces.length !== ui.localWorkspaces.length) {
    ui.localWorkspaces = nextLocalWorkspaces;
    saveLocalWorkspaces();
  }

  const adoptedActiveId = adoptedWorkspaceIds.get(ui.activeId);
  if (adoptedActiveId) {
    saveActiveId(adoptedActiveId);
  }
}

function buildMachineList(machineRows, workspaces) {
  const machineMap = new Map();
  for (const row of Array.isArray(machineRows) ? machineRows : []) {
    if (!row || typeof row !== "object") {
      continue;
    }
    const machine = String(row.machine || "").trim();
    if (!machine) {
      continue;
    }
    machineMap.set(machine, {
      machine,
      machine_dns: String(row.machine_dns || "").trim(),
      reported_at: String(row.reported_at || "").trim(),
      session_count: Number.parseInt(String(row.session_count || 0), 10) || 0,
      online: Boolean(row.online),
    });
  }
  for (const workspace of workspaces) {
    if (!machineMap.has(workspace.machine)) {
      machineMap.set(workspace.machine, {
        machine: workspace.machine,
        machine_dns: String(workspace.machine_dns || "").trim(),
        reported_at: String(workspace.updated_at || "").trim(),
        session_count: 0,
        online: Boolean(workspace.machine_dns),
      });
    }
  }
  return [...machineMap.values()]
    .filter((machine) => machine.machine)
    .sort((left, right) => left.machine.localeCompare(right.machine));
}

function syncLocalWorkspaces() {
  ui.localWorkspaces = sanitizeLocalWorkspaces(ui.localWorkspaces);
  saveLocalWorkspaces();
}

function materializeState(payload) {
  ui.serverWorkspaces = sortWorkspaces(Array.isArray(payload.workspaces) ? payload.workspaces : []);
  syncLocalWorkspaces();
  reconcileLocalWorkspaces(ui.serverWorkspaces);
  ui.workspaces = sortWorkspaces([...ui.localWorkspaces, ...ui.serverWorkspaces]);
  ui.machines = buildMachineList(payload.machines, [...ui.serverWorkspaces, ...ui.localWorkspaces]);
  ui.visibleTabCount = ui.workspaces.length
    ? Math.min(Math.max(ui.visibleTabCount, TAB_RENDER_BATCH), ui.workspaces.length)
    : TAB_RENDER_BATCH;
  ui.selectedWorkspaceIds = new Set(
    [...ui.selectedWorkspaceIds].filter((workspaceId) => ui.serverWorkspaces.some((workspace) => workspace.id === workspaceId)),
  );
}

function ensureSeparator() {
  if (ui.archiveSeparator) {
    return ui.archiveSeparator;
  }
  const fragment = separatorTemplate.content.cloneNode(true);
  ui.archiveSeparator = fragment.querySelector(".workspace-separator");
  return ui.archiveSeparator;
}

function ensureTabVisibleById(id) {
  if (!id) {
    return;
  }
  const index = ui.workspaces.findIndex((workspace) => workspace.id === id);
  if (index === -1 || index < ui.visibleTabCount) {
    return;
  }
  ui.visibleTabCount = Math.min(
    Math.ceil((index + 1) / TAB_RENDER_BATCH) * TAB_RENDER_BATCH,
    ui.workspaces.length,
  );
}

function visibleTabWorkspaces(workspaces) {
  ensureTabVisibleById(ui.activeId);
  return workspaces.filter((workspace, index) => index < ui.visibleTabCount);
}

function revealMoreTabs() {
  if (ui.visibleTabCount >= ui.workspaces.length) {
    return;
  }
  const previousScroll = tabStrip.scrollLeft;
  ui.visibleTabCount = Math.min(ui.visibleTabCount + TAB_RENDER_BATCH, ui.workspaces.length);
  renderShell(ui.workspaces);
  tabStrip.scrollLeft = previousScroll;
}

function maybeLoadMoreTabs() {
  if (ui.visibleTabCount >= ui.workspaces.length) {
    return;
  }
  const remaining = tabStrip.scrollWidth - (tabStrip.scrollLeft + tabStrip.clientWidth);
  if (remaining < 240) {
    revealMoreTabs();
  }
}

function ensurePanel(workspace) {
  if (!workspace || ui.panels.has(workspace.id)) {
    return;
  }
  const panelFragment = panelTemplate.content.cloneNode(true);
  const panel = panelFragment.querySelector(".frame-panel");
  panel.dataset.workspaceId = workspace.id;
  panel.setAttribute("aria-hidden", "true");
  const overlayLink = panel.querySelector(".frame-card-link");
  overlayLink.addEventListener("click", () => activate(workspace.id, { acknowledge: true }));
  const iframe = panel.querySelector(".workspace-frame");
  iframe.addEventListener("load", () => {
    panel.classList.add("is-ready");
  });
  frameDeck.append(panelFragment);
  const insertedPanel = frameDeck.lastElementChild;
  ui.panels.set(workspace.id, insertedPanel);
  syncPanel(workspace);
}

function syncPanel(workspace) {
  const panel = workspace ? ui.panels.get(workspace.id) : null;
  if (!workspace || !panel) {
    return;
  }
  panel.querySelector(".frame-card-title").textContent = workspace.title;
  panel.querySelector(".frame-card-copy").textContent =
    workspace.detail || "Open the workspace directly if you want full browser focus.";
  panel.querySelector(".frame-card-link").href = workspace.code_server_url;
}

function ensureStructures(allWorkspaces, tabWorkspaces) {
  const nextTabIds = new Set(tabWorkspaces.map((workspace) => workspace.id));
  const nextWorkspaceIds = new Set(allWorkspaces.map((workspace) => workspace.id));

  for (const [id, item] of ui.items.entries()) {
    if (nextTabIds.has(id)) {
      continue;
    }
    item.shell.remove();
    ui.items.delete(id);
  }

  for (const [id, panel] of ui.panels.entries()) {
    if (nextWorkspaceIds.has(id)) {
      continue;
    }
    panel.remove();
    ui.panels.delete(id);
    ui.loadedFrames.delete(id);
  }

  for (const workspace of tabWorkspaces) {
    if (!ui.items.has(workspace.id)) {
      const tabFragment = tabTemplate.content.cloneNode(true);
      const shell = tabFragment.querySelector(".workspace-tab-item");
      const tab = shell.querySelector(".workspace-tab");
      const copyButton = shell.querySelector(".workspace-tab-copy");
      const actionButton = shell.querySelector(".workspace-tab-archive");
      shell.dataset.workspaceId = workspace.id;
      tab.dataset.workspaceId = workspace.id;
      tab.addEventListener("click", () => activate(workspace.id, { acknowledge: true }));
      copyButton.addEventListener("click", async (event) => {
        event.preventDefault();
        event.stopPropagation();
        const current = getWorkspaceById(workspace.id);
        if (!current) {
          return;
        }
        const command = codexCommand(current);
        if (!command) {
          return;
        }
        const copied = await copyTextToClipboard(command);
        const previousLabel = copyButton.textContent;
        const previousTitle = copyButton.title;
        copyButton.textContent = copied ? "OK" : "!!";
        copyButton.title = copied ? "Copied Codex command" : "Copy failed";
        copyButton.classList.toggle("is-copied", copied);
        window.setTimeout(() => {
          copyButton.textContent = previousLabel;
          copyButton.title = previousTitle;
          copyButton.classList.remove("is-copied");
        }, 1100);
      });
      actionButton.addEventListener("click", async (event) => {
        event.preventDefault();
        event.stopPropagation();
        const current = getWorkspaceById(workspace.id);
        if (!current) {
          return;
        }
        if (current.is_local) {
          closeLocalWorkspace(workspace.id);
          return;
        }
        await toggleArchive(workspace.id);
      });
      tabStrip.append(tabFragment);
      ui.items.set(workspace.id, { shell, tab, copyButton, actionButton });
    }
  }
}

function reorderTabStrip(workspaces, allWorkspaces) {
  const desiredShellOrder = [
    ...workspaces.filter((workspace) => !workspace.archived).map((workspace) => workspace.id),
    ...(workspaces.some((workspace) => workspace.archived) ? ["__archive_separator__"] : []),
    ...workspaces.filter((workspace) => workspace.archived).map((workspace) => workspace.id),
    ...(allWorkspaces.length > workspaces.length ? [`__more__:${allWorkspaces.length - workspaces.length}`] : []),
  ];
  const currentShellOrder = [
    ...tabStrip.querySelectorAll(".workspace-tab-item, .workspace-separator, .workspace-more"),
  ].map((element) => {
    if (element.classList.contains("workspace-separator")) {
      return "__archive_separator__";
    }
    if (element.classList.contains("workspace-more")) {
      return `__more__:${Math.max(allWorkspaces.length - workspaces.length, 0)}`;
    }
    return element.dataset.workspaceId || "";
  });
  if (desiredShellOrder.join("|") === currentShellOrder.join("|")) {
    ui.orderedWorkspaceIds = allWorkspaces.map((workspace) => workspace.id);
    return;
  }

  for (const existingMoreButton of tabStrip.querySelectorAll(".workspace-more")) {
    existingMoreButton.remove();
  }
  const active = [];
  const archived = [];

  for (const workspace of workspaces) {
    const item = ui.items.get(workspace.id);
    if (!item) {
      continue;
    }
    if (workspace.archived) {
      archived.push(item.shell);
    } else {
      active.push(item.shell);
    }
  }

  const fragment = document.createDocumentFragment();
  for (const shell of active) {
    fragment.append(shell);
  }
  if (archived.length) {
    const separator = ensureSeparator();
    separator.querySelector(".workspace-separator-count").textContent = String(archived.length);
    fragment.append(separator);
    for (const shell of archived) {
      fragment.append(shell);
    }
  } else if (ui.archiveSeparator) {
    ui.archiveSeparator.remove();
  }
  const hiddenCount = Math.max(allWorkspaces.length - workspaces.length, 0);
  if (hiddenCount > 0) {
    const moreButton = document.createElement("button");
    moreButton.type = "button";
    moreButton.className = "workspace-more";
    moreButton.textContent = `+${hiddenCount} more`;
    moreButton.addEventListener("click", () => revealMoreTabs());
    fragment.append(moreButton);
  }
  tabStrip.append(fragment);
  ui.orderedWorkspaceIds = allWorkspaces.map((workspace) => workspace.id);
}

function hasPendingEvent(workspace) {
  if (workspace.is_local) {
    return false;
  }
  return Boolean(workspace.needs_attention);
}

function deriveDisplayStatus(workspace) {
  if (workspace.local_status === "new") {
    return "new";
  }
  return String(workspace.display_state || workspace.activity_state || "idle");
}

function isRecentTimestamp(value, maxAgeMs) {
  if (!value) {
    return false;
  }
  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return false;
  }
  return Date.now() - timestamp.getTime() <= maxAgeMs;
}

function buildWorkspaceTooltip(workspace, displayStatus) {
  return [
    workspace.folder_name || folderNameFromPath(workspace.cwd),
    workspace.machine,
    formatStatusText(displayStatus),
    workspace.latest_user_message,
    workspace.is_local ? "workspace tab" : "agent session",
    workspace.archived ? "archived" : "active",
  ]
    .filter(Boolean)
    .join(" · ");
}

function buildTabHeading(workspace, displayStatus) {
  const folder = workspace.folder_name || folderNameFromPath(workspace.cwd) || "workspace";
  const machine = String(workspace.machine || "").trim();
  const status = formatStateLabel(displayStatus);
  if (machine) {
    return `${folder} @ ${machine} · ${status}`;
  }
  return `${folder} · ${status}`;
}

function buildTabSubtitle(workspace) {
  return String(workspace.latest_user_message || "").trim();
}

function formatStateLabel(state) {
  switch (state) {
    case "awaiting_approval":
      return "apr";
    case "planning":
      return "pln";
    case "working":
      return "wrk";
    case "needs_input":
      return "ask";
    case "done":
      return "fin";
    case "seen":
      return "see";
    case "stale":
      return "stl";
    case "errored":
      return "err";
    case "starting":
      return "str";
    case "idle":
      return "idl";
    case "new":
      return "new";
    default:
      return "std";
  }
}

function formatStatusText(state) {
  switch (state) {
    case "awaiting_approval":
      return "Awaiting approval";
    case "planning":
      return "Planning";
    case "working":
      return "Working";
    case "needs_input":
      return "Needs input";
    case "done":
      return "Done";
    case "seen":
      return "Seen";
    case "stale":
      return "Stale";
    case "errored":
      return "Errored";
    case "starting":
      return "Starting";
    case "idle":
      return "Idle";
    case "new":
      return "New";
    default:
      return "Unknown";
  }
}

function buildWindowTitle(workspace) {
  if (!workspace) {
    return "Klimkit";
  }
  const folder = workspace.folder_name || folderNameFromPath(workspace.cwd) || workspace.title || "workspace";
  const machine = String(workspace.machine || "").trim();
  const status = formatStatusText(deriveDisplayStatus(workspace));
  const parts = [machine ? `${folder} @ ${machine}` : folder];
  parts.push(status);
  if (workspace.archived) {
    parts.push("Archived");
  }
  return `${parts.join(" · ")} | Klimkit`;
}

function syncDocumentTitle() {
  const activeWorkspace = getWorkspaceById(ui.activeId) || ui.workspaces[0] || null;
  document.title = buildWindowTitle(activeWorkspace);
}

function formatTimestamp(value) {
  if (!value) {
    return "—";
  }
  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return value;
  }
  const now = new Date();
  const sameDay = timestamp.toDateString() === now.toDateString();
  return sameDay
    ? timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : timestamp.toLocaleDateString([], { month: "short", day: "numeric" });
}

function renderShell(workspaces) {
  const tabWorkspaces = visibleTabWorkspaces(workspaces);
  ensureStructures(workspaces, tabWorkspaces);

  if (workspaces.length && (!ui.activeId || !workspaces.some((workspace) => workspace.id === ui.activeId))) {
    saveActiveId(workspaces[0]?.id || null);
  }

  workspaces.forEach((workspace, index) => {
    const item = ui.items.get(workspace.id);
    if (!item) {
      return;
    }

    const displayStatus = deriveDisplayStatus(workspace);
    const isPending = hasPendingEvent(workspace);
    item.tab.querySelector(".workspace-tab-title").textContent = buildTabHeading(workspace, displayStatus);
    item.tab.querySelector(".workspace-tab-subtitle").textContent = buildTabSubtitle(workspace);
    item.tab.querySelector(".workspace-tab-status").textContent = formatStateLabel(displayStatus);
    item.tab.querySelector(".workspace-tab-number").textContent = String(index + 1);
    item.shell.classList.toggle("is-starting", displayStatus === "starting");
    item.shell.classList.toggle("is-planning", displayStatus === "planning");
    item.shell.classList.toggle("is-working", displayStatus === "working");
    item.shell.classList.toggle("is-awaiting_approval", displayStatus === "awaiting_approval");
    item.shell.classList.toggle("is-done", displayStatus === "done");
    item.shell.classList.toggle("is-seen", displayStatus === "seen");
    item.shell.classList.toggle("is-needs_input", displayStatus === "needs_input");
    item.shell.classList.toggle("is-stale", displayStatus === "stale");
    item.shell.classList.toggle("is-errored", displayStatus === "errored");
    item.shell.classList.toggle("is-new", displayStatus === "new");
    item.shell.classList.toggle("is-archived", Boolean(workspace.archived));
    item.shell.classList.toggle("has-pending", isPending);
    item.tab.classList.toggle("show-hints", ui.hintMode);
    item.tab.setAttribute("title", buildWorkspaceTooltip(workspace, displayStatus));
    item.tab.querySelector(".workspace-tab-pending").hidden = !isPending;

    const actionLabel = workspace.is_local ? "Close" : workspace.archived ? "Unarchive" : "Archive";
    item.actionButton.textContent = actionLabel;
    item.actionButton.setAttribute("aria-label", `${actionLabel} ${workspace.title}`);
    item.actionButton.disabled = !workspace.is_local && ui.archiveRequests.has(workspace.id);
    const command = codexCommand(workspace);
    item.copyButton.disabled = !command;
    item.copyButton.setAttribute("aria-label", `Copy Codex command for ${workspace.title}`);
    item.copyButton.title = command || "No Codex command is available for this workspace";

    syncPanel(workspace);
  });

  reorderTabStrip(tabWorkspaces, workspaces);
  if (ui.activeId) {
    activate(ui.activeId, { preserveScroll: true, acknowledge: false, focusTab: false, skipVisibility: true });
  } else {
    syncDocumentTitle();
  }
  syncLoadedFrames(workspaces);
  maybeNotify(workspaces);
}

function renderState(payload) {
  materializeState(payload);
  renderShell(ui.workspaces);
  renderDrawer();
}

function notificationStatusForWorkspace(workspace) {
  if (!workspace || workspace.is_local || workspace.archived || !workspace.needs_attention) {
    return "";
  }
  const attentionKind = String(workspace.attention_kind || "").trim();
  if (attentionKind === "completion_unseen") {
    return "done";
  }
  if (["needs_input", "awaiting_approval", "error"].includes(attentionKind)) {
    return attentionKind;
  }
  const eventStatus = String(workspace.latest_event_status || "").trim();
  return ["needs_input", "awaiting_approval", "error"].includes(eventStatus) ? eventStatus : "";
}

function notificationMemoryKeyForWorkspace(workspace) {
  if (!workspace) {
    return "";
  }
  const sessionId = String(workspace.session_id || "").trim();
  if (sessionId) {
    return `session:${sessionId}`;
  }
  return `workspace:${String(workspace.id || "").trim()}`;
}

function notificationSignatureForWorkspace(workspace, eventStatus) {
  return [
    String(eventStatus || "").trim(),
    String(workspace?.latest_event_id || "").trim(),
    String(workspace?.latest_event_created_at || "").trim(),
  ].join(":");
}

function maybeNotify(workspaces) {
  if (!("Notification" in window) || Notification.permission !== "granted") {
    return;
  }

  for (const workspace of workspaces) {
    const eventId = workspace.latest_event_id;
    const eventStatus = notificationStatusForWorkspace(workspace);
    if (!eventId || !eventStatus) {
      continue;
    }

    const memoryKey = notificationMemoryKeyForWorkspace(workspace);
    const signature = notificationSignatureForWorkspace(workspace, eventStatus);
    if (!memoryKey || !signature) {
      continue;
    }

    const announced = ui.notificationMemory[memoryKey];
    if (announced === signature) {
      continue;
    }

    const title =
      eventStatus === "needs_input"
        ? `Input needed · ${workspace.folder_name || folderNameFromPath(workspace.cwd)}`
        : eventStatus === "awaiting_approval"
          ? `Approval needed · ${workspace.folder_name || folderNameFromPath(workspace.cwd)}`
          : eventStatus === "error"
            ? `Agent errored · ${workspace.folder_name || folderNameFromPath(workspace.cwd)}`
            : `Agent finished · ${workspace.folder_name || folderNameFromPath(workspace.cwd)}`;
    let notification;
    try {
      notification = new Notification(title, {
        body: workspace.latest_user_message || workspace.latest_event_message || workspace.folder_name,
        tag: signature,
        requireInteraction: eventStatus === "needs_input" || eventStatus === "awaiting_approval" || eventStatus === "error",
      });
    } catch (error) {
      console.warn("Failed to show Switchboard2 notification", error);
      continue;
    }

    ui.notificationMemory[memoryKey] = signature;
    saveJson("switchboard-notification-memory", ui.notificationMemory);

    notification.onclick = () => {
      window.focus();
      const target = resolveNotificationTargetWorkspace(workspace);
      activate(target.id, { acknowledge: true, focusTab: true });
      notification.close();
    };
  }
}

function maybeRequestNotificationPermission() {
  if (
    ui.notificationPrompted ||
    !("Notification" in window) ||
    Notification.permission !== "default"
  ) {
    return;
  }
  ui.notificationPrompted = true;
  Notification.requestPermission()
    .catch(() => {})
    .finally(() => maybeNotify(ui.workspaces));
}

function activate(id, options = {}) {
  if (!id) {
    return;
  }
  saveActiveId(id);
  if (!options.skipVisibility) {
    ensureTabVisibleById(id);
    if (!ui.items.has(id)) {
      renderShell(ui.workspaces);
      return;
    }
  }
  const workspace = getWorkspaceById(id);
  if (!workspace) {
    return;
  }
  ensurePanel(workspace);

  for (const candidate of ui.workspaces) {
    const item = ui.items.get(candidate.id);
    const panel = ui.panels.get(candidate.id);
    const active = candidate.id === id;
    if (item) {
      item.shell.classList.toggle("is-active", active);
      item.tab.setAttribute("aria-selected", String(active));
    item.tab.setAttribute("tabindex", active ? "0" : "-1");
      if (active && !options.preserveScroll) {
        item.shell.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "smooth" });
      }
    }
    if (panel) {
      panel.classList.toggle("is-active", active);
      panel.setAttribute("aria-hidden", String(!active));
    }
  }

  ensureFrameLoaded(workspace);
  syncDocumentTitle();
  const activeItem = ui.items.get(workspace.id);
  if (activeItem && options.focusTab) {
    activeItem.tab.focus({ preventScroll: true });
  }

  if (options.acknowledge && workspace.latest_event_id) {
    ui.acknowledgedEvents[workspace.id] = workspace.latest_event_id;
    saveJson("switchboard-acknowledged-events", ui.acknowledgedEvents);
    const item = ui.items.get(workspace.id);
    if (item && workspace.attention_kind === "completion_unseen") {
      item.shell.classList.remove("has-pending");
      item.tab.querySelector(".workspace-tab-pending").hidden = true;
    }
    if (!workspace.is_local && workspace.attention_kind === "completion_unseen") {
      const acknowledgedEventId = workspace.latest_event_id;
      workspace.needs_attention = false;
      workspace.attention_kind = "";
      workspace.display_state = "seen";
      if (item) {
        item.shell.classList.add("is-seen");
        item.shell.classList.remove("is-done");
      }
      void acknowledgeWorkspace(workspace.id, acknowledgedEventId)
        .then(() => refresh())
        .catch(() => {});
    }
  }
}

function ensureFrameLoaded(workspace) {
  if (ui.loadedFrames.has(workspace.id)) {
    return;
  }
  const panel = ui.panels.get(workspace.id);
  if (!panel || !workspace.code_server_url) {
    return;
  }
  const iframe = panel.querySelector(".workspace-frame");
  iframe.src = workspace.code_server_url;
  iframe.title = `${workspace.title} workspace`;
  ui.loadedFrames.add(workspace.id);
}

function unloadFrame(workspaceId) {
  const panel = ui.panels.get(workspaceId);
  const iframe = panel?.querySelector(".workspace-frame");
  if (iframe) {
    iframe.src = "about:blank";
    iframe.removeAttribute("src");
    iframe.title = "";
  }
  panel?.classList.remove("is-ready");
  ui.loadedFrames.delete(workspaceId);
}

function desiredLoadedWorkspaceIds(workspaces) {
  const desired = new Set();
  const activeWorkspace = getWorkspaceById(ui.activeId);
  if (activeWorkspace) {
    desired.add(activeWorkspace.id);
  }
  for (const workspace of workspaces) {
    if (desired.size >= MAX_LOADED_FRAMES) {
      break;
    }
    if (workspace.archived || desired.has(workspace.id)) {
      continue;
    }
    if (HOT_FRAME_STATES.has(deriveDisplayStatus(workspace))) {
      desired.add(workspace.id);
    }
  }
  return desired;
}

function syncLoadedFrames(workspaces) {
  const desired = desiredLoadedWorkspaceIds(workspaces);
  for (const workspaceId of [...ui.loadedFrames]) {
    if (!desired.has(workspaceId)) {
      unloadFrame(workspaceId);
    }
  }
  for (const workspace of workspaces) {
    if (!desired.has(workspace.id) || ui.loadedFrames.has(workspace.id)) {
      continue;
    }
    ensurePanel(workspace);
    ensureFrameLoaded(workspace);
  }
}

function activateAdjacent(offset) {
  if (!ui.orderedWorkspaceIds.length) {
    return;
  }
  const currentIndex = Math.max(0, ui.orderedWorkspaceIds.indexOf(ui.activeId));
  const nextIndex = (currentIndex + offset + ui.orderedWorkspaceIds.length) % ui.orderedWorkspaceIds.length;
  const nextId = ui.orderedWorkspaceIds[nextIndex];
  if (!nextId) {
    return;
  }
  maybeRequestNotificationPermission();
  activate(nextId, { acknowledge: true, focusTab: true });
}

function updateHintMode(enabled) {
  ui.hintMode = enabled;
  for (const item of ui.items.values()) {
    item.tab.classList.toggle("show-hints", enabled);
  }
}

function handleKeydown(event) {
  const withControlAlt = event.ctrlKey && event.altKey && !event.metaKey;
  if (withControlAlt) {
    updateHintMode(true);
  }

  if (event.key === "Escape" && ui.drawerOpen) {
    closeDrawer();
    return;
  }

  if (!withControlAlt) {
    return;
  }

  const lowerKey = String(event.key || "").toLowerCase();
  if (lowerKey === "f") {
    event.preventDefault();
    toggleDrawer("catalog");
    return;
  }
  if (lowerKey === "n") {
    event.preventDefault();
    toggleDrawer("create");
    return;
  }
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    activateAdjacent(-1);
    return;
  }
  if (event.key === "ArrowRight") {
    event.preventDefault();
    activateAdjacent(1);
    return;
  }

  const digitMatch = /^Digit([1-9])$/.exec(event.code || "");
  if (digitMatch) {
    const index = Number.parseInt(digitMatch[1], 10) - 1;
    const id = ui.orderedWorkspaceIds[index];
    event.preventDefault();
    if (id) {
      maybeRequestNotificationPermission();
      activate(id, { acknowledge: true, focusTab: true });
    }
  }
}

function handleKeyup(event) {
  if (!event.ctrlKey || !event.altKey) {
    updateHintMode(false);
  }
}

function closeLocalWorkspace(workspaceId) {
  ui.localWorkspaces = ui.localWorkspaces.filter((workspace) => workspace.id !== workspaceId);
  if (ui.activeId === workspaceId) {
    saveActiveId(ui.workspaces.find((workspace) => workspace.id !== workspaceId && !workspace.archived)?.id || null);
  }
  saveLocalWorkspaces();
  renderState({ workspaces: ui.serverWorkspaces, machines: ui.machines });
}

async function toggleArchive(workspaceId) {
  const workspace = getWorkspaceById(workspaceId);
  if (!workspace || workspace.is_local || ui.archiveRequests.has(workspaceId)) {
    return;
  }

  ui.archiveRequests.add(workspaceId);
  renderShell(ui.workspaces);
  try {
    await setArchiveState(workspaceId, !workspace.archived);
    await refresh();
  } catch (error) {
    console.error(error);
    syncDocumentTitle();
  } finally {
    ui.archiveRequests.delete(workspaceId);
    renderShell(ui.workspaces);
  }
}

async function applyBatchArchive(archived) {
  const sessionIds = [...ui.selectedWorkspaceIds].filter((workspaceId) =>
    ui.serverWorkspaces.some((workspace) => workspace.id === workspaceId),
  );
  if (!sessionIds.length) {
    return;
  }

  for (const workspaceId of sessionIds) {
    ui.archiveRequests.add(workspaceId);
  }
  renderShell(ui.workspaces);
  try {
    await setArchiveStates(sessionIds, archived);
    ui.selectedWorkspaceIds.clear();
    await refresh();
  } catch (error) {
    console.error(error);
    syncDocumentTitle();
  } finally {
    for (const workspaceId of sessionIds) {
      ui.archiveRequests.delete(workspaceId);
    }
    renderShell(ui.workspaces);
    renderDrawer();
  }
}

function openDrawer(mode) {
  ui.drawerOpen = true;
  drawer.hidden = false;
  drawer.classList.add("is-open");
  renderDrawer();
  if (mode === "create" || mode === "new") {
    newWorkspaceMachine.focus({ preventScroll: true });
    return;
  }
  catalogSearch.focus({ preventScroll: true });
}

function closeDrawer() {
  ui.drawerOpen = false;
  drawer.classList.remove("is-open");
  drawer.hidden = true;
  closeFolderPicker();
}

function toggleDrawer(mode) {
  if (ui.drawerOpen) {
    if (mode === "create" || mode === "new") {
      newWorkspaceMachine.focus({ preventScroll: true });
      return;
    }
    if (mode === "catalog") {
      catalogSearch.focus({ preventScroll: true });
      return;
    }
    closeDrawer();
    return;
  }
  openDrawer(mode);
}

function filteredCatalogWorkspaces() {
  const search = String(ui.catalogFilters.search || "").trim().toLowerCase();
  return ui.workspaces.filter((workspace) => {
    const status = deriveDisplayStatus(workspace);
    if (!ui.catalogFilters.showArchived && workspace.archived) {
      return false;
    }
    if (ui.catalogFilters.machine && workspace.machine !== ui.catalogFilters.machine) {
      return false;
    }
    if (ui.catalogFilters.status && status !== ui.catalogFilters.status) {
      return false;
    }
    if (!search) {
      return true;
    }
    const haystack = [
      workspace.title,
      workspace.folder_name,
      workspace.cwd,
      workspace.branch,
      workspace.machine,
      workspace.detail,
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(search);
  });
}

function syncSelectOptions(select, options, defaultLabel) {
  const previous = select.value;
  select.textContent = "";
  const emptyOption = document.createElement("option");
  emptyOption.value = "";
  emptyOption.textContent = defaultLabel;
  select.append(emptyOption);
  for (const option of options) {
    const element = document.createElement("option");
    element.value = option.value;
    element.textContent = option.label;
    select.append(element);
  }
  if ([...select.options].some((option) => option.value === previous)) {
    select.value = previous;
  }
}

function renderCatalogRows() {
  const visible = filteredCatalogWorkspaces();
  const fragment = document.createDocumentFragment();

  for (const workspace of visible) {
    const displayStatus = deriveDisplayStatus(workspace);
    const row = document.createElement("tr");
    row.className = "catalog-row";
    row.classList.toggle("is-active", workspace.id === ui.activeId);
    row.classList.toggle("is-local", Boolean(workspace.is_local));

    const selectCell = document.createElement("td");
    selectCell.className = "catalog-col-select";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = ui.selectedWorkspaceIds.has(workspace.id);
    checkbox.disabled = Boolean(workspace.is_local);
    checkbox.addEventListener("click", (event) => event.stopPropagation());
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        ui.selectedWorkspaceIds.add(workspace.id);
      } else {
        ui.selectedWorkspaceIds.delete(workspace.id);
      }
      renderDrawer();
    });
    selectCell.append(checkbox);

    const actionCell = document.createElement("td");
    actionCell.className = "catalog-action-cell";
    const actionButton = document.createElement("button");
    actionButton.type = "button";
    actionButton.className = "catalog-row-action";
    actionButton.textContent = "⧉";
    actionButton.ariaLabel = "Copy Codex command";
    const command = codexCommand(workspace);
    if (command) {
      actionButton.title = command;
      actionButton.addEventListener("click", async (event) => {
        event.stopPropagation();
        const copied = await copyTextToClipboard(command);
        const previousLabel = actionButton.textContent;
        const previousTitle = actionButton.title;
        actionButton.textContent = copied ? "OK" : "!!";
        actionButton.title = copied ? "Copied Codex command" : "Copy failed";
        actionButton.classList.toggle("is-copied", copied);
        window.setTimeout(() => {
          actionButton.textContent = previousLabel;
          actionButton.title = previousTitle;
          actionButton.classList.remove("is-copied");
        }, 1100);
      });
    } else {
      actionButton.disabled = true;
      actionButton.title = "No Codex command is available for this workspace";
    }
    actionCell.append(actionButton);

    const cells = [
      formatStatusText(displayStatus),
      workspace.title,
      workspace.machine,
      workspace.folder_name || folderNameFromPath(workspace.cwd),
      workspace.branch || "—",
      formatTimestamp(workspace.updated_at || workspace.created_at || workspace.latest_event_created_at),
      workspace.is_local ? "workspace" : workspace.archived ? "archived" : "session",
    ].map((text) => {
      const cell = document.createElement("td");
      cell.textContent = text;
      return cell;
    });
    cells[0].classList.add("catalog-status-cell", `status-${displayStatus}`);
    cells[1].classList.add("catalog-title-cell");

    row.append(selectCell, actionCell, ...cells);
    row.addEventListener("click", (event) => {
      if (event.target instanceof HTMLElement && event.target.closest("input, button, a")) {
        return;
      }
      activate(workspace.id, { acknowledge: true, focusTab: true });
      closeDrawer();
    });
    fragment.append(row);
  }

  catalogBody.replaceChildren(fragment);

  const visibleArchivableIds = visible.filter((workspace) => !workspace.is_local).map((workspace) => workspace.id);
  const selectedArchivableIds = visibleArchivableIds.filter((workspaceId) => ui.selectedWorkspaceIds.has(workspaceId));
  catalogSelectAll.checked = visibleArchivableIds.length > 0 && selectedArchivableIds.length === visibleArchivableIds.length;
  catalogSelectAll.indeterminate =
    selectedArchivableIds.length > 0 && selectedArchivableIds.length < visibleArchivableIds.length;
  catalogSelectionCount.textContent = `${ui.selectedWorkspaceIds.size} selected`;
  catalogBatchBar.hidden = ui.selectedWorkspaceIds.size === 0;
  catalogArchiveSelected.disabled = selectedArchivableIds.length === 0;
  catalogUnarchiveSelected.disabled = selectedArchivableIds.length === 0;
}

function currentNewWorkspaceMachine() {
  return ui.machines.find((machine) => machine.machine === newWorkspaceMachine.value) || null;
}

function recentFoldersForMachine(machineName) {
  return [...new Set(
    ui.workspaces
      .filter((workspace) => workspace.machine === machineName)
      .map((workspace) => workspace.cwd)
      .filter(Boolean),
  )].sort((left, right) => left.localeCompare(right));
}

function buildFolderPickerItems() {
  const selectedMachine = currentNewWorkspaceMachine();
  const typedValue = String(newWorkspaceFolder.value || "").trim();
  const normalizedValue = typedValue ? normalizePath(typedValue) : "";
  const query = typedValue.toLowerCase();
  const folders = selectedMachine ? recentFoldersForMachine(selectedMachine.machine) : [];
  const matchingFolders = folders
    .filter((folder) => !query || folder.toLowerCase().includes(query))
    .sort((left, right) => {
      const leftStarts = left.toLowerCase().startsWith(query);
      const rightStarts = right.toLowerCase().startsWith(query);
      if (leftStarts !== rightStarts) {
        return leftStarts ? -1 : 1;
      }
      return left.localeCompare(right);
    })
    .slice(0, FOLDER_SUGGESTION_LIMIT);
  const exactExisting = normalizedValue && folders.some((folder) => normalizePath(folder) === normalizedValue);
  const items = matchingFolders.map((folder) => ({
    kind: "existing",
    label: folder,
    meta: "Known folder",
    value: folder,
  }));
  if (normalizedValue && isAbsolutePath(normalizedValue) && !exactExisting) {
    items.unshift({
      kind: "create",
      label: normalizedValue,
      meta: "Create fresh tab for new folder path",
      value: normalizedValue,
    });
  }
  return items;
}

function closeFolderPicker() {
  folderPicker.open = false;
  folderPicker.activeIndex = -1;
  folderPicker.items = [];
  newWorkspaceFolder.setAttribute("aria-expanded", "false");
  newWorkspaceFolderOptions.hidden = true;
  newWorkspaceFolderOptions.replaceChildren();
}

function renderFolderPicker() {
  const selectedMachine = currentNewWorkspaceMachine();
  if (!folderPicker.open || !selectedMachine) {
    closeFolderPicker();
    return;
  }
  folderPicker.items = buildFolderPickerItems();
  if (folderPicker.items.length === 0) {
    folderPicker.activeIndex = -1;
  } else if (folderPicker.activeIndex >= folderPicker.items.length) {
    folderPicker.activeIndex = folderPicker.items.length - 1;
  }

  const fragment = document.createDocumentFragment();
  if (folderPicker.items.length) {
    folderPicker.items.forEach((item, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `catalog-folder-option${item.kind === "create" ? " catalog-folder-option--create" : ""}`;
      button.setAttribute("role", "option");
      button.setAttribute("aria-selected", String(index === folderPicker.activeIndex));
      button.classList.toggle("is-active", index === folderPicker.activeIndex);
      button.addEventListener("mousedown", (event) => {
        event.preventDefault();
        newWorkspaceFolder.value = item.value;
        closeFolderPicker();
        newWorkspaceFolder.focus({ preventScroll: true });
        renderNewWorkspaceView();
      });

      const label = document.createElement("span");
      label.className = "catalog-folder-option-label";
      label.textContent = item.label;
      const meta = document.createElement("span");
      meta.className = "catalog-folder-option-meta";
      meta.textContent = item.meta;
      button.append(label, meta);
      fragment.append(button);
    });
  } else {
    const empty = document.createElement("div");
    empty.className = "catalog-folder-options-empty";
    const typedValue = String(newWorkspaceFolder.value || "").trim();
    empty.textContent = typedValue && !isAbsolutePath(typedValue)
      ? "Type an absolute path to create a new folder tab."
      : "No matching folders yet. Type a new absolute path to create one.";
    fragment.append(empty);
  }

  newWorkspaceFolderOptions.replaceChildren(fragment);
  newWorkspaceFolderOptions.hidden = false;
  newWorkspaceFolder.setAttribute("aria-expanded", "true");
}

function openFolderPicker() {
  folderPicker.open = true;
  folderPicker.activeIndex = -1;
  renderFolderPicker();
}

function renderNewWorkspaceView() {
  const machineOptions = ui.machines
    .filter((machine) => machine.machine)
    .map((machine) => ({
      value: machine.machine,
      label: machine.online ? machine.machine : `${machine.machine} (offline)`,
    }));
  const previous = newWorkspaceMachine.value;
  newWorkspaceMachine.textContent = "";
  for (const option of machineOptions) {
    const element = document.createElement("option");
    element.value = option.value;
    element.textContent = option.label;
    newWorkspaceMachine.append(element);
  }
  if (machineOptions.length && machineOptions.some((option) => option.value === previous)) {
    newWorkspaceMachine.value = previous;
  } else if (machineOptions.length && !newWorkspaceMachine.value) {
    newWorkspaceMachine.value = machineOptions[0].value;
  }

  const selectedMachine = currentNewWorkspaceMachine();
  const currentFolder = String(newWorkspaceFolder.value || "").trim();
  const normalizedFolder = currentFolder ? normalizePath(currentFolder) : "";
  const knownFolders = selectedMachine ? recentFoldersForMachine(selectedMachine.machine) : [];
  const folderExists = normalizedFolder && knownFolders.some((folder) => normalizePath(folder) === normalizedFolder);
  newWorkspaceHint.textContent = selectedMachine
    ? selectedMachine.online
      ? normalizedFolder && isAbsolutePath(normalizedFolder)
        ? folderExists
          ? "Create a fresh workspace tab for this folder. Existing tabs will stay open."
          : "Create a fresh workspace tab for this new folder path. Switchboard will target it immediately."
        : "Pick a machine, choose an existing folder or type a new absolute path, and Switchboard will create a fresh workspace tab."
      : "This machine is offline. You can still stage a fresh tab, but the iframe may not load until the machine reports again."
    : "No launchable machines are available yet.";
  renderFolderPicker();
}

function renderDrawer() {
  catalogCount.textContent = String(ui.workspaces.length);
  if (!ui.drawerOpen) {
    return;
  }
  const tableScrollTop = catalogTableShell ? catalogTableShell.scrollTop : 0;

  drawerEyebrow.textContent = "Workspace Catalog";
  drawerTitle.textContent = "All tabs";

  syncSelectOptions(
    catalogMachineFilter,
    ui.machines.map((machine) => ({ value: machine.machine, label: machine.machine })),
    "All machines",
  );
  catalogSearch.value = ui.catalogFilters.search;
  catalogMachineFilter.value = ui.catalogFilters.machine;
  catalogStatusFilter.value = ui.catalogFilters.status;
  catalogShowArchived.checked = Boolean(ui.catalogFilters.showArchived);
  renderCatalogRows();
  renderNewWorkspaceView();
  if (catalogTableShell) {
    const restoreScroll = () => {
      catalogTableShell.scrollTop = Math.min(
        tableScrollTop,
        Math.max(0, catalogTableShell.scrollHeight - catalogTableShell.clientHeight),
      );
    };
    restoreScroll();
    window.requestAnimationFrame(() => {
      restoreScroll();
      window.requestAnimationFrame(restoreScroll);
    });
  }
}

function addLocalWorkspace(machine, folder) {
  const normalizedFolder = normalizePath(folder);
  const folderName = folderNameFromPath(normalizedFolder) || "workspace";
  const workspace = {
    id: createLocalWorkspaceId(machine.machine, normalizedFolder),
    session_id: "",
    machine: machine.machine,
    machine_dns: String(machine.machine_dns || "").trim(),
    cwd: normalizedFolder,
    folder_name: folderName,
    code_server_url: buildWorkspaceCodeServerUrl(machine.machine_dns, normalizedFolder),
    same_origin_helper_url: "",
    title: folderName,
    branch: "workspace",
    detail: "Ad hoc workspace tab opened from Switchboard.",
    activity_state: "idle",
    local_status: "new",
    archived: false,
    archived_at: "",
    created_at: isoNow(),
    updated_at: isoNow(),
    latest_event_id: "",
    latest_event_status: "",
    latest_event_message: "",
    latest_event_created_at: "",
    is_local: true,
  };
  ui.localWorkspaces = sortWorkspaces([workspace, ...ui.localWorkspaces]);
  saveLocalWorkspaces();
  return workspace;
}

async function handleNewWorkspaceSubmit(event) {
  event.preventDefault();
  const machine = ui.machines.find((entry) => entry.machine === newWorkspaceMachine.value);
  const folder = normalizePath(newWorkspaceFolder.value);
  if (!machine || !folder) {
    newWorkspaceHint.textContent = "Pick a machine and provide an absolute folder path.";
    return;
  }
  if (!isAbsolutePath(folder)) {
    newWorkspaceHint.textContent = "Folder paths must be absolute, for example /home/user/project.";
    openFolderPicker();
    return;
  }
  const workspace = addLocalWorkspace(machine, folder);
  await bootstrapLocalWorkspace(workspace);
  renderState({ workspaces: ui.serverWorkspaces, machines: ui.machines });
  activate(workspace.id, { acknowledge: false, focusTab: true });
  closeDrawer();
}

async function refresh() {
  if (refreshPromise) {
    return refreshPromise;
  }
  refreshPromise = (async () => {
    try {
      const payload = await fetchState();
      renderState(payload);
    } catch (error) {
      console.error(error);
      syncDocumentTitle();
    } finally {
      refreshPromise = null;
    }
  })();
  return refreshPromise;
}

function cancelScheduledRefresh() {
  const scheduledPoll = window[APP_POLL_TIMER_KEY];
  if (scheduledPoll) {
    window.clearTimeout(scheduledPoll);
  }
  window[APP_POLL_TIMER_KEY] = null;
  window[APP_POLL_SEQUENCE_KEY] = Number(window[APP_POLL_SEQUENCE_KEY] || 0) + 1;
  pollTimer = null;
}

function closeStream() {
  const activeStream = window[APP_STREAM_KEY];
  if (activeStream) {
    activeStream.close();
  }
  window[APP_STREAM_KEY] = null;
  stream = null;
}

function cancelUiVersionPolling() {
  const scheduledPoll = window[APP_UI_VERSION_TIMER_KEY];
  if (scheduledPoll) {
    window.clearTimeout(scheduledPoll);
  }
  window[APP_UI_VERSION_TIMER_KEY] = null;
  uiVersionPollTimer = null;
}

function connectStream() {
  if (!("EventSource" in window)) {
    return;
  }
  closeStream();
  const generation = appGeneration;
  stream = new EventSource(streamUrl);
  window[APP_STREAM_KEY] = stream;
  stream.addEventListener("invalidate", () => {
    if (window[APP_GENERATION_KEY] !== generation) {
      return;
    }
    void refresh();
  });
  stream.onerror = () => {
    if (window[APP_GENERATION_KEY] !== generation) {
      return;
    }
    scheduleRefresh(1000);
  };
}

function scheduleRefresh(delay = POLL_INTERVAL_MS) {
  cancelScheduledRefresh();
  const generation = appGeneration;
  const sequence = Number(window[APP_POLL_SEQUENCE_KEY] || 0) + 1;
  window[APP_POLL_SEQUENCE_KEY] = sequence;
  pollTimer = window.setTimeout(async () => {
    if (window[APP_GENERATION_KEY] !== generation) {
      return;
    }
    if (window[APP_POLL_SEQUENCE_KEY] !== sequence) {
      return;
    }
    pollTimer = null;
    window[APP_POLL_TIMER_KEY] = null;
    await refresh();
    if (window[APP_GENERATION_KEY] !== generation) {
      return;
    }
    if (window[APP_POLL_SEQUENCE_KEY] !== sequence) {
      return;
    }
    scheduleRefresh(POLL_INTERVAL_MS);
  }, delay);
  window[APP_POLL_TIMER_KEY] = pollTimer;
}

function scheduleUiVersionPoll(delay = UI_VERSION_POLL_INTERVAL_MS) {
  cancelUiVersionPolling();
  const generation = appGeneration;
  uiVersionPollTimer = window.setTimeout(async () => {
    if (window[APP_GENERATION_KEY] !== generation) {
      return;
    }
    try {
      const nextVersion = await fetchUiVersion();
      if (currentUiVersion && nextVersion && nextVersion !== currentUiVersion) {
        window.location.reload();
        return;
      }
      if (nextVersion) {
        currentUiVersion = nextVersion;
      }
    } catch {
      // Ignore transient UI-version poll failures and retry on the next interval.
    }
    if (window[APP_GENERATION_KEY] !== generation) {
      return;
    }
    scheduleUiVersionPoll(UI_VERSION_POLL_INTERVAL_MS);
  }, delay);
  window[APP_UI_VERSION_TIMER_KEY] = uiVersionPollTimer;
}

async function registerServiceWorker() {
  if (!("serviceWorker" in window.navigator) || !window.isSecureContext) {
    return;
  }
  if (window.location.pathname.includes("/proxy/")) {
    return;
  }
  try {
    const currentController = window.navigator.serviceWorker.controller;
    if (currentController && !String(currentController.scriptURL || "").includes("/service-worker.js")) {
      return;
    }
    let didRefreshForController = false;
    window.navigator.serviceWorker.addEventListener("controllerchange", () => {
      if (didRefreshForController) {
        return;
      }
      didRefreshForController = true;
      window.location.reload();
    });
    const registration = await window.navigator.serviceWorker.register("./service-worker.js", { scope: "./" });
    await registration.update();
  } catch {
    // Ignore service worker registration failures so the main shell still works.
  }
}

function wireEvents() {
  restoreTabStripScroll();
  tabStrip.addEventListener(
    "wheel",
    (event) => {
      if (Math.abs(event.deltaY) <= Math.abs(event.deltaX)) {
        return;
      }
      tabStrip.scrollLeft += event.deltaY;
      event.preventDefault();
    },
    { passive: false },
  );
  tabStrip.addEventListener("scroll", () => {
    window.localStorage.setItem("switchboard-tab-strip-scroll-left", String(tabStrip.scrollLeft));
    maybeLoadMoreTabs();
  });

  catalogToggle.addEventListener("click", () => toggleDrawer());
  drawerClose.addEventListener("click", () => closeDrawer());
  drawer.addEventListener("click", (event) => {
    if (event.target === drawer) {
      closeDrawer();
    }
  });

  catalogSearch.addEventListener("input", () => {
    ui.catalogFilters.search = catalogSearch.value;
    saveCatalogFilters();
    renderDrawer();
  });
  catalogMachineFilter.addEventListener("change", () => {
    ui.catalogFilters.machine = catalogMachineFilter.value;
    saveCatalogFilters();
    renderDrawer();
  });
  catalogStatusFilter.addEventListener("change", () => {
    ui.catalogFilters.status = catalogStatusFilter.value;
    saveCatalogFilters();
    renderDrawer();
  });
  catalogShowArchived.addEventListener("change", () => {
    ui.catalogFilters.showArchived = catalogShowArchived.checked;
    saveCatalogFilters();
    renderDrawer();
  });
  catalogSelectVisible.addEventListener("click", () => {
    for (const workspace of filteredCatalogWorkspaces()) {
      if (!workspace.is_local) {
        ui.selectedWorkspaceIds.add(workspace.id);
      }
    }
    renderDrawer();
  });
  catalogClearSelection.addEventListener("click", () => {
    ui.selectedWorkspaceIds.clear();
    renderDrawer();
  });
  catalogArchiveSelected.addEventListener("click", async () => {
    await applyBatchArchive(true);
  });
  catalogUnarchiveSelected.addEventListener("click", async () => {
    await applyBatchArchive(false);
  });
  catalogSelectAll.addEventListener("change", () => {
    const visibleArchivable = filteredCatalogWorkspaces().filter((workspace) => !workspace.is_local);
    if (catalogSelectAll.checked) {
      for (const workspace of visibleArchivable) {
        ui.selectedWorkspaceIds.add(workspace.id);
      }
    } else {
      for (const workspace of visibleArchivable) {
        ui.selectedWorkspaceIds.delete(workspace.id);
      }
    }
    renderDrawer();
  });

  newWorkspaceMachine.addEventListener("change", () => {
    folderPicker.activeIndex = -1;
    renderNewWorkspaceView();
  });
  newWorkspaceFolder.addEventListener("focus", () => {
    openFolderPicker();
  });
  newWorkspaceFolder.addEventListener("input", () => {
    folderPicker.open = true;
    folderPicker.activeIndex = -1;
    renderNewWorkspaceView();
  });
  newWorkspaceFolder.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeFolderPicker();
      return;
    }
    if (event.key === "ArrowDown") {
      event.preventDefault();
      if (!folderPicker.open) {
        openFolderPicker();
        return;
      }
      if (!folderPicker.items.length) {
        return;
      }
      folderPicker.activeIndex = (folderPicker.activeIndex + 1 + folderPicker.items.length) % folderPicker.items.length;
      renderFolderPicker();
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      if (!folderPicker.open) {
        openFolderPicker();
        return;
      }
      if (!folderPicker.items.length) {
        return;
      }
      folderPicker.activeIndex = folderPicker.activeIndex <= 0
        ? folderPicker.items.length - 1
        : folderPicker.activeIndex - 1;
      renderFolderPicker();
      return;
    }
    if (event.key === "Enter" && folderPicker.open && folderPicker.activeIndex >= 0) {
      event.preventDefault();
      const selected = folderPicker.items[folderPicker.activeIndex];
      if (!selected) {
        return;
      }
      newWorkspaceFolder.value = selected.value;
      closeFolderPicker();
      renderNewWorkspaceView();
    }
  });
  newWorkspaceFolder.addEventListener("blur", () => {
    window.setTimeout(() => {
      const activeElement = document.activeElement;
      if (activeElement && newWorkspaceFolderOptions.contains(activeElement)) {
        return;
      }
      closeFolderPicker();
    }, 120);
  });
  newWorkspaceForm.addEventListener("submit", (event) => {
    handleNewWorkspaceSubmit(event).catch(() => {});
  });

  window.addEventListener("pointerdown", (event) => {
    if (event.target instanceof Node && !newWorkspaceForm.contains(event.target)) {
      closeFolderPicker();
    }
  }, true);
  window.addEventListener("pointerdown", maybeRequestNotificationPermission, true);
  window.addEventListener("keydown", maybeRequestNotificationPermission, true);
  window.addEventListener("keydown", handleKeydown, true);
  window.addEventListener("keyup", handleKeyup, true);
  window.addEventListener("blur", () => updateHintMode(false));
}

async function start() {
  if (window[APP_INSTANCE_KEY]) {
    return;
  }
  window[APP_INSTANCE_KEY] = true;
  appGeneration = Number(window[APP_GENERATION_KEY] || 0) + 1;
  window[APP_GENERATION_KEY] = appGeneration;
  wireEvents();
  await registerServiceWorker();
  currentUiVersion = await fetchUiVersion().catch(() => "");
  renderState({ workspaces: [], machines: [] });
  await refresh();
  connectStream();
  scheduleRefresh(POLL_INTERVAL_MS);
  scheduleUiVersionPoll(UI_VERSION_POLL_INTERVAL_MS);
}

void start();
