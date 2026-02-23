# Mihomo 配置从入门到进阶：三阶段完全教程

> **参考来源：**
> [虚空终端官方文档](https://wiki.metacubex.one/) 

---

## 写在最前

Mihomo（原名 Clash Meta）是目前功能最完整、社区最活跃的 Clash 衍生内核。它本身没有图形界面，完全靠读取一份 **YAML 格式**的配置文件来工作。

本教程分三个阶段，每一阶段都有独立的完整示例，你可以从任一阶段开始阅读。**第一阶段**是能跑起来的最小配置，**第二阶段**引入规则集和锚点写法，**第三阶段**覆盖 TUN 透明代理、dialer-proxy 代理链、性能调优等进阶话题。

---

## YAML 基础：动笔前必读

### 缩进规则

YAML **绝对禁止使用 Tab**，只能用空格。同一层级的键必须对齐，缩进多少空格无所谓，但必须一致。这是新手最常见的报错来源。

```yaml
# ✅ 正确
dns:
  enable: true
  listen: 0.0.0.0:1053

# ❌ 错误（第二行用了 Tab）
dns:
	enable: true
```

### 四种等价写法

mihomo 的配置文件支持 YAML 和 JSON 混写，下面四种写法完全等价：

```yaml
# 写法一：标准多行 YAML（可读性最好，适合顶层配置）
tun:
  enable: true
  stack: mixed
  auto-route: true

# 写法二：多行 JSON 花括号（proxy-groups 中常用）
tun: {
  enable: true,
  stack: mixed,
  auto-route: true
}

# 写法三：单行 JSON 花括号（proxy-groups 列表项常用，极大缩短配置长度）
tun: { enable: true, stack: mixed, auto-route: true }

# 写法四：数组的单行写法
nameserver: [223.5.5.5, 119.29.29.29]
# 等价于：
nameserver:
  - 223.5.5.5
  - 119.29.29.29
```

### YAML 锚点：进阶配置的灵魂

当你有大量结构相同的配置项（比如几十个代理组都要写相同的 `url`、`interval`、`timeout`），就可以用 YAML 锚点来消除重复：

```yaml
# & 定义锚点，给这块内容起一个名字
# * 引用锚点
# <<: 将引用的内容"合并"进当前对象（覆盖同名键，缺失的键则补入）

# 第一步：在顶层定义锚点（键名 p 不存在于 mihomo，会被忽略，只用于锚点）
p: &p                         # &p 给这个块起名叫 p
  type: http
  interval: 86400
  health-check:
    enable: true
    url: "https://www.gstatic.com/generate_204"
    interval: 300
    lazy: true

# 第二步：在 proxy-providers 中用 <<: *p 引用
proxy-providers:
  机场A:
    <<: *p                    # 把 p 锚点的所有字段合并进来
    url: "https://your-airport-a.com/subscribe?token=xxx"
    path: ./proxy_providers/airport-a.yaml

  机场B:
    <<: *p                    # 同样引用 p，避免重复
    url: "https://your-airport-b.com/subscribe?token=xxx"
    path: ./proxy_providers/airport-b.yaml
```

等价展开后是：

```yaml
proxy-providers:
  机场A:
    type: http
    interval: 86400
    health-check: { enable: true, url: "...", interval: 300, lazy: true }
    url: "https://your-airport-a.com/subscribe?token=xxx"
    path: ./proxy_providers/airport-a.yaml
  # 机场B 同理...
```

**注意：** 锚点内有重复键时，当前块的键优先（不会被锚点覆盖）。例如 `机场B` 里如果单独写了 `interval: 43200`，则该值覆盖锚点里的 `86400`。

---

# 第一阶段：小白篇 —— 能跑起来就是胜利

**目标：** 写出一份能让 mihomo 正常启动、可以翻墙的最小可用配置。每一行都知道它在做什么，不留死角。

---

## 一、配置文件的整体骨架

```
全局设置（端口、模式、日志等）
DNS 配置
域名嗅探（Sniff，可选）
TUN 入站（可选，进阶用）
出站代理节点（proxies）
代理提供者（proxy-providers，机场订阅）
代理组（proxy-groups）—— 策略核心
规则提供者（rule-providers）
路由规则（rules）
```

规则从上往下逐条匹配，**第一条匹配到的规则立即生效，后面的规则不再检查**。

---

## 二、全局设置

```yaml
# ══ 端口 ══════════════════════════════════════════════════════
mixed-port: 7890          # HTTP + SOCKS5 混合端口（推荐只用这一个）
allow-lan: false          # 是否允许局域网内其他设备接入代理
                          # 个人电脑设 false；软路由/共享代理设 true
bind-address: "*"         # allow-lan 为 true 时绑定哪些网卡，* 表示全部

# ══ 运行模式 ══════════════════════════════════════════════════
mode: rule                # rule=按规则分流（日常使用）
                          # global=所有流量走代理（调试用）
                          # direct=所有流量直连（调试用）

# ══ 日志 ══════════════════════════════════════════════════════
log-level: warning        # silent / error / warning / info / debug
                          # 日常用 warning；排查问题时改 debug

# ══ 杂项 ══════════════════════════════════════════════════════
ipv6: false               # 不建议新手开启，避免意外问题
find-process-mode: strict # 是否匹配进程名（路由器/软路由推荐 off）
unified-delay: true       # 统一延迟测试：用实际往返时间，更准确
tcp-concurrent: true      # TCP 并发：同时向所有解析 IP 发起连接，选最快的
global-client-fingerprint: chrome  # 全局 TLS 指纹伪装

# ══ 外部控制（Web 面板）══════════════════════════════════════
external-controller: 127.0.0.1:9090
# secret: "your_strong_password"   # 如果对外暴露务必设置密码
external-ui: ui                     # Web UI 存放目录（相对于配置文件目录）
external-ui-url: "https://github.com/MetaCubeX/metacubexd/archive/refs/heads/gh-pages.zip"

# ══ GeoData 数据库地址 ════════════════════════════════════════
geox-url:
  geoip:   "https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geoip.dat"
  geosite: "https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geosite.dat"
  mmdb:    "https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/country.mmdb"

# ══ 配置持久化 ════════════════════════════════════════════════
profile:
  store-selected: true    # 记住你在 Web UI 中的节点选择，重启后不丢失
  store-fake-ip: true     # 持久化 fake-ip 映射表
```

---

## 三、DNS 配置

### 为什么需要配置 DNS？

当你访问 `google.com`，你的设备需要先把域名解析成 IP。如果用运营商的默认 DNS，它会对很多国外域名返回错误或污染的 IP，导致代理失效。

mihomo 内置了一个 DNS 服务器，它会：
1. 拦截所有 DNS 请求，按规则处理
2. 国内域名走国内 DNS，解析快且准
3. 国外域名的解析通过代理完成，得到正确 IP

### 关于 "DNS 泄露"

很多教程把"DNS 泄露"描述得非常可怕，但这个问题其实被过度渲染了。DNS 泄露的本质是：**访问国外域名时，DNS 查询用的是国内 DNS 而非代理侧 DNS**，可能导致 CDN 解析不优化（你连的是代理节点，但 DNS 告诉 CDN 你在中国，CDN 给你分配了国内节点）。这会影响访问速度，但不是什么隐私灾难。**关键在于：分流规则写好，非直连流量不在本地做 DNS 解析，这才是真正重要的。**（参考：[iyyh 的分析](https://iyyh.net/posts/mihomo-self-config) 与 [SukkA 的文章](https://blog.skk.moe/post/lets-talk-about-dns-cdn-fake-ip/)）

### fake-ip 模式（新手推荐）

```yaml
dns:
  enable: true
  listen: 0.0.0.0:1053
  ipv6: false
  prefer-h3: true               # 优先使用 HTTP/3 协议（DoH3），更快
  enhanced-mode: fake-ip        # 推荐模式，速度快，与规则配合最好
  fake-ip-range: 198.18.0.1/16

  # fake-ip 白名单：这些域名不返回假 IP，直接正常解析
  # 主要是局域网服务、NTP、游戏 STUN 等不适合 fake-ip 的场景
  fake-ip-filter:
    - "*.lan"
    - "*.local"
    - "*.localhost"
    - "time.windows.com"
    - "time.nist.gov"
    - "time.apple.com"
    - "+.stun.*.*"
    - "+.stun.*.*.*"
    - "+.xboxlive.com"
    - "+.nintendo.net"

  # respect-rules: true         # DNS 解析遵循路由规则（如需国外域名走代理 DNS，开启此项）

  # 解析代理节点域名用的 DNS（避免代理节点域名本身被污染）
  proxy-server-nameserver:
    - https://223.5.5.5/dns-query
    - https://doh.pub/dns-query

  # 默认 nameserver：国内 DNS，并发查询取最快结果
  nameserver:
    - system                           # 当地运营商 DNS（一般最快）
    - https://223.5.5.5/dns-query      # 阿里 DoH
    - https://doh.pub/dns-query        # 腾讯 DoH
```

**什么是 fake-ip？** mihomo 收到 DNS 查询时，立刻返回一个假 IP（如 `198.18.0.1`）并在内部建立映射。当流量发到这个假 IP，mihomo 知道它对应的真实域名，然后按**域名规则**决定直连或走代理。这样规则匹配在 DNS 解析完成之前就发生了，速度极快，且代理流量不需要在本地做 DNS 解析。

**关于 `fallback` 的重要说明：** 很多老教程要求配置 `fallback`，但它有一个关键问题——一旦配置了 `fallback`，mihomo 会**等待 fallback DNS 的结果**才继续，即使 `nameserver` 已经返回了结果。这会使所有 DNS 查询都变慢。更好的方案是直接用 `nameserver-policy` 分域名精细控制（见第二阶段）。

---

## 四、域名嗅探（Sniff）

```yaml
sniffer:
  enable: true
  # override-destination：用嗅探到的真实域名覆盖连接目标
  # 在 TUN 模式下必须开启，否则拿到的是 IP，域名规则无法匹配
  sniff:
    HTTP:
      ports: [80, 8080-8880]
      override-destination: true
    TLS:
      ports: [443, 8443]
    QUIC:
      ports: [443, 8443]
  skip-domain:
    - "Mijia Cloud"            # 小米云，跳过嗅探
    - "+.push.apple.com"       # 苹果推送
```

---

## 五、出站代理节点（proxies）

手写自建节点，机场用户可直接跳到第六节用 `proxy-providers`。

```yaml
proxies:
  # ── Shadowsocks ─────────────────────────────────────────────
  - name: "我的SS节点"
    type: ss
    server: your.server.com
    port: 12345
    cipher: aes-128-gcm        # 常见加密：aes-128-gcm / chacha20-ietf-poly1305
    password: "your_password"
    udp: true

  # ── VMess + WebSocket + TLS ──────────────────────────────────
  - name: "我的VMess节点"
    type: vmess
    server: your.server.com
    port: 443
    uuid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    alterId: 0                 # 建议为 0（AEAD 模式）
    cipher: auto
    tls: true
    network: ws
    ws-opts:
      path: "/your-path"
      headers:
        Host: your.server.com

  # ── VLESS + Reality（当前主流抗封锁方案）─────────────────────
  - name: "我的Reality节点"
    type: vless
    server: your.server.com
    port: 443
    uuid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    network: tcp
    tls: true
    flow: xtls-rprx-vision     # Reality 必须
    client-fingerprint: chrome # TLS 指纹
    servername: www.apple.com  # 伪装域名（与服务端一致）
    reality-opts:
      public-key: "your_public_key"
      short-id: "your_short_id"
    udp: true

  # ── Hysteria2 ────────────────────────────────────────────────
  - name: "我的HY2节点"
    type: hysteria2
    server: your.server.com
    port: 443
    password: "your_password"
    sni: your.server.com
    udp: true
    skip-cert-verify: false    # 生产环境务必为 false
```

---

## 六、代理提供者（proxy-providers）—— 机场订阅

```yaml
proxy-providers:
  机场A:
    type: http
    url: "https://your-airport.com/subscribe?token=xxx"
    interval: 86400            # 每天自动更新一次
    path: ./proxy_providers/airport-a.yaml
    health-check:
      enable: true
      url: "https://www.gstatic.com/generate_204"
      # 注意：不建议用 google.com 测速，可能触发 Google 对 IP 的风控
      interval: 300
      timeout: 5000
      lazy: true               # 懒加载：只在有流量时测速，节省资源
    # 过滤掉机场的"流量剩余/到期提醒"等信息节点
    filter: "^(?!.*(剩余|到期|官网|免费|试用|套餐|重置|过期|流量|时间)).*$"
```

---

## 七、代理组（proxy-groups）—— 策略核心

新手可先用这套简洁结构，理解逻辑后再扩展。

```yaml
proxy-groups:
  # 顶层入口：手动选哪个就用哪个
  - name: "🚀 节点选择"
    type: select
    include-all: true          # include-all: true 自动包含所有 proxy-providers 的节点
    proxies:
      - "♻️ 自动选择"
      - DIRECT

  # 自动选择延迟最低的节点
  - name: "♻️ 自动选择"
    type: url-test
    include-all: true
    url: "https://www.gstatic.com/generate_204"
    interval: 300
    tolerance: 50              # 延迟差在 50ms 内不触发切换，避免抖动
    timeout: 2000
    lazy: true

  # 兜底：所有未匹配规则的流量
  - name: "🐟 漏网之鱼"
    type: select
    proxies:
      - "🚀 节点选择"
      - DIRECT
```

**`include-all` 说明：** 设置为 `true` 后，代理组会自动包含所有 `proxy-providers` 里的所有节点，不需要逐个在 `use:` 里列出 provider 名字。大大简化了配置。

---

## 八、路由规则（rules）

**极其重要的规则顺序原则：把所有非 IP 类规则写在 IP 类规则之前。**

原因：在 fake-ip 模式下，当规则是域名类（如 `DOMAIN-SUFFIX`、`GEOSITE`），mihomo 不需要做 DNS 解析就能匹配。但一旦遇到 IP 类规则（`IP-CIDR`、`GEOIP`），mihomo 就要先做 DNS 解析得到真实 IP 再来匹配。代理流量不应该在本地做 DNS 解析——如果在 `GEOSITE,CN,DIRECT` 之前用了 `GEOIP,CN,DIRECT`，所有域名流量都会被强制 DNS 解析一次，既慢又可能引起污染。

```yaml
rules:
  # ── 非 IP 类规则（不触发 DNS 解析）─────────────────────── ──
  - DOMAIN,localhost,DIRECT
  - DOMAIN-SUFFIX,local,DIRECT

  # 国内域名直连（域名数据库匹配，不解析 DNS）
  - GEOSITE,CN,DIRECT

  # ── IP 类规则（会触发 DNS 解析，放在最后）────────────────────
  - GEOIP,LAN,DIRECT,no-resolve      # 私有 IP 直连
  - GEOIP,CN,DIRECT                   # 国内 IP 直连

  # ── 最终兜底：必须存在且是最后一条 ──────────────────────────
  - MATCH,🐟 漏网之鱼
```

**`no-resolve` 说明：** 在 IP 类规则后面加 `no-resolve`，对于还没解析成 IP 的域名流量，直接跳过这条规则（不做 DNS 解析），等后续规则处理。这样可以避免不必要的 DNS 查询。

---

## 九、最小可用完整示例

```yaml
# ══════════════════════════════════════════════════════════════
# Mihomo 最小可用配置 · 小白起步版
# ══════════════════════════════════════════════════════════════

mixed-port: 7890
allow-lan: false
mode: rule
log-level: warning
ipv6: false
find-process-mode: strict
unified-delay: true
tcp-concurrent: true
global-client-fingerprint: chrome

external-controller: 127.0.0.1:9090
external-ui: ui
external-ui-url: "https://github.com/MetaCubeX/metacubexd/archive/refs/heads/gh-pages.zip"

profile:
  store-selected: true
  store-fake-ip: true

geox-url:
  geoip:   "https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geoip.dat"
  geosite: "https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geosite.dat"

# ── DNS ────────────────────────────────────────────────────────
dns:
  enable: true
  listen: 0.0.0.0:1053
  ipv6: false
  prefer-h3: true
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  fake-ip-filter:
    - "*.lan"
    - "*.local"
    - "+.stun.*.*"
  proxy-server-nameserver:
    - https://223.5.5.5/dns-query
  nameserver:
    - system
    - https://223.5.5.5/dns-query
    - https://doh.pub/dns-query

# ── 嗅探 ──────────────────────────────────────────────────────
sniffer:
  enable: true
  sniff:
    HTTP:  { ports: [80, 8080-8880], override-destination: true }
    TLS:   { ports: [443, 8443] }
    QUIC:  { ports: [443, 8443] }

# ── 代理节点（填你自己的节点或改用 proxy-providers）──────────
proxies:
  - name: "我的节点"
    type: ss
    server: your.server.com
    port: 12345
    cipher: aes-128-gcm
    password: "your_password"
    udp: true

# ── 机场订阅（有订阅的填这里，无订阅可删掉）──────────────────
# proxy-providers:
#   机场A:
#     type: http
#     url: "https://your-airport.com/subscribe?token=xxx"
#     interval: 86400
#     path: ./proxy_providers/airport-a.yaml
#     health-check: { enable: true, url: "https://www.gstatic.com/generate_204", interval: 300, lazy: true }

# ── 代理组 ────────────────────────────────────────────────────
proxy-groups:
  - name: "🚀 节点选择"
    type: select
    proxies: ["♻️ 自动选择", "我的节点", DIRECT]

  - name: "♻️ 自动选择"
    type: url-test
    proxies: ["我的节点"]
    url: "https://www.gstatic.com/generate_204"
    interval: 300
    tolerance: 50

  - name: "🐟 漏网之鱼"
    type: select
    proxies: ["🚀 节点选择", DIRECT]

# ── 路由规则 ──────────────────────────────────────────────────
rules:
  - DOMAIN,localhost,DIRECT
  - GEOSITE,CN,DIRECT
  - GEOIP,LAN,DIRECT,no-resolve
  - GEOIP,CN,DIRECT
  - MATCH,🐟 漏网之鱼
```

**验证方法：** 启动 mihomo 后访问 `http://127.0.0.1:9090/ui`，能看到 Web 面板并显示节点则说明配置基本正确。

---

# 第二阶段：新手篇 —— 锚点、规则集、精准分流

**目标：** 用 YAML 锚点消除重复，用规则集代替手写规则，设计完整的多地区代理组体系。

---

## 一、用锚点统一管理 proxy-providers

```yaml
# ── 锚点定义区（键名随意，mihomo 会忽略不认识的顶层键）─────────
# 订阅提供者基础参数锚点
p: &p
  type: http
  interval: 86400
  path: ./proxy_providers/  # 注意：每个 provider 要有不同的 path！
  health-check:
    enable: true
    url: "https://www.gstatic.com/generate_204"
    interval: 300
    timeout: 5000
    lazy: true
  filter: "^(?!.*(剩余|到期|官网|免费|试用|套餐|重置|过期|流量|时间|有效|网址|禁止|邮箱|发布|客服|订阅|节点)).*$"

proxy-providers:
  机场A:
    <<: *p
    url: "https://airport-a.com/subscribe?token=xxx"
    path: ./proxy_providers/airport-a.yaml

  机场B:
    <<: *p
    url: "https://airport-b.com/subscribe?token=xxx"
    path: ./proxy_providers/airport-b.yaml
    interval: 43200           # 单独覆盖：这个机场每 12 小时更新（比锚点的 86400 更短）
```

---

## 二、用锚点统一管理 proxy-groups

这是进阶用户常见的写法，来自 [iyyh 的配置仓库](https://github.com/yyhhyyyyyy/selfproxy)：

```yaml
# ── 代理组基础参数锚点 ─────────────────────────────────────────
# 手动选择
g_select: &g_select
  type: select
  url: "https://www.gstatic.com/generate_204"
  include-all: true            # 自动包含所有 proxy-providers 的节点

# 自动测速（延迟最低）
g_urltest: &g_urltest
  type: url-test
  url: "https://www.gstatic.com/generate_204"
  interval: 300
  lazy: true
  tolerance: 50
  timeout: 2000
  max-failed-times: 3          # 连续失败 3 次触发重新检查
  include-all: true
  hidden: true                 # 在面板中隐藏（减少界面噪音）

# 自动回退（当前节点失败就切下一个）
g_fallback: &g_fallback
  type: fallback
  url: "https://www.gstatic.com/generate_204"
  interval: 300
  lazy: true
  timeout: 2000
  max-failed-times: 3
  include-all: true
  hidden: true

# 负载均衡（一致性散列）
g_balance: &g_balance
  type: load-balance
  strategy: consistent-hashing  # round-robin / consistent-hashing / sticky-sessions
  url: "https://www.gstatic.com/generate_204"
  interval: 300
  lazy: true
  timeout: 2000
  include-all: true
  hidden: true
```

---

## 三、节点过滤正则表达式

好的 filter 正则是代理组工作的基础。来自社区实践的完整版本：

```yaml
# 在锚点区定义节点筛选正则（YAML 锚点也可以存储字符串）
FilterHK: &FilterHK '^(?=.*(🇭🇰|港|HK|Hong Kong))(?!.*(回国|校园|游戏|剩余|到期|官网|客服|订阅|节点|过期|时间)).*$'
FilterTW: &FilterTW '^(?=.*(🇹🇼|台|TW|Taiwan))(?!.*(回国|校园|游戏|剩余|到期|官网|客服|订阅|节点|过期|时间)).*$'
FilterJP: &FilterJP '^(?=.*(🇯🇵|日|JP|Japan|Tokyo|Osaka))(?!.*(回国|校园|游戏|剩余|到期|官网|客服|订阅|节点|过期|时间)).*$'
FilterSG: &FilterSG '^(?=.*(🇸🇬|新|SG|Singapore))(?!.*(回国|校园|游戏|剩余|到期|官网|客服|订阅|节点|过期|时间)).*$'
FilterUS: &FilterUS '^(?=.*(🇺🇸|美|US|United States|Los Angeles|Silicon|Seattle))(?!.*(回国|校园|游戏|剩余|到期|官网|客服|订阅|节点|过期|时间)).*$'
FilterKR: &FilterKR '^(?=.*(🇰🇷|韩|KR|Korea))(?!.*(回国|校园|游戏|剩余|到期|官网|客服|订阅|节点|过期|时间)).*$'
FilterAll: &FilterAll '^(?=.*(.))(?!.*(回国|校园|剩余|到期|官网|客服|订阅|节点|过期|时间|流量|邮箱|工单|贩卖|通知|频道|试用|套餐|\d{4}-\d{2}-\d{2}|\d+G)).*$'
```

**正则说明：**
- `(?=.*(关键词))` → 正向前瞻，要求字符串中**包含**这些词
- `(?!.*(关键词))` → 负向前瞻，要求字符串中**不包含**这些词
- 两者组合：**必须含有地区词**且**不能含有垃圾词**

---

## 四、完整代理组设计

```yaml
proxy-groups:
  # ── 顶层主入口 ────────────────────────────────────────────────
  - name: "🎯 节点选择"
    type: select
    proxies:
      - "🌐 智能选择"
      - "✋ 手动选择"
      - DIRECT
    include-all: true

  # ── 二级入口：智能 vs 手动 ────────────────────────────────────
  - name: "🌐 智能选择"
    type: select
    proxies:
      - "🇭🇰 香港"
      - "🇸🇬 新加坡"
      - "🇯🇵 日本"
      - "🇺🇸 美国"
      - "🇰🇷 韩国"
      - "🇹🇼 台湾"

  - name: "✋ 手动选择"
    <<: *g_select

  # ── 功能性分组（指向具体地区）─────────────────────────────────
  - name: "🤖 AI 服务"
    type: select
    proxies: ["🇺🇸 美国", "🇸🇬 新加坡", "🎯 节点选择"]

  - name: "📹 流媒体"
    type: select
    proxies: ["🇭🇰 香港", "🇸🇬 新加坡", "🇯🇵 日本", "🇺🇸 美国", "🎯 节点选择"]

  - name: "✈️ 电报消息"
    type: select
    proxies: ["🎯 节点选择", "🇸🇬 新加坡", "🇭🇰 香港"]

  - name: "🍎 苹果服务"
    type: select
    proxies: [DIRECT, "🎯 节点选择", "🇭🇰 香港"]

  - name: "Ⓜ️ 微软服务"
    type: select
    proxies: [DIRECT, "🎯 节点选择", "🇺🇸 美国"]

  - name: "🛡️ 广告拦截"
    type: select
    proxies: [REJECT, DIRECT]     # REJECT = 直接拦截；REJECT-DROP = 静默丢弃

  - name: "🐟 漏网之鱼"
    type: select
    proxies: ["🎯 节点选择", DIRECT]

  # ── 地区组：每个地区都有"自动测速 / 自动回退 / 负载均衡"三合一 ──
  - name: "🇭🇰 香港"
    type: select
    proxies: ["🇭🇰 香港-自动", "🇭🇰 香港-回退", "🇭🇰 香港-均衡"]

  - name: "🇸🇬 新加坡"
    type: select
    proxies: ["🇸🇬 新加坡-自动", "🇸🇬 新加坡-回退", "🇸🇬 新加坡-均衡"]

  - name: "🇯🇵 日本"
    type: select
    proxies: ["🇯🇵 日本-自动", "🇯🇵 日本-回退", "🇯🇵 日本-均衡"]

  - name: "🇺🇸 美国"
    type: select
    proxies: ["🇺🇸 美国-自动", "🇺🇸 美国-回退", "🇺🇸 美国-均衡"]

  - name: "🇰🇷 韩国"
    type: select
    proxies: ["🇰🇷 韩国-自动", "🇰🇷 韩国-回退", "🇰🇷 韩国-均衡"]

  - name: "🇹🇼 台湾"
    type: select
    proxies: ["🇹🇼 台湾-自动", "🇹🇼 台湾-回退", "🇹🇼 台湾-均衡"]

  # ── 地区自动测速（用锚点 + 花括号单行，极简写法）──────────────
  - { name: "🇭🇰 香港-自动",   <<: *g_urltest,  filter: *FilterHK }
  - { name: "🇸🇬 新加坡-自动", <<: *g_urltest,  filter: *FilterSG }
  - { name: "🇯🇵 日本-自动",   <<: *g_urltest,  filter: *FilterJP }
  - { name: "🇺🇸 美国-自动",   <<: *g_urltest,  filter: *FilterUS }
  - { name: "🇰🇷 韩国-自动",   <<: *g_urltest,  filter: *FilterKR }
  - { name: "🇹🇼 台湾-自动",   <<: *g_urltest,  filter: *FilterTW }

  # ── 地区自动回退 ──────────────────────────────────────────────
  - { name: "🇭🇰 香港-回退",   <<: *g_fallback, filter: *FilterHK }
  - { name: "🇸🇬 新加坡-回退", <<: *g_fallback, filter: *FilterSG }
  - { name: "🇯🇵 日本-回退",   <<: *g_fallback, filter: *FilterJP }
  - { name: "🇺🇸 美国-回退",   <<: *g_fallback, filter: *FilterUS }
  - { name: "🇰🇷 韩国-回退",   <<: *g_fallback, filter: *FilterKR }
  - { name: "🇹🇼 台湾-回退",   <<: *g_fallback, filter: *FilterTW }

  # ── 地区负载均衡 ──────────────────────────────────────────────
  - { name: "🇭🇰 香港-均衡",   <<: *g_balance,  filter: *FilterHK }
  - { name: "🇸🇬 新加坡-均衡", <<: *g_balance,  filter: *FilterSG }
  - { name: "🇯🇵 日本-均衡",   <<: *g_balance,  filter: *FilterJP }
  - { name: "🇺🇸 美国-均衡",   <<: *g_balance,  filter: *FilterUS }
  - { name: "🇰🇷 韩国-均衡",   <<: *g_balance,  filter: *FilterKR }
  - { name: "🇹🇼 台湾-均衡",   <<: *g_balance,  filter: *FilterTW }
```

---

## 五、规则集（rule-providers）

规则集是社区维护的域名/IP 列表，自动更新，覆盖全面，远比手写规则靠谱。

强烈推荐使用 **SukkA 规则集**（[ruleset.skk.moe](https://ruleset.skk.moe/)），规则质量极高，分类细致，并且严格区分"非 IP 类规则"和"IP 类规则"，便于按顺序摆放。

```yaml
# ── 规则集锚点 ─────────────────────────────────────────────────
rs_classical: &rs_classical { type: http, behavior: classical, interval: 43200, format: text }
rs_domain:    &rs_domain    { type: http, behavior: domain,    interval: 43200, format: text }
rs_ipcidr:    &rs_ipcidr    { type: http, behavior: ipcidr,    interval: 43200, format: text }
# 如果使用 MetaCubeX 官方的 .mrs 格式（更快更小）：
rs_mrs:       &rs_mrs       { type: http, behavior: domain,    interval: 86400, format: mrs }

rule-providers:
  # ── 非 IP 类：广告拦截 ────────────────────────────────────────
  reject_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/reject.txt"
    path: ./rule_set/reject_non_ip.txt

  reject_non_ip_drop:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/reject-drop.txt"
    path: ./rule_set/reject_non_ip_drop.txt

  reject_domainset:
    <<: *rs_domain
    url: "https://ruleset.skk.moe/Clash/domainset/reject.txt"
    path: ./rule_set/reject_domainset.txt

  # ── 非 IP 类：AI 服务 ─────────────────────────────────────────
  ai_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/ai.txt"
    path: ./rule_set/ai_non_ip.txt

  # ── 非 IP 类：电报 ────────────────────────────────────────────
  telegram_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/telegram.txt"
    path: ./rule_set/telegram_non_ip.txt

  # ── 非 IP 类：流媒体 ──────────────────────────────────────────
  stream_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/stream.txt"
    path: ./rule_set/stream_non_ip.txt

  # ── 非 IP 类：苹果、微软 ──────────────────────────────────────
  apple_cdn:
    <<: *rs_domain
    url: "https://ruleset.skk.moe/Clash/domainset/apple_cdn.txt"
    path: ./rule_set/apple_cdn.txt

  apple_services:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/apple_services.txt"
    path: ./rule_set/apple_services.txt

  apple_cn_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/apple_cn.txt"
    path: ./rule_set/apple_cn_non_ip.txt

  microsoft_cdn_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/microsoft_cdn.txt"
    path: ./rule_set/microsoft_cdn_non_ip.txt

  microsoft_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/microsoft.txt"
    path: ./rule_set/microsoft_non_ip.txt

  # ── 非 IP 类：国内/国外/直连 ──────────────────────────────────
  global_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/global.txt"
    path: ./rule_set/global_non_ip.txt

  domestic_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/domestic.txt"
    path: ./rule_set/domestic_non_ip.txt

  direct_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/direct.txt"
    path: ./rule_set/direct_non_ip.txt

  lan_non_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/non_ip/lan.txt"
    path: ./rule_set/lan_non_ip.txt

  # ── IP 类规则（放在最后匹配）──────────────────────────────────
  reject_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/ip/reject.txt"
    path: ./rule_set/reject_ip.txt

  telegram_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/ip/telegram.txt"
    path: ./rule_set/telegram_ip.txt

  stream_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/ip/stream.txt"
    path: ./rule_set/stream_ip.txt

  domestic_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/ip/domestic.txt"
    path: ./rule_set/domestic_ip.txt

  lan_ip:
    <<: *rs_classical
    url: "https://ruleset.skk.moe/Clash/ip/lan.txt"
    path: ./rule_set/lan_ip.txt

  china_ip:
    <<: *rs_ipcidr
    url: "https://ruleset.skk.moe/Clash/ip/china_ip.txt"
    path: ./rule_set/china_ip.txt
```

---

## 六、精准路由规则

严格遵守：**所有非 IP 类规则在前，IP 类规则在后**。

```yaml
rules:
  # ════ 非 IP 类规则 ════════════════════════════════════════════

  # 广告拦截（最优先）
  - RULE-SET,reject_non_ip,🛡️ 广告拦截
  - RULE-SET,reject_domainset,🛡️ 广告拦截
  - RULE-SET,reject_non_ip_drop,REJECT-DROP   # 静默丢弃，防止某些探测

  # AI 服务
  - RULE-SET,ai_non_ip,🤖 AI 服务

  # 电报
  - RULE-SET,telegram_non_ip,✈️ 电报消息

  # 流媒体
  - RULE-SET,stream_non_ip,📹 流媒体

  # 苹果（CDN 直连，服务走苹果组，国内苹果直连）
  - RULE-SET,apple_cdn,DIRECT
  - RULE-SET,apple_cn_non_ip,DIRECT
  - RULE-SET,apple_services,🍎 苹果服务

  # 微软（CDN 直连，服务走微软组）
  - RULE-SET,microsoft_cdn_non_ip,DIRECT
  - RULE-SET,microsoft_non_ip,Ⓜ️ 微软服务

  # 国外流量走代理
  - RULE-SET,global_non_ip,🎯 节点选择

  # 国内 / 直连
  - RULE-SET,domestic_non_ip,DIRECT
  - RULE-SET,direct_non_ip,DIRECT
  - RULE-SET,lan_non_ip,DIRECT

  # ════ IP 类规则（会触发 DNS 解析，务必放在域名规则后面）═════

  - RULE-SET,reject_ip,🛡️ 广告拦截
  - RULE-SET,telegram_ip,✈️ 电报消息
  - RULE-SET,stream_ip,📹 流媒体
  - RULE-SET,lan_ip,DIRECT
  - RULE-SET,domestic_ip,DIRECT
  - RULE-SET,china_ip,DIRECT

  # ════ 兜底 ═══════════════════════════════════════════════════
  - MATCH,🐟 漏网之鱼
```

---

## 七、更精细的 DNS：nameserver-policy

当你有了清晰的规则集后，可以用 `nameserver-policy` 替代 `fallback`，实现真正的"自家人用自家 DNS"：

```yaml
dns:
  enable: true
  listen: 0.0.0.0:1053
  ipv6: false
  prefer-h3: true
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  respect-rules: true          # DNS 解析遵守路由规则：代理域名走代理侧解析

  proxy-server-nameserver:
    - https://223.5.5.5/dns-query
    - https://doh.pub/dns-query

  # nameserver-policy：指定特定域名走特定 DNS（优先级最高）
  nameserver-policy:
    # 国内主要厂商用自家 DNS，解析结果最准确
    "geosite:cn,private":
      - https://223.5.5.5/dns-query
      - https://doh.pub/dns-query
    # 国外域名走加密 DNS（配合 respect-rules 会走代理）
    "geosite:geolocation-!cn":
      - "tls://8.8.8.8"
      - "tls://1.1.1.1"
    # 也可以使用 SukkA 的 nameserver-policy（质量极高）
    # 参见：https://ruleset.skk.moe/Internal/clash_nameserver_policy.yaml

  # 默认 nameserver（nameserver-policy 未覆盖的域名使用这里）
  nameserver:
    - system
    - https://223.5.5.5/dns-query
    - https://doh.pub/dns-query
```

---

# 第三阶段：进阶篇 —— TUN、dialer-proxy、性能极致

**目标：** 开启 TUN 透明代理接管全部系统流量，掌握 dialer-proxy 代理链的正确写法（relay 已废弃），以及各项性能调优参数。

---

## 一、TUN 透明代理

### 什么是 TUN？

TUN 模式通过创建虚拟网卡，在**系统层面**接管所有流量。不需要应用程序支持代理协议，游戏、命令行工具（git、curl）、任何网络程序都会自动走代理，是目前最彻底的代理方式。

**前置条件：** 需要管理员 / root 权限运行 mihomo。

```yaml
tun:
  enable: true
  stack: mixed              # 协议栈：mixed（推荐）/ system / gvisor
                            # system：速度最快，兼容性最好，内存最低
                            # gvisor：用户态网络栈，UDP 支持更好，但性能略低
                            # mixed：TCP 走 system，UDP 走 gvisor，均衡之选
  device: mihomo            # 虚拟网卡名称（可自定义，Linux 下常见 tun0）
  dns-hijack:
    - "any:53"              # 劫持所有发往 53 端口的 DNS 请求
    - "tcp://any:53"        # 同时劫持 TCP 的 DNS
  auto-detect-interface: true   # 自动识别出口网卡（推荐）
  auto-route: true              # 自动配置系统路由表（TUN 接管全流量的关键）
  strict-route: true            # 严格路由：防止流量绕过 TUN（会影响某些 VPN 场景）
  mtu: 9000                     # MTU，适当提高减少分片（以太网推荐 1500，虚拟网络可更高）

  # 以下 IP 段排除在 TUN 之外（直接走本机网络）
  route-exclude-address:
    - "192.168.0.0/16"
    - "10.0.0.0/8"
    - "172.16.0.0/12"
    # 如果使用 ZeroTier / Tailscale 等内网穿透，把对应网段也加进来

  # gso: true               # 通用分段卸载（仅 Linux，可提升 UDP 性能）
  # gso-max-size: 65536
```

**三种协议栈速查：**

| 协议栈 | TCP 性能 | UDP 性能 | 内存占用 | 推荐场景 |
|--------|----------|----------|----------|----------|
| `system` | ⭐⭐⭐ 最快 | ⭐⭐ | 最低 | 日常主力 |
| `gvisor` | ⭐⭐ | ⭐⭐⭐ 最好 | 最高 | UDP 密集场景 |
| `mixed` | ⭐⭐⭐ | ⭐⭐⭐ | 居中 | **推荐，均衡** |

**TUN + Sniffer 必须同时开启：** TUN 模式拿到的是 IP 地址（因为流量在 IP 层就被截获了），没有域名信息。嗅探器负责从流量的应用层内容（TLS SNI、HTTP Host 等）中提取真实域名，再把这个域名映射回规则匹配。如果不开嗅探，基于域名的规则在 TUN 模式下几乎全部失效。

---

## 二、dialer-proxy：代理链的正确姿势

### relay 已废弃，请用 dialer-proxy

`relay` 类型的 proxy-group 在官方文档中已明确标注"即将废弃"，且存在 mux 多路复用场景下的问题。**现在正确的代理链写法是 `dialer-proxy`**，它写在 proxy 节点的配置上，而不是 proxy-group 类型。

### dialer-proxy 的原理

```
内核 ─── 落地节点(出口) ──→ 前置节点包装 ═══ 前置节点 ══→ 落地节点服务端 ─→ 目标
```

最终效果：
- 目标网站只看到**落地节点**的 IP
- 你的宽带运营商只看到你在连接**前置节点**
- 前置节点只知道它在帮你连接落地节点

### 场景一：用订阅节点作为前置，连接自建 VPS

```yaml
proxies:
  # 你自己在 VPS 上搭建的落地节点（出口 IP 是你 VPS 的 IP）
  - name: "我的VPS-落地"
    type: ss
    server: your-vps.com
    port: 12345
    cipher: aes-128-gcm
    password: "vps_password"
    udp: true
    dialer-proxy: "🎯 节点选择"   # 通过这个代理组来连接落地节点

proxy-providers:
  机场A:
    type: http
    url: "https://airport.com/subscribe?token=xxx"
    interval: 86400
    path: ./proxy_providers/airport-a.yaml
    health-check: { enable: true, url: "https://www.gstatic.com/generate_204", interval: 300, lazy: true }

proxy-groups:
  - name: "🎯 节点选择"    # 前置节点：从机场订阅里选
    type: select
    include-all: true

  # 流量走向：浏览器 → mihomo → 机场节点（前置）→ 我的VPS（落地）→ 目标网站
  - name: "🔗 VPS落地"
    type: select
    proxies: ["我的VPS-落地"]

rules:
  - MATCH,🔗 VPS落地
```

**注意：** 落地节点建议使用简单协议（`ss`、`vmess`），**不要**用 UDP 类协议（`hysteria2`、`tuic`、`wg`）作为落地，因为前置节点到落地节点的连接是 TCP，UDP 落地在这种链路下无法正常工作。

### 场景二：通过 proxy-providers override 批量设置前置

```yaml
proxies:
  - name: "前置节点"
    type: ss
    server: your-relay.com
    port: 12345
    cipher: aes-128-gcm
    password: "relay_password"

proxy-providers:
  # 这个 provider 里所有节点都经由"前置节点"转发
  落地节点池:
    type: http
    url: "https://landing-nodes.com/subscribe?token=xxx"
    interval: 86400
    path: ./proxy_providers/landing.yaml
    health-check: { enable: true, url: "https://www.gstatic.com/generate_204", interval: 300 }
    override:
      dialer-proxy: "前置节点"    # provider 里所有节点都走这个前置

proxy-groups:
  - name: "🔗 链式代理"
    type: select
    use: ["落地节点池"]

rules:
  - MATCH,🔗 链式代理
```

### relay 迁移到 dialer-proxy

如果你之前有这样的 relay 配置：

```yaml
# ❌ 旧写法（relay 已废弃）
proxy-groups:
  - name: "链式"
    type: relay
    proxies: ["前置选择", "落地选择"]
  - name: "前置选择"
    type: select
    proxies: ["proxy1", "proxy2"]
  - name: "落地选择"
    type: select
    proxies: ["proxy3", "proxy4"]
```

迁移后的正确写法：

```yaml
# ✅ 新写法（dialer-proxy）
proxies:
  - { name: "proxy1", type: "socks", ... }
  - { name: "proxy2", type: "socks", ... }

proxy-groups:
  - name: "前置选择"
    type: select
    proxies: ["proxy1", "proxy2"]

  # 落地节点放进 proxy-providers（inline 类型或 http/file 类型）
  # 通过 override.dialer-proxy 批量指定前置
  - name: "落地选择"
    type: select
    use: ["落地provider"]

proxy-providers:
  落地provider:
    type: inline
    override:
      dialer-proxy: "前置选择"   # 所有落地节点都经过"前置选择"这个组
    payload:
      - { name: "proxy3", type: "socks", ... }
      - { name: "proxy4", type: "socks", ... }
```

---

## 三、WireGuard + dialer-proxy（WARP 套娃）

这是一个常见的进阶用法：让 WireGuard/WARP 节点通过另一个代理节点建立连接。

```yaml
proxies:
  # 前置节点（SS/VMess/Trojan 等，负责连到 WireGuard 服务器）
  - name: "🚀 前置"
    type: ss
    server: your.relay.com
    port: 12345
    cipher: aes-128-gcm
    password: "password"

  # WireGuard 节点（通过前置节点建立 WG 隧道）
  - name: "☁️ WARP"
    type: wireguard
    server: engage.cloudflareclient.com
    port: 2408
    ip: "172.16.0.2/32"
    private-key: "your_private_key"
    public-key: "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo="
    udp: true
    mtu: 1280
    dialer-proxy: "🚀 前置"        # WARP 通过前置节点建立连接
    remote-dns-resolve: true
    dns:
      - https://dns.cloudflare.com/dns-query
```

---

## 四、子规则（sub-rule）

子规则允许在命中某个规则后，进入一个子规则集进一步细分，实现嵌套分流：

```yaml
sub-rules:
  # 当流量进入流媒体规则后，进一步细分到具体平台
  streaming:
    - GEOSITE,netflix,🎬 Netflix
    - GEOSITE,youtube,📺 YouTube
    - GEOSITE,bilibili,DIRECT          # B站直连
    - GEOSITE,bahamut,🇹🇼 台湾         # 巴哈姆特需台湾节点
    - MATCH,📹 流媒体                   # 其他流媒体走通用组

proxy-groups:
  - name: "🎬 Netflix"
    type: select
    proxies: ["🇺🇸 美国", "🇸🇬 新加坡", "🇭🇰 香港"]

  - name: "📺 YouTube"
    type: select
    proxies: ["🇭🇰 香港", "🇸🇬 新加坡", "🇯🇵 日本"]

rules:
  # 流媒体流量进入子规则
  - RULE-SET,stream_non_ip,SUB-RULE,streaming
  # ... 其他规则
  - MATCH,🐟 漏网之鱼
```

---

## 五、性能调优

```yaml
# ══ 全局性能参数 ══════════════════════════════════════════════
mixed-port: 7890
unified-delay: true            # 统一延迟：用实际往返时间，比握手时间更准
tcp-concurrent: true           # TCP 并发建连：选最快的 IP
keep-alive-interval: 30        # TCP keepalive 探测间隔（秒）
keep-alive-idle: 600           # TCP keepalive 空闲等待时间（秒）

# ══ GeoData 加载优化 ═══════════════════════════════════════════
geodata-mode: true
geodata-loader: memconservative  # 内存节省模式（路由器/内存小的设备推荐）
                                 # standard：性能更高，内存占用也更多
geosite-matcher: succinct        # succinct（精简）/ mph（哈希，速度最快）

# ══ 出口网卡绑定（多网卡环境）════════════════════════════════
# interface-name: eth0           # 指定出口网卡，防止意外走错网卡
# routing-mark: 666              # Linux 路由策略标记（配合 ip rule 使用）
```

**rule-providers 格式选择：** 优先选 `.mrs` 格式（mihomo 专用二进制格式），加载速度比 `.yaml` 快 10 倍以上，内存占用更低。只有在 `.mrs` 格式的规则集不可用时才选 `.yaml`。

---

## 六、进阶 DNS 完整配置

```yaml
dns:
  enable: true
  listen: 0.0.0.0:1053
  ipv6: false
  prefer-h3: true
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  respect-rules: true         # 代理域名走代理侧 DNS，直连域名走本地 DNS

  fake-ip-filter:
    - "*.lan"
    - "*.local"
    - "*.localhost"
    - "time.*.com"
    - "time.nist.gov"
    - "+.stun.*.*"
    - "+.stun.*.*.*"
    - "+.xboxlive.com"
    - "+.nintendo.net"
    - "+.push.apple.com"

  # 解析代理节点域名用
  proxy-server-nameserver:
    - https://223.5.5.5/dns-query
    - https://doh.pub/dns-query

  # 精细 DNS 分流（优先级高于 nameserver）
  nameserver-policy:
    # 国内域名 → 国内 DNS
    "geosite:cn,private":
      - https://223.5.5.5/dns-query
      - https://doh.pub/dns-query
    # 国外域名 → 走代理侧 DNS（配合 respect-rules）
    "geosite:geolocation-!cn":
      - "tls://8.8.8.8"
      - "tls://1.1.1.1"

  # 兜底 DNS
  nameserver:
    - system
    - https://223.5.5.5/dns-query
    - https://doh.pub/dns-query
```

---

## 七、完整进阶配置模板

```yaml
# ══════════════════════════════════════════════════════════════
# Mihomo 进阶配置模板 · 综合所有进阶特性
# ══════════════════════════════════════════════════════════════

# ── 全局 ──────────────────────────────────────────────────────
mixed-port: 7890
allow-lan: false
mode: rule
log-level: warning
ipv6: false
find-process-mode: strict
unified-delay: true
tcp-concurrent: true
global-client-fingerprint: chrome
keep-alive-interval: 30
keep-alive-idle: 600
geodata-mode: true
geodata-loader: memconservative
geosite-matcher: succinct

external-controller: 127.0.0.1:9090
# secret: "your_strong_password"
external-ui: ui
external-ui-url: "https://github.com/MetaCubeX/metacubexd/archive/refs/heads/gh-pages.zip"

profile: { store-selected: true, store-fake-ip: true }

geox-url:
  geoip:   "https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geoip.dat"
  geosite: "https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geosite.dat"
  mmdb:    "https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/country.mmdb"

# ── TUN ───────────────────────────────────────────────────────
tun:
  enable: true
  stack: mixed
  device: mihomo
  dns-hijack: ["any:53", "tcp://any:53"]
  auto-detect-interface: true
  auto-route: true
  strict-route: true
  mtu: 9000
  route-exclude-address: ["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"]

# ── 嗅探 ──────────────────────────────────────────────────────
sniffer:
  enable: true
  sniff:
    HTTP:  { ports: [80, 8080-8880], override-destination: true }
    TLS:   { ports: [443, 8443] }
    QUIC:  { ports: [443, 8443] }
  skip-domain:
    - "Mijia Cloud"
    - "+.push.apple.com"

# ── DNS ───────────────────────────────────────────────────────
dns:
  enable: true
  listen: 0.0.0.0:1053
  ipv6: false
  prefer-h3: true
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  respect-rules: true
  fake-ip-filter:
    - "*.lan"
    - "*.local"
    - "+.stun.*.*"
    - "+.stun.*.*.*"
    - "time.*.com"
    - "+.xboxlive.com"
    - "+.nintendo.net"
    - "+.push.apple.com"
  proxy-server-nameserver:
    - https://223.5.5.5/dns-query
    - https://doh.pub/dns-query
  nameserver-policy:
    "geosite:cn,private":
      - https://223.5.5.5/dns-query
      - https://doh.pub/dns-query
    "geosite:geolocation-!cn":
      - "tls://8.8.8.8"
      - "tls://1.1.1.1"
  nameserver:
    - system
    - https://223.5.5.5/dns-query
    - https://doh.pub/dns-query

# ══ 锚点定义区（键名不在 mihomo 文档中，会被忽略，仅作 YAML 引用）══

# 订阅提供者基础参数
p: &p
  type: http
  interval: 86400
  health-check: { enable: true, url: "https://www.gstatic.com/generate_204", interval: 300, lazy: true }
  filter: "^(?!.*(剩余|到期|官网|免费|试用|套餐|重置|过期|流量|时间|邮箱|客服|订阅)).*$"

# 规则集基础参数
rs_classical: &rs_classical { type: http, behavior: classical, interval: 43200, format: text }
rs_domain:    &rs_domain    { type: http, behavior: domain,    interval: 43200, format: text }
rs_ipcidr:    &rs_ipcidr    { type: http, behavior: ipcidr,    interval: 43200, format: text }

# 代理组基础参数
g_select:   &g_select   { type: select,       url: "https://www.gstatic.com/generate_204", include-all: true }
g_urltest:  &g_urltest  { type: url-test,     url: "https://www.gstatic.com/generate_204", interval: 300, lazy: true, tolerance: 50, timeout: 2000, max-failed-times: 3, include-all: true, hidden: true }
g_fallback: &g_fallback { type: fallback,     url: "https://www.gstatic.com/generate_204", interval: 300, lazy: true, timeout: 2000, max-failed-times: 3, include-all: true, hidden: true }
g_balance:  &g_balance  { type: load-balance, url: "https://www.gstatic.com/generate_204", interval: 300, lazy: true, timeout: 2000, strategy: consistent-hashing, max-failed-times: 3, include-all: true, hidden: true }

# 节点过滤正则
FilterHK: &FilterHK '^(?=.*(🇭🇰|港|HK|Hong Kong))(?!.*(回国|校园|剩余|到期|官网|客服|订阅|节点|过期)).*$'
FilterTW: &FilterTW '^(?=.*(🇹🇼|台|TW|Taiwan))(?!.*(回国|校园|剩余|到期|官网|客服|订阅|节点|过期)).*$'
FilterJP: &FilterJP '^(?=.*(🇯🇵|日|JP|Japan|Tokyo|Osaka))(?!.*(回国|校园|剩余|到期|官网|客服|订阅|节点|过期)).*$'
FilterSG: &FilterSG '^(?=.*(🇸🇬|新|SG|Singapore))(?!.*(回国|校园|剩余|到期|官网|客服|订阅|节点|过期)).*$'
FilterUS: &FilterUS '^(?=.*(🇺🇸|美|US|United States))(?!.*(回国|校园|剩余|到期|官网|客服|订阅|节点|过期)).*$'
FilterKR: &FilterKR '^(?=.*(🇰🇷|韩|KR|Korea))(?!.*(回国|校园|剩余|到期|官网|客服|订阅|节点|过期)).*$'

# ── 代理提供者 ────────────────────────────────────────────────
proxy-providers:
  机场订阅:
    <<: *p
    url: "https://your-airport.com/subscribe?token=xxx"
    path: ./proxy_providers/airport.yaml

# ── 代理组 ────────────────────────────────────────────────────
proxy-groups:
  - name: "🎯 节点选择"
    type: select
    proxies: ["🌐 智能选择", "✋ 手动选择", DIRECT]
    include-all: true

  - name: "🌐 智能选择"
    type: select
    proxies: ["🇭🇰 香港", "🇸🇬 新加坡", "🇯🇵 日本", "🇺🇸 美国", "🇰🇷 韩国", "🇹🇼 台湾"]

  - { name: "✋ 手动选择",  <<: *g_select }

  - name: "🤖 AI 服务"
    type: select
    proxies: ["🇺🇸 美国", "🇸🇬 新加坡", "🎯 节点选择"]

  - name: "📹 流媒体"
    type: select
    proxies: ["🇭🇰 香港", "🇸🇬 新加坡", "🇯🇵 日本", "🇺🇸 美国", "🎯 节点选择"]

  - name: "✈️ 电报消息"
    type: select
    proxies: ["🎯 节点选择", "🇸🇬 新加坡", "🇭🇰 香港"]

  - name: "🍎 苹果服务"
    type: select
    proxies: [DIRECT, "🎯 节点选择", "🇭🇰 香港"]

  - name: "Ⓜ️ 微软服务"
    type: select
    proxies: [DIRECT, "🎯 节点选择", "🇺🇸 美国"]

  - name: "🛡️ 广告拦截"
    type: select
    proxies: [REJECT, DIRECT]

  - name: "🐟 漏网之鱼"
    type: select
    proxies: ["🎯 节点选择", DIRECT]

  # 地区三合一
  - name: "🇭🇰 香港"
    type: select
    proxies: ["🇭🇰 香港-自动", "🇭🇰 香港-回退", "🇭🇰 香港-均衡"]
  - name: "🇸🇬 新加坡"
    type: select
    proxies: ["🇸🇬 新加坡-自动", "🇸🇬 新加坡-回退", "🇸🇬 新加坡-均衡"]
  - name: "🇯🇵 日本"
    type: select
    proxies: ["🇯🇵 日本-自动", "🇯🇵 日本-回退", "🇯🇵 日本-均衡"]
  - name: "🇺🇸 美国"
    type: select
    proxies: ["🇺🇸 美国-自动", "🇺🇸 美国-回退", "🇺🇸 美国-均衡"]
  - name: "🇰🇷 韩国"
    type: select
    proxies: ["🇰🇷 韩国-自动", "🇰🇷 韩国-回退", "🇰🇷 韩国-均衡"]
  - name: "🇹🇼 台湾"
    type: select
    proxies: ["🇹🇼 台湾-自动", "🇹🇼 台湾-回退", "🇹🇼 台湾-均衡"]

  - { name: "🇭🇰 香港-自动",   <<: *g_urltest,  filter: *FilterHK }
  - { name: "🇸🇬 新加坡-自动", <<: *g_urltest,  filter: *FilterSG }
  - { name: "🇯🇵 日本-自动",   <<: *g_urltest,  filter: *FilterJP }
  - { name: "🇺🇸 美国-自动",   <<: *g_urltest,  filter: *FilterUS }
  - { name: "🇰🇷 韩国-自动",   <<: *g_urltest,  filter: *FilterKR }
  - { name: "🇹🇼 台湾-自动",   <<: *g_urltest,  filter: *FilterTW }

  - { name: "🇭🇰 香港-回退",   <<: *g_fallback, filter: *FilterHK }
  - { name: "🇸🇬 新加坡-回退", <<: *g_fallback, filter: *FilterSG }
  - { name: "🇯🇵 日本-回退",   <<: *g_fallback, filter: *FilterJP }
  - { name: "🇺🇸 美国-回退",   <<: *g_fallback, filter: *FilterUS }
  - { name: "🇰🇷 韩国-回退",   <<: *g_fallback, filter: *FilterKR }
  - { name: "🇹🇼 台湾-回退",   <<: *g_fallback, filter: *FilterTW }

  - { name: "🇭🇰 香港-均衡",   <<: *g_balance,  filter: *FilterHK }
  - { name: "🇸🇬 新加坡-均衡", <<: *g_balance,  filter: *FilterSG }
  - { name: "🇯🇵 日本-均衡",   <<: *g_balance,  filter: *FilterJP }
  - { name: "🇺🇸 美国-均衡",   <<: *g_balance,  filter: *FilterUS }
  - { name: "🇰🇷 韩国-均衡",   <<: *g_balance,  filter: *FilterKR }
  - { name: "🇹🇼 台湾-均衡",   <<: *g_balance,  filter: *FilterTW }

# ── 规则集 ────────────────────────────────────────────────────
rule-providers:
  reject_non_ip:      { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/reject.txt",          path: ./rule_set/reject_non_ip.txt }
  reject_non_ip_drop: { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/reject-drop.txt",     path: ./rule_set/reject_non_ip_drop.txt }
  reject_domainset:   { <<: *rs_domain,    url: "https://ruleset.skk.moe/Clash/domainset/reject.txt",       path: ./rule_set/reject_domainset.txt }
  ai_non_ip:          { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/ai.txt",              path: ./rule_set/ai_non_ip.txt }
  telegram_non_ip:    { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/telegram.txt",        path: ./rule_set/telegram_non_ip.txt }
  stream_non_ip:      { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/stream.txt",          path: ./rule_set/stream_non_ip.txt }
  apple_cdn:          { <<: *rs_domain,    url: "https://ruleset.skk.moe/Clash/domainset/apple_cdn.txt",    path: ./rule_set/apple_cdn.txt }
  apple_services:     { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/apple_services.txt", path: ./rule_set/apple_services.txt }
  apple_cn_non_ip:    { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/apple_cn.txt",       path: ./rule_set/apple_cn_non_ip.txt }
  microsoft_cdn_non_ip: { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/microsoft_cdn.txt", path: ./rule_set/microsoft_cdn_non_ip.txt }
  microsoft_non_ip:   { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/microsoft.txt",      path: ./rule_set/microsoft_non_ip.txt }
  global_non_ip:      { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/global.txt",         path: ./rule_set/global_non_ip.txt }
  domestic_non_ip:    { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/domestic.txt",       path: ./rule_set/domestic_non_ip.txt }
  direct_non_ip:      { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/direct.txt",         path: ./rule_set/direct_non_ip.txt }
  lan_non_ip:         { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/non_ip/lan.txt",            path: ./rule_set/lan_non_ip.txt }
  reject_ip:          { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/ip/reject.txt",             path: ./rule_set/reject_ip.txt }
  telegram_ip:        { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/ip/telegram.txt",           path: ./rule_set/telegram_ip.txt }
  stream_ip:          { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/ip/stream.txt",             path: ./rule_set/stream_ip.txt }
  domestic_ip:        { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/ip/domestic.txt",           path: ./rule_set/domestic_ip.txt }
  lan_ip:             { <<: *rs_classical, url: "https://ruleset.skk.moe/Clash/ip/lan.txt",                path: ./rule_set/lan_ip.txt }
  china_ip:           { <<: *rs_ipcidr,    url: "https://ruleset.skk.moe/Clash/ip/china_ip.txt",           path: ./rule_set/china_ip.txt }

# ── 路由规则 ──────────────────────────────────────────────────
rules:
  # 非 IP 类（不触发 DNS 解析）
  - RULE-SET,reject_non_ip,🛡️ 广告拦截
  - RULE-SET,reject_domainset,🛡️ 广告拦截
  - RULE-SET,reject_non_ip_drop,REJECT-DROP
  - RULE-SET,ai_non_ip,🤖 AI 服务
  - RULE-SET,telegram_non_ip,✈️ 电报消息
  - RULE-SET,stream_non_ip,📹 流媒体
  - RULE-SET,apple_cdn,DIRECT
  - RULE-SET,apple_cn_non_ip,DIRECT
  - RULE-SET,apple_services,🍎 苹果服务
  - RULE-SET,microsoft_cdn_non_ip,DIRECT
  - RULE-SET,microsoft_non_ip,Ⓜ️ 微软服务
  - RULE-SET,global_non_ip,🎯 节点选择
  - RULE-SET,domestic_non_ip,DIRECT
  - RULE-SET,direct_non_ip,DIRECT
  - RULE-SET,lan_non_ip,DIRECT
  # IP 类（会触发 DNS 解析，放在最后）
  - RULE-SET,reject_ip,🛡️ 广告拦截
  - RULE-SET,telegram_ip,✈️ 电报消息
  - RULE-SET,stream_ip,📹 流媒体
  - RULE-SET,lan_ip,DIRECT
  - RULE-SET,domestic_ip,DIRECT
  - RULE-SET,china_ip,DIRECT
  - MATCH,🐟 漏网之鱼
```

---

## 八、常见问题与排查

**Q：启动报错 `yaml: line N: did not find expected...`**

这是 YAML 格式错误。最常见原因：混用了 Tab 和空格；冒号后面没有加空格；字符串里有特殊字符没有用引号包裹。建议用 VS Code 安装 YAML 插件，它会实时标红错误。

**Q：`mode: global` 能翻墙但 `mode: rule` 不行？**

说明规则写错了。最大可能：国外域名被某条规则匹配到 DIRECT，或者国内 IP 被匹配到代理。调试步骤：在 Web 面板的 Logs 里查看哪条规则命中了问题流量，再针对性调整。

**Q：节点延迟正常但某些网站打不开？**

如果是 `fake-ip` 模式下的特定应用（游戏、某些 APP），可能该应用不兼容 fake-ip，尝试把它的域名加入 `fake-ip-filter`。如果是所有网站都慢，检查 DNS 配置，确认 `proxy-server-nameserver` 正常工作。

**Q：开启 TUN 后 DNS 查询很慢？**

确认 `dns-hijack: ["any:53"]` 已设置，且 `sniffer` 已开启。如果 `strict-route: true` 导致某些流量异常，尝试关闭严格路由。

**Q：`dialer-proxy` 配置后节点测速失败？**

落地节点的服务端协议不能是纯 UDP 类型（如 `hysteria2`、`tuic`），因为 dialer-proxy 链的 TCP 连接无法承载这些协议的 UDP 数据。落地节点请选用 `ss`（AEAD）或 `vmess` / `trojan`。

**Q：规则集更新失败 / 下载很慢？**

将 `proxy-providers` 和 `rule-providers` 的更新请求通过代理拉取：在相应 provider 中加入 `proxy: "🎯 节点选择"` 字段，让更新请求走代理出去。

---

## 附录：推荐资源

| 类型 | 名称 | 地址 |
|------|------|------|
| 规则集（强烈推荐） | SukkA RuleSet | [ruleset.skk.moe](https://ruleset.skk.moe/) |
| 规则数据库 | MetaCubeX meta-rules-dat | [github.com/MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat) |
| 配置参考 | iyyh 自用配置 | [iyyh.net/posts/mihomo-self-config](https://iyyh.net/posts/mihomo-self-config) |
| 配置合集 | HenryChiao YAMLS | [github.com/HenryChiao/MIHOMO_YAMLS](https://github.com/HenryChiao/MIHOMO_YAMLS) |
| 官方文档 | 虚空终端 Docs | [wiki.metacubex.one](https://wiki.metacubex.one/) |
| DNS 深度解析 | SukkA DNS 文章 | [blog.skk.moe/post/lets-talk-about-dns-cdn-fake-ip](https://blog.skk.moe/post/lets-talk-about-dns-cdn-fake-ip/) |
| Web 面板 | MetaCubeX Dashboard | [github.com/MetaCubeX/metacubexd](https://github.com/MetaCubeX/metacubexd) |
| Web 面板 | Zashboard | [github.com/Zephyruso/zashboard](https://github.com/Zephyruso/zashboard) |
| 客户端（Windows/Linux/macOS） | Clash Verge Rev | [github.com/clash-verge-rev/clash-verge-rev](https://github.com/clash-verge-rev/clash-verge-rev) |
| 客户端（Windows） | Sparkle | [github.com/xishang0128/sparkle](https://github.com/xishang0128/sparkle) |

---

> **一句话总结：** 不要复制你看不懂的配置。从小白的最小示例出发，每解决一个"这里不对劲"就多理解一个概念，配置文件是你对自己网络需求的精确表达，没有"最好的配置"，只有最适合你的配置。
