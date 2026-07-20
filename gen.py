# -*- coding: utf-8 -*-
"""生成 7 个云厂商测速页 + config/descs。
- aliyun/huawei/tengxun/vultr 节点按 feitsui 增删
- bandwagonhost/qiniu/virmach 保持原样
- 从原页提取"原理说明+广告iframe"区块，保证广告链接不变
"""
import os, re, io

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, ".workbuddy", "backup_site", "original")  # 下载的原始站（备份）
OUT  = ROOT                                 # 交付根目录

# ----------------- 节点定义 -----------------
# (key, url, 中文描述)
NODES = {
    "aliyun": [
        ("aliyun-cn-qingdao","https://oss-cn-qingdao.aliyuncs.com","青岛 华北1"),
        ("aliyun-cn-beijing","https://oss-cn-beijing.aliyuncs.com","北京 华北2"),
        ("aliyun-cn-zhangjiakou","https://oss-cn-zhangjiakou.aliyuncs.com","张家口 华北3"),
        ("aliyun-cn-huhehaote","https://oss-cn-huhehaote.aliyuncs.com","呼和浩特 华北5"),
        ("aliyun-cn-chengdu","https://oss-cn-chengdu.aliyuncs.com","成都 西南1"),
        ("aliyun-cn-guangzhou","https://oss-cn-guangzhou.aliyuncs.com","广州 华南2"),
        ("aliyun-cn-heyuan","https://oss-cn-heyuan.aliyuncs.com","河源 华南3"),
        ("aliyun-cn-hangzhou","https://oss-cn-hangzhou.aliyuncs.com","杭州 华东1"),
        ("aliyun-cn-shanghai","https://oss-cn-shanghai.aliyuncs.com","上海 华东2"),
        ("aliyun-cn-shenzhen","https://oss-cn-shenzhen.aliyuncs.com","深圳 华南1"),
        ("aliyun-cn-wulanchabu","https://oss-cn-wulanchabu.aliyuncs.com","乌兰察布 华北6"),
        ("aliyun-cn-hongkong","https://oss-cn-hongkong.aliyuncs.com","中国香港"),
        ("aliyun-ap-southeast-1","https://oss-ap-southeast-1.aliyuncs.com","新加坡 亚太东南1"),
        ("aliyun-ap-southeast-2","https://oss-ap-southeast-2.aliyuncs.com","悉尼 亚太东南2"),
        ("aliyun-ap-southeast-3","https://oss-ap-southeast-3.aliyuncs.com","吉隆坡 亚太东南3"),
        ("aliyun-ap-southeast-5","https://oss-ap-southeast-5.aliyuncs.com","雅加达 亚太东南5"),
        ("aliyun-ap-southeast-6","https://oss-ap-southeast-6.aliyuncs.com","马尼拉 亚太东南6"),
        ("aliyun-ap-southeast-7","https://oss-ap-southeast-7.aliyuncs.com","曼谷 亚太东南7"),
        ("aliyun-ap-northeast-1","https://oss-ap-northeast-1.aliyuncs.com","东京 亚太东北1"),
        ("aliyun-ap-northeast-2","https://oss-ap-northeast-2.aliyuncs.com","首尔 亚太东北2"),
        ("aliyun-us-west-1","https://oss-us-west-1.aliyuncs.com","硅谷 美国西部1"),
        ("aliyun-us-east-1","https://oss-us-east-1.aliyuncs.com","弗吉尼亚 美国东部1"),
        ("aliyun-eu-central-1","https://oss-eu-central-1.aliyuncs.com","法兰克福 欧洲中部1"),
        ("aliyun-eu-west-1","https://oss-eu-west-1.aliyuncs.com","伦敦 英国"),
        ("aliyun-me-east-1","https://oss-me-east-1.aliyuncs.com","迪拜 中东东部1"),
        ("aliyun-ap-south-1","https://oss-ap-south-1.aliyuncs.com","孟买 亚太南部1"),
    ],
    "tengxun": [
        ("ap-beijing","https://cos.ap-beijing.myqcloud.com","北京 Beijing"),
        ("ap-chengdu","https://cos.ap-chengdu.myqcloud.com","成都 Chengdu"),
        ("ap-chongqing","https://cos.ap-chongqing.myqcloud.com","重庆 Chongqing"),
        ("ap-guangzhou","https://cos.ap-guangzhou.myqcloud.com","广州 Guangzhou"),
        ("ap-nanjing","https://cos.ap-nanjing.myqcloud.com","南京 Nanjing"),
        ("ap-shanghai","https://cos.ap-shanghai.myqcloud.com","上海 Shanghai"),
        ("ap-beijing-fsi","https://cos.ap-beijing-fsi.myqcloud.com","北京金融 Beijing FSI"),
        ("ap-shanghai-fsi","https://cos.ap-shanghai-fsi.myqcloud.com","上海金融 Shanghai FSI"),
        ("ap-shenzhen-fsi","https://cos.ap-shenzhen-fsi.myqcloud.com","深圳金融 Shenzhen FSI"),
        ("ap-hongkong","https://cos.ap-hongkong.myqcloud.com","香港 Hongkong"),
        ("ap-bangkok","https://cos.ap-bangkok.myqcloud.com","曼谷 Bangkok"),
        ("ap-jakarta","https://cos.ap-jakarta.myqcloud.com","雅加达 Jakarta"),
        ("ap-seoul","https://cos.ap-seoul.myqcloud.com","首尔 Seoul"),
        ("ap-singapore","https://cos.ap-singapore.myqcloud.com","新加坡 Singapore"),
        ("ap-tokyo","https://cos.ap-tokyo.myqcloud.com","东京 Tokyo"),
        ("eu-frankfurt","https://cos.eu-frankfurt.myqcloud.com","法兰克福 Frankfurt"),
        ("na-ashburn","https://cos.na-ashburn.myqcloud.com","美东 阿什本 Ashburn"),
        ("na-siliconvalley","https://cos.na-siliconvalley.myqcloud.com","美西 硅谷 Silicon Valley"),
        ("sa-saopaulo","https://cos.sa-saopaulo.myqcloud.com","巴西 圣保罗 Sao Paulo"),
    ],
    "vultr": [
        ("syd-au","https://syd-au-ping.vultr.com","悉尼 Sydney"),
        ("mel-au","https://mel-au-ping.vultr.com","墨尔本 Melbourne"),
        ("hnd-jp","https://hnd-jp-ping.vultr.com","东京 Tokyo"),
        ("sel-kor","https://sel-kor-ping.vultr.com","首尔 Seoul"),
        ("sgp","https://sgp-ping.vultr.com","新加坡 Singapore"),
        ("lax-ca-us","https://lax-ca-us-ping.vultr.com","洛杉矶 Los Angeles"),
        ("sjo-ca-us","https://sjo-ca-us-ping.vultr.com","硅谷 Silicon Valley"),
        ("fl-us","https://fl-us-ping.vultr.com","迈阿密 Miami"),
        ("ga-us","https://ga-us-ping.vultr.com","亚特兰大 Atlanta"),
        ("hon-hi-us","https://hon-hi-us-ping.vultr.com","檀香山 Honolulu"),
        ("il-us","https://il-us-ping.vultr.com","芝加哥 Illinois"),
        ("nj-us","https://nj-us-ping.vultr.com","纽约 New Jersey"),
        ("tx-us","https://tx-us-ping.vultr.com","达拉斯 Dallas"),
        ("wa-us","https://wa-us-ping.vultr.com","西雅图 Seattle"),
        ("tor-ca","https://tor-ca-ping.vultr.com","多伦多 Toronto"),
        ("mex-mx","https://mex-mx-ping.vultr.com","墨西哥城 Mexico City"),
        ("sao-br","https://sao-br-ping.vultr.com","圣保罗 Sao Paulo"),
        ("fra-de","https://fra-de-ping.vultr.com","法兰克福 Frankfurt"),
        ("mad-es","https://mad-es-ping.vultr.com","马德里 Madrid"),
        ("par-fr","https://par-fr-ping.vultr.com","巴黎 Paris"),
        ("lon-gb","https://lon-gb-ping.vultr.com","伦敦 London"),
        ("ams-nl","https://ams-nl-ping.vultr.com","阿姆斯特丹 Amsterdam"),
        ("waw-pl","https://waw-pl-ping.vultr.com","华沙 Warsaw"),
        ("sto-se","https://sto-se-ping.vultr.com","斯德哥尔摩 Stockholm"),
    ],
    # 以下三个厂商 feitsui 未收录，保持原样（从原 config.js 读取）
    "bandwagonhost": "KEEP",
    "qiniu": "KEEP",
    "virmach": "KEEP",
}

