const NATIVE_W = 16384;
const NATIVE_H = 8192;
const MAX_ZOOM = 6;
const TILE_SIZE = 256;

const TEXT = {
  zh: {
    title: "独特奇观",
    subtitle: "世界地图",
    search: "搜索奇观或地点...",
    count: (shown, total) => `${shown} / ${total} 个奇观`,
    location: "地点",
    base: "原型",
    size: "规模",
    category: "类别",
    requirements: "建造条件",
    effects: "效果",
    modifier: "修正",
    scope: "范围",
    years: "年",
    anyOf: "满足任一：",
  },
  en: {
    title: "Unique Wonders",
    subtitle: "World Map",
    search: "Search wonders or locations...",
    count: (shown, total) => `${shown} / ${total} wonders`,
    location: "Location",
    base: "Prototype",
    size: "Size",
    category: "Category",
    requirements: "Build Conditions",
    effects: "Effects",
    modifier: "Modifier",
    scope: "Scope",
    years: "years",
    anyOf: "Any of:",
  },
};

const EXTRA_TEXT = {
  zh: {
    localWonders: "\u5f53\u5730\u5947\u89c2",
    previousLocalWonder: "\u4e0a\u4e00\u4e2a\u5f53\u5730\u5947\u89c2",
    nextLocalWonder: "\u4e0b\u4e00\u4e2a\u5f53\u5730\u5947\u89c2",
  },
  en: {
    localWonders: "Local wonders",
    previousLocalWonder: "Previous local wonder",
    nextLocalWonder: "Next local wonder",
  },
};

const elements = {
  title: document.getElementById("app-title"),
  subtitle: document.getElementById("app-subtitle"),
  search: document.getElementById("search"),
  count: document.getElementById("count-line"),
  list: document.getElementById("wonder-list"),
  detail: document.getElementById("detail"),
  detailName: document.getElementById("detail-name"),
  detailBody: document.getElementById("detail-body"),
  detailClose: document.getElementById("detail-close"),
  languageButtons: Array.from(document.querySelectorAll("[data-lang]")),
};

const state = {
  lang: "zh",
  query: "",
  wonders: [],
  locationGroups: new Map(),
  selectedKey: "",
};

const customCRS = L.extend({}, L.CRS.Simple, {
  scale: (zoom) => Math.pow(2, zoom - MAX_ZOOM),
  zoom: (scale) => Math.log(scale) / Math.LN2 + MAX_ZOOM,
  wrapLng: [0, NATIVE_W],
});

function computeMinZoom() {
  const mapEl = document.getElementById("map");
  const viewportWidth = mapEl.clientWidth || window.innerWidth;
  const minZoom = Math.log2(viewportWidth / NATIVE_W) + MAX_ZOOM;
  return Math.max(0, Math.min(MAX_ZOOM, minZoom));
}

const map = L.map("map", {
  crs: customCRS,
  minZoom: computeMinZoom(),
  maxZoom: MAX_ZOOM,
  zoomControl: false,
  attributionControl: false,
  zoomSnap: 0.25,
  preferCanvas: true,
  maxBoundsViscosity: 1.0,
});

L.control.zoom({ position: "bottomright" }).addTo(map);

const visibleBounds = [[-NATIVE_H, 0], [0, NATIVE_W]];
L.tileLayer("tiles/{z}/{x}/{y}.png", {
  tileSize: TILE_SIZE,
  minZoom: 0,
  maxZoom: MAX_ZOOM,
  noWrap: false,
  bounds: visibleBounds,
}).addTo(map);
map.setMaxBounds([[-NATIVE_H, -Infinity], [0, Infinity]]);
map.fitBounds(visibleBounds);

window.addEventListener("resize", () => {
  const zoom = computeMinZoom();
  map.setMinZoom(zoom);
  if (map.getZoom() < zoom) {
    map.setZoom(zoom);
  }
});

const pinLayers = new Map();

function t(key) {
  return TEXT[state.lang][key] ?? EXTRA_TEXT[state.lang]?.[key] ?? EXTRA_TEXT.en?.[key] ?? key;
}

