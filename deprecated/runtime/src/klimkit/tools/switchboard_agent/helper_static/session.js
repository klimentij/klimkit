const params = new URLSearchParams(window.location.search);
const folder = params.get("folder") || "";
const sessionId = params.get("session_id") || "";
const title = params.get("title") || "";
const codeServerUrl = params.get("code_server_url") || "";
const autoClose = params.get("autoclose") === "1";
const autoTrust = params.get("auto_trust") === "1";
const isController = params.get("controller") === "1";

const ui = {
  headline: document.querySelector("#headline"),
  summary: document.querySelector("#summary"),
  folder: document.querySelector("#fact-folder"),
  session: document.querySelector("#fact-session"),
  title: document.querySelector("#fact-title"),
  status: document.querySelector("#status-pill"),
  logList: document.querySelector("#log-list"),
  retry: document.querySelector("#retry-button"),
  workspaceLink: document.querySelector("#workspace-link"),
};

const workspaceUrl = codeServerUrl ? new URL(codeServerUrl) : new URL("/", window.location.href);
if (!codeServerUrl && folder) {
  workspaceUrl.searchParams.set("folder", folder);
}

const workspaceWindowName = `switchboard-workspace-${hashToken(folder || sessionId || "default")}`;
const controllerWindowName = `switchboard-controller-${hashToken(folder || sessionId || "default")}`;

ui.folder.textContent = folder || "(missing)";
ui.session.textContent = sessionId || "(missing)";
ui.title.textContent = title || "(missing)";
ui.workspaceLink.href = workspaceUrl.toString();
ui.retry.addEventListener("click", () => {
  void run();
});

function hashToken(value) {
  let hash = 0;
  for (const character of value) {
    hash = (hash * 33 + character.charCodeAt(0)) >>> 0;
  }
  return hash.toString(16);
}

function logEntry(level, heading, detail) {
  const item = document.createElement("li");
  item.className = `log-entry log-entry--${level}`;
  const strong = document.createElement("strong");
  strong.textContent = heading;
  const detailNode = document.createElement("span");
  detailNode.textContent = detail;
  item.append(strong, detailNode);
  ui.logList.append(item);
}

function setStatus(kind, text) {
  ui.status.textContent = text;
  ui.status.className = `status-pill status-${kind}`;
}

