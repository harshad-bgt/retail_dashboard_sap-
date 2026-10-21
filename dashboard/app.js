/**
 * Retail Sales Intelligence & Forecasting Platform
 * Interactive Dashboard Logic & State Controller
 */

// Global State
let rawData = [];
let forecastData = [];
let chartInstances = {};
let currentPresSectionIdx = 0;

const PRES_SECTIONS = [
  { id: "secExecutive", name: "Section 1: Executive Overview" },
  { id: "secTrends", name: "Section 2: Sales & Profit Trends" },
  { id: "secForecast", name: "Section 3: Short-Term Sales Forecast" },
  { id: "secCategory", name: "Section 4: Category Performance" },
  { id: "secRegional", name: "Section 5: Regional Analysis" },
  { id: "secProducts", name: "Section 6: Product Leaders & Laggards" },
  { id: "secCustomer", name: "Section 7: Customer Segments" },
  { id: "secDiscount", name: "Section 8: Discount & Margin Sensitivity" },
  { id: "secInsights", name: "Section 9: Business Insights" },
  { id: "secRecommendations", name: "Section 10: Management Action Plan" }
];

document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await loadDashboardData();
});

function setupEventListeners() {
  document.getElementById("filterYear").addEventListener("change", applyFilters);
  document.getElementById("filterCategory").addEventListener("change", applyFilters);
  document.getElementById("filterRegion").addEventListener("change", applyFilters);
  document.getElementById("filterSegment").addEventListener("change", applyFilters);
  document.getElementById("btnResetFilters").addEventListener("click", resetFilters);

  // Modal handlers
  const modal = document.getElementById("modalArchitecture");
  document.getElementById("btnArchitectureModal").addEventListener("click", () => {
    modal.style.display = "flex";
  });
  document.getElementById("btnCloseModal").addEventListener("click", () => {
    modal.style.display = "none";
  });
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  // Presentation mode toggle
  const btnPres = document.getElementById("btnTogglePresentation");
  btnPres.addEventListener("click", togglePresentationMode);
  document.getElementById("btnExitPres").addEventListener("click", togglePresentationMode);

  document.getElementById("btnPresNext").addEventListener("click", () => {
    if (currentPresSectionIdx < PRES_SECTIONS.length - 1) {
      currentPresSectionIdx++;
      scrollToPresSection();
    }
  });

  document.getElementById("btnPresPrev").addEventListener("click", () => {
    if (currentPresSectionIdx > 0) {
      currentPresSectionIdx--;
      scrollToPresSection();
    }
  });
}

function togglePresentationMode() {
  const isPres = document.body.classList.toggle("presentation-mode");
  const nav = document.getElementById("presentationNav");
  const btnTxt = document.getElementById("txtPresentationMode");

  if (isPres) {
    nav.style.display = "flex";
    btnTxt.textContent = "Exit Presentation";
    currentPresSectionIdx = 0;
    scrollToPresSection();
  } else {
    nav.style.display = "none";
    btnTxt.textContent = "Presentation Mode";
  }
}

function scrollToPresSection() {
  const sec = PRES_SECTIONS[currentPresSectionIdx];
  const el = document.getElementById(sec.id);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    document.getElementById("presSectionIndicator").textContent = sec.name;
  }
}

async function loadDashboardData() {
  try {
    const res = await fetch("/api/data");
    const json = await res.json();
    rawData = json.records || [];
    forecastData = json.forecast || [];
  } catch (err) {
    console.warn("Could not fetch from /api/data, attempting embedded fallback...", err);
    // If running from static file:/// URL or standalone web server without API
    if (window.EMBEDDED_DATA) {
      rawData = window.EMBEDDED_DATA.records || [];
      forecastData = window.EMBEDDED_DATA.forecast || [];
    }
  }

  applyFilters();
}

function resetFilters() {
  document.getElementById("filterYear").value = "ALL";
  document.getElementById("filterCategory").value = "ALL";
  document.getElementById("filterRegion").value = "ALL";
  document.getElementById("filterSegment").value = "ALL";
  applyFilters();
}