function localized(value) {
  if (!value || typeof value !== "object") {
    return String(value ?? "");
  }
  return value[state.lang] || value.en || value.zh || "";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatValue(value, row = {}) {
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }
  if (typeof value === "number") {
    if (row.value_kind === "percent") {
      return `${value >= 0 ? "+" : ""}${String(Number((value * 100).toFixed(row.decimals ?? 2))).replace(/\.0+$/, "")}%`;
    }
    if (row.value_kind === "already_percent") {
      return `${value >= 0 ? "+" : ""}${String(Number(value.toFixed(row.decimals ?? 2))).replace(/\.0+$/, "")}%`;
    }
    if (Number.isInteger(value)) {
      return `${value > 0 && row.value_kind !== "boolean" ? "+" : ""}${value}`;
    }
    return `${value > 0 ? "+" : ""}${String(Number(value.toFixed(row.decimals ?? 5))).replace(/\.0+$/, "")}`;
  }
  return String(value);
}

function pinColorForSize(size) {
  const colors = {
    small: "#78a47a",
    medium: "#c4b268",
    large: "#c1736f",
  };
  return colors[String(size || "").toLowerCase()] || "#9aa1a8";
}

function visibleWorldIndexes() {
  const bounds = map.getBounds();
  const west = Math.floor(bounds.getWest() / NATIVE_W) - 1;
  const east = Math.floor(bounds.getEast() / NATIVE_W) + 1;
  const indexes = [];
  for (let index = west; index <= east; index += 1) {
    indexes.push(index);
  }
  return indexes;
}

function px(x, y, worldIndex = 0) {
  return L.latLng(-y, x + worldIndex * NATIVE_W);
}

function filteredWonders() {
  const query = state.query.trim().toLowerCase();
  if (!query) {
    return state.wonders;
  }
  return state.wonders.filter((wonder) => wonder._haystack.includes(query));
}

function selectedWonder() {
  return state.wonders.find((wonder) => wonder.key === state.selectedKey) || null;
}

function locationKeyForWonder(wonder) {
  if (wonder.location_key) {
    return wonder.location_key;
  }
  if (Array.isArray(wonder.centroid)) {
    return `xy:${wonder.centroid.join(",")}`;
  }
  return wonder.key;
}

function groupedByLocation(wonders) {
  const groups = new Map();
  for (const wonder of wonders) {
    const locationKey = locationKeyForWonder(wonder);
    if (!groups.has(locationKey)) {
      groups.set(locationKey, []);
    }
    groups.get(locationKey).push(wonder);
  }
  return groups;
}

function rebuildLocationGroups() {
  state.locationGroups = groupedByLocation(state.wonders);
}

function localWondersFor(wonder) {
  if (!wonder) {
    return [];
  }
  return state.locationGroups.get(locationKeyForWonder(wonder)) || [wonder];
}

function filteredLocationGroups() {
  const visibleGroups = groupedByLocation(filteredWonders());
  return Array.from(visibleGroups, ([key, wonders]) => ({
    key,
    wonders,
    allWonders: state.locationGroups.get(key) || wonders,
  }));
}

function activeWonderForGroup(group) {
  return group.wonders.find((wonder) => wonder.key === state.selectedKey)
    || group.allWonders.find((wonder) => wonder.key === state.selectedKey)
    || group.wonders[0];
}

function groupCentroid(group) {
  const activeWonder = activeWonderForGroup(group);
  return activeWonder?.centroid || group.wonders[0]?.centroid || [0, 0];
}

function selectLocationGroup(locationKey, options = {}) {
  const localWonders = state.locationGroups.get(locationKey) || [];
  if (!localWonders.length) {
    return;
  }
  const currentIndex = localWonders.findIndex((wonder) => wonder.key === state.selectedKey);
  const nextIndex = currentIndex >= 0 ? (currentIndex + 1) % localWonders.length : 0;
  selectWonder(localWonders[nextIndex].key, options);
}

function selectAdjacentLocalWonder(step) {
  const wonder = selectedWonder();
  const localWonders = localWondersFor(wonder);
  if (!wonder || localWonders.length <= 1) {
    return;
  }
  const currentIndex = Math.max(0, localWonders.findIndex((item) => item.key === wonder.key));
  const nextIndex = (currentIndex + step + localWonders.length) % localWonders.length;
  selectWonder(localWonders[nextIndex].key, { pan: false });
}

function pinShapeForSize(size) {
  const shapes = {
    small: "circle",
    medium: "square",
    large: "large",
  };
  return shapes[String(size || "").toLowerCase()] || "circle";
}

function markerSizeClass(size) {
  const normalized = String(size || "").toLowerCase();
  return ["small", "medium", "large"].includes(normalized) ? normalized : "unknown";
}

