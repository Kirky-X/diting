# tests/SKIPPED.md — 未纳入自动化测试的脚本

本目录为 diting 的离线冒烟测试套件（unittest，`python3 -m pytest tests -q` 可跑，
无网络、无第三方依赖）。以下脚本**刻意不写自动化测试**，原因与替代验证方式记录如下。

## scripts/install-skill.sh

- **类型**：副作用脚本。核心路径是 `rm -rf` / `mkdir -p` / `cp -r` / `git pull` /
  `git reset --hard` 等对真实文件系统与 git 仓库的破坏性/状态性操作。
- **不写假测试的原因**：
  1. 用 mock 假装 `cp`/`rm` 成功只能验证"脚本调用了命令"，验证不了安装结果，
     属于假覆盖；
  2. 真实执行会向磁盘写入 agent 目录（`.claude/skills/` 等）并可能触发 git 操作，
     违反离线、无副作用约束；
  3. 脚本依赖调用位置（multi-skill 父目录模式 vs standalone 仓模式），与部署环境强耦合。
- **替代验证**：人工/演练验证清单——
  - `./install-skill.sh list-skills`、`list-agents`、`status`（只读子命令，可手动冒烟）；
  - `install`/`uninstall` 在临时 target 目录演练，确认 `EXCLUDE_PATTERNS`
    （.git/.venv/node_modules/specmark 等）未带入目标；
  - `uninstall` 的路径逃逸防护（skill-name 含 `/`、realpath 越界拒绝）靠 code review 把关。
- **关联**：仓库根 `/home/kirky/projects/skills/scripts/install-skill.sh` 是同一脚本的多仓
  管理副本，同样不纳入本套件。
