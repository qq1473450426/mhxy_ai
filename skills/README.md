# Skill 目录

把本地 Skill 数据放在这里。推荐按功能分类：

```text
skills/
├── maps/        # 地图/场景与坐标
├── navigation/  # 路线
├── battle/      # 战斗状态与动作定义
├── daily/       # 日常任务步骤
└── templates/   # UI 模板说明
```

Skill 是数据/规则层，不是协议注入层。V2 的 SkillStore 支持关键词搜索和简单 `x: 123, y: 456` 坐标提取。

## 示例

```yaml
name: demo_daily
world: 示例场景
route:
  - {x: 100, y: 200, action: move}
  - {x: 120, y: 220, action: interact}
```