function markerMetricsForSize(size, selected) {
  if (String(size || "").toLowerCase() === "large") {
    return selected
      ? { iconSize: [54, 38], iconAnchor: [16, 15] }
      : { iconSize: [48, 34], iconAnchor: [14, 13] };
  }
  return selected
    ? { iconSize: [44, 30], iconAnchor: [11, 11] }
    : { iconSize: [39, 26], iconAnchor: [9, 9] };
}

function markerIcon(wonder, selected, count) {
  const color = pinColorForSize(wonder.size);
  const shape = pinShapeForSize(wonder.size);
  const sizeClass = markerSizeClass(wonder.size);
  const metrics = markerMetricsForSize(wonder.size, selected);
  return L.divIcon({
    className: "",
    iconSize: metrics.iconSize,
    iconAnchor: metrics.iconAnchor,
    html: `
      <div class="wonder-marker wonder-marker-${sizeClass}${selected ? " selected" : ""}">
        <div class="wonder-pin wonder-pin-${shape}${selected ? " selected" : ""}" style="--pin-color:${color}"></div>
        <span class="wonder-count-badge">${escapeHtml(count)}</span>
      </div>
    `,
  });
}

function markerTooltip(group) {
  const localWonders = group.allWonders;
  if (localWonders.length <= 1) {
    return escapeHtml(localized(localWonders[0]?.name));
  }
  const locationName = localized(localWonders[0]?.location_name);
  const wonderNames = localWonders.map((wonder) => escapeHtml(localized(wonder.name))).join("<br>");
  return `<strong>${escapeHtml(locationName)}</strong><br>${wonderNames}`;
}

function syncPinLayers() {
  const wantedIndexes = new Set(visibleWorldIndexes());
  for (const [index, layer] of pinLayers) {
    if (!wantedIndexes.has(index)) {
      layer.remove();
      pinLayers.delete(index);
    }
  }
  for (const index of wantedIndexes) {
    const oldLayer = pinLayers.get(index);
    if (oldLayer) {
      oldLayer.remove();
    }
    const group = L.layerGroup();
    for (const groupInfo of filteredLocationGroups()) {
      const [x, y] = groupCentroid(groupInfo);
      const activeWonder = activeWonderForGroup(groupInfo);
      const selected = groupInfo.allWonders.some((wonder) => wonder.key === state.selectedKey);
      const count = groupInfo.allWonders.length;
      const marker = L.marker(px(x, y, index), {
        icon: markerIcon(activeWonder, selected, count),
        title: `${localized(activeWonder.name)} (${count})`,
        riseOnHover: true,
      });
      marker.on("click", () => selectLocationGroup(groupInfo.key, { pan: false }));
      marker.bindTooltip(markerTooltip(groupInfo), {
        direction: "top",
        opacity: 0.92,
        sticky: true,
      });
      group.addLayer(marker);
    }
    group.addTo(map);
    pinLayers.set(index, group);
  }
}

function renderLanguage() {
  elements.title.textContent = t("title");
  elements.subtitle.textContent = t("subtitle");
  elements.search.placeholder = t("search");
  elements.languageButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.lang === state.lang);
  });
}

function renderList() {
  const visible = filteredWonders();
  elements.count.textContent = t("count")(visible.length, state.wonders.length);
  elements.list.innerHTML = "";

  for (const wonder of visible) {
    const row = document.createElement("button");
    row.type = "button";
    row.className = `wonder-row${wonder.key === state.selectedKey ? " selected" : ""}`;
    row.setAttribute("role", "option");
    row.setAttribute("aria-selected", wonder.key === state.selectedKey ? "true" : "false");
    row.innerHTML = `
      <div class="wonder-row-main">
        <span class="wonder-name">${escapeHtml(localized(wonder.name))}</span>
        <span class="wonder-id">${escapeHtml(String(wonder.id))}</span>
      </div>
      <div class="wonder-meta">
        <span class="swatch" style="background:${pinColorForSize(wonder.size)}"></span>
        <span>${escapeHtml(localized(wonder.location_name))}</span>
        <span>${escapeHtml(localized(wonder.size_label))}</span>
      </div>
    `;
    row.addEventListener("click", () => selectWonder(wonder.key));
    elements.list.append(row);
  }
}

function metaLine(label, value) {
  return `<div><strong>${escapeHtml(label)}:</strong> ${escapeHtml(value)}</div>`;
}

