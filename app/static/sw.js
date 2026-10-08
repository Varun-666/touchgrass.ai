const CACHE = "touchgrass-v1";
const ASSETS = ["/", "/static/index.html", "/static/app.js", "/static/styles.css", "/static/manifest.json"];
self.addEventListener("install", event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS))));
self.addEventListener("fetch", event => {
  if (event.request.url.includes("/api/")) return;
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request)));
});
