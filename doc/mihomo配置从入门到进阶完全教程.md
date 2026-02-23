# Mihomo 配置从入门到进阶：三阶段完全教程

> **参考来源：**
> [虚空终端官方文档](https://wiki.metacubex.one/) · [官方语法手册](https://wiki.metacubex.one/en/handbook/syntax/) · [官方 dialer-proxy 文档](https://wiki.metacubex.one/en/config/proxies/dialer-proxy/) · [iyyh 自用配置](https://iyyh.net/posts/mihomo-self-config) · [SukkA 规则集](https://ruleset.skk.moe/) · [HenryChiao YAMLS 合集](https://github.com/HenryChiao/MIHOMO_YAMLS)

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

### 📊 各流派锚点写法对比

社区里存在四种主要的锚点使用风格，各有侧重，没有绝对的好坏，理解区别后选择适合自己的即可。

---

**流派一：只锚定 proxy-providers（最简单，入门首选）**

```yaml
# 来源：大量入门教程、官方示例
p: &p
  type: http
  interval: 86400
  health-check: { enable: true, url: "https://www.gstatic.com/generate_204", interval: 300 }

proxy-providers:
  机场A: { <<: *p, url: "...", path: ./proxy_providers/a.yaml }
  机场B: { <<: *p, url: "...", path: ./proxy_providers/b.yaml }

# proxy-groups 部分仍然手写，没有锚点
proxy-groups:
  - name: "🚀 节点选择"
    type: select
    use: [机场A, 机场B]
    proxies: [DIRECT]
```

| 优点 | 缺点 |
|------|------|
| 结构清晰，一眼看懂 | proxy-groups 部分仍有大量重复 |
| 对新手友好，易于调试 | 地区组多时维护成本上升 |
| 修改 provider 参数只需改一处 | 不适合十几个地区的大型配置 |

---

**流派二：providers + groups 全部锚定（iyyh 风格，社区主流）**

```yaml
# 来源：iyyh 自用配置 / 多数进阶教程
# 特点：同时锚定 provider 参数 和 group 类型参数，filter 正则也锚定为字符串

NodeParam: &NodeParam
  type: http
  interval: 86400
  health-check: { enable: true, url: "https://...", interval: 300 }

# 代理组四种类型全部锚定
Select:    &Select    { type: select,       include-all: true }
UrlTest:   &UrlTest   { type: url-test,     include-all: true, interval: 300, lazy: true, tolerance: 50, timeout: 2000, hidden: true }
FallBack:  &FallBack  { type: fallback,     include-all: true, interval: 300, lazy: true, timeout: 2000, hidden: true }
LoadBalance: &LoadBalance { type: load-balance, include-all: true, interval: 300, lazy: true, strategy: consistent-hashing, hidden: true }

# filter 正则也锚定为字符串引用
FilterHK: &FilterHK '^(?=.*(🇭🇰|港|HK))(?!.*(剩余|到期|客服)).*$'

proxy-providers:
  Node: { <<: *NodeParam, url: "...", path: ./proxy_providers/node.yaml }

proxy-groups:
  - { name: "🇭🇰 香港-自动",   <<: *UrlTest,    filter: *FilterHK }
  - { name: "🇭🇰 香港-回退",   <<: *FallBack,   filter: *FilterHK }
  - { name: "🇭🇰 香港-均衡",   <<: *LoadBalance, filter: *FilterHK }
  - { name: "🇭🇰 手动选择",   <<: *Select,     filter: *FilterHK }
```

| 优点 | 缺点 |
|------|------|
| 极大减少重复，地区组增减只需一行 | 初次阅读有一定理解门槛 |
| filter 锚点保证正则一致，不怕改漏 | 调试时需要展开锚点才能看完整参数 |
| 是目前社区最主流的进阶写法 | `<<:` 合并不能覆盖数组，只能整体替换 |

---

**流派三：proxies 选项也锚定（旧式兼容写法）**

```yaml
# 来源：部分早期教程，官方示例中也有体现
# 特点：把一组 proxy-groups 里常用的 proxies 列表也做成锚点，方便多个功能组复用

# 一个"通用备选节点列表"
pr: &pr
  type: select
  proxies: ["手动选择", "自动选择", "🇭🇰 香港", "🇯🇵 日本", "🇸🇬 新加坡", "🇺🇸 美国", DIRECT]

proxy-groups:
  - name: "🤖 AI 服务"
    <<: *pr              # 直接继承完整 proxies 列表

  - name: "📹 流媒体"
    <<: *pr              # 同一套选项

  - name: "✈️ 电报消息"
    <<: *pr
```

| 优点 | 缺点 |
|------|------|
| 功能组的 proxies 选项保持统一，不容易漏写 | 各功能组的首选节点无法个性化（比如 AI 想默认美国、流媒体想默认香港） |
| 配置极短，适合"懒人"场景 | 如果某个功能组需要不同的 proxies 顺序，锚点就无法满足，反而要额外处理 |
| | 随着需求复杂，这种锚定方式往往最终被放弃 |

> **注意一个 YAML 限制：** `<<:` 合并时，如果锚点和当前块都有同名的列表键（如 `proxies`），**不会合并列表，而是当前块的值整体覆盖锚点的值**。所以 `<<: *pr` + 单独写 `proxies:` 时，单独写的 `proxies` 完全替换锚点里的 `proxies`，两个列表不会合并。

---

**流派四：单行 JSON 花括号 + 锚点极简写法（HenryChiao / YYDS 等配置合集风格）**

```yaml
# 来源：HenryChiao YAMLS、666OS/YYDS 等重度配置合集
# 特点：把锚点和单行花括号结合到极致，一行一个 group，视觉上类似表格

# 锚点定义
p:  &p  { type: http, interval: 86400, health-check: { enable: true, url: "https://www.gstatic.com/generate_204", interval: 300, lazy: true } }
g_t: &g_t { type: url-test,  url: "https://www.gstatic.com/generate_204", interval: 300, lazy: true, tolerance: 50, timeout: 2000, include-all: true, hidden: true }
g_f: &g_f { type: fallback,  url: "https://www.gstatic.com/generate_204", interval: 300, lazy: true, timeout: 2000, include-all: true, hidden: true }
g_b: &g_b { type: load-balance, url: "https://www.gstatic.com/generate_204", interval: 300, strategy: consistent-hashing, include-all: true, hidden: true }
FHK: &FHK '^(?=.*(🇭🇰|港|HK|Hong))(?!.*(回国|剩余|到期|客服|订阅)).*$'
FSG: &FSG '^(?=.*(🇸🇬|新|SG|Singapore))(?!.*(回国|剩余|到期|客服|订阅)).*$'
FJP: &FJP '^(?=.*(🇯🇵|日|JP|Japan))(?!.*(回国|剩余|到期|客服|订阅)).*$'

proxy-providers:
  机场A: { <<: *p, url: "...", path: ./proxy_providers/a.yaml }
  机场B: { <<: *p, url: "...", path: ./proxy_providers/b.yaml }

proxy-groups:
  # 地区三合一，一气呵成
  - { name: "🇭🇰 香港-自动", <<: *g_t, filter: *FHK }
  - { name: "🇭🇰 香港-回退", <<: *g_f, filter: *FHK }
  - { name: "🇭🇰 香港-均衡", <<: *g_b, filter: *FHK }
  - { name: "🇸🇬 新加坡-自动", <<: *g_t, filter: *FSG }
  - { name: "🇸🇬 新加坡-回退", <<: *g_f, filter: *FSG }
  - { name: "🇯🇵 日本-自动",   <<: *g_t, filter: *FJP }
  # ... 每个地区三行，极其整齐
```

| 优点 | 缺点 |
|------|------|
| 配置文件最短，视觉最整洁，像表格一样一目了然 | 对 YAML 锚点不熟悉的人几乎无法读懂 |
| 增加一个地区只需加三行，维护成本极低 | 单行花括号不能加注释，调试困难 |
| 结构高度一致，适合大型配置（几十个地区） | 锚点名称短（如 `g_t`）不语义化，需要配套文档 |
| 是目前大型配置仓库的主流做法 | 一旦某个 group 需要特殊参数，要单独处理，破坏整齐感 |

---

**流派五：三层嵌套锚点（理论最优，有重要限制）**

这是来自 [HenryChiao MIHOMO_AIO](https://github.com/HenryChiao/MIHOMO_AIO) 以及 issue #2274 中社区用户提议的终极写法，思路是把锚点再拆一层：**基础参数层** → **组类型层** → **地区层**，三层级联继承。

```yaml
# 来源：HenryChiao AIO / 社区 Issue #2274 的理想写法
# 思路：把"公共基础"、"组类型"、"地区 filter+icon" 各自锚定，然后合并

# 第一层：所有 group 共享的基础参数
area: &area
  url: "https://www.gstatic.com/generate_204"
  interval: 300
  include-all: true
  lazy: true
  timeout: 2000

# 第二层：在 area 基础上叠加各类型特有参数
auto:  &auto  { type: url-test,      <<: *area, tolerance: 50, max-failed-times: 3, hidden: true }
fall:  &fall  { type: fallback,      <<: *area, max-failed-times: 3, hidden: true }
bal:   &bal   { type: load-balance,  <<: *area, strategy: consistent-hashing, hidden: true }

# 第三层：每个地区的 filter + icon 也锚定成一个对象
hk: &hk { filter: "^(?=.*(🇭🇰|港|HK|Hong))(?!.*(回国|剩余|到期|客服)).*$", icon: "https://example.com/hk.svg" }
sg: &sg { filter: "^(?=.*(🇸🇬|新|SG|Singapore))(?!.*(回国|剩余|到期|客服)).*$", icon: "https://example.com/sg.svg" }
jp: &jp { filter: "^(?=.*(🇯🇵|日|JP|Japan))(?!.*(回国|剩余|到期|客服)).*$", icon: "https://example.com/jp.svg" }

# ── 理想写法（目前 mihomo 不支持！会静默忽略第二个 <<:）────────────────
proxy-groups:
  - { name: "香港|自动", <<: *auto, <<: *hk }   # ❌ 第二个 <<: *hk 被忽略
  - { name: "香港|回退", <<: *fall, <<: *hk }   # ❌ icon 和 filter 都丢失
  - { name: "香港|均衡", <<: *bal,  <<: *hk }   # ❌ 同上

# ── 当前实际可用的绕过写法（手动把 filter 和 icon 写进去）────────────────
proxy-groups:
  - { name: "香港|自动", <<: *auto, filter: "^(?=.*(🇭🇰|港|HK|Hong))(?!.*(回国|剩余|到期|客服)).*$", icon: "https://example.com/hk.svg" }
  - { name: "香港|回退", <<: *fall, filter: "^(?=.*(🇭🇰|港|HK|Hong))(?!.*(回国|剩余|到期|客服)).*$", icon: "https://example.com/hk.svg" }
  # 或者用字符串锚点替代 filter，但 icon 还是得重复写：
  - { name: "香港|自动", <<: *auto, filter: *hk_filter, icon: "https://example.com/hk.svg" }
```

> **⚠️ 关键限制（来自 [mihomo issue #2274](https://github.com/MetaCubeX/mihomo/issues/2274)，于 2025 年 9 月提出，closed as not planned）：**
>
> 在**单行 JSON 花括号**格式中，mihomo 目前只支持**一个** `<<:` 合并操作。如果你写了两个 `<<:`（如 `{ <<: *auto, <<: *hk }`），第二个会被 YAML 解析器静默忽略（YAML 规范中同名键后者覆盖前者，而 `<<:` 本身就是一个键）。
>
> **标准多行 YAML 格式中也有同样限制**——多个 `<<:` 在 YAML 1.1 规范里理论上是允许的，但 mihomo 使用的 Go YAML 库只处理第一个。
>
> 结论：**三层锚点思路是最优雅的，但第三层（地区的 filter+icon）目前无法通过第二个 `<<:` 合并进来，只能手写或用字符串锚点替代 filter。** 等这个特性被支持后，流派五将是最推荐的写法。

| 优点 | 缺点 |
|------|------|
| 逻辑分层最清晰，修改基础参数只需改 `area`，改某类型参数只需改 `auto`/`fall` 等 | 多 `<<:` 合并目前不被支持，第三层地区锚点只是"理想" |
| 增加新地区理论上只需加一行 | 现实中仍需手动重复 filter/icon，部分抵消了优雅性 |
| icon 参数与 filter 打包，视觉管理更方便 | 三层嵌套对新手完全不友好，调试链路更长 |
| 代表了社区对锚点用法的最新探索方向 | 当前最佳实践仍是流派二或流派四，而非流派五 |

---

**流派六（a）：官方 geox 快捷配置风格（`pr` 极简锚点，来自官方 Wiki 示例）**

这是 [MetaCubeX 官方 Wiki 快捷配置示例](https://wiki.metacubex.one/example/conf/)的写法，也是早期社区教程广泛流传的格式。

```yaml
# 来源：官方 Wiki geox 快捷配置 / Discussion #1024
# 特点：只锚定"功能组候选列表"，地区组直接 include-all-providers

pr: &pr
  type: select
  proxies:
    - 默认
    - 香港
    - 台湾
    - 日本
    - 新加坡
    - 美国
    - 全部节点
    - 自动选择
    - DIRECT

p: &p
  type: http
  interval: 3600
  health-check:
    enable: true
    url: https://www.gstatic.com/generate_204
    interval: 300

proxy-providers:
  provider1: { <<: *p, url: "..." }
  provider2: { <<: *p, url: "..." }

proxy-groups:
  # 顶层和功能组全部用 pr 锚点（极简两行）
  - { name: 默认,      type: select, proxies: [自动选择, DIRECT, 香港, 台湾, 日本, 新加坡, 美国, 全部节点] }
  - { name: Google,    <<: *pr }
  - { name: Telegram,  <<: *pr }
  - { name: YouTube,   <<: *pr }
  - { name: NETFLIX,   <<: *pr }
  # 地区组：include-all-providers 直接取所有 provider，按 filter 筛选
  - { name: 香港, type: select, include-all-providers: true, filter: "(?i)港|hk|hongkong|hong kong" }
  - { name: 台湾, type: select, include-all-providers: true, filter: "(?i)台|tw|taiwan" }
  - { name: 全部节点,   type: select, include-all-providers: true }
  - { name: 自动选择,   type: url-test, include-all-providers: true, tolerance: 10 }
```

| 优点 | 缺点 |
|------|------|
| 配置文件极短，即抄即用，适合新手快速上手 | 所有功能组候选列表完全相同，无法给 AI 配美国优先、给流媒体配香港优先 |
| 官方维护，写法稳定，不依赖任何第三方规则集 | 地区组用 select 而不是 url-test，没有自动测速 |
| 功能组用 `<<: *pr` 一行搞定，对应到 `pr` 锚点就知道有哪些选项 | 一旦需要差异化，这种模式就要大改，扩展性差 |
| 作为模板起点很好，在此基础上逐步添加功能 | 不区分"自动测速"和"手动选择"层次，结构比较扁平 |

---

**流派六（b）：echs-top 风格（`use` 锚点嵌套 + `zl`/`dl` 双模板，来自真实个人配置）**

这是 [echs-top/proxy](https://github.com/echs-top/proxy) 的真实个人配置（持续更新至 2026 年），也是 Issue #2274 的提交者本人使用的写法。它有几个和其他流派完全不同的设计思路：

```yaml
# 来源：echs-top/proxy（2026-02-21 更新）
# 核心特色：
#  1. providers 锚点（包含 exclude-filter，一次性净化垃圾节点）
#  2. use 锚点（锚定"使用哪些 provider"）
#  3. fall 锚点嵌套引用 use 锚点（锚点套锚点）
#  4. zl/dl 双模板（直连优先 vs 代理优先）

providers: &providers
  type: http
  interval: 86400
  proxy: 直接连接
  health-check: { enable: true, url: 'https://dns.google/generate_204', expected-status: 204, interval: 600, timeout: 3000, max-failed-times: 2, lazy: false }
  exclude-filter: '(?i)套餐|剩余|流量|到期|重置|频道|订阅|官网|禁止|客户端|有效|联系|测试|节点|...'

proxy-providers:
  link1: { <<: *providers, url: '订阅链接1', path: ./providers/link1.yaml }
  link2: { <<: *providers, url: '订阅链接2', path: ./providers/link2.yaml }
  link3: { <<: *providers, url: '订阅链接3', path: ./providers/link3.yaml }

# ── 关键设计：use 锚点定义"哪些 provider 进自动组"
use: &use { use: [link1, link2] }    # link3 是手动组专用，不进自动测速

# ── fall 锚点嵌套引用 use 锚点（<<: *use 会展开 use 字段）
fall: &fall { type: fallback, <<: *use, hidden: true }

# ── zl（直连优先选择）和 dl（代理优先选择）两套功能组模板
zl: &zl { type: select, proxies: [直接连接, 代理连接, 最低延迟, 香港|故障转移, ...], include-all-providers: true }
dl: &dl { type: select, proxies: [代理连接, 直接连接, 最低延迟, 香港|故障转移, ...], include-all-providers: true }

proxy-groups:
  - { name: 代理连接, type: select, proxies: [最低延迟, 香港|故障转移, ...], include-all-providers: true, icon: '...' }
  - { name: 直接连接, type: select, proxies: [DIRECT, ipv4-prefer, ipv6-prefer], icon: '...' }
  # zl 用于"直连时也允许代理"的服务（如 FCM 推送）
  - { name: FCM推送,  <<: *zl, icon: '...' }
  # dl 用于"走代理为主"的服务
  - { name: TELEGRAM, <<: *dl, icon: '...' }
  - { name: 国外AI,   <<: *dl, icon: '...' }
  # 最低延迟：url-test
  - { name: 最低延迟, type: url-test, tolerance: 30, <<: *use, hidden: true, icon: '...' }
  # 地区组：只用 fallback，没有 url-test + load-balance 三合一
  - { name: 香港|故障转移, <<: *fall, filter: '(?i)🇭🇰|香港|\bHK\b', icon: '...' }
  - { name: 日本|故障转移, <<: *fall, filter: '(?i)🇯🇵|日本|\bJP\b', icon: '...' }
  # ...
```

**几个真正独特的设计决策：**

1. **`use` 锚点嵌套**：把"哪些 provider 进组"也抽象成锚点。`fall: &fall { type: fallback, <<: *use }` 展开后 `use` 字段直接从锚点继承，这样修改参与自动组的 provider 只需改一行 `use` 锚点。

2. **`zl` / `dl` 双模板**：zl（直连优先）和 dl（代理优先）本质上是同一套候选列表，区别在于 `proxies` 列表里"直接连接"和"代理连接"的先后顺序不同。功能组选哪套模板，就决定了面板里的默认选项是什么——而不是所有功能组都用同一套。

3. **只用 fallback，不用 url-test + load-balance**：echs-top 的选择是"只要能用就用，挂了再切"（fallback），而不是"持续测速选最快的"（url-test）。这降低了节点的健康检查频率和流量消耗。

4. **`exclude-filter` 在 provider 层而不是 filter**：用"黑名单"排除垃圾节点，而不是"白名单"只保留想要的，这样一个订阅里不同地区的节点都能被各自地区组正确筛选。

| 特点 | 说明 |
|------|------|
| `use` 锚点嵌套 | 地区组的 provider 来源集中管理，不用重复写 `use: [link1, link2]` |
| `zl`/`dl` 双模板 | 功能组有"直连优先"和"代理优先"两套候选顺序，而不是统一的一套 |
| 只用 fallback | 减少健康检查流量，适合节点稳定的场景；代价是没有实时测速排序 |
| `exclude-filter` 净化 | provider 层用黑名单排垃圾，比用 filter 白名单更能保留有效节点 |
| 与 iyyh 的本质差异 | iyyh 用三合一（自动/回退/均衡），每个地区三个组；echs-top 只用一个 fallback 组 |
| 不设 url-test 地区组 | 不追求最低延迟，追求稳定连接，适合不需要精细调节速度的用户 |

---

**横向对比一：`filter` 的三种写法**

这是锚点写法中最容易忽视的细节差异，不同风格对 filter 的处理方式不同：

```yaml
# 写法 A：filter 完全内联（不用锚点）
# 优点：直观；缺点：同一地区的多个 group 要粘贴三遍相同正则，改一处要改三处
- { name: "香港|自动", <<: *g_t, filter: "^(?=.*(🇭🇰|港|HK|Hong))(?!.*(剩余|到期)).*$" }
- { name: "香港|回退", <<: *g_f, filter: "^(?=.*(🇭🇰|港|HK|Hong))(?!.*(剩余|到期)).*$" }
- { name: "香港|均衡", <<: *g_b, filter: "^(?=.*(🇭🇰|港|HK|Hong))(?!.*(剩余|到期)).*$" }

# 写法 B：filter 锚定为字符串（iyyh 风格，目前最佳）
# 优点：正则统一管理，改一处全部生效；缺点：需要额外一行定义
FilterHK: &FilterHK "^(?=.*(🇭🇰|港|HK|Hong))(?!.*(剩余|到期)).*$"

- { name: "香港|自动", <<: *g_t, filter: *FilterHK }
- { name: "香港|回退", <<: *g_f, filter: *FilterHK }
- { name: "香港|均衡", <<: *g_b, filter: *FilterHK }

# 写法 C：filter + icon 锚定为对象（HenryChiao AIO 理想写法）
# 优点：连 icon 也一起管理，最终极；缺点：受限于多 <<: 不支持，需要绕过
hk: &hk
  filter: "^(?=.*(🇭🇰|港|HK|Hong))(?!.*(剩余|到期)).*$"
  icon: "https://example.com/flags/hk.svg"

# 当前绕过写法：只能用 *hk 引用 filter，icon 要从锚点中取出或单独写
# 待 issue #2274 支持后可直接 <<: *hk 合并
```

| | 写法 A（完全内联） | 写法 B（字符串锚点） | 写法 C（对象锚点） |
|--|--|--|--|
| 正则维护 | ❌ 每处单独维护 | ✅ 集中管理 | ✅ 集中管理 |
| icon 维护 | 手动或省略 | 手动 | ✅ 打包（待支持） |
| 可读性 | ✅ 最直观 | ✅ 清晰 | ⚠️ 需理解锚点 |
| 当前可用性 | ✅ 完全可用 | ✅ 完全可用 | ⚠️ filter 可用，icon 合并受限 |
| 推荐程度 | 小型配置 | **推荐** | 待特性支持后推荐 |

---

**横向对比二：`include-all` vs 显式 `use: [provider]`**

这两种写法决定了代理组"从哪里取节点"，混淆使用会导致节点消失或重复：

```yaml
# 写法 A：显式列出 use（老写法，精确控制）
proxy-groups:
  - name: "🚀 节点选择"
    type: select
    use:
      - 机场A          # 只包含 机场A 的节点
      - 机场B          # 再加上 机场B 的节点
    proxies:
      - DIRECT

# 写法 B：include-all（新写法，自动包含一切）
proxy-groups:
  - name: "🚀 节点选择"
    type: select
    include-all: true  # 自动包含所有 proxies + 所有 proxy-providers
    proxies:
      - DIRECT          # proxies 里手写的条目仍然有效，排在 include-all 节点之前

# 写法 C：include-all-proxies / include-all-providers（拆分控制）
proxy-groups:
  - name: "🚀 节点选择"
    type: select
    include-all-proxies: true    # 只包含 proxies 段手写的节点
    include-all-providers: false # 不包含 proxy-providers 的节点
    proxies: [DIRECT]
```

| | 写法 A（显式 use） | 写法 B（include-all） | 写法 C（拆分） |
|--|--|--|--|
| 新增 provider 后 | ❌ 要手动去每个 group 加 `use` | ✅ 自动包含，零维护 | 按需控制 |
| 精确指定来源 | ✅ 精确到 provider 级别 | ❌ 全包含，无法排除某个 provider | ✅ 可分别控制 |
| 搭配 filter 使用 | ✅ 在 group 层 filter | ✅ 在 group 层 filter | ✅ |
| 推荐场景 | 多机场各司其职、不想混合 | **日常主力，最省事** | 精细控制场景 |

> **注意：** `include-all` 时 `use:` 字段会失效，`include-all-providers` 设为 true 后同样使 `use:` 失效。不要同时写两者。

---

**流派六：liuran001「懒人配置」风格（`pr` + `use` 双锚点，完全不同的思路）**

这是 [liuran001 的社区高星配置（584 stars）](https://gist.github.com/liuran001/5ca84f7def53c70b554d3f765ff86a33) 代表的另一套完全不同的锚点哲学：**不锚定组类型参数，而是锚定"功能组的 proxies 候选列表"和"订阅组的完整定义"**。

```yaml
# 来源：liuran001 懒人配置（社区高星）
# 核心思路：
#   pr  锚定所有功能组共用的 proxies 候选列表
#   use 锚定订阅组的完整写法（类型+订阅来源）
#   p   锚定 proxy-provider 参数（与其他风格相同）

# 1. pr：所有功能组共享的代理候选列表
pr: &pr
  type: select
  proxies:
    - 节点选择
    - 香港
    - 台湾
    - 日本
    - 新加坡
    - 美国
    - 其它地区
    - 全部节点
    - 自动选择
    - DIRECT

# 2. use：订阅聚合组的完整写法
use: &use
  type: url-test        # 改为 type: select 则变成手动选择
  use:
    - 订阅一
    - 订阅二

# 3. p：provider 参数
p: &p
  type: http
  interval: 3600
  health-check:
    enable: true
    url: https://cp.cloudflare.com
    interval: 300
    timeout: 1000
    tolerance: 100

proxy-providers:
  订阅一:
    <<: *p
    url: "https://airport-a.com/..."
  订阅二:
    <<: *p
    url: "https://airport-b.com/..."

proxy-groups:
  # 顶层入口
  - name: 节点选择
    <<: *use          # 直接用 use 锚点，订阅类型和来源一行搞定

  # 地区自动组（不用锚点，直接写）
  - name: 香港
    type: url-test
    use: [订阅一, 订阅二]
    filter: "(?i)🇭🇰|香港|HK"
    url: https://cp.cloudflare.com
    interval: 300

  # 功能组全部继承 pr 候选列表
  - name: "🤖 AI 服务"
    <<: *pr           # 一行继承完整候选列表

  - name: "📹 流媒体"
    <<: *pr           # 同上，功能组配置极简
```

| 特点 | 说明 |
|------|------|
| `pr` 锚点 | 把所有功能组的候选 proxies 列表统一管理，加减地区只改一处 |
| `use` 锚点 | 订阅聚合组的写法也锚定，多个聚合组（全部节点、自动选择等）复用 |
| 与 iyyh 风格的本质区别 | iyyh 锚定"组类型参数"；liuran001 锚定"组的 proxies 候选列表" |
| 优点 | 功能组极其简洁（两行），新手容易看懂 proxies 来源 |
| 缺点 | 所有功能组候选列表完全相同，无法给 AI 服务单独配美国优先、流媒体配香港优先；`pr` 锚点一旦修改影响所有功能组 |
| DNS 模式 | 该配置使用 `redir-host`（不是 `fake-ip`），这是另一个值得对比的设计选择（见下文） |

---

**横向对比三：`fake-ip` vs `redir-host`——两种主流 DNS 模式的真实差异**

这是配置文件中争议最多的选项之一，两种模式在不同场景下各有优劣：

```yaml
# 模式 A：fake-ip（iyyh / 本教程主推）
dns:
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  # ✅ 特点：收到 DNS 查询后立即返回假 IP，流量发到假 IP 后才真正建立连接
  # 域名规则在 DNS 解析完成前就能匹配，速度快，fake-ip 不在本地真正解析代理域名

# 模式 B：redir-host（liuran001 / 路由器常用）
dns:
  enhanced-mode: redir-host
  # ✅ 特点：正常完成 DNS 解析，用真实 IP 匹配规则；DNS 解析结果透传给应用
  # 路由器兼容性最好；某些不兼容 fake-ip 的 APP（游戏/国内支付）更稳定
```

| 对比项 | fake-ip | redir-host |
|--------|---------|------------|
| 连接速度 | ⭐⭐⭐ 更快（无需等待真实 DNS） | ⭐⭐ 稍慢（需完成真实 DNS 解析） |
| 规则匹配 | 域名规则优先，无需 DNS 就能匹配 | 先 DNS 再匹配，可能触发 DNS 解析 |
| 游戏/特殊 APP 兼容 | ⚠️ 部分游戏/支付不兼容，需加白名单 | ✅ 原生兼容，无需白名单 |
| 路由器场景 | ⚠️ 需额外配置 fake-ip-filter | ✅ 首选，兼容性最好 |
| DNS 泄露控制 | ✅ 代理流量不在本地解析，最干净 | ⚠️ 代理域名仍在本地 DNS 解析一次 |
| 推荐场景 | 个人电脑/手机日常使用 | 软路由/OpenWrt/旁路由/路由器 |

> **结论：** 个人设备日常使用推荐 `fake-ip`，路由器/软路由部署推荐 `redir-host`。两种模式的规则写法相同，只需改 `enhanced-mode` 一行，其他规则无需调整。

---

**总结：八种锚点风格横向速查表**

| | 锚定对象 | 代表配置 | 配置长度 | 可读性 | 灵活性 | 推荐 |
|--|--|--|--|--|--|--|
| 流派一 | 只锚 provider 参数 | 官方示例 / 入门教程 | 长 | ⭐⭐⭐ | ⭐⭐ | 新手入门 |
| 流派二 | provider + group 类型参数 | iyyh / 进阶主流 | 中 | ⭐⭐ | ⭐⭐⭐ | ✅ 日常主力 |
| 流派三 | proxies 候选列表 | 早期教程 | 中 | ⭐⭐⭐ | ⭐ | 不推荐 |
| 流派四 | provider + group（单行极简） | HenryChiao / YYDS | 最短 | ⭐ | ⭐⭐⭐ | ✅ 大型配置 |
| 流派五 | 三层嵌套（含地区 filter+icon） | 社区理想（issue #2274） | 最短（理论） | ⭐ | ⭐⭐⭐⭐ | 等特性支持 |
| 流派六 | proxies 候选列表 + 订阅聚合组 | liuran001 懒人配置 | 中 | ⭐⭐⭐ | ⭐⭐ | 懒人/入门 |
| **流派七（a）** | provider + `pr` 功能组模板（官方极简） | 官方 geox 快捷配置 | 极短 | ⭐⭐⭐ | ⭐ | 临时过渡 |
| **流派七（b）** | `use` 订阅组 + `zl`/`dl` 双功能模板 + 嵌套锚点 | echs-top | 短 | ⭐⭐ | ⭐⭐⭐ | 进阶自用 |

**如何选择：**

- 刚入门、想跑通：流派七(a) 或流派六
- 个人日常使用、想精准控制：流派二（iyyh 风格）
- 配置地区多（8+）、追求文件最短：流派四（极简单行）
- 不在乎延迟最低、只要稳定连接、节点多且稳：流派七(b)（echs-top）
- 想等未来功能：流派五（多 `<<:` 支持后升级）

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

## 二·五、📊 proxy-groups 锚点策略深度对比

教程前面介绍了 iyyh 的"锚定组类型参数"风格。这里对比另一种完全不同的设计：**锚定 proxies 候选列表**，以及 TheFullSmart 中两者结合的综合风格。

---

**策略一：锚定"组类型"（iyyh 风格）**

```yaml
# 锚点存储的是：组的运行参数（type/url/interval/include-all 等）
g_urltest: &g_urltest
  type: url-test
  url: "https://www.gstatic.com/generate_204"
  interval: 300
  include-all: true
  hidden: true

# 使用时通过 filter 决定节点范围，proxies 手动指定跳转目标
- { name: "🇭🇰 香港-自动", <<: *g_urltest, filter: *FilterHK }
- { name: "🇸🇬 新加坡-自动", <<: *g_urltest, filter: *FilterSG }
```

---

**策略二：锚定"proxies 候选列表"（TheFullSmart 风格，来源：HenryChiao/MIHOMO_AIO）**

```yaml
# 锚点存储的是：功能组的完整候选跳转列表（不同优先级有不同列表）
SelectFB: &SelectFB {type: select, proxies: [故障转移, 香港策略, 狮城策略, 日本策略, 韩国策略, 美国策略, 台湾策略, 欧盟策略, 冷门自选, 全球手动, 直接连接]}
SelectPY: &SelectPY {type: select, proxies: [默认代理, 故障转移, 香港策略, 狮城策略, 日本策略, 韩国策略, 美国策略, 台湾策略, 欧盟策略, 冷门自选, 全球手动, 直接连接]}
SelectDC: &SelectDC {type: select, proxies: [直接连接, 默认代理, 故障转移, 香港策略, ...]}  # 直连优先
SelectHK: &SelectHK {type: select, proxies: [香港策略, 默认代理, 故障转移, 狮城策略, ...]}  # 香港优先
SelectUS: &SelectUS {type: select, proxies: [美国策略, 默认代理, 故障转移, 香港策略, ...]}  # 美国优先

# 使用时一行继承，功能组配置极度简洁
- {name: 油管视频, <<: *SelectPY, icon: "..."}   # 默认代理优先
- {name: 人工智能, <<: *SelectUS, icon: "..."}   # 美国优先
- {name: 国内流量, <<: *SelectDC, icon: "..."}   # 直连优先
- {name: 新闻媒体, <<: *SelectUS, icon: "..."}   # 美国优先
```

不同功能服务有不同的首选地区，通过 **多套 SelectXX 锚点**，功能组只需一行 `<<: *SelectUS` 就能表达"这个服务优先走美国"，无需重复写 proxies 列表。

| 对比项 | iyyh（锚定组类型）| TheFullSmart（锚定 proxies 列表）|
|--------|------------------|----------------------------------|
| 锚点存储内容 | 运行参数（type/interval/url）| 跳转目标列表（proxies 优先顺序）|
| 功能组个性化 | 每个功能组手写 proxies 列表 | 用不同 SelectXX 锚点表达优先级 |
| 地区组个性化 | 统一 include-all + filter | 需 include-all + filter 且在功能层通过 Select 锚点间接选地区 |
| 维护更新 | 加地区只改地区层 | 加地区要同步更新每个 SelectXX 锚点 |
| 适用场景 | 服务需求简单、地区较少 | 有明确地区偏好（AI→美、流媒体→港）的精细分流 |

---

**策略三：两层地区组架构——`策略` 入口 + `智能` 底层**

这是 TheFullSmart 与 iyyh 最显著的架构差异：

```yaml
# iyyh 风格：地区三合一，用户进入"香港"后手选"自动/回退/均衡"
- {name: "🇭🇰 香港", type: select, proxies: ["🇭🇰 香港-自动", "🇭🇰 香港-回退", "🇭🇰 香港-均衡"]}
- {name: "🇭🇰 香港-自动", <<: *g_urltest, filter: *FilterHK}
- {name: "🇭🇰 香港-回退", <<: *g_fallback, filter: *FilterHK}
- {name: "🇭🇰 香港-均衡", <<: *g_balance, filter: *FilterHK}

# TheFullSmart 风格：地区两层，入口层允许手选个别节点，底层用 smart 自动
- {name: 香港策略, type: select, proxies: [香港智能], include-all: true, filter: *FilterHK}
  # ↑ 入口层：平时走"香港智能"自动，也可手选某个具体节点（应急用）

- {name: 香港智能, <<: *BaseSmart, include-all: true, filter: *FilterHK,
   policy-priority: '优:2;中:1;备:0.2'}
  # ↑ 底层：type: smart 自动决策，hidden 对面板隐藏
```

---

**`type: smart` 组——TheFullSmart 的核心特性（教程其他地方均未提及）**

`type: smart` 是 mihomo 特有的代理组类型，使用机器学习（LightGBM）模型根据节点历史表现自动选择最优节点，而不是简单按延迟排序：

```yaml
BaseSmart: &BaseSmart
  type: smart
  interval: 200
  lazy: true
  url: 'https://www.google.com/generate_204'
  hidden: true
  uselightgbm: true    # 启用 LightGBM 模型（需要 mihomo 支持该特性）

# 关键特有参数：policy-priority
# 格式：'节点名关键词:权重' 用分号分隔
# 权重越大，该关键词匹配的节点优先级越高
- {name: 香港智能, <<: *BaseSmart, filter: *FilterHK, include-all: true,
   policy-priority: '优:2;中:1;备:0.2'}
# 效果：节点名含"优"的权重是"备"的 10 倍，smart 模型会更倾向选"优"质节点
# 适合有多机场且按名称前缀标注质量的用户（配合 override.additional-prefix 使用）
```

`policy-priority` 与 `override.additional-prefix` 配合使用效果最好：

```yaml
proxy-providers:
  优质机场: {<<: *BaseProvider, url: "...", override: {additional-prefix: '[优] '}}
  备用机场: {<<: *BaseProvider, url: "...", override: {additional-prefix: '[备] '}}

# 这样节点名变成 "[优] 香港01" / "[备] 香港01"
# policy-priority: '优:2;备:0.2' 即可按质量加权
```

| 对比项 | `url-test` | `fallback` | `load-balance` | `smart` |
|--------|------------|------------|----------------|---------|
| 选节点逻辑 | 最低延迟 | 按顺序回退 | 多节点分流 | ML 综合历史表现 |
| 适应抖动 | 差（频繁切换）| 差（固定顺序）| 中 | ✅ 好（有记忆）|
| 流量分布 | 全走最快 | 全走首个可用 | 均摊 | 按质量权重分配 |
| `policy-priority` | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ 支持 |
| 需要 mihomo 版本 | 通用 | 通用 | 通用 | 需支持 smart 特性 |
| 适合场景 | 延迟优先 | 稳定性优先 | 大流量分流 | 多机场质量分层 |

> **注意：** `type: smart` 和 `uselightgbm: true` 是 mihomo 的扩展特性，需要较新版本。如果版本不支持，配置会报错或降级。使用前确认内核版本。

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

## 三·一、📊 Filter 正则写法流派对比

不同配置在正则细节上差异很大，覆盖精度、可维护性、误杀率各有侧重。

---

**风格 A：iyyh 风格——中文关键词 + Emoji 为主**

```yaml
FilterHK: &FilterHK '^(?=.*(🇭🇰|港|HK|Hong Kong))(?!.*(回国|校园|游戏|剩余|到期|官网|客服|订阅|节点|过期|时间)).*$'
FilterJP: &FilterJP '^(?=.*(🇯🇵|日|JP|Japan|Tokyo|Osaka))(?!.*(回国|校园|游戏|剩余|到期|官网|客服|订阅|节点|过期|时间)).*$'
FilterUS: &FilterUS '^(?=.*(🇺🇸|美|US|United States|Los Angeles|Silicon|Seattle))(?!.*(回国|校园|游戏|剩余|到期|官网|客服|订阅|节点|过期|时间)).*$'
```

优点：排除词详尽，误杀率低，可读性好，便于人工检查。缺点：只匹配少量城市名，机场用 IATA 代码命名的节点容易漏掉；不加 `(?i)` 大小写敏感，`HK`/`hk` 都要手写。

---

**风格 B：TheFullSmart 风格——`(?i)` 内联 + IATA 机场代码（来源：HenryChiao/MIHOMO_AIO）**

```yaml
FilterHK: &FilterHK '^(?=.*(?i)(港|🇭🇰|HK|Hong|HKG))(?!.*(排除1|排除2|5x)).*$'
FilterJP: &FilterJP '^(?=.*(?i)(日|🇯🇵|JP|Japan|NRT|HND|KIX|CTS|FUK))(?!.*(尼日利亚|排除1|5x)).*$'
FilterUS: &FilterUS '^(?=.*(?i)(美|🇺🇸|US|USA|JFK|SJC|LAX|ORD|ATL|DFW|SFO|MIA|SEA|IAD))(?!.*(Plus|Australia|5x)).*$'

# "其他地区"专用 FilterOT：纯排除式，不写白名单，只排除已知地区
FilterOT: &FilterOT '^(?!.*(DIRECT|直接|美|港|台|日|韩|欧|🇭🇰|🇺🇸|🇯🇵|HK|TW|SG|JP|KR|US|NRT|LAX|HKG|TPE|SIN))'

# "全部有效节点" FilterAL：只排除垃圾/信息节点，不区分地区
FilterAL: &FilterAL '^(?!.*(DIRECT|直接|群|邀请|返利|循环|官网|客服|订阅|流量|到期|机场|过期|邮箱|工单|USE|TOTAL|EXPIRE|Panel|Author))'
```

`FilterOT` 是一个值得关注的设计：它用纯负向模式，把所有不在已知地区里的节点都兜住，用来构建"冷门地区"组，不需要逐一列举小众国家。

| 特性 | iyyh 风格 | TheFullSmart 风格 |
|------|-----------|-------------------|
| 大小写处理 | 手写大小写变体 | `(?i)` 内联，自动不区分大小写 |
| 机场代码覆盖 | 少量城市名 | IATA 三字码（NRT/LAX/HKG 等），覆盖率更高 |
| 排除词策略 | 详尽中文垃圾词列表 | 占位符 + 倍率词（`5x`），需针对自己机场修改 |
| "其他地区"处理 | 归入漏网之鱼 | 专用 `FilterOT` 负向捕捉 |
| "全部节点"处理 | 无专用 filter | `FilterAL` 只排垃圾词，覆盖所有有效节点 |
| 欧盟覆盖 | 不单独建组 | 穷举式 `FilterEU`，中文+Emoji+IATA 全覆盖 |

> **实际使用提示：** TheFullSmart 风格中的排除词 `排除1`/`排除2`/`5x` 都是占位符，使用前需替换成自己机场里实际需要排除的关键词（如倍率节点名称、特定套餐前缀等）。

---

## 三·五、📊 节点引入方式对比：`use` / `include-all` / 双层 `filter`

这是新手最容易混淆的地方。往 proxy-group 里引入节点，有以下几种方式，它们在行为、灵活性和维护性上差异显著。

---

**方式一：`use` 显式指定 provider**

```yaml
proxy-providers:
  机场A:
    type: http
    url: "..."
    filter: "(?i)港|HK"   # ← provider 层过滤：订阅拉下来后只保留香港节点

proxy-groups:
  - name: "🇭🇰 香港-自动"
    type: url-test
    use: [机场A]           # 只引入机场A，不引入机场B
    url: "https://www.gstatic.com/generate_204"
    interval: 300
```

| 特点 | 说明 |
|------|------|
| 精确控制 | 明确知道哪个 group 用哪个 provider，不会意外引入多余节点 |
| 适合多机场有差异时 | 机场A专门放地区A，机场B专门放地区B，互不干扰 |
| 缺点 | 每个 group 都要手写 `use: [机场名]`，provider 多时很繁琐 |

---

**方式二：`include-all: true`（推荐主流用法）**

```yaml
proxy-groups:
  - name: "🇭🇰 香港-自动"
    type: url-test
    include-all: true      # 自动包含所有 proxies 段的节点 + 所有 proxy-providers 的节点
    filter: "(?i)港|HK"   # ← group 层过滤：从全部节点里筛出香港的
    url: "https://www.gstatic.com/generate_204"
    interval: 300
```

| 特点 | 说明 |
|------|------|
| 最省事 | 新加一个 provider 后，所有 group 自动包含，不需要改 group 配置 |
| filter 在 group 层 | provider 里保留所有节点，由 group 自己筛选，灵活性最高 |
| 缺点 | 如果某个 provider 里有重名节点，会出现冲突 |
| 注意 | `include-all` = `include-all-proxies` + `include-all-providers`，可分别单独使用 |

---

**方式三：provider 层 filter + group 层 filter 双重过滤**

```yaml
proxy-providers:
  机场A:
    type: http
    url: "..."
    # provider 层：先排除信息节点（剩余流量、到期提醒等）
    filter: "^(?!.*(剩余|到期|官网|客服|订阅|过期|流量)).*$"

proxy-groups:
  - name: "🇭🇰 香港-自动"
    type: url-test
    include-all: true
    # group 层：再从"已净化"的节点里筛出香港
    filter: "(?i)港|HK|Hong Kong"
    url: "https://www.gstatic.com/generate_204"
    interval: 300
```

| 特点 | 说明 |
|------|------|
| 最干净 | provider 层过滤掉垃圾节点（它们不会被任何 group 引用），group 层再按地区筛选 |
| 责任分离清晰 | provider 管"净化"，group 管"分类" |
| 推荐写法 | 这是目前社区中最常见的最佳实践 |
| 缺点 | 正则要写两套，初次上手稍繁琐 |

---

**方式四：`exclude-filter` + `exclude-type`（组合排除）**

```yaml
proxy-providers:
  机场A:
    type: http
    url: "..."
    exclude-filter: "剩余|到期|官网|免费|试用"   # 排除含这些词的节点
    exclude-type: "ss|http"                      # 排除 ss 和 http 协议的节点（类型精确匹配）

proxy-groups:
  - name: "🇭🇰 香港-自动"
    type: url-test
    include-all: true
    filter: "(?i)港|HK"
    exclude-filter: "IPLC|专线"    # group 层再排除 IPLC 专线（防止过载）
```

| 特点 | 说明 |
|------|------|
| `filter` vs `exclude-filter` | filter 是"白名单"（只留匹配的），exclude-filter 是"黑名单"（排除匹配的） |
| `exclude-type` | 按协议类型排除，不支持正则，用 `|` 分隔，如 `ss|vmess|http` |
| 两者可以同时使用 | filter + exclude-filter 组合，先用 filter 圈范围，再用 exclude-filter 精细剔除 |
| 注意 | `exclude-type` 在 provider 和 group 中均可使用，但含义略有不同（详见官方文档） |

---

**方式五：`override` 批量覆盖节点属性**

```yaml
proxy-providers:
  机场A:
    type: http
    url: "..."
    override:
      additional-prefix: "[优] "    # 给所有节点名加前缀，多机场时便于区分来源
      additional-suffix: " | A"     # 同时也可加后缀
      udp: true                     # 强制开启所有节点的 UDP（即使节点本身没配）
      skip-cert-verify: false       # 强制关闭不安全的证书跳过
      # proxy-name 可以用正则批量改名
      proxy-name:
        - pattern: "IPLC-(.*?)倍"   # 匹配类似 "IPLC-3倍" 的节点名
          target: "iplc x $1"       # 改为 "iplc x 3"
```

**`additional-prefix` 的典型使用场景（多机场区分来源）：**

```yaml
proxy-providers:
  优质机场:
    type: http
    url: "..."
    override:
      additional-prefix: "[优] "   # 节点显示为 "[优] 香港01"

  备用机场:
    type: http
    url: "..."
    override:
      additional-prefix: "[备] "   # 节点显示为 "[备] 香港01"

# 这样在 group 面板里同名节点也能区分来源
```

| 特点 | 说明 |
|------|------|
| 解决多机场同名节点冲突 | 加 prefix/suffix 后节点名唯一，不会出现引用歧义 |
| 批量统一节点参数 | 不需要逐个节点设置 `udp: true`，在 provider 层一次搞定 |
| proxy-name 正则改名 | 可以把机场节点的乱命名标准化，便于 filter 正则匹配 |
| 缺点 | 加了 prefix 之后，filter 正则也要考虑 prefix 部分（如 `[优] 香港01` 里的 `[优] `）|

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

## 四·五、📊 代理组架构设计流派对比

完成了代理组的细节写法后，值得停下来对比一下几种主流的**整体架构**思路，因为架构决定了你的配置有多好用、多好维护。

---

**架构一：平铺式（新手最常见，维护困难）**

```yaml
proxy-groups:
  - name: "节点选择"
    type: select
    use: [机场A]

  - name: "香港"
    type: url-test
    use: [机场A]
    filter: "HK"

  - name: "AI 服务"
    type: select
    proxies: ["香港", "节点选择"]  # 直接把香港 group 放进来
```

特点：所有 group 在同一层级，没有层级嵌套。简单直观，但 group 多了以后顶层入口变得混乱，面板里什么都显示。

---

**架构二：漏斗型（iyyh / 主流进阶，推荐）**

```
顶层（主入口）
  ├── 功能组（AI、流媒体、电报...）→ 指向地区组
  ├── 智能选择 → 指向各地区自动组
  └── 手动选择 → include-all，用户自己点

地区层（中间层，不直接暴露给用户）
  ├── 🇭🇰 香港 → [香港-自动, 香港-回退, 香港-均衡]（让用户选策略）
  └── 🇺🇸 美国 → [美国-自动, 美国-回退, 美国-均衡]

底层（自动组，hidden: true，面板不显示）
  ├── 香港-自动（url-test）
  ├── 香港-回退（fallback）
  └── 香港-均衡（load-balance）

兜底
  └── 漏网之鱼
```

特点：功能组不直接持有节点，而是通过地区组间接调度。面板里的信息层次清晰，不被大量底层 group 淹没。

---

**架构三：扁平 + hidden 过滤（HenryChiao YAMLS / YYDS 风格）**

和架构二本质相同，但利用 `hidden: true` 把所有自动/回退/均衡组隐藏，面板里只暴露顶层和地区层。加上 `icon` 字段让面板图标更好看：

```yaml
- { name: "🇭🇰 香港-自动", <<: *g_urltest, filter: *FHK }   # hidden: true（在锚点里）

# 地区组 hidden: false，用户能看到
- name: "🇭🇰 香港"
  type: select
  proxies: ["🇭🇰 香港-自动", "🇭🇰 香港-回退", "🇭🇰 香港-均衡"]
  icon: "https://raw.githubusercontent.com/Orz-3/mini/master/Color/HK.png"
```

`icon` 字段需要 Web 面板支持（metacubexd / zashboard 均支持），可以让面板里每个 group 显示国旗或服务商图标，视觉体验好很多。

| 架构 | 适合场景 | 面板体验 | 维护成本 |
|------|----------|----------|----------|
| 平铺式 | 只有 3-5 个 group 的超简配置 | 混乱 | 低 |
| 漏斗型 | 个人日常使用（推荐） | 清晰 | 中 |
| 扁平+hidden | 大型配置 / 配置仓库（5+ 地区） | 最佳 | 低（锚点加持） |

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

## 六·五、📊 规则集来源与格式对比

规则集的来源和格式选择，直接影响启动速度、内存占用和覆盖准确性。这也是各大配置仓库分歧最大的地方之一。

---

**来源一：SukkA 规则集（ruleset.skk.moe）**

```yaml
# 特点：文本格式（classical/domain），分类极细，区分非IP和IP类，质量最高
reject_non_ip:
  type: http
  behavior: classical
  url: "https://ruleset.skk.moe/Clash/non_ip/reject.txt"
  format: text
  interval: 43200
```

| 项目 | 说明 |
|------|------|
| 格式 | `.txt` 文本，`classical` / `domain` / `ipcidr` 三种 behavior |
| 更新频率 | 每 12 小时（43200 秒）较为合理 |
| 核心优势 | 严格区分非 IP 类和 IP 类，便于正确排序；规则逻辑清晰，有详细说明文档 |
| 注意 | 需要 mihomo 联网拉取，首次启动慢；格式是文本，加载比 `.mrs` 慢 |
| 适合 | 追求高质量、规则准确的用户；愿意花时间理解规则分类的人 |

---

**来源二：MetaCubeX 官方 meta-rules-dat（`.mrs` 格式）**

```yaml
# 特点：二进制格式，加载极快，GeoSite 数据库直接分发
cn-domain:
  type: http
  behavior: domain
  url: "https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geo/geosite/cn.mrs"
  format: mrs          # ← mihomo 专用二进制，速度是 yaml/text 的 10 倍以上
  interval: 86400
```

| 项目 | 说明 |
|------|------|
| 格式 | `.mrs`（二进制），加载速度最快，内存最低 |
| 更新频率 | 每 24 小时（86400 秒）即可 |
| 核心优势 | 基于 GeoSite 数据库，规模大；`.mrs` 格式对内存和 CPU 最友好 |
| 注意 | 不区分"非IP类"和"IP类"，需要自己按 behavior 类型排序放置；规则颗粒度不如 SukkA 细 |
| 适合 | 追求启动速度和低内存的用户；路由器/软路由等资源有限的设备 |

---

**来源三：iyyh + SukkA 混合（自用配置的选择）**

```yaml
# iyyh 的配置完全使用 SukkA 规则集，格式是 classical text
# 优点：分类最准确；缺点：首次加载慢，格式体积比 .mrs 大

# 另一种常见的混合用法：
# - 国内/国外分流用 .mrs（速度快）
# - 广告拦截/AI/流媒体用 SukkA（质量高）
```

---

**来源四：GEOSITE + GEOIP 直接用（最简，新手过渡方案）**

```yaml
# 不用 rule-providers，直接在 rules 里用 GEOSITE / GEOIP
rules:
  - GEOSITE,CN,DIRECT
  - GEOIP,CN,DIRECT
  - MATCH,🐟 漏网之鱼
```

| 项目 | 说明 |
|------|------|
| 优点 | 零配置，不需要 rule-providers 块，配置文件极短 |
| 缺点 | 规则颗粒度极粗，无法细分广告/AI/流媒体；依赖 GeoData 数据库 |
| 适合 | 小白第一阶段临时用，后续应升级为 rule-providers |

---

**格式速查表：**

| 格式 | behavior | 加载速度 | 体积 | 支持版本 |
|------|----------|----------|------|----------|
| `.mrs` | domain / ipcidr | ⭐⭐⭐ 最快 | 最小 | mihomo 专用 |
| `.txt` (text) | classical | ⭐⭐ | 中 | 通用 |
| `.yaml` | 三种都支持 | ⭐ 最慢 | 最大 | 通用（Clash 系） |

**结论：** 如果你的设备性能够用且不在意启动速度，用 SukkA 规则集质量最好；如果在路由器等资源受限设备上，优先 `.mrs` 格式的官方规则集，加载速度快内存低。**两者混用也没问题**，在 rule-providers 里分别定义各自的锚点即可。

---

**来源五：666OS/rules（TheFullSmart 使用的规则集，全 `.mrs`，含 IP 配套）**

```yaml
# 来源：HenryChiao/MIHOMO_AIO TheFullSmart_test_version.yaml
# 特点：每个分类都同时提供 domain 版本 + IP 版本，成对出现
BehaviorDN: &BehaviorDN {type: http, behavior: domain, format: mrs, interval: 86400}
BehaviorIP: &BehaviorIP {type: http, behavior: ipcidr, format: mrs, interval: 86400}

rule-providers:
  Telegram:   {<<: *BehaviorDN, url: https://github.com/666OS/rules/raw/release/mihomo/domain/Telegram.mrs}
  TelegramIP: {<<: *BehaviorIP, url: https://github.com/666OS/rules/raw/release/mihomo/ip/Telegram.mrs}
  AI:         {<<: *BehaviorDN, url: https://github.com/666OS/rules/raw/release/mihomo/domain/AI.mrs}
  AIIP:       {<<: *BehaviorIP, url: https://github.com/666OS/rules/raw/release/mihomo/ip/AI.mrs}
  # ... 每个服务都有对应的 domain 版 + ip 版
```

对应 rules 的写法也配套：

```yaml
rules:
  - RULE-SET,Telegram,电报消息          # 域名规则（不触发 DNS）
  - RULE-SET,TelegramIP,电报消息,no-resolve  # IP 规则（no-resolve 避免重复解析）
```

| 对比项 | SukkA 规则集 | 666OS/rules |
|--------|-------------|-------------|
| 格式 | `.txt` (classical/domain) | 全 `.mrs`（二进制）|
| IP/域名分离 | ✅ 严格分 non_ip 和 ip | ✅ 每类都有 domain + IP 两份 |
| 更新来源 | 作者手工维护 | 第三方汇总 |
| 启动速度 | 稍慢（文本解析）| 最快（二进制）|
| 适合 | 追求规则精度、愿意理解规则逻辑 | 追求速度和简洁、不关心规则来源细节 |

---

## 六·六、📊 `fake-ip-filter` 两种配置方式对比

传统写法和 TheFullSmart 的 `rule` 模式在维护性和精度上差异明显。

---

**方式一：传统域名列表（大多数教程的写法）**

```yaml
dns:
  fake-ip-filter:
    - "*.lan"
    - "*.local"
    - "localhost.ptlogin2.qq.com"
    - "+.push.apple.com"
    # 手动维护一个域名白名单列表
```

优点：简单直观，复制即用。缺点：列表手动维护，覆盖不全；无法引用 rule-providers，与规则集完全独立。

---

**方式二：`fake-ip-filter-mode: rule` — 基于规则集的精确控制（TheFullSmart 风格）**

```yaml
# 来源：HenryChiao/MIHOMO_AIO TheFullSmart_test_version.yaml
dns:
  fake-ip-filter-mode: rule    # 切换为规则模式，每条 filter 可单独指定 real-ip 或 fake-ip
  fake-ip-filter:
    # 直接引用 rule-providers，格式：RULE-SET,规则集名称,real-ip|fake-ip
    - RULE-SET,fakeip-filter,real-ip   # 这个规则集里的域名返回真实 IP（不造假）
    - RULE-SET,Private,real-ip         # 内网域名不造假
    - RULE-SET,Direct,real-ip          # 直连域名不造假
    - RULE-SET,China,real-ip           # 国内域名不造假

    - RULE-SET,AI,fake-ip              # AI 服务强制走 fake-ip（确保走代理路由）
    - RULE-SET,Telegram,fake-ip        # 电报强制 fake-ip
    - RULE-SET,Netflix,fake-ip         # 奈飞强制 fake-ip
    - DOMAIN-KEYWORD,speedtest,fake-ip # 关键词也可以用

    - MATCH,real-ip                    # 兜底：其余域名返回真实 IP
```

| 对比项 | 传统列表模式 | `rule` 模式 |
|--------|-------------|-------------|
| 配置来源 | 手写域名白名单 | 复用 rule-providers，与分流规则联动 |
| 维护成本 | 高（手动更新）| 低（规则集自动更新）|
| 精度 | 粗（只能指定 real-ip，无法强制 fake-ip）| 高（每条规则可单独指定 real-ip 或 fake-ip）|
| 强制 fake-ip | ❌ 不支持 | ✅ 支持，确保代理域名被路由层正确识别 |
| 复杂度 | 低 | 中（需要理解规则集与 DNS 的联动）|
| mihomo 版本要求 | 通用 | 需要较新版本支持 `fake-ip-filter-mode` |

> **实际意义：** `fake-ip-filter-mode: rule` 最大的价值在于可以**强制某些域名走 fake-ip**，确保它们被路由层以 fake-ip 形式识别进而走代理，而不是因为 fake-ip-filter 把它们放行了、让它们以真实 IP 绕过路由规则。

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

## 三·五、📊 `listeners` 分区端口 vs 统一端口

大多数教程只介绍 `mixed-port` 单一端口，但 TheFullSmart 使用 `listeners` 字段实现**每个地区固定一个端口**，这是一个进阶用法，适合软路由/服务器场景。

```yaml
# 来源：HenryChiao/MIHOMO_AIO TheFullSmart_test_version.yaml
listeners:
  # 入口型：Shadowsocks 协议，供远端设备接入
  - {name: SS-IN, type: shadowsocks, listen: '::', port: 10010,
     udp: true, password: yourpassword, cipher: aes-256-gcm}

  # 地区专用端口：每个端口绑定到对应的 proxy-group
  - {name: MIXED-FB, type: mixed, port: 49999, proxy: 故障转移}
  - {name: MIXED-HK, type: mixed, port: 50000, proxy: 香港策略}
  - {name: MIXED-SG, type: mixed, port: 50001, proxy: 狮城策略}
  - {name: MIXED-JP, type: mixed, port: 50002, proxy: 日本策略}
  - {name: MIXED-TW, type: mixed, port: 50003, proxy: 台湾策略}
  - {name: MIXED-US, type: mixed, port: 50004, proxy: 美国策略}
  - {name: MIXED-KR, type: mixed, port: 50005, proxy: 韩国策略}
  - {name: MIXED-DIRECT, type: mixed, port: 10086, proxy: 直接连接}
```

**使用场景：** 其他设备或应用将代理地址设为 `192.168.1.x:50000`，流量就自动走香港策略，不需要在应用内手动选组。适合：

- 软路由为局域网内不同设备分配不同出口（NAS走直连、游戏机走日本）
- 服务器上多个容器/服务需要不同地区出口
- 搭配 `liuran001` 配置里的 listeners 注释示例（`name: hk, port: 12991, proxy: 香港`）

| 方式 | 适合场景 | 复杂度 |
|------|----------|--------|
| 单 `mixed-port` | 个人电脑，手动在面板选组 | 低 |
| `listeners` 多端口 | 软路由/服务器，多设备/多服务分区出口 | 中 |

---

## 三·六、📊 `tunnels` 直通隧道

`tunnels` 是另一个教程中完全没有提及的特性。它的作用是：**把本地某个端口的 TCP/UDP 流量，通过指定的 proxy-group 直接转发到远端 IP:端口**，不依赖任何规则匹配。

```yaml
# 来源：HenryChiao/MIHOMO_AIO TheFullSmart_test_version.yaml
# 用途：把 Telegram 的 MTProto 服务器 IP 直接 tunnel 过去，绕过规则匹配延迟
tunnels:
  - {network: [tcp, udp], address: 0.0.0.0:9100, target: 91.108.56.147:443, proxy: "电报消息"}
  - {network: [tcp, udp], address: 0.0.0.0:9101, target: 91.108.56.117:443, proxy: "电报消息"}
  - {network: [tcp, udp], address: 0.0.0.0:9102, target: 149.154.167.91:443,  proxy: "电报消息"}
  - {network: [tcp, udp], address: 0.0.0.0:9103, target: 149.154.167.92:443,  proxy: "电报消息"}
```

配合 `hosts` 和 IP 映射一起使用，把 Telegram 客户端解析到的 IP 重定向到本地 tunnel 端口：

```yaml
hosts:
  # 把这些 Telegram IP 重映射，让所有请求通过 tunnel 走代理
  '91.108.56.100': [91.108.56.147, 91.108.56.117, 91.108.56.135]
  '91.108.56.101': [91.108.56.147, 91.108.56.117, 91.108.56.135]
```

**实际用途：**
- Telegram MTProto 直连优化：某些网络环境下 Telegram 规则匹配后仍然不稳定，通过 tunnel 强制绑定到代理
- 本地服务转发：把本地端口流量 tunnel 到远端服务，类似反向代理但通过代理链走

| 方式 | 规则依赖 | 适合场景 |
|------|----------|----------|
| 普通 `RULE-SET` 规则匹配 | 需要先匹配规则 | 通用分流 |
| `tunnels` 直通 | 无需规则，直接绑定 proxy-group | IP 固定的服务（Telegram/特定游戏服务器）|

> **注意：** `tunnels` 里写死了目标 IP，目标 IP 变动需手动更新。Telegram DC 的 IP 相对稳定，但也不是永久不变。如果 Telegram 上线新 DC，要补充新的 tunnel 条目。

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

## 六·五、📊 `nameserver-policy` 写法对比：geosite vs rule-set 引用

`nameserver-policy` 支持两种键格式，在精度和维护性上差异明显。

---

**写法一：`geosite:` 引用（iyyh 风格，简洁）**

```yaml
nameserver-policy:
  "geosite:cn,private":
    - https://223.5.5.5/dns-query
    - https://doh.pub/dns-query
  "geosite:geolocation-!cn":
    - "tls://8.8.8.8"
    - "tls://1.1.1.1"
```

优点：写法简洁，不需要额外引用 rule-providers，GeoSite 数据库自动维护。缺点：依赖 GeoSite 数据库，精度取决于数据库质量；`geolocation-!cn` 是内置标签，覆盖范围较粗。

---

**写法二：`rule-set:` 引用（TheFullSmart 风格，与分流规则联动）**

```yaml
# 来源：HenryChiao/MIHOMO_AIO TheFullSmart_test_version.yaml
# 直接引用 rule-providers 里已经定义好的规则集
nameserver-policy:
  # 这些规则集内的域名用国内 DNS
  "rule-set:LocationDKS,Private,Direct,XPTV,Download,AppleCN,China":
    - 1.12.12.12
    - 180.184.1.1
  # 这些规则集内的域名用国外 DNS
  "rule-set:Github,AI,Speedtest,Twitter,Telegram,SocialMedia,Games,Proxy":
    - https://8.8.8.8/dns-query#RULES&ecs=223.5.5.0/24
    - https://cloudflare-dns.com/dns-query
  # 关键词匹配也支持
  "domain-keyword:speedtest":
    - https://8.8.8.8/dns-query
```

注意其中的 `#RULES&ecs=223.5.5.0/24` 参数：
- `#RULES` 表示这个 DNS 请求也遵循路由规则（即这条 DNS 请求本身也走代理）
- `ecs=223.5.5.0/24` 是 DNS ECS（EDNS Client Subnet）参数，告诉 DNS 服务器客户端在中国大陆，使 CDN 能返回更适合的 IP（即使 DNS 请求走了代理，CDN 也知道"用户在哪"）

**DNS 锚点写法：** TheFullSmart 还把 DNS 服务器列表也做成锚点，减少重复：

```yaml
# 国内 DNS 列表锚点
direct-dns: &direct-dns
  - 'https://dns.alidns.com/dns-query#DIRECT'
  - 'https://doh.pub/dns-query#DIRECT&h3=false'  # h3=false 禁用 HTTP/3（稳定性）

# 国外 DNS 列表锚点
global-dns: &global-dns
  - "https://1.1.1.1/dns-query"
  - "https://dns.google/dns-query"
  - "https://dns.quad9.net/dns-query"
  - "tls://cloudflare-dns.com:853"
  - "tls://dns.google:853"

# 使用锚点引用
dns:
  nameserver-policy:
    "rule-set:China,Private": *direct-dns   # 引用国内 DNS 锚点
    "rule-set:Proxy,AI":      *global-dns   # 引用国外 DNS 锚点
```

| 对比项 | geosite 写法 | rule-set 写法 |
|--------|-------------|--------------|
| 与分流规则联动 | ❌ 独立维护 | ✅ 同一套规则集，改一处生效 |
| 精度控制 | 依赖 GeoSite 数据库质量 | 精确到具体服务分类 |
| ECS 支持 | 需手动在 nameserver 行加 `#RULES&ecs=` | 同上，但配合服务分类更精确 |
| 配置复杂度 | 低 | 中（需要 rule-providers 已定义）|
| DNS 列表复用 | 需重复写 | ✅ 可用锚点统一管理 DNS 服务器列表 |

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