function renderRowLabel(row) {
  const label = localized(row.label) || row.key;
  const key = row.key && row.key !== label
    ? `<span class="effect-code">${escapeHtml(row.key)}</span>`
    : "";
  const description = localized(row.description);
  const title = description ? ` title="${escapeHtml(description)}"` : "";
  return `<span class="effect-label"${title}>${escapeHtml(label)}${key}</span>`;
}

function renderRequirementList(rows) {
  if (!rows.length) {
    return `<div class="empty-note">-</div>`;
  }
  const anyRows = rows.filter((row) => row.logic === "any");
  const allRows = rows.filter((row) => row.logic !== "any");
  const renderItems = (items) => items.map((row) => `
    <div class="requirement-row">
      <span>${renderRowLabel(row)}</span>
    </div>
  `).join("");
  return `
    <div class="requirements-list">
      ${allRows.length ? renderItems(allRows) : ""}
      ${anyRows.length ? `<div class="requirements-any">${escapeHtml(t("anyOf"))}</div>${renderItems(anyRows)}` : ""}
    </div>
  `;
}

function renderEffectSection(effect) {
  const title = localized(effect.title);
  const valueLabel = localized(effect.value_label);
  const rows = Array.isArray(effect.rows) ? effect.rows : [];
  const metaEntries = Object.entries(effect.meta || {}).filter(([, value]) => value !== null && value !== "");
  const metaHtml = metaEntries.length
    ? `<div class="effect-meta">${metaEntries.map(([key, value]) => `<span class="meta-pill">${escapeHtml(key)}: ${escapeHtml(formatValue(value))}</span>`).join("")}</div>`
    : "";
  const rowHtml = rows.length
    ? `
      <div class="effect-table">
        <div class="effect-row header">
          <span>${escapeHtml(effect.scope === "reward" ? "Type" : t("modifier"))}</span>
          <span>${escapeHtml(valueLabel)}</span>
        </div>
        ${rows.map((row) => `
          <div class="effect-row">
            ${renderRowLabel(row)}
            <span class="effect-value">${escapeHtml(formatValue(row.value, row))}</span>
          </div>
        `).join("")}
      </div>
    `
    : "";

  return `
    <section class="effect-group">
      <div class="effect-head">
        <h4>${escapeHtml(title)}</h4>
        <span class="effect-scope">${escapeHtml(effect.scope || "")}</span>
      </div>
      ${metaHtml}
      ${rowHtml}
    </section>
  `;
}

function renderLocationSwitcher(wonder) {
  const localWonders = localWondersFor(wonder);
  if (localWonders.length <= 1) {
    return "";
  }
  const currentIndex = Math.max(0, localWonders.findIndex((item) => item.key === wonder.key));
  return `
    <section class="local-switcher">
      <div class="local-switcher-head">
        <span>${escapeHtml(t("localWonders"))}</span>
        <span>${currentIndex + 1} / ${localWonders.length}</span>
      </div>
      <div class="local-switcher-controls">
        <button type="button" class="local-cycle-button" data-local-shift="-1" aria-label="${escapeHtml(t("previousLocalWonder"))}" title="${escapeHtml(t("previousLocalWonder"))}">&lt;</button>
        <div class="local-wonder-tabs">
          ${localWonders.map((item) => `
            <button type="button" class="local-wonder-tab${item.key === wonder.key ? " selected" : ""}" data-local-wonder-key="${escapeHtml(item.key)}">
              ${escapeHtml(localized(item.name))}
            </button>
          `).join("")}
        </div>
        <button type="button" class="local-cycle-button" data-local-shift="1" aria-label="${escapeHtml(t("nextLocalWonder"))}" title="${escapeHtml(t("nextLocalWonder"))}">&gt;</button>
      </div>
    </section>
  `;
}

function bindDetailControls() {
  elements.detailBody.querySelectorAll("[data-local-wonder-key]").forEach((button) => {
    button.addEventListener("click", () => selectWonder(button.dataset.localWonderKey, { pan: false }));
  });
  elements.detailBody.querySelectorAll("[data-local-shift]").forEach((button) => {
    button.addEventListener("click", () => selectAdjacentLocalWonder(Number(button.dataset.localShift)));
  });
}

