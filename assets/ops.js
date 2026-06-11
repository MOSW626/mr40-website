// 운영 시트 공통 접근 계층. 각 탭은 config.js의 OPS_SHEETS URL로 연결한다.
(function () {
  "use strict";

  var memory = {};

  function rows(name) {
    if (memory[name]) return memory[name];
    var key = "mr40_ops_" + name;
    var url = CONFIG.OPS_SHEETS && CONFIG.OPS_SHEETS[name];
    var cached = [];
    try { cached = JSON.parse(localStorage.getItem(key) || "[]"); } catch (e) {}
    if (!url) {
      memory[name] = Promise.resolve(cached);
      return memory[name];
    }
    var separator = url.indexOf("?") === -1 ? "?" : "&";
    memory[name] = fetch(url + separator + "t=" + Date.now())
      .then(function (res) {
        if (!res.ok) throw new Error(res.status);
        return res.text();
      })
      .then(function (text) {
        var lines = text.split(/\r?\n/).filter(Boolean);
        var headers = parseCsvLine(lines.shift() || "");
        var result = lines.map(parseCsvLine).map(function (values) {
          var item = {};
          headers.forEach(function (header, index) { item[header.trim()] = values[index] || ""; });
          return item;
        }).filter(function (item) {
          return Object.keys(item).some(function (keyName) { return item[keyName]; });
        });
        localStorage.setItem(key, JSON.stringify(result));
        return result;
      })
      .catch(function () { return cached; });
    return memory[name];
  }

  function active(item) {
    return !item || !item.active || /^(1|true|yes|y|공개)$/i.test(item.active);
  }

  function eventMap(items) {
    return (items || []).reduce(function (result, item) {
      if (item.key) result[item.key.trim()] = (item.value || "").trim();
      return result;
    }, {});
  }

  function number(value, fallback) {
    var parsed = Number(String(value || "").replace(/[^0-9.-]/g, ""));
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  window.MR40Ops = {
    rows: rows,
    active: active,
    eventMap: eventMap,
    number: number,
  };
})();