META = {
    "aliyun":          ("阿里云", "Aliyun", "阿里"),
    "tengxun":         ("腾讯云", "Tencent Cloud", "腾讯"),
    "qiniu":           ("七牛云", "Qiniu", "七牛"),
    "bandwagonhost":   ("搬瓦工", "BandwagonHost", "BW"),
    "vultr":           ("Vultr", "Vultr", "V"),
    "virmach":         ("VirMach", "VirMach", "VM"),
}

# 导航（首页 + 6 厂商）
NAV_LINKS = [
    ("../", "首页"),
    ("../aliyun/", "阿里云"),
    ("../tengxun/", "腾讯云"),
    ("../qiniu/", "七牛云"),
    ("../bandwagonhost/", "搬瓦工"),
    ("../vultr/", "Vultr"),
    ("../virmach/", "VirMach"),
]

# 各厂商头部/首页卡片使用的品牌 favicon（本地托管）
LOGO = {
    "aliyun": "aliyun.png",
    "tengxun": "tengxun.png",
    "qiniu": "qiniu.ico",
    "vultr": "vultr.png",
    "virmach": "virmach.jpg",
    "bandwagonhost": "bandwagonhost.svg",  # 无官方 favicon，用品牌色 monogram 兜底
}

# 联盟链接归一化：阿里云类 -> aliyunxiaozhan，腾讯云类 -> txmiaosha
AFFILIATE = [
    ("https://iil.ink/alidaijinquan",
     "https://inurl.link/aliyunxiaozhan"),
    ("https://promotion.aliyun.com/ntms/yunparter/invite.html?userCode=ffsbbyn0",
     "https://inurl.link/aliyunxiaozhan"),
    ("https://cloud.tencent.com/redirect.php?redirect=1005&cps_key=ff47a5bb6fc88a1b3721636857446f74&from=console",
     "https://inurl.link/txmiaosha"),
]