function applyFilters() {
  const year = document.getElementById("filterYear").value;
  const category = document.getElementById("filterCategory").value;
  const region = document.getElementById("filterRegion").value;
  const segment = document.getElementById("filterSegment").value;

  const filtered = rawData.filter(d => {
    if (year !== "ALL" && String(d.year) !== year) return false;
    if (category !== "ALL" && d.category !== category) return false;
    if (region !== "ALL" && d.region !== region) return false;
    if (segment !== "ALL" && d.customer_segment !== segment) return false;
    return true;
  });

  updateRecordCount(filtered.length, rawData.length);
  updateKPIs(filtered);
  renderMonthlyTrendsChart(filtered);
  renderForecastChart(filtered, forecastData);
  renderCategoryCharts(filtered);
  renderRegionalChartsAndTable(filtered);
  renderProductTables(filtered);
  renderCustomerSegmentCharts(filtered);
  renderDiscountTierTable(filtered);
}

function updateRecordCount(current, total) {
  const lbl = document.getElementById("lblRecordCount");
  lbl.textContent = `Showing ${current.toLocaleString()} of ${total.toLocaleString()} transactions`;
}

function updateKPIs(data) {
  let rev = 0, cost = 0, profit = 0, qty = 0;
  const ordersSet = new Set();
  const customersSet = new Set();

  data.forEach(d => {
    rev += d.revenue;
    cost += d.cost;
    profit += d.profit;
    qty += d.quantity;
    ordersSet.add(d.order_id);
    customersSet.add(d.customer_id);
  });

  const ordersCount = ordersSet.size;
  const marginPct = rev > 0 ? (profit / rev) * 100 : 0;
  const aov = ordersCount > 0 ? rev / ordersCount : 0;

  document.getElementById("valTotalRevenue").textContent = `$${rev.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  document.getElementById("valTotalProfit").textContent = `$${profit.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  document.getElementById("valProfitMargin").textContent = `${marginPct.toFixed(2)}% Margin`;
  document.getElementById("valTotalOrders").textContent = ordersCount.toLocaleString();
  document.getElementById("valTotalUnits").textContent = `${qty.toLocaleString()} Units`;
  document.getElementById("valTotalCustomers").textContent = customersSet.size.toLocaleString();
  document.getElementById("valAOV").textContent = `$${aov.toFixed(2)}`;
  document.getElementById("valTotalCost").textContent = `$${cost.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// -----------------------------------------------------------------------------
// Chart Renderers
// -----------------------------------------------------------------------------
function destroyChart(key) {
  if (chartInstances[key]) {
    chartInstances[key].destroy();
    delete chartInstances[key];
  }
}

function renderMonthlyTrendsChart(data) {
  destroyChart("trends");
  const ctx = document.getElementById("chartMonthlyTrends").getContext("2d");

  // Group by YYYY-MM
  const monthsMap = {};
  data.forEach(d => {
    const ym = d.order_date.substring(0, 7); // YYYY-MM
    if (!monthsMap[ym]) {
      monthsMap[ym] = { revenue: 0, profit: 0, date: d.order_date };
    }
    monthsMap[ym].revenue += d.revenue;
    monthsMap[ym].profit += d.profit;
  });

  const sortedKeys = Object.keys(monthsMap).sort();
  const labels = sortedKeys.map(k => {
    const [y, m] = k.split("-");
    const d = new Date(y, m - 1);
    return d.toLocaleString("en-US", { month: "short", year: "2-digit" });
  });

  const revData = sortedKeys.map(k => (monthsMap[k].revenue / 1000).toFixed(2));
  const profitData = sortedKeys.map(k => (monthsMap[k].profit / 1000).toFixed(2));

  chartInstances["trends"] = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Monthly Revenue ($K)",
          data: revData,
          borderColor: "#0070f3",
          backgroundColor: "rgba(0, 112, 243, 0.05)",
          borderWidth: 2.5,
          tension: 0.25,
          pointRadius: 3.5,
          pointBackgroundColor: "#0070f3"
        },
        {
          label: "Monthly Net Profit ($K)",
          data: profitData,
          borderColor: "#059669",
          backgroundColor: "rgba(5, 150, 105, 0.12)",
          borderWidth: 2.5,
          tension: 0.25,
          fill: true,
          pointRadius: 3.5,
          pointBackgroundColor: "#059669"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: $${parseFloat(ctx.raw).toLocaleString()}K`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "#f1f5f9" },
          ticks: { callback: v => `$${v}K` }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderForecastChart(histData, forecastArr) {
  destroyChart("forecast");
  const ctx = document.getElementById("chartForecastTimeline").getContext("2d");

  // Historical aggregation by YYYY-MM
  const monthsMap = {};
  histData.forEach(d => {
    const ym = d.order_date.substring(0, 7);
    monthsMap[ym] = (monthsMap[ym] || 0) + d.revenue;
  });

  const sortedKeys = Object.keys(monthsMap).sort();
  const histLabels = sortedKeys.map(k => {
    const [y, m] = k.split("-");
    const d = new Date(y, m - 1);
    return d.toLocaleString("en-US", { month: "short", year: "2-digit" });
  });
  const histVals = sortedKeys.map(k => (monthsMap[k] / 1000).toFixed(2));

  // Connect forecast points to the last historical point
  const lastHistVal = histVals[histVals.length - 1];
  const lastHistLabel = histLabels[histLabels.length - 1];

  const futureMonths = forecastArr.length ? forecastArr : [
    { month_name: "Jan 2026", forecast_revenue: 49178.45, lower_bound_80: 41671.59, upper_bound_80: 56685.31 },
    { month_name: "Feb 2026", forecast_revenue: 52979.03, lower_bound_80: 42362.72, upper_bound_80: 63595.34 },
    { month_name: "Mar 2026", forecast_revenue: 51776.76, lower_bound_80: 38774.50, upper_bound_80: 64779.03 }
  ];

  const fcLabels = futureMonths.map(f => f.month_name);
  const combinedLabels = [...histLabels, ...fcLabels];

  // Build forecast dataset (null for historical except connecting point)
  const fcDatasetVals = new Array(histVals.length - 1).fill(null);
  fcDatasetVals.push(lastHistVal);
  futureMonths.forEach(f => fcDatasetVals.push((f.forecast_revenue / 1000).toFixed(2)));

  chartInstances["forecast"] = new Chart(ctx, {
    type: "line",
    data: {
      labels: combinedLabels,
      datasets: [
        {
          label: "Historical Revenue ($K)",
          data: [...histVals, null, null, null],
          borderColor: "#0070f3",
          borderWidth: 2.5,
          pointRadius: 3,
          tension: 0.2
        },
        {
          label: "Forecast Horizon ($K)",
          data: fcDatasetVals,
          borderColor: "#e11d48",
          borderDash: [5, 5],
          borderWidth: 2.5,
          pointRadius: 5,
          pointBackgroundColor: "#e11d48",
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { callback: v => `$${v}K` },
          grid: { color: "#f1f5f9" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderCategoryCharts(data) {
  destroyChart("catRev");
  destroyChart("catMargin");

  const catMap = {};
  data.forEach(d => {
    if (!catMap[d.category]) catMap[d.category] = { rev: 0, profit: 0 };
    catMap[d.category].rev += d.revenue;
    catMap[d.category].profit += d.profit;
  });

  const categories = Object.keys(catMap).sort((a, b) => catMap[b].rev - catMap[a].rev);
  const revenuesK = categories.map(c => (catMap[c].rev / 1000).toFixed(1));
  const marginsPct = categories.map(c => catMap[c].rev > 0 ? ((catMap[c].profit / catMap[c].rev) * 100).toFixed(1) : 0);

  // Category Revenue Chart
  chartInstances["catRev"] = new Chart(document.getElementById("chartCategoryRevenue").getContext("2d"), {
    type: "bar",
    data: {
      labels: categories,
      datasets: [{
        label: "Revenue ($K)",
        data: revenuesK,
        backgroundColor: "#0070f3",
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { callback: v => `$${v}K` }, grid: { color: "#f1f5f9" } },
        y: { grid: { display: false } }
      }
    }
  });

  // Category Margin Chart
  chartInstances["catMargin"] = new Chart(document.getElementById("chartCategoryMargin").getContext("2d"), {
    type: "bar",
    data: {
      labels: categories,
      datasets: [{
        label: "Profit Margin (%)",
        data: marginsPct,
        backgroundColor: "#059669",
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { callback: v => `${v}%` }, grid: { color: "#f1f5f9" }, max: 60 },
        y: { grid: { display: false } }
      }
    }
  });
}

function renderRegionalChartsAndTable(data) {
  destroyChart("regional");

  const regMap = {};
  data.forEach(d => {
    if (!regMap[d.region]) {
      regMap[d.region] = { rev: 0, profit: 0, orders: new Set() };
    }
    regMap[d.region].rev += d.revenue;
    regMap[d.region].profit += d.profit;
    regMap[d.region].orders.add(d.order_id);
  });

  const regions = Object.keys(regMap).sort((a, b) => regMap[b].rev - regMap[a].rev);
  const revsK = regions.map(r => (regMap[r].rev / 1000).toFixed(1));
  const profitsK = regions.map(r => (regMap[r].profit / 1000).toFixed(1));

  chartInstances["regional"] = new Chart(document.getElementById("chartRegionalBars").getContext("2d"), {
    type: "bar",
    data: {
      labels: regions,
      datasets: [
        { label: "Revenue ($K)", data: revsK, backgroundColor: "#0070f3", borderRadius: 4 },
        { label: "Net Profit ($K)", data: profitsK, backgroundColor: "#059669", borderRadius: 4 }
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: { ticks: { callback: v => `$${v}K` }, grid: { color: "#f1f5f9" } },
        x: { grid: { display: false } }
      }
    }
  });

  // Populate Table
  const tbody = document.querySelector("#tblRegionalSummary tbody");
  tbody.innerHTML = "";
  regions.forEach(r => {
    const item = regMap[r];
    const orderCount = item.orders.size;
    const margin = item.rev > 0 ? (item.profit / item.rev) * 100 : 0;
    const aov = orderCount > 0 ? item.rev / orderCount : 0;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${r}</strong></td>
      <td class="text-right">$${item.rev.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
      <td class="text-right">$${item.profit.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
      <td class="text-right text-success"><strong>${margin.toFixed(2)}%</strong></td>
      <td class="text-right">${orderCount.toLocaleString()}</td>
      <td class="text-right">$${aov.toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderProductTables(data) {
  const prdMap = {};
  data.forEach(d => {
    if (!prdMap[d.product_name]) {
      prdMap[d.product_name] = { name: d.product_name, category: d.category, rev: 0, profit: 0, qty: 0 };
    }
    prdMap[d.product_name].rev += d.revenue;
    prdMap[d.product_name].profit += d.profit;
    prdMap[d.product_name].qty += d.quantity;
  });

  const prds = Object.values(prdMap).map(p => ({
    ...p,
    margin: p.rev > 0 ? (p.profit / p.rev) * 100 : 0
  }));

  const top5 = [...prds].sort((a, b) => b.profit - a.profit).slice(0, 5);
  const bottom5 = [...prds].sort((a, b) => a.margin - b.margin).slice(0, 5);

  const topTbody = document.querySelector("#tblTopProducts tbody");
  topTbody.innerHTML = "";
  top5.forEach(p => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${p.name}</strong></td>
      <td><span class="badge badge-neutral">${p.category}</span></td>
      <td class="text-right">$${p.rev.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
      <td class="text-right text-success"><strong>$${p.profit.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></td>
      <td class="text-right">${p.margin.toFixed(1)}%</td>
    `;
    topTbody.appendChild(tr);
  });

  const botTbody = document.querySelector("#tblBottomProducts tbody");
  botTbody.innerHTML = "";
  bottom5.forEach(p => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${p.name}</strong></td>
      <td><span class="badge badge-neutral">${p.category}</span></td>
      <td class="text-right">$${p.rev.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
      <td class="text-right">$${p.profit.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
      <td class="text-right text-warning"><strong>${p.margin.toFixed(1)}%</strong></td>
    `;
    botTbody.appendChild(tr);
  });
}

function renderCustomerSegmentCharts(data) {
  destroyChart("segmentPie");
  destroyChart("segmentAOV");

  const segMap = {};
  data.forEach(d => {
    if (!segMap[d.customer_segment]) {
      segMap[d.customer_segment] = { rev: 0, profit: 0, orders: new Set() };
    }
    segMap[d.customer_segment].rev += d.revenue;
    segMap[d.customer_segment].profit += d.profit;
    segMap[d.customer_segment].orders.add(d.order_id);
  });

  const segments = Object.keys(segMap);
  const revs = segments.map(s => segMap[s].rev);
  const aovs = segments.map(s => segMap[s].orders.size > 0 ? (segMap[s].rev / segMap[s].orders.size).toFixed(2) : 0);

  chartInstances["segmentPie"] = new Chart(document.getElementById("chartCustomerSegmentPie").getContext("2d"), {
    type: "doughnut",
    data: {
      labels: segments,
      datasets: [{
        data: revs,
        backgroundColor: ["#0070f3", "#059669", "#d97706"],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: $${parseFloat(ctx.raw).toLocaleString("en-US", { maximumFractionDigits: 0 })}`
          }
        }
      }
    }
  });

  chartInstances["segmentAOV"] = new Chart(document.getElementById("chartCustomerSegmentAOV").getContext("2d"), {
    type: "bar",
    data: {
      labels: segments,
      datasets: [{
        label: "Average Order Value ($)",
        data: aovs,
        backgroundColor: ["#0070f3", "#059669", "#d97706"],
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { ticks: { callback: v => `$${v}` }, grid: { color: "#f1f5f9" } },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderDiscountTierTable(data) {
  const tiers = ["No Discount (0%)", "Low (1-10%)", "Medium (11-20%)", "High (>20%)"];
  const tierMap = {};
  tiers.forEach(t => tierMap[t] = { count: 0, discountSum: 0, rev: 0, profit: 0 });

  data.forEach(d => {
    const t = d.discount_tier || "No Discount (0%)";
    if (tierMap[t]) {
      tierMap[t].count++;
      tierMap[t].discountSum += d.discount_rate;
      tierMap[t].rev += d.revenue;
      tierMap[t].profit += d.profit;
    }
  });

  const fullPriceMargin = tierMap["No Discount (0%)"].rev > 0
    ? (tierMap["No Discount (0%)"].profit / tierMap["No Discount (0%)"].rev) * 100
    : 0;

  const tbody = document.querySelector("#tblDiscountTiers tbody");
  tbody.innerHTML = "";

  tiers.forEach(t => {
    const item = tierMap[t];
    const avgDisc = item.count > 0 ? (item.discountSum / item.count) * 100 : 0;
    const margin = item.rev > 0 ? (item.profit / item.rev) * 100 : 0;
    const diff = margin - fullPriceMargin;
    const diffClass = diff >= 0 ? "text-success" : "text-danger";

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${t}</strong></td>
      <td class="text-right">${avgDisc.toFixed(1)}%</td>
      <td class="text-right">${item.count.toLocaleString()}</td>
      <td class="text-right">$${item.rev.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
      <td class="text-right">$${item.profit.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
      <td class="text-right"><strong>${margin.toFixed(2)}%</strong></td>
      <td class="text-right ${diffClass}"><strong>${diff >= 0 ? "+" : ""}${diff.toFixed(2)}%</strong></td>
    `;
    tbody.appendChild(tr);
  });
}
