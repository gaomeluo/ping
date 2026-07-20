# -*- coding: utf-8 -*-
"""生成 favicon.svg 与 6 个厂商 monogram 图标到 assets/img/。
风格：品牌色渐变圆角方块 + 白色小云朵 + 厂商简称，呼应站点暗色科技风。
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "img", "logos")
os.makedirs(OUT, exist_ok=True)

# 厂商简称、浅色、深色（品牌色）
PROVIDERS = {
    "aliyun":        ("阿里", "#FF8A1F", "#E65A00", 22),
    "tengxun":       ("腾讯", "#3B9BFF", "#0066E0", 22),
    "qiniu":         ("七牛", "#25C2F5", "#0A86C2", 22),
    "bandwagonhost": ("搬瓦", "#19D27E", "#00995C", 22),
    "vultr":         ("V",    "#5B8DEF", "#1E2A4D", 30),
    "virmach":       ("VM",   "#2DD4BF", "#0B7C72", 24),
}

CLOUD = "M17.5 19a4.5 4.5 0 0 0 0-9 6 6 0 0 0-11.6-1.5A4 4 0 0 0 6.5 19h11z"

def logo(name, label, light, dark, fs):
    svg = f'''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{light}"/>
      <stop offset="1" stop-color="{dark}"/>
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="16" fill="url(#g)"/>
  <path d="{CLOUD}" fill="#ffffff" opacity="0.92" transform="translate(32.5,4.2) scale(0.85)"/>
  <text x="32" y="46" text-anchor="middle" font-family="-apple-system,Segoe UI,PingFang SC,Microsoft YaHei,sans-serif" font-size="{fs}" font-weight="800" fill="#ffffff">{label}</text>
</svg>
'''
    with open(os.path.join(OUT, f"{name}.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print("✅ logo", name)

for n, (label, light, dark, fs) in PROVIDERS.items():
    logo(n, label, light, dark, fs)

# ---- favicon：暗色方块 + 青色云 + 绿色实时探测点 ----
fav = '''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b1224"/>
      <stop offset="1" stop-color="#05080f"/>
    </linearGradient>
    <linearGradient id="cl" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#22d3ee"/>
      <stop offset="1" stop-color="#3b82f6"/>
    </linearGradient>
  </defs>
  <rect width="24" height="24" rx="6" fill="url(#bg)" stroke="#21304f" stroke-width="1"/>
  <path d="M17.5 18.5a4.5 4.5 0 0 0 0-9 6 6 0 0 0-11.6-1.5A4 4 0 0 0 6.5 18.5h11z" fill="url(#cl)"/>
  <circle cx="18.2" cy="6.4" r="1.9" fill="#34d399"/>
</svg>
'''
with open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(fav)
print("✅ favicon.svg")
