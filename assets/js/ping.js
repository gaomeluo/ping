/* ============================================================
   并行延迟测速引擎（高性能版）
   替代原串行 Image 逻辑：所有节点并发探测 + 每节点超时，
   多轮采样取最优/中位，实时排序渲染。
   依赖全局变量：_URLS(key->url)、_DESCS(key->中文名)、_PROVIDER(名称)
   ============================================================ */
(function () {
  "use strict";

  var TIMEOUT = 4000;     // 单个节点超时(ms)
  var MAX_SAMPLES = 12;   // 每个节点保留的最大样本数
  var ROUND_GAP = 1500;   // 自动轮询间隔(ms)
  var CONCURRENCY = 24;   // 单轮最大并发数（防止瞬间请求过多被限流）

  var KEYS = [];
  var results = {};       // key -> [ms, ms, ...]
  var lastShown = {};     // key -> 最近一次显示值
  var running = false;
  var stopFlag = false;
  var tbody, statusEl, toggleEl;

  for (var k in _URLS) {
    if (!_URLS.hasOwnProperty(k)) continue;
    KEYS.push(k);
    results[k] = [];
  }

  function median(arr) {
    if (!arr.length) return null;
    var c = arr.slice().sort(function (a, b) { return a - b; });
    return c[Math.floor(c.length / 2)];
  }

  /* 单次探测：Image 探针，兼容 http(被动混合内容) 与 https 节点，含超时 */
  function probe(url) {
    return new Promise(function (resolve) {
      var img = new Image();
      var start = (performance && performance.now) ? performance.now() : Date.now();
      var done = false;
      var cb = function (ok) {
        if (done) return;
        done = true;
        clearTimeout(timer);
        var end = (performance && performance.now) ? performance.now() : Date.now();
        resolve(ok ? Math.round(end - start) : null);
      };
      var timer = setTimeout(function () { cb(false); }, TIMEOUT);
      img.onload = function () { cb(true); };
      img.onerror = function () { cb(true); }; // 连接建立/响应即计耗时，错误也说明可达
      var sep = url.indexOf("?") >= 0 ? "&" : "?";
      img.src = url + sep + "_t=" + Date.now() + "_" + Math.random().toString(36).slice(2, 7);
    });
  }

  /* 分批并发，避免瞬间请求过多 */
  function runBatch(keys) {
    var chains = [];
    for (var i = 0; i < keys.length; i += CONCURRENCY) {
      chains.push(keys.slice(i, i + CONCURRENCY));
    }
    return chains.reduce(function (p, batch) {
      return p.then(function () {
        return Promise.all(batch.map(function (key) {
          return probe(_URLS[key]).then(function (ms) {
            if (ms !== null && ms > 0) {
              results[key].push(ms);
              if (results[key].length > MAX_SAMPLES) results[key].shift();
            }
          });
        }));
      });
    }, Promise.resolve());
  }

  function latencyClass(ms) {
    if (ms == null) return "r";
    if (ms < 60) return "g";
    if (ms < 150) return "y";
    if (ms < 300) return "o";
    return "r";
  }
  function barWidth(ms) {
    if (ms == null) return 0;
    return Math.min(100, Math.round((ms / 600) * 100));
  }
  function shortUrl(u) {
    return u.replace(/^https?:\/\//, "").replace(/\?.*$/, "");
  }

  function render() {
    var arr = KEYS.map(function (key) {
      var m = median(results[key]);
      return { key: key, ms: m };
    }).filter(function (x) { return x.ms != null; });
    arr.sort(function (a, b) { return a.ms - b.ms; });
    var bestKey = arr.length ? arr[0].key : null;

    var html = "";
    // 已完成（有数据）在前，按延迟排序
    arr.forEach(function (row) {
      var cls = latencyClass(row.ms);
      var desc = (_DESCS && _DESCS[row.key]) || row.key;
      var url = _URLS[row.key];
      html +=
        '<tr class="' + (row.key === bestKey ? "best" : "") + '">' +
        '<td><span class="region">' + desc +
        '<span class="key">' + row.key + "</span></span></td>" +
        '<td><span class="nodeurl">' + shortUrl(url) + "</span></td>" +
        '<td><div class="lat"><span class="val ' + cls + '">' + row.ms + "ms</span>" +
        '<span class="bar"><i class="' + cls + '" style="width:' + barWidth(row.ms) + '%"></i></span></div></td>' +
        "</tr>";
    });
    // 未完成（pending）
    KEYS.forEach(function (key) {
      if (results[key].length) return;
      var desc = (_DESCS && _DESCS[key]) || key;
      var url = _URLS[key];
      html +=
        '<tr class="pending"><td><span class="region">' + desc +
        '<span class="key">' + key + "</span></span></td>" +
        '<td><span class="nodeurl">' + shortUrl(url) + "</span></td>" +
        '<td><div class="lat"><span class="val">测速中…</span><span class="bar"><i style="width:0"></i></span></div></td></tr>';
    });
    tbody.innerHTML = html;
  }

  function setStatus(text, isRunning) {
    if (!statusEl) return;
    statusEl.className = "status-pill" + (isRunning ? " running" : "");
    statusEl.innerHTML = '<span class="led"></span>' + text;
  }

  function loop() {
    if (stopFlag) return;
    runBatch(KEYS).then(function () {
      render();
      if (!stopFlag) {
        setTimeout(loop, ROUND_GAP);
      }
    });
  }

  function start() {
    if (running) return;
    running = true;
    stopFlag = false;
    toggleEl.className = "toggle stop";
    toggleEl.innerHTML = "■ 停止测速";
    setStatus("测速进行中…", true);
    loop();
  }

  function stop() {
    stopFlag = true;
    running = false;
    toggleEl.className = "toggle";
    toggleEl.innerHTML = "▶ 开始测速";
    setStatus("已停止", false);
  }

  function init() {
    tbody = document.getElementById("result-body");
    statusEl = document.getElementById("status");
    toggleEl = document.getElementById("toggle");
    if (!tbody) return;
    if (toggleEl) {
      toggleEl.addEventListener("click", function () {
        if (running) stop(); else start();
      });
    }
    render(); // 先画出骨架
    // 自动开始（页面加载后略延迟，避免与首屏渲染抢资源）
    setTimeout(start, 400);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
