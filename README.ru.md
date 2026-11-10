<div align="center">

# 📡 Iran VPN Radar

**Бесплатные VPN-подписки, протестированные изнутри Ирана — обновляются автоматически каждые 2 часа**

</div>

**Языки:** [فارسی (основной)](README.md) · [English](README.en.md) · [العربية](README.ar.md) · [中文](README.zh.md) · **Русский** · [Español](README.es.md)

> ⚠️ **Перевод.** Основной язык проекта — персидский ([README.md](README.md)).

## 📥 Ссылки на подписки

Скопируйте ссылку и добавьте её в свой VPN-клиент. Готово.

| Протокол | Ссылка на подписку |
|----------|--------------------|
| **Все протоколы** | [`subscriptions/all`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/all) |
| VLESS | [`subscriptions/vless`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless) |
| VMess | [`subscriptions/vmess`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vmess) |
| Trojan | [`subscriptions/trojan`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/trojan) |
| Shadowsocks | [`subscriptions/shadowsocks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/shadowsocks) |
| Hysteria2 | [`subscriptions/hysteria2`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/hysteria2) |
| TUIC | [`subscriptions/tuic`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/tuic) |
| SOCKS | [`subscriptions/socks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/socks) |
| HTTP | [`subscriptions/http`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/http) |

> Версия в Base64 доступна с суффиксом `.b64`.

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

## ⭐ Кандидаты с приоритетом Ирана

Конфигурации, для которых установлен **реальный туннель** **и** которые были доступны с иранской сетевой точки. Это лучшие доступные варианты, пока не выполнен полный тест туннеля изнутри Ирана.

| | |
|---|---|
| **Все протоколы** | [`subscriptions/iran-priority/all`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/all) |
| VLESS | [`subscriptions/iran-priority/vless`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vless) |
| VMess | [`subscriptions/iran-priority/vmess`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vmess) |
| Trojan | [`subscriptions/iran-priority/trojan`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/trojan) |
| Shadowsocks | [`subscriptions/iran-priority/shadowsocks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/shadowsocks) |
| Hysteria2 | [`subscriptions/iran-priority/hysteria2`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/hysteria2) |
| TUIC | [`subscriptions/iran-priority/tuic`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/tuic) |
| SOCKS | [`subscriptions/iran-priority/socks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/socks) |
| HTTP | [`subscriptions/iran-priority/http`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/http) |

> Они **не проверены изнутри Ирана** (туннель установлен с нашего хоста), но имеют доказательства доступности из иранской сети и имеют наивысший приоритет среди кандидатов.

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
