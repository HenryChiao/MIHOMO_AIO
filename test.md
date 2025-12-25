<div align="center">

# 🚀 Mihomo YAMLs Collection

**Mihomo / Clash Meta 核心专用配置精选合集**

[![Build Status](https://img.shields.io/github/actions/workflow/status/HenryChiao/mihomo_yamls/main.yml?label=Auto-Update&style=flat-square)](https://github.com/HenryChiao/mihomo_yamls/actions)
[![Repo Size](https://img.shields.io/github/repo-size/HenryChiao/mihomo_yamls?style=flat-square&color=blue)](https://github.com/HenryChiao/mihomo_yamls)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](./LICENSE)

<p>
  每日自动抓取更新 · 严格分类整理 · 纯净开箱即用
</p>

[⬇️ 下载客户端](#-mihomo-客户端与核心清单-clients) • [📖 如何使用](#-如何使用-usage) • [📂 查看配置](#-配置分类导航-categories)

</div>

---

> [!CAUTION]
> **禁止任何形式的转载或发布至🇨🇳大陆平台**
>
> Any form of reprinting or posting to the 🇨🇳 mainland platform is prohibited.

> [!WARNING]
> **中国大陆用户使用请遵守本国法律法规**
>
> Mainland China users please abide by the laws and regulations of your country.

---

## 📂 配置分类导航 (Categories)

> 请点击卡片标题进入对应文件夹查看详细列表。

<table width="100%">
  <tr>
    <td width="50%" valign="top">
      <h3>1️⃣ <a href="./Official_Examples">官方与基础示例</a></h3>
      <p><b>📂 <a href="./Official_Examples">Official Examples</a></b></p>
      <ul>
        <li>🎓 <b>适合</b>: 开发者、从零学习者</li>
        <li>✨ <b>特点</b>: 收录 Wiki 标准 <code>rule-set</code> 和 <code>geox</code> 模板。</li>
        <li>🌱 <b>用途</b>: 最纯净的参考标准，适合魔改。</li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <h3>2️⃣ <a href="./General_Config">通用进阶配置 (推荐)</a></h3>
      <p><b>📂 <a href="./General_Config">General Config</a></b></p>
      <ul>
        <li>💻 <b>适合</b>: PC / Mac / 手机日常用户</li>
        <li>🚀 <b>特点</b>: 包含 HenryChiao, 666OS, JohnsonRan 等大佬作品。</li>
        <li>🔥 <b>用途</b>: 主力推荐，含分流、去广告、故障转移。</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>3️⃣ <a href="./Smart_Mode">Smart / 路由专用</a></h3>
      <p><b>📂 <a href="./Smart_Mode">Smart Mode</a></b></p>
      <ul>
        <li>🏠 <b>适合</b>: OpenClash、软路由、SmartDNS</li>
        <li>🛠️ <b>特点</b>: 侧重 DNS 优化与底层网络接管。</li>
        <li>🧠 <b>用途</b>: 适合家庭网络网关设备。</li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <h3>4️⃣ <a href="./Mobile_Modules">安卓手机模块</a></h3>
      <p><b>📂 <a href="./Mobile_Modules">Mobile Modules</a></b></p>
      <ul>
        <li>📱 <b>适合</b>: Magisk / KernelSU 模块用户</li>
        <li>🧩 <b>特点</b>: 提取自 Surfing, Box 等透明代理模块。</li>
        <li>🔌 <b>用途</b>: 配合 ROOT 模块使用的内置配置。</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🚀 Mihomo 客户端与核心清单 (Clients)

此处整理了各平台适配 **Mihomo (Clash Meta)** 核心的图形化客户端。

| 平台 | 客户端名称 | 推荐度 | 核心特点/优势 | 说明/缺点 | 链接 |
|---|---|---|---|---|---|
| **核心** | **Mihomo Core** | 🟢 | 官方核心，无界面。支持 Rule-set, GeoX 等所有新特性。 | 所有 GUI 的基础。适合开发者、Linux 服务器或手搓配置党。 | [Github](https://github.com/MetaCubeX/mihomo/releases) |
| **核心** | **Mihomo (Smart)** | 🟢 | 路由/DNS 专用。指使用 Core 配合 TProxy/Tun 做透明网关。 | 这里的 "Smart" 通常指直接运行 Core 进行底层网络接管。 | [Guide](https://wiki.metacubex.one/) |
|  |  |  |  |  |  |
| **MacOS** | **FlClash** | 🟢 | 状态栏切换节点，多端同步，对 Meta 配置可视化极佳。 | 窗口管理比 Verge 更适合 Mac，Flutter 开发。 | [Github](https://github.com/chen08209/FlClash/releases) |
| **MacOS** | **Sparkle** | 🟢 | 原生感极强，支持状态栏切换，核心成员开发。 | 暂无明显缺点，Swift 开发。 | [Github](https://github.com/xishang0128/sparkle/releases) |
| **MacOS** | **Clash Verge Rev** | 🟢 | 功能强大，覆写设置丰富。 | 与 Mac 状态栏融合度一般，不如前两者丝滑。 | [Github](https://github.com/clash-verge-rev/clash-verge-rev/releases) |
| **MacOS** | Clash Party | 🟡 | 丝滑度高，原 Mihomo Party 分支。 | 存在项目所有权变更风险，目前迭代较快。 | [Github](https://github.com/mihomo-party-org/mihomo-party/releases) |
| **MacOS** | ClashMac | 🟡 | SwiftUI 开发，美观轻量，类 ClashX Meta 逻辑。 | 闭源项目。 | [Github](https://github.com/ClashMac/ClashMac) |
| **MacOS** | ClashX Meta | 🟡 | 官方维护，稳定性尚可。 | UI 审美较为独特，易与其他 App 冲突，已不再是首选。 | [Github](https://github.com/MetaCubeX/ClashX.Meta/releases) |
|  |  |  |  |  |  |
| **Windows** | **FlClash** | 🟢 | 极度轻量，更新极其勤快，功能全。 | UI 风格偏移动端 (Material Design)。 | [Github](https://github.com/chen08209/FlClash/releases) |
| **Windows** | **Clash Verge Rev** | 🟢 | 目前主流，内存占用少，功能最全。 | 2.0+ 版本架构变动大，UI 设计中规中矩。 | [Github](https://github.com/clash-verge-rev/clash-verge-rev/releases) |
| **Windows** | **Sparkle** | 🟢 | 核心成员作品，对 Meta 原生写法适配最好。 | 软件体积较大，更新频率随缘。 | [Github](https://github.com/xishang0128/sparkle/releases) |
| **Windows** | Clash Party | 🟡 | 原 Mihomo Party 分支。 | 继任者为利益相关方，有潜在风险。 | [Github](https://github.com/mihomo-party-org/mihomo-party/releases) |
| **Windows** | GUI.for.Clash | 🟡 | 插件化设计，鼠标点选生成配置。 | 适合极简/小白用户，功能自定义程度低。 | [Github](https://github.com/GUI-for-Cores/GUI.for.Clash/releases) |
| **Windows** | Clash Nyanpasu | 🟠 | 界面二次元化。 | 更新随缘。 | [Github](https://github.com/keiko233/clash-nyanpasu/releases) |
|  |  |  |  |  |  |
| **Linux** | **Mihomo** (裸核) | 🟢 | 利用 nftables 以 `auto_redirect` TUN 模式运行。 | 部署简便、性能较强。适合服务器/极客。 | [Github](https://github.com/MetaCubeX/mihomo/releases) |
| **Linux** | **FlClash** | 🟢 | Linux 桌面端首选 GUI，体验一致。 | AppImage 格式，开箱即用。 | [Github](https://github.com/chen08209/FlClash/releases) |
| **Linux** | Clash Verge Rev | 🟢 | 传统的 Linux GUI 客户端。 | 支持 Deb/Rpm/AppImage。 | [Github](https://github.com/clash-verge-rev/clash-verge-rev/releases) |
|  |  |  |  |  |  |
| **SteamOS** | **ToMoon** | 🟢 | Steam Deck 专用插件，基于 Mihomo 核心。 | 掌机模式下直接管理。 | [Github](https://github.com/YukiCoco/ToMoon) |
| **SteamOS** | DeckyClash | 🟢 | Steam Deck 插件，基于 Mihomo 核心。 | 需要 Decky Loader。 | [Github](https://github.com/NotGlop/DeckyClash) |
|  |  |  |  |  |  |
| **Android** | **FlClash** | 🟢 | 仿 Surfboard 界面，全协议，更省电。 | 覆写选项比 CMFA 略少。 | [Github](https://github.com/chen08209/FlClash/releases) |
| **Android** | **Clash Meta (CMFA)** | 🟢 | 官方分支，设置选项最全，兼容性最好。 | UI 交互逻辑一般，已停止大版本更新(但仍好用)。 | [Github](https://github.com/MetaCubeX/ClashMetaForAndroid/releases) |
| **Android** | Clash Mi | 🟡 | KaringX 作者新作，全协议支持。 | 新项目，处于早期阶段。 | [Telegram](https://t.me/clash_mi) |
| **Android** | YumeBox | 🟡 | UI 美观，集成 Sub-Store 和 Smart 策略组。 | 策略组切换操作较繁琐。 | [Github](https://github.com/Dreamacro/clash/issues) |
| **Android** | Surfing | 🟠 | Root 模块。集成配置，开箱即用。 | 需 Magisk/KSU 环境。 | [Github](https://github.com/GitMetaio/Surfing) |
| **Android** | Box4Magisk | 🟠 | Root 模块。全能核心 (Mihomo/Sing-box等)。 | 纯命令行/模块，无界面，门槛高。 | [Github](https://github.com/boxproxy/box) |
| **HarmonyOS** | **ClashBox** | 🟢 | (原 ClashNEXT) 基于安卓端 FlClash 二次开发。 | 需切换海外 App 商店下载，适配纯血鸿蒙。 | [Github](https://github.com/xiaobaigroup/ClashBox) |
|  |  |  |  |  |  |
| **iOS** | **Stash** ($5.99) | 🟢 | 强大的分流与重写，集成 MitM。 | 配置文件与标准 Mihomo 不完全互通，新协议跟进慢。 | [App Store](https://apps.apple.com/app/stash/id1596063349) |
| **iOS** | **Pharos Pro** ($2.99) | 🟢 | 一份配置通杀全平台，兼容性好。 | 佛系更新，缺席极个别 2025 新协议。 | [App Store](https://apps.apple.com/us/app/pharos-pro/id1456610173) |
| **iOS** | Clash Mi | 🟢 | 免费/TestFlight，全协议支持。 | KaringX 新项目。 | [Telegram](https://t.me/clash_mi) |
|  |  |  |  |  |  |
| **路由器** | **OpenClash** | 🟢 | (OpenWrt) 功能最全，设置极其丰富。 | 启动慢，界面臃肿，吃 CPU 性能。 | [Github](https://github.com/vernesong/OpenClash) |
| **路由器** | **Nikki** | 🟢 | (OpenWrt) 轻量化，启动快，依赖 nftables。 | 原 MihomoTProxy，适合现代 OpenWrt。 | [Github](https://github.com/nikkinikki-org/OpenWrt-nikki) |
| **路由器** | ShellCrash | 🟢 | (小米/SSH) 性能强，通过 SSH 管理。 | 无 Web UI (或仅有简单面板)。 | [Github](https://github.com/juewuy/ShellCrash) |
| **路由器** | MerlinClash2 | 🟢 | (华硕) 梅林固件首选，精简重构。 | 不支持老旧 CPU 型号。 | [Website](https://mclash.cn/) |

---

## 📖 如何使用 (Usage)

1.  点击上方 **分类导航** 中的标题，进入子文件夹。
2.  在子页面的表格中，浏览并找到你需要的 `.yaml` 配置。
3.  点击对应行的 **"查看配置"** 链接。
4.  在文件详情页，点击右上角的 `Raw` 按钮获取直链，或者直接复制内容到你的客户端中。

### 🚫 广告拦截效果测试 (AdBlock Test)
如果使用了去广告配置，可访问以下网站测试拦截效果：
* [AdBlock Tester](https://adblock-tester.com)
* [Block Ads! Adblock test](https://blockads.fivefilters.org/)
* [Ad Blocker Test](https://adblock.turtlecute.org/)

---

## ⚖️ 免责申明 (Disclaimer)

> [!IMPORTANT]
> **任何以任何方式查看此项目的人或直接或间接使用该项目的使用者都应仔细阅读此声明。**
>
> 1.  本项目涉及的文件仅用于资源共享和学习研究，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断。
> 2.  **请勿将本项目的任何内容用于商业或非法目的，否则后果自负。**
> 3.  一旦使用并复制了该项目的任何文件，则视为您已接受此免责声明。
> 4.  保留随时更改或补充此免责声明的权利。

---

## 🔗 致谢与来源 (Credits)

本仓库文件自动聚合自以下开源项目，特别感谢以下作者的无私分享。
**请大家给原作者的项目点个 Star 🌟 支持！**

<details>
<summary><strong>👉 点击展开查看完整致谢列表 (Click to expand)</strong></summary>

### ✍️ 配置作者 (Config Authors)

> 以下链接直达作者的原项目仓库，Star 数据实时获取。

* **HenryChiao** (MIHOMO_AIO)
    <br>
    [![Stars](https://img.shields.io/github/stars/HenryChiao/MIHOMO_AIO?style=social)](https://github.com/HenryChiao/MIHOMO_AIO)
* **666OS** (YYDS)
    <br>
    [![Stars](https://img.shields.io/github/stars/666OS/YYDS?style=social)](https://github.com/666OS/YYDS)
* **JohnsonRan** (CRules)
    <br>
    [![Stars](https://img.shields.io/github/stars/JohnsonRan/CRules?style=social)](https://github.com/JohnsonRan/CRules)
* **yiteei** (Share)
    <br>
    [![Stars](https://img.shields.io/github/stars/yiteei/Share?style=social)](https://github.com/yiteei/Share)
* **liandu2024** (Little)
    <br>
    [![Stars](https://img.shields.io/github/stars/liandu2024/little?style=social)](https://github.com/liandu2024/little)
* **Lanlan13-14** (Rules)
    <br>
    [![Stars](https://img.shields.io/github/stars/Lanlan13-14/Rules?style=social)](https://github.com/Lanlan13-14/Rules)
* **yyhhyyyyyy** (SelfProxy)
    <br>
    [![Stars](https://img.shields.io/github/stars/yyhhyyyyyy/selfproxy?style=social)](https://github.com/yyhhyyyyyy/selfproxy)
* **echs-top** (Proxy)
    <br>
    [![Stars](https://img.shields.io/github/stars/echs-top/proxy?style=social)](https://github.com/echs-top/proxy)
* **qichiyuhub** (Rule)
    <br>
    [![Stars](https://img.shields.io/github/stars/qichiyuhub/rule?style=social)](https://github.com/qichiyuhub/rule)
* **iKeLee** (Source: luestr/ProxyResource)
    <br>
    [![Stars](https://img.shields.io/github/stars/luestr/ProxyResource?style=social)](https://github.com/luestr/ProxyResource)
* **Fᴜғᴜ** (Source: sunfing/iNg)
    <br>
    [![Stars](https://img.shields.io/github/stars/sunfing/iNg?style=social)](https://github.com/sunfing/iNg)

### 📱 模块来源 (Mobile Modules)

* **Surfing**
    <br>
    [![Stars](https://img.shields.io/github/stars/GitMetaio/Surfing?style=social)](https://github.com/GitMetaio/Surfing)
* **AkashaProxy**
    <br>
    [![Stars](https://img.shields.io/github/stars/akashaProxy/akashaProxy?style=social)](https://github.com/akashaProxy/akashaProxy)
* **ClashMix**
    <br>
    [![Stars](https://img.shields.io/github/stars/AXEVO/Clash-MIX?style=social)](https://github.com/AXEVO/Clash-MIX)
* **BoxProxy**
    <br>
    [![Stars](https://img.shields.io/github/stars/boxproxy/box?style=social)](https://github.com/boxproxy/box)

### 📚 参考文档
* [Metacubex Wiki](https://wiki.metacubex.one/)

</details>

---

> [!TIP]
> **Life is a two-way street. This is a simple, profound, and undeniable truth.**
>
> 如果你在使用过程中遇到问题或有任何建议，欢迎指出。请确保你的帖子包含对他人有用的细节与信息，并通过 GitHub 社区分享你的发现。
>
> If you find this project helpful, please click ⭐Star in the upper-right corner to support us — and help more people discover and use it.