function renderDetail() {
  const wonder = selectedWonder();
  if (!wonder) {
    elements.detail.hidden = true;
    return;
  }

  elements.detail.hidden = false;
  elements.detailName.textContent = localized(wonder.name);
  const effects = Array.isArray(wonder.effects) ? wonder.effects : [];
  const requirements = Array.isArray(wonder.construction_requirements) ? wonder.construction_requirements : [];
  elements.detailBody.innerHTML = `
    <div class="detail-meta">
      ${metaLine(t("location"), localized(wonder.location_name))}
      ${metaLine(t("base"), localized(wonder.base_name))}
      ${metaLine(t("size"), localized(wonder.size_label))}
      ${metaLine(t("category"), localized(wonder.category_label))}
    </div>
    ${renderLocationSwitcher(wonder)}
    <p class="detail-description">${escapeHtml(localized(wonder.description))}</p>
    <section class="detail-section">
      <h3>${escapeHtml(t("requirements"))}</h3>
      ${renderRequirementList(requirements)}
    </section>
    <section class="detail-section">
      <h3>${escapeHtml(t("effects"))}</h3>
      ${effects.map(renderEffectSection).join("")}
    </section>
  `;
  bindDetailControls();
}

function selectWonder(key, options = {}) {
  state.selectedKey = key;
  renderList();
  renderDetail();
  syncPinLayers();
  if (options.pan === false) {
    return;
  }
  const wonder = selectedWonder();
  if (wonder) {
    const [x, y] = wonder.centroid;
    map.flyTo(px(x, y), Math.max(map.getZoom(), 4), { duration: 0.45 });
  }
}

function renderAll() {
  renderLanguage();
  renderList();
  renderDetail();
  syncPinLayers();
}

async function loadData() {
  const response = await fetch("data/unique_wonders.json");
  if (!response.ok) {
    throw new Error(`Failed to load unique_wonders.json: ${response.status}`);
  }
  const payload = await response.json();
  state.wonders = [...(payload.wonders || [])].sort((a, b) =>
    localized(a.name).localeCompare(localized(b.name), state.lang === "zh" ? "zh-CN" : "en")
  );
  for (const wonder of state.wonders) {
    wonder._haystack = [
      wonder.key,
      wonder.base_key,
      wonder.location_key,
      localized(wonder.name),
      wonder.name?.en,
      wonder.name?.zh,
      localized(wonder.location_name),
      wonder.location_name?.en,
      localized(wonder.base_name),
      wonder.base_name?.en,
      ...(wonder.construction_requirements || []).flatMap((row) => [
        row.key,
        localized(row.label),
        row.label?.en,
        row.label?.zh,
      ]),
      ...(wonder.effects || []).flatMap((effect) =>
        (effect.rows || []).flatMap((row) => [
          row.key,
          localized(row.label),
          row.label?.en,
          row.label?.zh,
        ])
      ),
    ].join(" ").toLowerCase();
  }
  rebuildLocationGroups();
  if (state.wonders.length) {
    state.selectedKey = state.wonders[0].key;
  }
  renderAll();
}

elements.search.addEventListener("input", () => {
  state.query = elements.search.value;
  renderList();
  syncPinLayers();
});

elements.detailClose.addEventListener("click", () => {
  state.selectedKey = "";
  renderAll();
});

elements.languageButtons.forEach((button) => {
  button.addEventListener("click", () => {
    state.lang = button.dataset.lang;
    state.wonders.sort((a, b) =>
      localized(a.name).localeCompare(localized(b.name), state.lang === "zh" ? "zh-CN" : "en")
    );
    for (const wonder of state.wonders) {
      wonder._haystack = [
        wonder.key,
        wonder.base_key,
        wonder.location_key,
        wonder.name?.en,
        wonder.name?.zh,
        wonder.location_name?.en,
        wonder.base_name?.en,
        wonder.base_name?.zh,
        ...(wonder.construction_requirements || []).flatMap((row) => [
          row.key,
          row.label?.en,
          row.label?.zh,
        ]),
        ...(wonder.effects || []).flatMap((effect) =>
          (effect.rows || []).flatMap((row) => [
            row.key,
            row.label?.en,
            row.label?.zh,
          ])
        ),
      ].join(" ").toLowerCase();
    }
    rebuildLocationGroups();
    renderAll();
  });
});

map.on("moveend zoomend", syncPinLayers);

loadData().catch((error) => {
  elements.list.innerHTML = `<div class="wonder-row"><span class="wonder-name">${escapeHtml(error.message)}</span></div>`;
  throw error;
});
