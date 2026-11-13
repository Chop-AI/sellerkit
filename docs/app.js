(() => {
  const cfg = window.SELLERKIT_CONFIG || {};
  const $ = (id) => document.getElementById(id);
  const money = (v) =>
    new Intl.NumberFormat("ru-RU", {
      style: "currency",
      currency: "RUB",
      maximumFractionDigits: 0,
    }).format(v || 0);
  const num = (id) => Number($(id).value || 0);

  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      $(btn.dataset.tab).classList.add("active");
    });
  });

  $("mp").addEventListener("change", () => {
    const fees = cfg.defaultFees || { wb: 15, ozon: 14, yandex: 12 };
    $("fee").value = fees[$("mp").value] ?? 15;
    calcUnit();
  });

  function calcUnit() {
    const price = num("price");
    const cogs = num("cogs");
    const feePct = num("fee") / 100;
    const logistics = num("logistics");
    const buyout = Math.max(1, num("buyout")) / 100;
    const ads = num("ads");
    const other = num("other");
    const logEff = logistics + (logistics * (1 - buyout)) / buyout;
    const feeRub = price * feePct;
    const costs = cogs + feeRub + logEff + ads + other;
    const profit = price - costs;
    const margin = price > 0 ? (profit / price) * 100 : 0;

    $("profit").textContent = money(profit);
    $("profit").className = "kpi " + (profit >= 0 ? "ok" : "bad");
    $("margin").textContent = margin.toFixed(1) + "%";
    $("feeRub").textContent = money(feeRub);
    $("logEff").textContent = money(logEff);
    $("costs").textContent = money(costs);

    let verdict = "";
    let cls = "verdict ";
    if (margin >= 25) {
      verdict = "Сильная карточка — можно масштабировать трафик.";
      cls += "ok";
    } else if (margin >= 12) {
      verdict = "Рабочая маржа. Следи за ДРР и выкупом.";
      cls += "ok";
    } else if (margin >= 0) {
      verdict = "Тонкая экономика. Режь комиссию/логистику или поднимай цену.";
      cls += "warn";
    } else {
      verdict = "Убыточная модель на текущих вводных — не закупай партию.";
      cls += "bad";
    }
    $("verdict").textContent = verdict;
    $("verdict").className = cls;
  }

  function calcDrr() {
    const budget = num("adBudget");
    const revenue = num("adRevenue");
    const orders = num("adOrders");
    const drr = revenue > 0 ? (budget / revenue) * 100 : 0;
    const cpo = orders > 0 ? budget / orders : 0;
    const roas = budget > 0 ? revenue / budget : 0;
    $("drrValue").textContent = drr.toFixed(1) + "%";
    $("drrValue").className = "kpi " + (drr <= 15 ? "ok" : drr <= 25 ? "warn" : "bad");
    $("cpo").textContent = money(cpo);
    $("roas").textContent = roas.toFixed(2) + "×";
    let verdict = "";
    let cls = "verdict ";
    if (drr <= 12) {
      verdict = "Отличный ДРР — можно повышать бюджет.";
      cls += "ok";
    } else if (drr <= 20) {
      verdict = "Нормальный ДРР для теста. Оптимизируй ставки и креативы.";
      cls += "warn";
    } else {
      verdict = "ДРР высокий — сужай запросы или улучшай карточку.";
      cls += "bad";
    }
    $("drrVerdict").textContent = verdict;
    $("drrVerdict").className = cls;
  }

  function calcBe() {
    const fixed = num("fixed");
    const unit = Math.max(1, num("unitProfit"));
    const target = num("target");
    const zero = Math.ceil(fixed / unit);
    const goal = Math.ceil((fixed + target) / unit);
    $("beOrders").textContent = String(zero);
    $("beOrders").className = "kpi ok";
    $("beTargetOrders").textContent = String(goal) + " заказов";
    $("beVerdict").textContent =
      "Нужно примерно " + zero + " заказов/мес, чтобы выйти в ноль, и " + goal + " — чтобы взять целевую прибыль.";
    $("beVerdict").className = "verdict ok";
  }

  $("unitCalc").addEventListener("click", calcUnit);
  $("drrCalc").addEventListener("click", calcDrr);
  $("beCalc").addEventListener("click", calcBe);
  ["price", "cogs", "fee", "logistics", "buyout", "ads", "other"].forEach((id) =>
    $(id).addEventListener("input", calcUnit)
  );

  const slot = $("affiliateSlot");
  if (cfg.affiliateUrl) {
    slot.innerHTML =
      '<a href="' +
      cfg.affiliateUrl +
      '" target="_blank" rel="noopener sponsored">' +
      (cfg.affiliateLabel || "Рекомендуем") +
      "</a>";
  } else if (cfg.telegramBot) {
    slot.innerHTML =
      'Бот в Telegram: <a href="https://t.me/' +
      cfg.telegramBot.replace(/^@/, "") +
      '" target="_blank" rel="noopener">@' +
      cfg.telegramBot.replace(/^@/, "") +
      "</a>";
  } else {
    slot.textContent = "Скоро: Telegram-бот и партнёрские офферы для селлеров.";
  }

  calcUnit();
  calcDrr();
  calcBe();
})();