def nav_html(active):
    items = []
    for href, label in NAV_LINKS:
        cls = "active" if href == active else ""
        items.append('<a class="%s" href="%s">%s</a>' % (cls, href, label))
    return "\n        ".join(items)

# 优惠活动卡片区（保留原广告联盟链接：阿里云/腾讯云推广）
PROMO_HTML = '''
<section class="promos">
  <div class="promos-head"><span class="ph-line"></span>优惠活动 · 选购云服务器可领<span class="ph-line"></span></div>
  <div class="promo-grid">
    <a class="promo-card ali" href="https://inurl.link/aliyunxiaozhan" target="_blank" rel="nofollow">
      <span class="promo-tag">阿里云</span>
      <div class="promo-title">2000 元代金券</div>
      <div class="promo-desc">新用户专享，云服务器低至 1 折起</div>
      <span class="promo-cta">立即领取 →</span>
    </a>
    <a class="promo-card tx" href="https://inurl.link/txmiaosha" target="_blank" rel="nofollow">
      <span class="promo-tag">腾讯云</span>
      <div class="promo-title">限时秒杀</div>
      <div class="promo-desc">2 核 2G 轻量应用服务器特价抢购</div>
      <span class="promo-cta">立即抢购 →</span>
    </a>
    <a class="promo-card vultr" href="https://inurl.link/vultr" target="_blank" rel="nofollow">
      <span class="promo-tag">Vultr</span>
      <div class="promo-title">可能是最便宜的国外 VPS</div>
      <div class="promo-desc">最便宜的 VPS 低至 12＄/年</div>
      <span class="promo-cta">立即查看 →</span>
    </a>
    <a class="promo-card bwh" href="https://inurl.link/bandwagonhost" target="_blank" rel="nofollow">
      <span class="promo-tag">搬瓦工</span>
      <div class="promo-title">可能是国内用户最多的国外 VPS</div>
      <div class="promo-desc">速度快，拥有国内 3 大电信的线路</div>
      <span class="promo-cta">立即查看 →</span>
    </a>
  </div>
</section>
'''

def extract_about(provider):
    """从原页提取 about-content 内部 HTML（原理说明 + 广告iframe），保持广告链接不变。"""
    path = os.path.join(SITE, provider + ".html")
    html = open(path, encoding="utf-8", errors="ignore").read()
    m = re.search(r'class="about-content[^"]*"[^>]*>(.*?)(<img id="pingimg">)', html, re.S)
    if not m:
        m = re.search(r'class="about-content[^"]*"[^>]*>(.*?)</div>\s*</div>', html, re.S)
    if not m:
        return "<p>无法提取原说明区块。</p>"
    inner = m.group(1)
    # 去掉外层 mdl 栅格类遗留的闭合/空标签噪音，保留内容
    inner = inner.replace('class="about-content mdl-cell mdl-cell--6-col mdl-cell--1-offset-tablet mdl-cell--3-offset-desktop"', "")
    # 去掉 twitter 分享图标（用户要求移除）
    inner = re.sub(r'<center>\s*<a[^>]*id="tweet-link"[\s\S]*?</center>', '', inner)
    # 联盟链接归一化（阿里云 -> aliyunxiaozhan，腾讯云 -> txmiaosha）
    for old, new in AFFILIATE:
        inner = inner.replace(old, new)
    # 修正原站残留的损坏前缀（如 virmach 的 hhttps://）
    inner = inner.replace("hhttps://", "https://")
    return inner.strip()

def read_keep_nodes(provider):
    """读取原 config.js / descs.js 的节点（保持原样）。"""
    cfg = open(os.path.join(SITE, provider, "js", "config.js"), encoding="utf-8", errors="ignore").read()
    dsc = open(os.path.join(SITE, provider, "js", "descs.js"), encoding="utf-8", errors="ignore").read()
    urls = dict(re.findall(r'"([^"]+)":\s*"([^"]+)"', cfg))
    descs = dict(re.findall(r"'([^']+)':\s*'([^']+)'", dsc))
    out = []
    for k, u in urls.items():
        out.append((k, u, descs.get(k, k)))
    return out

