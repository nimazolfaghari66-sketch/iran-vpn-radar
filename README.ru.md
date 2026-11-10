<div align="center">

# 📡 Iran VPN Radar

**Автоматический поиск, тестирование и публикация бесплатных VPN-подписок для пользователей в Иране**

</div>

**Языки:** [فارسی (основной)](README.md) · [English](README.en.md) · [العربية](README.ar.md) · [中文](README.zh.md) · **Русский** · [Español](README.es.md)

> ⚠️ **Перевод.** Основной язык проекта — персидский ([README.md](README.md)). Этот файл — вычитанный перевод.

---

## ⚠️ Статус иранского тестирования

В проекте есть одно незыблемое правило: **конфигурация публикуется как «проверенная в Иране» только если её действительно протестировал зонд, физически находящийся в Иране.**

Пока зонд не подключён:

* все конфигурации остаются в состоянии `PENDING_IRAN_TEST`;
* опубликованные файлы подписок намеренно **пусты**;
* результаты из-за рубежа или синтетические результаты никогда не выдаются за иранские.

## Что это за проект?

Автоматизированная система с открытым исходным кодом, которая:

1. **Находит** публичные источники бесплатных конфигураций VPN.
2. **Извлекает**, нормализует и **удаляет дубликаты**.
3. **Тестирует их изнутри Ирана** реальными клиентами протоколов.
4. **Удаляет** нерабочие и дублирующиеся конфигурации.
5. **Публикует** подписки, разделённые по протоколам.
6. **Повторяет** цикл **каждые 2 часа**.

## Поддерживаемые протоколы

| Протокол | Файл подписки |
|----------|---------------|
| Все | `subscriptions/all` |
| VLESS | `subscriptions/vless` |
| VMess | `subscriptions/vmess` |
| Trojan | `subscriptions/trojan` |
| Shadowsocks | `subscriptions/shadowsocks` |
| Hysteria2 | `subscriptions/hysteria2` |
| TUIC | `subscriptions/tuic` |
| SOCKS | `subscriptions/socks` |
| HTTP/HTTPS | `subscriptions/http` |

## Ссылки на подписки

```
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/all
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vmess
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/trojan
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/shadowsocks
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/hysteria2
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/tuic
```

Версия в Base64 доступна с суффиксом `.b64`.

## Иранское тестирование

Зонд должен работать на хосте внутри Ирана:

```bash
export IRAN_PROBE_TOKEN="надёжный-общий-секрет"
python3 probe/probe_agent.py --port 8787
```

Затем центральный движок:

```bash
export IRAN_RADAR_PROBE_MODE=remote
export IRAN_PROBE_URL="https://probe.example.ir:8787"
export IRAN_PROBE_TOKEN="тот-же-секрет"
```

Этапы теста: DNS, доступность сервера, рукопожатие протокола, установка туннеля, интернет через туннель, задержка, ограниченная загрузка, краткосрочная стабильность.

## Политика качества

`DISCOVERED` → `PENDING_IRAN_TEST` → `TESTING` → `WORKING` / `DEGRADED` / `FAILED` / `EXPIRED` / `DUPLICATE`

Одна ошибка подряд: `DEGRADED` (публикуется). Две подряд: удаляется из вывода.

## Безопасность и приватность

Все конфигурации **публичны** и могут быть небезопасны или нестабильны. Проект никогда не хранит и не публикует пароли, токены или закрытые ключи. См. [SECURITY.md](SECURITY.md).

## Участие

[CONTRIBUTING.md](CONTRIBUTING.md) — предложить публичный источник, сообщить о нерабочей конфигурации, улучшить код, перевести документацию.

## Лицензия

[MIT](LICENSE)
