<div align="center">

# 📡 Iran VPN Radar

**Бесплатные VPN-подписки, протестированные изнутри Ирана — обновляются автоматически каждые 2 часа**

</div>

**Языки:** [فارسی (основной)](README.md) · [English](README.en.md) · [العربية](README.ar.md) · [中文](README.zh.md) · **Русский** · [Español](README.es.md)

> ⚠️ **Перевод.** Основной язык проекта — персидский ([README.md](README.md)).

<!-- radar:subscriptions:start -->
## 📥 Ссылки на подписки

Скопируйте ссылку и добавьте её в свой VPN-клиент. Готово.

**Все протоколы (all):** [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/all](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/all)

| Протокол | Ссылка на подписку | Активных конфигураций |
|---|---|---|
| **VLESS** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vless](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vless) | 101 |
| **VMess** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vmess](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vmess) | 11 |
| **Trojan** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/trojan](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/trojan) | 72 |
| **Shadowsocks** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/shadowsocks](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/shadowsocks) | 38 |
| **Hysteria2** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/hysteria2](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/hysteria2) | 0 |
| **TUIC** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/tuic](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/tuic) | 0 |
| **SOCKS** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/socks](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/socks) | 5 |
| **HTTP** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/http](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/http) | 2 |

> Версия в Base64 доступна с суффиксом `.b64`.

> Эти ссылки относятся к уровню «приоритет Ирана»: реальный туннель установлен и есть свидетельства доступности из иранской сети, но они не проверены изнутри Ирана.
<!-- radar:subscriptions:end -->

### Как использовать

1. Скопируйте ссылку нужного протокола из таблицы выше.
2. В клиенте выберите **Добавить подписку (Add subscription)**.
3. Вставьте ссылку и обновите.
4. Выберите сервер и подключитесь.

## 📊 Статус

* **Обновление:** автоматически, каждые 2 часа.
* **Текущий статус:** [status/summary.json](status/summary.json)

> ⚠️ **Внимание:** публикуются только конфигурации, прошедшие реальный тест
> изнутри Ирана. Пока конфигурация не прошла этот тест, файлы остаются пустыми.
> Мы никогда не помечаем непроверенную конфигурацию как рабочую.

## 📈 Статус по протоколам

Счётчики обновляются каждые 2 часа. **Здоровые** — установлен реальный туннель. Цель — **100** рабочих конфигураций для каждого протокола; счётчики протоколов не суммируются.

| Протокол | Обнаружено | Протестировано | Успешных | Здоровых | Цель | Дефицит | Приоритет Ирана | Подписка |
|---|---|---|---|---|---|---|---|---|
| **vless** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.vless&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.vless&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.vless&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.vless&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.vless&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.vless&color=yellowgreen) | [`subscriptions/candidates/vless`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/vless) |
| **vmess** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.vmess&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.vmess&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.vmess&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.vmess&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.vmess&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.vmess&color=yellowgreen) | [`subscriptions/candidates/vmess`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/vmess) |
| **trojan** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.trojan&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.trojan&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.trojan&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.trojan&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.trojan&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.trojan&color=yellowgreen) | [`subscriptions/candidates/trojan`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/trojan) |
| **shadowsocks** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.shadowsocks&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.shadowsocks&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.shadowsocks&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.shadowsocks&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.shadowsocks&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.shadowsocks&color=yellowgreen) | [`subscriptions/candidates/shadowsocks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/shadowsocks) |
| **hysteria2** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.hysteria2&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.hysteria2&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.hysteria2&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.hysteria2&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.hysteria2&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.hysteria2&color=yellowgreen) | [`subscriptions/candidates/hysteria2`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/hysteria2) |
| **tuic** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.tuic&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.tuic&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.tuic&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.tuic&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.tuic&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.tuic&color=yellowgreen) | [`subscriptions/candidates/tuic`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/tuic) |
| **socks** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.socks&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.socks&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.socks&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.socks&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.socks&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.socks&color=yellowgreen) | [`subscriptions/candidates/socks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/socks) |
| **http** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.http&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.http&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.http&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.http&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.http&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.http&color=yellowgreen) | [`subscriptions/candidates/http`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/http) |

## 🧪 Пул кандидатов (не проверено из Ирана)

Отдельный пул содержит конфигурации, туннель которых реально установлен
настоящим клиентом (sing-box) — но с нашего хоста-движка, который **не находится
в Иране**. Они отсортированы так, что первыми идут записи, которые иранский
зонд уже наблюдал как доступные.

* Все кандидаты: [`subscriptions/candidates/all`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/all)
* По протоколам: `subscriptions/candidates/vless`, `.../vmess`, `.../trojan`,
  `.../shadowsocks`, `.../hysteria2`, `.../tuic`, `.../socks`, `.../http`

> Это **не** проверено из Ирана. Они могут быть заблокированы внутри Ирана.
> Используйте только как запасной вариант или отправную точку. Файлы выше
> (без `/candidates/`) — это проверенные из Ирана.

## 📱 Поддерживаемые клиенты

v2rayNG · v2rayN · sing-box · Hiddify / NekoBox · Clash / Clash.Meta

## ❓ Частые вопросы

**Как часто обновляются подписки?** Каждые 2 часа, автоматически.

**Почему файлы пусты?** Потому что ни одна конфигурация ещё не прошла тест
«проверено изнутри Ирана». Это сделано намеренно, чтобы не публиковать
нерабочие конфигурации.

**Как сообщить о нерабочей конфигурации?** Через
[Issues](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/issues).
Никогда не публикуйте пароли, личные ссылки или приватную информацию.

**Эти конфигурации безопасны?** Конфигурации **публичны** и могут быть
нестабильны или принадлежать другим людям. Используйте на свой риск.
См. [SECURITY.md](SECURITY.md).
