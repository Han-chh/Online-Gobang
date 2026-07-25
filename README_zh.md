# Online Gobang

一个使用 Python/Pygame 实现的五子棋项目，支持局域网点对点房间、落子同步、聊天、计时、声音和玩家统计。

[English](README.md)

## 项目概述

应用使用自定义 Pygame 界面创建或加入局域网房间。15×15 游戏模型支持轮流落子、胜负/平局判断、聊天消息、单步计时、连接检测和玩家记录持久化。

## 演示

![展示创建房间、同步落子、聊天和完整对局的 Online Gobang 双端动态演示](assets/visual-demos/online-gobang.gif)

[查看高清 MP4 演示](assets/visual-demos/online-gobang.mp4)

录屏展示两个运行中的对等端创建房间、同步落子与聊天，并完成一局游戏。

## 截图

<p align="center">
  <img src="assets/screenshots/online-gobang.png" width="49%" alt="包含创建房间和加入房间控件的 Online Gobang 主界面">
  <img src="assets/screenshots/online-gobang-gameplay.png" width="49%" alt="包含同步落子和聊天内容的 Online Gobang 棋盘">
</p>

## 功能

- P2P 局域网房间创建与发现
- 15×15 棋盘与五连判断
- 实时落子和聊天消息
- 单步倒计时与超时处理
- 声音控制与玩家统计
- 自定义 Pygame UI 组件

## 运行

```bash
pip install pygame
python3 main.py
```

运行完整多人流程需要同一局域网内的两个对等端。
