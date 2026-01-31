# MIHOMO ALL IN ONE

> 基于 [666OS/YYDS](https://github.com/666OS/YYDS) 仓库中 `MihomoPro.yaml` 衍生的配置集合，面向 vernnesong/mihomo 生态的集成与管理。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Upstream sync](https://img.shields.io/badge/upstream-synced-green)
<!-- 若启用 CI，请替换为 Actions badge -->
<!-- ![CI](https://github.com/HenryChiao/MIHOMO_AIO/actions/workflows/ci.yml/badge.svg) -->

## 目录
- [项目简介](#项目简介)
- [快速上手](#快速上手)
- [项目结构](#项目结构)
- [配置说明（简要）](#配置说明简要)
- [如何更新 & 与上游同步](#如何更新--与上游同步)
- [备份与恢复](#备份与恢复)
- [贡献指南](#贡献指南)
- [免责声明与许可](#免责声明与许可)
- [致谢](#致谢)

## 项目简介
本项目汇集并整理了适用于 Mihomo 的规则与配置片段，便于快速部署与个性化定制。内容来源参考并衍生自 [666OS/YYDS](https://github.com/666OS/YYDS)。仅供学习、研究与个人使用，请遵守相关法律与上游许可。

## 快速上手
1. 克隆仓库：
   ```bash
   git clone https://github.com/HenryChiao/MIHOMO_AIO.git
   cd MIHOMO_AIO
   ```
2. 使用 CONFIG 中的配置：
   - 直接复制到你的 mihomo 或路由配置目录：
     ```bash
     cp -r CONFIG/ /path/to/your/mihomo/configs/
     ```
3. OpenClash 覆写（如需）：
   - 覆写脚本位于 `OPENCLASH_OVERWRITE/`，按需复制到 OpenClash 配置目录并重启 OpenClash。

提示：建议先在测试环境验证配置是否符合你当前环境（不同版本或分支可能会影响规则语法或行为）。

## 项目结构
```
.
├── CONFIG/                   # 主配置文件与规则集
├── OPENCLASH_OVERWRITE/      # openclash 覆写模块脚本
├── BACKUP/                   # 归档（历史文件/弃用规则）
└── README.md                 # 项目说明
```

- CONFIG/: 按分组（General / SMART 等）组织配置，覆盖常见使用场景。
- OPENCLASH_OVERWRITE/: OpenClash 覆写脚本，便于快速替换与调试。
- BACKUP/: 存档与历史记录，便于回滚与参考。

## 配置说明（简要）
- General：面向大多数场景的通用配置与规则。
- SMART：适配 vernesong/mihomo smart 分支的配置。
- 具体每个文件的用途和适用场景请参考 `CONFIG/README.md`。

## 如何更新 & 与上游同步
建议通过添加上游 remote 的方式来同步原始仓库更新并保持可追溯性：

```bash
# 添加上游（仅需一次）
git remote add upstream https://github.com/666OS/YYDS.git

# 获取并查看上游分支
git fetch upstream

# 合并上游变更到本地 main（根据你团队流程选择 merge 或 rebase）
git checkout main
git merge upstream/main
# 或：git rebase upstream/main
```

合并后请在本地测试规则，处理冲突并在确认可用后推送到远程。

## 备份与恢复
在应用新配置前请务必备份当前配置：
```bash
cp -r /path/to/current/config /path/to/backup/config_$(date +%F)
```
若需恢复，请将备份文件复制回目标目录并重启相关服务。

## 贡献指南
欢迎贡献！简单流程：
1. Fork 本仓库
2. 新建分支（如：`feature/xxx` 或 `fix/yyy`）
3. 提交更改并发起 Pull Request，说明改动内容与测试方式
4. 维护者会审阅并给出合并建议

详细贡献规范请查看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 免责声明与许可
- 本项目仅供学习与交流使用，配置内容参考自 [666OS/YYDS](https://github.com/666OS/YYDS)。
- 请勿将本项目用于商业或非法用途。使用者���自行判断合法性并承担相关责任。
- 作者不对因使用本项目所造成的任何后果承担责任。

（如需明确许可，请在仓库添加 LICENSE 文件并在此处注明许可类型，如 MIT、Apache-2.0 等。）

## 致谢
- 感谢 [666OS/YYDS](https://github.com/666OS/YYDS) 的贡献与启发。
- 欢迎在 Issue 中指出问题或建议改进方向.
