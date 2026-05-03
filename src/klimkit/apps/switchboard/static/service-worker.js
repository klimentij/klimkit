const CACHE_NAME = "switchboard-shell-v2";
const SHELL_ASSETS = [
  "./",
  "./index.html",
  "./styles.css",
  "./app.js",
  "./manifest.webmanifest",
  "./icons/favicon.ico",
  "./icons/favicon-16.png",
  "./icons/favicon-32.png",
  "./icons/favicon-48.png",
  "./icons/apple-touch-icon.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-512-maskable.png",
];

function scopePath() {
  const pathname = new URL(self.registration.scope).pathname;
  return pathname.endsWith("/") ? pathname : `${pathname}/`;
}

function pathWithinScope(pathname) {
  const base = scopePath();
  const withoutSlash = base.endsWith("/") ? base.slice(0, -1) : base;
  if (pathname === withoutSlash) {
    return "/";
  }
  if (!pathname.startsWith(base)) {
    return null;
  }
  return pathname.slice(base.length - 1) || "/";
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))),
      )
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") {
    return;
  }

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) {
    return;
  }
  const scopedPath = pathWithinScope(url.pathname);
  if (scopedPath === null) {
    return;
  }
  if (scopedPath.startsWith("/api/")) {
    event.respondWith(fetch(request));
    return;
  }

  const isNavigation = request.mode === "navigate";
  if (isNavigation) {
    const isShellEntry = scopedPath === "/";
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok && isShellEntry) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put("./index.html", copy));
          }
          return response;
        })
        .catch(async () => {
          const cached = isShellEntry ? await caches.match("./index.html") : null;
          return cached || Response.error();
        }),
    );
    return;
  }

  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }
        return response;
      })
      .catch(async () => {
        const cached = await caches.match(request);
        return cached || Response.error();
      }),
  );
});
