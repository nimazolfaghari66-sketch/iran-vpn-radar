<div align="center">

# 📡 伊朗 VPN 雷达

**自动发现、测试并发布面向伊朗用户的免费 VPN 订阅**

</div>

**语言：** [فارسی（主要）](README.md) · [English](README.en.md) · [العربية](README.ar.md) · **中文** · [Русский](README.ru.md) · [Español](README.es.md)

> ⚠️ **翻译文件。** 项目的主要语言是波斯语（[README.md](README.md)）。本文件为经审校的翻译。

---

## ⚠️ 伊朗测试状态

本项目有一条不可妥协的原则：**只有由实际位于伊朗境内的探测器测试通过的配置，才会被发布为「伊朗验证」。**

在探测器接入之前：

* 所有配置保持 `PENDING_IRAN_TEST` 状态；
* 已发布的订阅文件**有意保持为空**；
* 绝不以境外测试或伪造结果冒充伊朗测试。

## 这是什么项目？

一个自动化的开源系统：

1. **自动发现**公开发布免费 VPN 配置的来源。
2. **提取**、规范化并**去重**配置。
3. 使用真实的协议客户端**从伊朗境内测试**。
4. **剔除**失效与重复的配置。
5. **发布**按协议分类的订阅文件。
6. **每 2 小时**重复一次上述流程。

## 支持的协议

| 协议 | 订阅文件 |
|------|----------|
| 全部 | `subscriptions/all` |
| VLESS | `subscriptions/vless` |
| VMess | `subscriptions/vmess` |
| Trojan | `subscriptions/trojan` |
| Shadowsocks | `subscriptions/shadowsocks` |
| Hysteria2 | `subscriptions/hysteria2` |
| TUIC | `subscriptions/tuic` |
| SOCKS | `subscriptions/socks` |
| HTTP/HTTPS | `subscriptions/http` |

## 订阅链接

```
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/all
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vmess
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/trojan
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/shadowsocks
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/hysteria2
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/tuic
```

每个文件的 Base64 版本带有 `.b64` 后缀。

## 伊朗测试

探测器必须运行在伊朗境内的主机上：

```bash
export IRAN_PROBE_TOKEN="强共享密钥"
python3 probe/probe_agent.py --port 8787
```

然后运行中央引擎：

```bash
export IRAN_RADAR_PROBE_MODE=remote
export IRAN_PROBE_URL="https://probe.example.ir:8787"
export IRAN_PROBE_TOKEN="同一个密钥"
```

测试阶段：DNS、服务器可达性、协议握手、隧道建立、隧道内联网、延迟、限速下载、短期稳定性。

## 质量与剔除策略

`DISCOVERED` → `PENDING_IRAN_TEST` → `TESTING` → `WORKING` / `DEGRADED` / `FAILED` / `EXPIRED` / `DUPLICATE`

连续失败一次：`DEGRADED`（仍发布）。连续失败两次：从输出中移除。

## 安全与隐私

所有配置都是**公开的**，可能不安全或不稳定。本项目绝不存储或发布密码、令牌或私钥。详见 [SECURITY.md](SECURITY.md)。

## 贡献

[CONTRIBUTING.md](CONTRIBUTING.md) —— 推荐公开来源、报告失效配置、改进代码、翻译文档。

## 许可证

[MIT](LICENSE)