function sleep(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

async function waitFor(test, { timeoutMs = 15000, intervalMs = 200, description = "condition" } = {}) {
  const startedAt = Date.now();
  while ((Date.now() - startedAt) < timeoutMs) {
    try {
      const result = test();
      if (result) {
        return result;
      }
    } catch {
      // Keep polling while the target window is still booting.
    }
    await sleep(intervalMs);
  }
  throw new Error(`Timed out waiting for ${description}`);
}

function normalizeText(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function getWorkspaceWindow() {
  if (isController && window.opener && !window.opener.closed) {
    return window.opener;
  }
  return window.open(workspaceUrl.toString(), workspaceWindowName, "popup,width=1480,height=960");
}

function launchControllerAndNavigate() {
  const controllerUrl = new URL(window.location.href);
  controllerUrl.searchParams.set("controller", "1");
  const controller = window.open(
    controllerUrl.toString(),
    controllerWindowName,
    "popup,width=460,height=720",
  );
  if (!controller) {
    return false;
  }
  window.location.replace(workspaceUrl.toString());
  return true;
}

function getCodexContext(targetWindow) {
  const hostFrame = [...targetWindow.document.querySelectorAll("iframe")].find((frame) =>
    String(frame.src || "").includes("extensionId=openai.chatgpt"),
  );
  const hostDoc = hostFrame?.contentWindow?.document;
  const appFrame = hostDoc?.querySelector('iframe[title="Codex"]') || hostDoc?.querySelector("#active-frame");
  const appWindow = appFrame?.contentWindow || null;
  const doc = appWindow?.document || null;
  return { hostFrame, hostDoc, appFrame, appWindow, doc };
}

function getCodexBodyText(targetWindow) {
  const context = getCodexContext(targetWindow);
  return normalizeText(context.doc?.body?.innerText || "");
}

function isConversationView(targetWindow) {
  const body = getCodexBodyText(targetWindow);
  if (!body) {
    return false;
  }
  if (title && body.startsWith(normalizeText(title))) {
    return true;
  }
  return !body.startsWith("Tasks ");
}

function findMainButton(targetWindow, matcher) {
  const nodes = targetWindow.document.querySelectorAll("button, a, [role='button'], div[role='button']");
  return [...nodes].find((node) => matcher(normalizeText(node.innerText || node.textContent || ""), node));
}

function findCodexTab(targetWindow) {
  return findMainButton(targetWindow, (text, node) => {
    const label = normalizeText(node.getAttribute("aria-label") || "");
    return text === "Codex" || label === "Codex";
  });
}

function findCodexSidebarButton(targetWindow) {
  return findMainButton(targetWindow, (text, node) => {
    const label = normalizeText(node.getAttribute("aria-label") || "");
    return text === "Open Codex Sidebar" || label === "Open Codex Sidebar";
  });
}

function findTrustButton(targetWindow) {
  return findMainButton(
    targetWindow,
    (text) => text === "Yes, I trust the authors" || text.endsWith("trust the authors"),
  );
}

async function ensureTrusted(targetWindow, { timeoutMs = 5000 } = {}) {
  try {
    await waitFor(() => findTrustButton(targetWindow) || targetWindow.document?.querySelector(".monaco-workbench"), {
      timeoutMs,
      description: "either the trust prompt or the workbench shell",
    });
  } catch {
    // The workspace might already be ready without ever showing a trust prompt.
  }
  const trustButton = findTrustButton(targetWindow);
  if (!trustButton) {
    return;
  }
  if (!autoTrust) {
    throw new Error("Workspace is still in restricted mode. Re-run with auto_trust=1 or trust it once manually.");
  }
  trustButton.click();
  logEntry("warn", "Trusted workspace", "The helper accepted the workspace trust prompt so Codex could load.");
  await sleep(900);
}

async function ensureCodexLoaded(targetWindow) {
  if (getCodexContext(targetWindow).appWindow) {
    return;
  }

  await ensureTrusted(targetWindow, { timeoutMs: 1200 });

  await waitFor(
    () => getCodexContext(targetWindow).appWindow || findCodexTab(targetWindow) || findCodexSidebarButton(targetWindow),
    {
      timeoutMs: 12000,
      description: "the Codex tab, Codex sidebar button, or mounted webview",
    },
  );
  if (getCodexContext(targetWindow).appWindow) {
    return;
  }

  const codexTab = findCodexTab(targetWindow);
  if (codexTab) {
    codexTab.click();
    logEntry("success", "Opened Codex tab", "Activated the Codex secondary-sidebar tab in code-server.");
  } else {
    const sidebarButton = findCodexSidebarButton(targetWindow);
    if (!sidebarButton) {
      throw new Error("Could not find a Codex tab or Open Codex Sidebar control.");
    }
    sidebarButton.click();
    logEntry("success", "Opened Codex sidebar", "Activated Codex from the editor toolbar.");
  }
  targetWindow.focus();

  await waitFor(() => getCodexContext(targetWindow).appWindow, {
    timeoutMs: 12000,
    description: "the Codex webview to mount",
  });
}

async function routeToSession(targetWindow) {
  if (!sessionId) {
    return false;
  }
  const context = getCodexContext(targetWindow);
  if (!context.appWindow) {
    return false;
  }
  context.appWindow.postMessage(
    {
      type: "navigate-to-route",
      path: `/local/${sessionId}`,
    },
    window.location.origin,
  );
  logEntry("success", "Sent route message", `Posted navigate-to-route for ${sessionId}.`);
  try {
    await waitFor(() => isConversationView(targetWindow), {
      timeoutMs: 8000,
      description: "the Codex route message to open the conversation",
    });
    return true;
  } catch {
    return false;
  }
}

async function clickConversationByTitle(targetWindow) {
  if (!title) {
    return false;
  }
  const context = getCodexContext(targetWindow);
  const target = [...(context.doc?.querySelectorAll("[role='button']") || [])].find((node) =>
    normalizeText(node.innerText || "").startsWith(normalizeText(title)),
  );
  if (!target) {
    return false;
  }
  target.click();
  logEntry("success", "Clicked conversation row", `Selected "${title}" from the Codex task list.`);
  await waitFor(() => isConversationView(targetWindow), {
    timeoutMs: 8000,
    description: "the clicked Codex conversation to open",
  });
  return true;
}

async function prepareWorkspaceWindow() {
  const targetWindow = getWorkspaceWindow();
  if (!targetWindow) {
    throw new Error("Popup blocked. Use the Open workspace button and then retry.");
  }
  targetWindow.focus();

  await waitFor(() => !targetWindow.closed && targetWindow.document?.readyState === "complete", {
    timeoutMs: 12000,
    description: "the code-server workspace window",
  });
  await ensureTrusted(targetWindow, { timeoutMs: 5000 });
  await waitFor(() => targetWindow.document?.querySelector(".monaco-workbench"), {
    timeoutMs: 15000,
    description: "the VS Code workbench shell",
  });
  await ensureTrusted(targetWindow, { timeoutMs: 1200 });
  return targetWindow;
}

async function run() {
  ui.logList.textContent = "";
  setStatus("pending", "Running");
  ui.headline.textContent = title ? `Opening ${title}` : "Opening requested Codex session";
  ui.summary.textContent = isController
    ? "This controller popup is attached to the workspace tab and is routing Codex into the requested session."
    : "This launcher tab will hand off into the workspace and let a controller popup complete the Codex routing.";

  if (!folder || (!sessionId && !title)) {
    setStatus("error", "Invalid");
    logEntry("error", "Missing parameters", "The helper needs at least folder plus session_id or title.");
    return;
  }

  if (!isController) {
    if (launchControllerAndNavigate()) {
      return;
    }
    logEntry("warn", "Controller popup blocked", "Falling back to driving a separate workspace popup from this launcher tab.");
  }

  try {
    const targetWindow = await prepareWorkspaceWindow();
    logEntry("success", "Workspace window ready", targetWindow.location.href);

    await ensureCodexLoaded(targetWindow);
    logEntry("success", "Codex loaded", "The nested OpenAI Codex webview is mounted and readable from the helper.");

    let opened = await routeToSession(targetWindow);
    if (!opened) {
      logEntry("warn", "Route message did not finish", "Falling back to clicking the matching conversation row by title.");
      opened = await clickConversationByTitle(targetWindow);
    }
    if (!opened) {
      throw new Error("The helper could not locate the requested conversation by id or title.");
    }

    targetWindow.focus();
    setStatus("success", "Ready");
    logEntry("success", "Conversation open", "The target code-server window is focused with the requested Codex conversation selected.");
    if (autoClose) {
      logEntry("success", "Closing helper", "Auto-close is enabled, so this launcher tab will close itself.");
      window.setTimeout(() => {
        window.close();
      }, 700);
    }
  } catch (error) {
    setStatus("error", "Blocked");
    logEntry("error", "Helper failed", error instanceof Error ? error.message : String(error));
  }
}

void run();
