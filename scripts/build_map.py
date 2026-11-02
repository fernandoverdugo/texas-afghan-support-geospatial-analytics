from pathlib import Path
import json

import folium
from branca.element import MacroElement, Template
import numpy as np
import pandas as pd

from folium.plugins import Fullscreen, HeatMap

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "asp_zip_metrics.csv"
GEOMETRY_DIR = ROOT / "data" / "geometry"
OUTPUT = ROOT / "docs" / "index.html"


class OpenFreeMapLayer(MacroElement):
    def __init__(self, style_url="https://tiles.openfreemap.org/styles/positron"):
        super().__init__()
        self._name = "OpenFreeMapLayer"
        self.style_url = style_url
        self._template = Template(
            """
            {% macro script(this, kwargs) %}
            var open_free_map = L.maplibreGL({
                style: {{ this.style_url|tojson }}
            }).addTo({{ this._parent.get_name() }});
            {{ this._parent.get_name() }}.attributionControl.addAttribution(
                'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> &middot; <a href="https://openfreemap.org/">OpenFreeMap</a>'
            );
            {% endmacro %}
            """
        )


class PortfolioControls(MacroElement):
    def __init__(
        self,
        map_name,
        metric_layers,
        heat_layer,
        top_layer,
        legend_data,
        zip_lookup,
        city_centers,
        bounds,
    ):
        super().__init__()
        self._name = "PortfolioControls"
        self.map_name = map_name
        self.households_layer = metric_layers["total_households"]
        self.participants_layer = metric_layers["total_participants"]
        self.ra_layer = metric_layers["ra_total"]
        self.fwc_layer = metric_layers["fwc_total"]
        self.heat_layer = heat_layer
        self.top_layer = top_layer
        self.legend_data = json.dumps(legend_data)
        self.zip_lookup = json.dumps(zip_lookup)
        self.city_centers = json.dumps(city_centers)
        self.bounds = json.dumps(bounds)
        self._template = Template(
            """
            {% macro html(this, kwargs) %}
            <style>
              :root {
                --asp-bg: rgba(255,255,255,.96);
                --asp-border: rgba(15,23,42,.14);
                --asp-text: #0f172a;
                --asp-muted: #64748b;
                --asp-shadow: 0 8px 28px rgba(15,23,42,.14);
              }
              .asp-card {
                position: fixed;
                z-index: 10020;
                background: var(--asp-bg);
                color: var(--asp-text);
                border: 1px solid var(--asp-border);
                border-radius: 12px;
                box-shadow: var(--asp-shadow);
                font: 13px/1.35 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                backdrop-filter: blur(5px);
              }
              #asp-title {
                top: 12px;
                left: 50%;
                transform: translateX(-50%);
                width: min(760px, calc(100vw - 330px));
                padding: 10px 14px;
                text-align: center;
                pointer-events: none;
              }
              #asp-title .title { font-size: 17px; font-weight: 750; letter-spacing: -.01em; }
              #asp-title .sub { margin-top: 2px; color: var(--asp-muted); font-size: 12px; }
              #asp-controls {
                top: 76px;
                left: 12px;
                width: 264px;
                padding: 12px;
              }
              #asp-controls h4,
              #asp-legend h4 { margin: 0 0 8px; font-size: 12px; text-transform: uppercase; letter-spacing: .04em; color: #475569; }
              .asp-radio, .asp-check { display: flex; gap: 8px; align-items: center; margin: 7px 0; cursor: pointer; }
              .asp-radio input, .asp-check input { margin: 0; }
              .asp-divider { height: 1px; background: rgba(15,23,42,.1); margin: 10px 0; }
              .asp-search-row { display: flex; gap: 6px; }
              #asp-zip-input {
                min-width: 0;
                flex: 1;
                border: 1px solid rgba(15,23,42,.2);
                border-radius: 8px;
                padding: 7px 8px;
                font: inherit;
                outline: none;
              }
              #asp-zip-input:focus { border-color: rgba(15,23,42,.48); box-shadow: 0 0 0 2px rgba(15,23,42,.06); }
              .asp-btn {
                border: 1px solid rgba(15,23,42,.18);
                border-radius: 8px;
                background: #fff;
                color: #0f172a;
                padding: 7px 9px;
                cursor: pointer;
                font: 600 12px/1 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
              }
              .asp-btn:hover { background: #f8fafc; }
              .asp-btn:focus-visible,
              .asp-guide-toggle:focus-visible,
              .asp-guide-close:focus-visible,
              #asp-zip-input:focus-visible,
              .asp-radio input:focus-visible,
              .asp-check input:focus-visible {
                outline: 3px solid rgba(37,99,235,.42);
                outline-offset: 2px;
              }
              .asp-sr-only {
                position: absolute !important;
                width: 1px !important;
                height: 1px !important;
                padding: 0 !important;
                margin: -1px !important;
                overflow: hidden !important;
                clip: rect(0, 0, 0, 0) !important;
                white-space: nowrap !important;
                border: 0 !important;
              }
              .asp-cities { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 7px; }
              .asp-cities .asp-btn { padding: 6px 7px; font-weight: 500; }
              #asp-search-msg { min-height: 16px; margin-top: 5px; color: #b91c1c; font-size: 11px; }
              .asp-guide-toggle {
                width: 100%;
                display: flex;
                align-items: center;
                gap: 8px;
                border: 0;
                background: transparent;
                color: #334155;
                padding: 2px 0;
                cursor: pointer;
                font: 700 12px/1.2 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                text-align: left;
              }
              .asp-guide-toggle:hover { color: #0f172a; }
              .asp-guide-icon {
                width: 24px;
                height: 24px;
                flex: 0 0 24px;
                border: 1px solid rgba(15,23,42,.28);
                border-radius: 999px;
                background: #fff;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                font-weight: 800;
              }
              #asp-guide {
                display: none;
                width: 390px;
                max-width: calc(100vw - 24px);
                padding: 14px 16px 16px;
                overflow-y: auto;
                overflow-x: hidden;
                box-sizing: border-box;
              }
              #asp-guide.open { display: block; }
              .asp-guide-head {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                margin-bottom: 8px;
              }
              .asp-guide-head strong {
                font-size: 14px;
                letter-spacing: -.01em;
              }
              .asp-guide-close {
                border: 0;
                background: transparent;
                color: #64748b;
                cursor: pointer;
                padding: 2px 4px;
                font: 700 18px/1 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
              }
              .asp-guide-close:hover { color: #0f172a; }
              .asp-guide-section {
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid rgba(15,23,42,.1);
              }
              .asp-guide-section:first-of-type {
                margin-top: 0;
                padding-top: 0;
                border-top: 0;
              }
              .asp-guide-section h5 {
                margin: 0 0 6px;
                color: #334155;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: .035em;
              }
              .asp-guide-section p {
                margin: 5px 0;
                color: #334155;
              }
              .asp-guide-section ul {
                margin: 5px 0 5px 18px;
                padding: 0;
                color: #334155;
              }
              .asp-guide-section li { margin: 3px 0; }
              .asp-guide-term {
                color: #0f172a;
                font-weight: 750;
              }
              .asp-guide-note {
                color: #64748b;
                font-size: 11px;
              }
              #asp-legend {
                right: 12px;
                bottom: 24px;
                width: 228px;
                padding: 12px;
              }
              #asp-legend-title { font-size: 13px; font-weight: 700; margin-bottom: 8px; }
              .asp-legend-row { display: grid; grid-template-columns: 18px 1fr; gap: 8px; align-items: center; margin: 5px 0; }
              .asp-swatch { height: 15px; width: 18px; border-radius: 3px; border: 1px solid rgba(15,23,42,.15); }
              .asp-legend-note { margin-top: 8px; color: var(--asp-muted); font-size: 11px; }
              .leaflet-tooltip.asp-tooltip {
                background: rgba(255,255,255,.97);
                border: 1px solid rgba(15,23,42,.14);
                border-radius: 12px;
                box-shadow: 0 12px 34px rgba(15,23,42,.18);
                color: #0f172a;
                padding: 0;
                max-width: min(520px, calc(100vw - 32px));
                max-height: calc(100vh - 28px);
                overflow-y: auto;
                overflow-x: hidden;
                box-sizing: border-box;
              }
              .leaflet-tooltip.asp-tooltip::-webkit-scrollbar {
                width: 7px;
              }
              .leaflet-tooltip.asp-tooltip::-webkit-scrollbar-thumb {
                background: rgba(71,85,105,.35);
                border-radius: 999px;
              }
              .leaflet-tooltip.asp-tooltip table {
                margin: 0;
                border-collapse: collapse;
                width: 100%;
              }
              .leaflet-tooltip.asp-tooltip td {
                padding: 0;
                text-align: initial;
                font-weight: 400;
              }
              .asp-tip {
                width: 470px;
                max-width: calc(100vw - 56px);
                padding: 13px 14px 14px;
                font: 13px/1.35 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
              }
              .asp-tip-top {
                display: flex;
                align-items: baseline;
                justify-content: space-between;
                gap: 18px;
                margin-bottom: 7px;
              }
              .asp-tip-zip {
                font-size: 15px;
                font-weight: 800;
                letter-spacing: -.01em;
              }
              .asp-tip-city {
                color: #475569;
                font-weight: 650;
              }
              .asp-tip-highlight {
                display: inline-block;
                margin: 0 0 8px;
                padding: 3px 7px;
                border-radius: 999px;
                background: #f8fafc;
                border: 1px solid rgba(15,23,42,.12);
                color: #475569;
                font-size: 11px;
                font-weight: 650;
              }
              .asp-tip-section {
                margin-top: 9px;
                padding-top: 8px;
                border-top: 1px solid rgba(15,23,42,.13);
              }
              .asp-tip-section-title {
                margin: 0 0 5px;
                text-align: center;
                font-size: 13px;
                font-weight: 800;
                color: #1e293b;
              }
              .asp-tip-row {
                display: grid;
                grid-template-columns: minmax(190px, 1fr) auto;
                gap: 18px;
                align-items: baseline;
                padding: 2px 0;
              }
              .asp-tip-label {
                color: #475569;
                font-weight: 650;
              }
              .asp-tip-value {
                text-align: right;
                color: #0f172a;
                font-weight: 650;
                white-space: nowrap;
              }
              .asp-tip-total .asp-tip-label,
              .asp-tip-total .asp-tip-value {
                font-weight: 800;
              }
              .asp-tip-change {
                color: #475569;
                font-weight: 550;
              }
              @media (max-width: 560px) {
                .asp-tip {
                  width: 340px;
                  max-width: calc(100vw - 48px);
                  padding: 10px 11px 11px;
                  font-size: 11px;
                }
                .asp-tip-row {
                  grid-template-columns: minmax(145px, 1fr) auto;
                  gap: 10px;
                }
                .asp-tip-section-title { font-size: 12px; }
              }
              .leaflet-control-attribution { font-size: 10px; }
              .maplibregl-canvas { outline: none; }

              @media (max-width: 820px) {
                #asp-title {
                  top: 8px;
                  width: calc(100vw - 24px);
                  padding: 8px 10px;
                }
                #asp-title .title { font-size: 14px; }
                #asp-title .sub { font-size: 10px; }
                #asp-controls {
                  top: 70px;
                  left: 8px;
                  width: 220px;
                  max-height: calc(100vh - 150px);
                  overflow-y: auto;
                  padding: 10px;
                }
                #asp-guide { width: 360px; }
                #asp-legend { right: 8px; bottom: 20px; width: 184px; padding: 10px; }
              }
              @media (max-width: 560px) {
                #asp-title .sub { display: none; }
                #asp-controls { width: 188px; font-size: 11px; }
                #asp-controls h4, #asp-legend h4 { font-size: 10px; }
                #asp-guide { width: calc(100vw - 16px); font-size: 11px; }
                #asp-legend { width: 158px; font-size: 10px; }
                .asp-cities { display: none; }
              }
            </style>

            <div id="asp-title" class="asp-card">
              <div class="title">Afghan Support Program — Texas Geospatial Analytics</div>
              <div class="sub">Synthetic ZIP-level portfolio data • 192 ZIP codes across five metropolitan areas</div>
            </div>

            <div id="asp-controls" class="asp-card" role="region" aria-label="Map controls">
              <h4 id="asp-metric-heading">Metric</h4>
              <div role="radiogroup" aria-labelledby="asp-metric-heading">
              <label class="asp-radio"><input type="radio" name="asp-metric" value="total_households" checked> Total households</label>
              <label class="asp-radio"><input type="radio" name="asp-metric" value="total_participants"> Total participants</label>
              <label class="asp-radio"><input type="radio" name="asp-metric" value="ra_total"> Rental assistance</label>
              <label class="asp-radio"><input type="radio" name="asp-metric" value="fwc_total"> Financial wellness attendance</label>

              </div>

              <div class="asp-divider"></div>
              <h4>Optional overlays</h4>
              <label class="asp-check"><input id="asp-heat" type="checkbox"> Participant heat map</label>
              <label class="asp-check"><input id="asp-top" type="checkbox"> Top-10 RA ZIPs by metro</label>

              <div class="asp-divider"></div>
              <h4>Navigate</h4>
              <label for="asp-zip-input" class="asp-sr-only">Five-digit ZIP code</label>
              <div class="asp-search-row">
                <input id="asp-zip-input" type="text" inputmode="numeric" maxlength="5" pattern="[0-9]{5}" autocomplete="postal-code" placeholder="ZIP code" aria-describedby="asp-search-msg">
                <button id="asp-zip-go" class="asp-btn" type="button" aria-label="Go to ZIP code">Go</button>
              </div>
              <div id="asp-search-msg" role="status" aria-live="polite"></div>
              <div class="asp-cities">
                <button class="asp-btn" data-city="Austin" type="button">Austin</button>
                <button class="asp-btn" data-city="Dallas" type="button">Dallas</button>
                <button class="asp-btn" data-city="Fort Worth" type="button">Fort Worth</button>
                <button class="asp-btn" data-city="Houston" type="button">Houston</button>
                <button class="asp-btn" data-city="San Antonio" type="button">San Antonio</button>
                <button id="asp-reset" class="asp-btn" type="button">Reset</button>
              </div>

              <div class="asp-divider"></div>
              <button id="asp-guide-toggle" class="asp-guide-toggle" type="button"
                      aria-expanded="false" aria-controls="asp-guide">
                <span class="asp-guide-icon" aria-hidden="true">?</span>
                <span>Map Guide</span>
              </button>
            </div>

            <div id="asp-guide" class="asp-card" role="dialog" aria-label="Map Guide" aria-modal="false" aria-hidden="true">
              <div class="asp-guide-head">
                <strong>Map Guide</strong>
                <button id="asp-guide-close" class="asp-guide-close" type="button" aria-label="Close Map Guide">×</button>
              </div>

              <div class="asp-guide-section">
                <h5>How to read the map</h5>
                <p><span class="asp-guide-term">Colors:</span> Choropleth layers use <em>quantile</em> bins so each color band contains a similar share of ZIP codes.</p>
                <ul>
                  <li><strong>Darker</strong> shades indicate higher values for the active metric.</li>
                  <li>The legend shows the numeric range represented by each shade.</li>
                </ul>
                <p><span class="asp-guide-term">Growth labels:</span> <strong>MoM</strong> means month-over-month change compared with the prior month, shown in parentheses such as <strong>+12%</strong> or <strong>−5%</strong>.</p>
                <p><span class="asp-guide-term">ZIP details:</span> Hover over a ZIP for a quick view, or click/tap it to keep the detail card open.</p>
                <p><span class="asp-guide-term">Highlights:</span> ZIPs are flagged when total rental assistance is in the top 10 within their metro area.</p>
              </div>

              <div class="asp-guide-section">
                <h5>What the metrics mean</h5>
                <p><span class="asp-guide-term">Total Households</span><br>
                Unique Primary Applicants (PAs) who are ASP-eligible and received at least one deposited/cashed rental-assistance check during July–September. Each PA is counted once and attributed to the program ZIP code.</p>

                <p><span class="asp-guide-term">Total Participants (PA + HHM)</span><br>
                Unique ASP-eligible clients, including Primary Applicants (PAs) and Household Members (HHMs). Each client is counted once and attributed to the program ZIP code.</p>

                <p><span class="asp-guide-term">Rental Assistance</span><br>
                Monthly rental-assistance amounts distributed in July, August, and September. Total RA is the three-month sum for the ZIP code.</p>

                <p><span class="asp-guide-term">Financial Wellness Course (FWC)</span><br>
                July/August/September values show unique attendees within each month. FWC Total shows unique attendees across the full July–September period.</p>
              </div>

              <div class="asp-guide-section">
                <h5>Optional overlays</h5>
                <p><span class="asp-guide-term">Participant heat map:</span> Shows the geographic concentration of total participants.</p>
                <p><span class="asp-guide-term">Top-10 RA ZIPs by metro:</span> Adds markers for the ten highest-rental-assistance ZIP codes within each metro area.</p>
                <p class="asp-guide-note">All values in this portfolio project are synthetic and shown at the aggregate ZIP-code level.</p>
              </div>
            </div>

            <div id="asp-legend" class="asp-card">
              <h4>Legend</h4>
              <div id="asp-legend-title"></div>
              <div id="asp-legend-rows"></div>
              <div class="asp-legend-note">Darker shades indicate higher values. Bands use within-metric quantiles.</div>
            </div>
            {% endmacro %}

            {% macro script(this, kwargs) %}
            (function(){
              const map = {{ this.map_name }};
              const metricLayers = {
                total_households: {{ this.households_layer }},
                total_participants: {{ this.participants_layer }},
                ra_total: {{ this.ra_layer }},
                fwc_total: {{ this.fwc_layer }}
              };
              const heatLayer = {{ this.heat_layer }};
              const topLayer = {{ this.top_layer }};
              const legendData = {{ this.legend_data|safe }};
              const zipLookup = {{ this.zip_lookup|safe }};
              const cityCenters = {{ this.city_centers|safe }};
              const initialBounds = {{ this.bounds|safe }};

              function updateLegend(key){
                const data = legendData[key];
                document.getElementById('asp-legend-title').textContent = data.title;
                const rows = document.getElementById('asp-legend-rows');
                rows.innerHTML = '';
                data.rows.forEach(item => {
                  const row = document.createElement('div');
                  row.className = 'asp-legend-row';
                  const swatch = document.createElement('div');
                  swatch.className = 'asp-swatch';
                  swatch.style.background = item.color;
                  const label = document.createElement('div');
                  label.textContent = item.label;
                  row.appendChild(swatch);
                  row.appendChild(label);
                  rows.appendChild(row);
                });
              }

              function setMetric(key){
                Object.entries(metricLayers).forEach(([name, layer]) => {
                  if (name === key) {
                    if (!map.hasLayer(layer)) map.addLayer(layer);
                  } else if (map.hasLayer(layer)) {
                    map.removeLayer(layer);
                  }
                });
                const radio = document.querySelector(`input[name="asp-metric"][value="${key}"]`);
                if (radio) radio.checked = true;
                updateLegend(key);
              }

              document.querySelectorAll('input[name="asp-metric"]').forEach(radio => {
                radio.addEventListener('change', function(){ setMetric(this.value); });
              });

              document.getElementById('asp-heat').addEventListener('change', function(){
                if (this.checked) map.addLayer(heatLayer); else map.removeLayer(heatLayer);
              });
              document.getElementById('asp-top').addEventListener('change', function(){
                if (this.checked) map.addLayer(topLayer); else map.removeLayer(topLayer);
              });

              function goZip(){
                const input = document.getElementById('asp-zip-input');
                const msg = document.getElementById('asp-search-msg');
                const z = (input.value || '').trim();
                if (!z) {
                  msg.textContent = 'Enter a 5-digit ZIP code.';
                } else if (!/^\\d{5}$/.test(z)) {
                  msg.textContent = 'ZIP code must contain exactly 5 digits.';
                } else if (zipLookup[z]) {
                  msg.textContent = '';
                  map.flyTo(zipLookup[z], 12, {duration: .8});
                } else {
                  msg.textContent = 'ZIP not found in this dataset.';
                }
              }
              document.getElementById('asp-zip-go').addEventListener('click', goZip);
              document.getElementById('asp-zip-input').addEventListener('keydown', function(e){
                if (e.key === 'Enter') goZip();
              });

              document.querySelectorAll('[data-city]').forEach(btn => {
                btn.addEventListener('click', function(){
                  const center = cityCenters[this.dataset.city];
                  if (center) map.flyTo(center, 10, {duration: .8});
                });
              });
              document.getElementById('asp-reset').addEventListener('click', function(){
                map.fitBounds(initialBounds, {padding: [34,34]});
              });

              const controlsEl = document.getElementById('asp-controls');
              const guideEl = document.getElementById('asp-guide');
              const guideToggle = document.getElementById('asp-guide-toggle');
              const guideClose = document.getElementById('asp-guide-close');

              function placeGuide(){
                if (!guideEl.classList.contains('open')) return;
                const controlRect = controlsEl.getBoundingClientRect();
                const mapRect = map.getContainer().getBoundingClientRect();
                const gap = 8;
                const pad = 8;

                let left = controlRect.left;
                const top = controlRect.bottom + gap;

                const guideWidth = guideEl.offsetWidth;
                if (left + guideWidth > mapRect.right - pad) {
                  left = Math.max(mapRect.left + pad, mapRect.right - guideWidth - pad);
                }

                guideEl.style.left = `${Math.round(left)}px`;
                guideEl.style.top = `${Math.round(top)}px`;
                guideEl.style.maxHeight = `${Math.max(160, Math.round(mapRect.bottom - top - pad))}px`;
              }

              function setGuideOpen(open){
                guideEl.classList.toggle('open', open);
                guideEl.setAttribute('aria-hidden', String(!open));
                guideToggle.setAttribute('aria-expanded', String(open));
                if (open) {
                  requestAnimationFrame(placeGuide);
                  setTimeout(() => guideClose.focus(), 0);
                }
              }

              guideToggle.addEventListener('click', function(){
                setGuideOpen(!guideEl.classList.contains('open'));
              });
              guideClose.addEventListener('click', function(){
                setGuideOpen(false);
                guideToggle.focus();
              });
              document.addEventListener('keydown', function(e){
                if (e.key === 'Escape' && guideEl.classList.contains('open')) {
                  setGuideOpen(false);
                  guideToggle.focus();
                }
              });
              map.on('resize', placeGuide);
              window.addEventListener('resize', placeGuide);

              let tooltipFitFrame = null;

              function fitOpenTooltip(){
                const mapEl = map.getContainer();
                const tip = mapEl.querySelector('.leaflet-tooltip.asp-tooltip');
                if (!tip) return;

                tip.style.marginLeft = '0px';
                tip.style.marginTop = '0px';

                const mapRect = mapEl.getBoundingClientRect();
                const tipRect = tip.getBoundingClientRect();
                const pad = 14;

                const leftEdge = mapRect.left + pad;
                const rightEdge = mapRect.right - pad;
                const topEdge = mapRect.top + pad;
                const bottomEdge = mapRect.bottom - pad;

                let dx = 0;
                let dy = 0;

                if (tipRect.left < leftEdge) {
                  dx += leftEdge - tipRect.left;
                }
                if (tipRect.right + dx > rightEdge) {
                  dx -= (tipRect.right + dx) - rightEdge;
                }
                if (tipRect.top < topEdge) {
                  dy += topEdge - tipRect.top;
                }
                if (tipRect.bottom + dy > bottomEdge) {
                  dy -= (tipRect.bottom + dy) - bottomEdge;
                }

                tip.style.marginLeft = `${Math.round(dx)}px`;
                tip.style.marginTop = `${Math.round(dy)}px`;
              }

              function scheduleTooltipFit(){
                if (tooltipFitFrame !== null) {
                  cancelAnimationFrame(tooltipFitFrame);
                }
                tooltipFitFrame = requestAnimationFrame(() => {
                  tooltipFitFrame = null;
                  fitOpenTooltip();
                });
              }

              map.on('tooltipopen', function(){
                scheduleTooltipFit();
                setTimeout(scheduleTooltipFit, 0);
              });
              map.on('zoomend moveend resize', scheduleTooltipFit);
              window.addEventListener('resize', scheduleTooltipFit);

              const tooltipPane = map.getPane('tooltipPane');
              if (tooltipPane && window.MutationObserver) {
                new MutationObserver(scheduleTooltipFit).observe(
                  tooltipPane,
                  {childList: true, subtree: true}
                );
              }

              setMetric('total_households');
            })();
            {% endmacro %}
            """
        )


