# 新区快速练级闭环执行说明

## 目标

把新区练级从“只会选任务”推进到统一闭环：

```text
状态识别
  ↓
安全检查
  ↓
候选任务生成
  ↓
练级策略评分
  ↓
选择任务
  ↓
执行任务
  ↓
验证是否完成
  ↓
读取等级/经验变化
  ↓
下一轮重新决策
```

## Controller

核心实现：

```text
engine/leveling_controller.py
```

`NewServerLevelingController.tick()` 每次只执行一个有限闭环，不在内部无限重试。

## Observer

Observer 必须提供：

```yaml
level: 50
level_known: true
exp_percent: 35
window_available: true
state: IDLE
candidates:
  - name: 抓鬼
    estimated_exp: 9000
    estimated_travel_seconds: 30
    failure_risk: 1
    repeatability: 10
    unlock_value: 0
    available: true
```

其中 `level_known=false` 时禁止自动选择任务，防止 OCR/识别错误导致错误操作。

## Executor

Executor 接收：

```text
execute(task, observation)
```

必须返回明确结果：

```yaml
completed: true
level: 51
progress: 20
```

或者：

```yaml
completed: false
retryable: true
reason: 任务目标未识别
```

只有 `completed=true` 才认为任务完成。

## 安全停止条件

以下任意条件出现，都必须停止真实动作：

- 游戏窗口不存在
- 等级无法可靠识别
- Worker 为 `ERROR`
- Worker 为 `DISCONNECTED`
- Skill 不存在
- 没有可执行候选任务
- 完成标志无法验证
- 连续失败达到上限

## Dry Run

开发阶段建议：

```text
Observer → Strategy → DryRun Executor
```

先验证：

- 等级识别
- 候选任务生成
- 任务评分
- 任务选择
- 完成判断
- 错误恢复

确认稳定后，再把真实地图、按钮模板和战斗动作接入 Executor。

## 下一层实现顺序

```text
1. 等级/经验 OCR
2. 当前地图识别
3. NPC/任务按钮模板
4. 地图路线 Skill
5. 任务领取与完成验证
6. 战斗状态识别
7. 战斗 Skill
8. 5开队伍同步
```

不要把这些客户端坐标直接写进 `leveling.py`；它们应该保持在 Skill/模板层。