def write_config(provider, nodes):
    lines = ["var _URLS = {"]
    for k, u, d in nodes:
        lines.append('  "%s": "%s",' % (k, u))
    lines.append("};")
    with open(os.path.join(OUT, provider, "js", "config.js"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def write_descs(provider, nodes):
    lines = ["let _DESCS = {"]
    for k, u, d in nodes:
        lines.append("  '%s': '%s'," % (k, d))
    lines.append("};")
    with open(os.path.join(OUT, provider, "js", "descs.js"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{name} Ping · 全球节点延迟测速 - {name_en}</title>
  <meta name="keywords" content="{name}ping,{name}延迟,{name}节点,{name}区域测速">
  <meta name="description" content="批量Ping测试{name}全球各区域节点延迟，帮你挑选延迟最低的云服务器区域。">
  <link rel="icon" type="image/svg+xml" href="../assets/img/favicon.svg">
  <link rel="stylesheet" href="../tanchuang/css/layui.css">
  <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
  <nav class="nav">
    <span class="brand"><span class="dot"></span>全球云节点测速</span>
    <span class="links">
        {nav}
    </span>
  </nav>

  <main class="wrap">
    <div class="phead">
      <img class="plogo" src="../assets/img/logos/{logo}" alt="{name}"/>
      <div>
        <h1 class="ptitle">{name} 全球节点延迟测速</h1>
        <p class="psub">测试您本机到 {name}（{name_en}）各区域节点的网络延迟，实时排序，越小越好。</p>
      </div>
      <span class="spacer"></span>
      <span id="status" class="status-pill"><span class="led"></span>准备中</span>
      <button id="toggle" class="toggle">▶ 开始测速</button>
    </div>

    {ads}

    <div class="hint-bar">
      <span class="hb-dot"></span>
      <span class="hb-note">提示：受网络波动影响，建议多等几轮取稳定值；长时间无数据可点击「停止测速」后重新开始。</span>
      <span class="hb-sep" aria-hidden="true"></span>
      <span class="hb-tag">重要提醒</span>
      <span class="hb-text">有的网站你打不开，可能需要一个节点多、非常便宜、稳定的机场：</span>
      <a class="hb-link" href="https://inurl.top/archives/mojie/" target="_blank" rel="nofollow">传送门 →</a>
    </div>

    <div class="table-card">
      <div class="tcap"><span><b>{count}</b> 个节点 · 并行实时测速</span><span>延迟越低越优 ★</span></div>
      <table class="results">
        <thead>
          <tr><th>区域</th><th>节点地址</th><th>延迟</th></tr>
        </thead>
        <tbody id="result-body">
          <tr><td colspan="3">初始化中…</td></tr>
        </tbody>
      </table>
    </div>

    <div class="about">
      {about}
    </div>
  </main>

  <footer class="footer">
    <div class="wrap">
      <div class="links">
        <a href="https://api.inurl.link/" target="_blank" rel="noopener">API Token大全</a>
        <a href="https://tools.inurl.link/" target="_blank" rel="noopener">工具箱</a>
        <a href="https://ping.gaomeluo.com/" target="_blank" rel="noopener">云测速</a>
        <a href="https://blog.gaomeluo.com/" target="_blank" rel="noopener">博客</a>
        <a href="https://www.lixiaoxin.com" target="_blank" rel="noopener">关于</a>
        <a href="https://inurl.link/dashboard" target="_blank" rel="noopener">短连接</a>
      </div>
      <div>© 全球云节点测速 · 数据由你的浏览器实时探测，仅供参考。</div>
    </div>
  </footer>

  <script src="js/config.js"></script>
  <script src="js/descs.js"></script>
  <script src="../assets/js/ping.js"></script>
  <script src="../tanchuang/layui.js"></script>
</body>
</html>
"""

def build():
    for provider, spec in NODES.items():
        if spec == "KEEP":
            nodes = read_keep_nodes(provider)
        else:
            nodes = spec
        os.makedirs(os.path.join(OUT, provider, "js"), exist_ok=True)
        write_config(provider, nodes)
        write_descs(provider, nodes)
        name, name_en, icon = META[provider]
        about = extract_about(provider)
        html = TPL.format(
            name=name, name_en=name_en, logo=LOGO[provider],
            nav=nav_html("../%s/" % provider),
            ads=PROMO_HTML,
            count=len(nodes),
            about=about,
        )
        with open(os.path.join(OUT, provider, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ %-16s 节点数=%-3d" % (provider, len(nodes)))

if __name__ == "__main__":
    build()