def geojson_bounds(geojson):
    lats = []
    lons = []

    def collect(coords):
        if not coords:
            return
        if isinstance(coords[0], (int, float)):
            lon, lat = coords[:2]
            lons.append(float(lon))
            lats.append(float(lat))
            return
        for item in coords:
            collect(item)

    for feature in geojson.get("features", []):
        geometry = feature.get("geometry") or {}
        collect(geometry.get("coordinates", []))

    if not lats or not lons:
        return [[25.8, -106.7], [36.6, -93.5]]

    return [[min(lats), min(lons)], [max(lats), max(lons)]]


METRICS = [
    (
        "total_households",
        "Total Households",
        ["#fee8c8", "#fdbb84", "#fc8d59", "#ef6548", "#d7301f", "#990000"],
        False,
    ),
    (
        "total_participants",
        "Total Participants",
        ["#f1eef6", "#d4b9da", "#c994c7", "#df65b0", "#e7298a", "#ce1256"],
        False,
    ),
    (
        "ra_total",
        "Total Rental Assistance",
        ["#ffffcc", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0", "#225ea8"],
        True,
    ),
    (
        "fwc_total",
        "Financial Wellness Attendance",
        ["#f7fcfd", "#e0ecf4", "#bfd3e6", "#9ebcda", "#8c96c6", "#8856a7"],
        False,
    ),
]


def quantile_edges(series, bins=6):
    values = pd.to_numeric(series, errors="coerce").dropna().to_numpy()
    edges = np.quantile(values, np.linspace(0, 1, bins + 1))
    edges = np.unique(edges)
    if len(edges) < 2:
        edges = np.array([values.min(), values.max() + 1])
    return edges.tolist()


def color_for(value, edges, colors):
    if value is None or pd.isna(value):
        return "#d9d9d9"
    index = int(np.searchsorted(edges[1:-1], float(value), side="right"))
    return colors[min(index, len(colors) - 1)]


def make_style(metric, edges, colors):
    def style(feature):
        value = feature["properties"].get(metric)
        return {
            "fillColor": color_for(value, edges, colors),
            "color": "#64748b",
            "weight": 0.75,
            "fillOpacity": 0.76,
        }
    return style


def format_value(value, money=False):
    if money:
        return f"${float(value):,.0f}"
    return f"{float(value):,.0f}"


def legend_rows(edges, colors, money=False):
    rows = []
    for i in range(len(edges) - 1):
        a = format_value(edges[i], money)
        b = format_value(edges[i + 1], money)
        rows.append({"color": colors[i], "label": f"{a} – {b}"})
    return rows


def pct_change(current, previous):
    if pd.isna(current) or pd.isna(previous) or float(previous) == 0:
        return None
    return (float(current) - float(previous)) / float(previous) * 100


def pct_display(value):
    if value is None or pd.isna(value):
        return ""
    rounded = int(round(float(value)))
    if rounded == 0:
        return ""
    sign = "+" if rounded > 0 else "−"
    return f" <span class='asp-tip-change'>({sign}{abs(rounded)}%)</span>"


def money_display(value):
    if pd.isna(value):
        return "—"
    return f"${float(value):,.0f}"


def count_display(value):
    if pd.isna(value):
        return "—"
    return f"{float(value):,.0f}"


def tooltip_row(label, value, total=False):
    total_class = " asp-tip-total" if total else ""
    return (
        f"<div class='asp-tip-row{total_class}'>"
        f"<div class='asp-tip-label'>{label}</div>"
        f"<div class='asp-tip-value'>{value}</div>"
        f"</div>"
    )


def build_tooltip_html(row):
    enroll_aug_change = pct_change(
        row["enrolled_august_cumulative"],
        row["enrolled_july_cumulative"],
    )
    enroll_sep_change = pct_change(
        row["enrolled_september_cumulative"],
        row["enrolled_august_cumulative"],
    )
    ra_aug_change = pct_change(row["ra_august"], row["ra_july"])
    ra_sep_change = pct_change(row["ra_september"], row["ra_august"])
    ra_total_change = pct_change(row["ra_total"], row["ra_july"])
    fwc_aug_change = pct_change(row["fwc_august"], row["fwc_july"])
    fwc_sep_change = pct_change(row["fwc_september"], row["fwc_august"])

    highlight = ""
    if bool(row["top10_ra_city"]):
        highlight = (
            f"<div class='asp-tip-highlight'>"
            f"Top-10 rental assistance ZIP in {row['city']}"
            f"</div>"
        )

    enrollment_rows = "".join(
        [
            tooltip_row(
                "Total Households Enrolled",
                count_display(row["total_households"]),
                total=True,
            ),
            tooltip_row("By July", count_display(row["enrolled_july_cumulative"])),
            tooltip_row(
                "By August (MoM)",
                count_display(row["enrolled_august_cumulative"])
                + pct_display(enroll_aug_change),
            ),
            tooltip_row(
                "By September (MoM)",
                count_display(row["enrolled_september_cumulative"])
                + pct_display(enroll_sep_change),
            ),
            tooltip_row(
                "Total Participants (PA + HHM)",
                count_display(row["total_participants"]),
                total=True,
            ),
        ]
    )

    ra_rows = "".join(
        [
            tooltip_row("July RA", money_display(row["ra_july"])),
            tooltip_row(
                "August RA (MoM)",
                money_display(row["ra_august"]) + pct_display(ra_aug_change),
            ),
            tooltip_row(
                "September RA (MoM)",
                money_display(row["ra_september"]) + pct_display(ra_sep_change),
            ),
            tooltip_row(
                "Total RA (since July)",
                money_display(row["ra_total"]) + pct_display(ra_total_change),
                total=True,
            ),
        ]
    )

    fwc_rows = "".join(
        [
            tooltip_row("July FWC attendance", count_display(row["fwc_july"])),
            tooltip_row(
                "August FWC attendance (MoM)",
                count_display(row["fwc_august"]) + pct_display(fwc_aug_change),
            ),
            tooltip_row(
                "September FWC attendance (MoM)",
                count_display(row["fwc_september"]) + pct_display(fwc_sep_change),
            ),
            tooltip_row(
                "Total FWC attendance",
                count_display(row["fwc_total"]),
                total=True,
            ),
        ]
    )

    return (
        "<div class='asp-tip'>"
        "<div class='asp-tip-top'>"
        f"<div class='asp-tip-zip'>ZIP {row.name}</div>"
        f"<div class='asp-tip-city'>{row['city']}</div>"
        "</div>"
        f"{highlight}"
        "<div class='asp-tip-section'>"
        "<div class='asp-tip-section-title'>ASP Participant Enrollment</div>"
        f"{enrollment_rows}"
        "</div>"
        "<div class='asp-tip-section'>"
        "<div class='asp-tip-section-title'>Rental Assistance Distributed</div>"
        f"{ra_rows}"
        "</div>"
        "<div class='asp-tip-section'>"
        "<div class='asp-tip-section-title'>Financial Wellness Course (unique attendees)</div>"
        f"{fwc_rows}"
        "</div>"
        "</div>"
    )


def enrich_geojson(geojson, df):
    lookup = df.set_index("zip_code")
    for feature in geojson.get("features", []):
        props = feature.setdefault("properties", {})
        zip_code = str(props.get("zip_code", props.get("Zip", ""))).zfill(5)
        if zip_code not in lookup.index:
            continue
        row = lookup.loc[zip_code].copy()
        row.name = zip_code
        props["zip_code"] = zip_code
        props["city"] = row["city"]
        props["total_households"] = float(row["total_households"])
        props["total_participants"] = float(row["total_participants"])
        props["ra_total"] = float(row["ra_total"])
        props["fwc_total"] = float(row["fwc_total"])
        props["tooltip_html"] = build_tooltip_html(row)
    return geojson


def main():
    df = pd.read_csv(DATA, dtype={"zip_code": str})
    geometry_files = sorted(GEOMETRY_DIR.glob("asp_zip_geometries_part_*.geojson"))
    if not geometry_files:
        raise FileNotFoundError("No ZIP geometry files found in data/geometry.")
    geojson = {"type": "FeatureCollection", "features": []}
    for geometry_file in geometry_files:
        part = json.loads(geometry_file.read_text(encoding="utf-8"))
        geojson["features"].extend(part.get("features", []))
    geojson = enrich_geojson(geojson, df)
    bounds = geojson_bounds(geojson)

    m = folium.Map(
        location=[31.0, -99.0],
        zoom_start=6,
        tiles=None,
        control_scale=True,
        zoom_control=True,
        prefer_canvas=True,
    )

    OpenFreeMapLayer().add_to(m)
    m.fit_bounds(bounds, padding=(34, 34))
    Fullscreen(position="bottomleft", title="Full screen", title_cancel="Exit full screen").add_to(m)

    tooltip_fields = ["tooltip_html"]


    metric_layer_names = {}
    legend_data = {}

    for i, (metric, name, colors, money) in enumerate(METRICS):
        edges = quantile_edges(df[metric])
        group = folium.FeatureGroup(name=name, show=(i == 0), overlay=True, control=False)
        folium.GeoJson(
            geojson,
            name=name,