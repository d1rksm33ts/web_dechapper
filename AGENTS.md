# Website startup requirement

The user requires prompt visible feedback on every YaNoa website and does not want to repeat this requirement. When changing frontend templates, assets, photographs, startup logic or deployment:

- Check first visible content in a fresh browser, on desktop and mobile, including a slow connection. An HTTP health check alone is insufficient.
- Run the shared checker in `../yanoa_infrastructure/scripts/check-site-loading.py` before and after publishing affected frontend changes. Usage and fleet inventory are in `../yanoa_infrastructure/docs/site-loading.md`.
- Default budgets are 2 seconds for first contentful paint normally and 3 seconds at 1.6 Mbit/s with 150 ms latency. Distinguish this from full image/application loading. If data takes longer, show navigation and clear loading text immediately and fetch it afterwards.
- Keep critical CSS/fonts/scripts local where practical. Never make first content wait for a public CDN, a whole gallery or `window.load`. Prioritize the hero; defer lower-page images.
- A loading overlay must have a bounded fallback and clear on successful or failed stylesheet loads. Verify slow/failed assets and the supported no-JavaScript path when changing startup behavior.
- Verify affected navigation, filters and forms. Browser checks against production must not submit forms or operate home devices.

Preserve unrelated user changes. In AllSky, the existing dirty upstream submodule is not permission to modify it.
