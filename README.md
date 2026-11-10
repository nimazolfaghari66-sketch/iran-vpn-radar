<div align="center" dir="rtl">

# 📡 ایران وی‌پی‌ان رادار (Iran VPN Radar)

**کشف، آزمایش و انتشار خودکار اشتراک‌های رایگان وی‌پی‌ان برای کاربران ایران**

[![CI](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

<div dir="rtl">

## 🌐 زبان‌ها

**فارسی (زبان اصلی)** · [English](README.en.md) · [العربية](README.ar.md) · [中文](README.zh.md) · [Русский](README.ru.md) · [Español](README.es.md)

---

## ⚠️ مهم: وضعیت آزمایش ایرانی

این پروژه یک اصل سخت‌گیرانه دارد: **هیچ کانفیگی به عنوان «تأییدشده از ایران» منتشر نمی‌شود مگر آنکه واقعاً از یک کاوشگر مستقر در ایران آزمایش شده باشد.**

کاوشگر ایران یک سرویس جداگانه است که باید روی میزبان داخل ایران اجرا شود. تا زمانی که چنین کاوشگری متصل نشده باشد:

* همهٔ کانفیگ‌ها در وضعیت `PENDING_IRAN_TEST` باقی می‌مانند.
* فایل‌های اشتراک منتشرشده خالی خواهند بود.
* هیچ نتیجهٔ ساختگی یا آزمایش خارج از ایران به‌عنوان آزمایش ایرانی گزارش نمی‌شود.

برای راه‌اندازی کاوشگر ایران به بخش [معماری آزمایش ایرانی](#-معماری-آزمایش-ایرانی) مراجعه کنید.

</div>

---

## English (summary)

**Iran VPN Radar** automatically discovers publicly available **free** VPN
subscription links, normalises them, de-duplicates them, tests them **from
inside Iran** with real protocol clients, and publishes protocol-specific
subscription files back to this repository.

**Current status:** the discovery, extraction, normalisation, de-duplication,
generation, validation and publishing pipeline is live and tested against real
public sources. Iranian testing requires an Iran-based probe agent; until one is
connected, all configurations stay `PENDING_IRAN_TEST` and the published
subscription files are intentionally empty. No test result is ever fabricated.

Full English documentation: **[README.en.md](README.en.md)**

---

<div dir="rtl">

## 🎯 این پروژه چیست؟

ایران وی‌پی‌ان رادار یک سیستم خودکار و متن‌باز است که:

1. منابع عمومی و رایگان انتشار کانفیگ را **به‌صورت خودکار کشف** می‌کند.
2. کانفیگ‌ها را استخراج، نرمال‌سازی و **یکتاسازی** می‌کند.
3. آن‌ها را **از داخل ایران** با کلاینت واقعی پروتکل آزمایش می‌کند.
4. کانفیگ‌های خراب و تکراری را حذف می‌کند.
5. فایل‌های اشتراک تفکیک‌شده بر اساس پروتکل را منتشر می‌کند.
6. این چرخه را **هر ۲ ساعت** تکرار می‌کند.

## 🔌 پروتکل‌های پشتیبانی‌شده

| پروتکل | فایل اشتراک | وضعیت |
|--------|-------------|-------|
| همه | `subscriptions/all` | ✅ |
| VLESS | `subscriptions/vless` | ✅ |
| VMess | `subscriptions/vmess` | ✅ |
| Trojan | `subscriptions/trojan` | ✅ |
| Shadowsocks | `subscriptions/shadowsocks` | ✅ |
| Hysteria2 | `subscriptions/hysteria2` | ✅ |
| TUIC | `subscriptions/tuic` | ✅ |
| SOCKS | `subscriptions/socks` | ✅ |
| HTTP/HTTPS | `subscriptions/http` | ✅ |

## 🔗 لینک‌های اشتراک

```
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/all
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vmess
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/trojan
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/shadowsocks
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/hysteria2
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/tuic
```

نسخهٔ Base64 هر فایل با پسوند `.b64` در دسترس است، مثلاً:

```
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless.b64
```

> **توجه:** تا اتصال کاوشگر ایران، این فایل‌ها خالی هستند. این رفتار عمدی و مطابق سیاست پروژه است.

## 📱 سازگاری با کلاینت‌ها

| کلاینت | پلتفرم | قالب پیشنهادی |
|--------|--------|----------------|
| v2rayNG | Android | لینک Base64 (`.b64`) |
| v2rayN | Windows | لینک Base64 |
| sing-box | چندسکویی | متن ساده |
| Clash / Clash.Meta | چندسکویی | از فایل‌های پروتکل استفاده کنید |
| NekoBox / Hiddify | چندسکویی | لینک Base64 |

## ⚙️ نحوهٔ کار

```
کشف منابع → دریافت → استخراج → نرمال‌سازی → یکتاسازی
      → آزمایش از ایران → سیاست کیفیت → تولید فایل → اعتبارسنجی → انتشار
```

هر ۲ ساعت یک چرخهٔ کامل اجرا می‌شود. اگر چیزی تغییر نکند، هیچ کامیت جدیدی ساخته نمی‌شود.

## 🛡️ سیاست کیفیت و حذف

| وضعیت | معنی |
|-------|------|
| `DISCOVERED` | کشف شد، هنوز آزمایش نشده |
| `PENDING_IRAN_TEST` | در انتظار آزمایش از ایران |
| `TESTING` | در حال آزمایش |
| `WORKING` | تأییدشده از ایران |
| `DEGRADED` | یک شکست پشت‌سرهم (هنوز منتشر می‌شود) |
| `FAILED` | دو شکست پشت‌سرهم (حذف از خروجی) |
| `EXPIRED` | منقضی یا نامعتبر (حذف از خروجی) |
| `DUPLICATE` | تکراری |

## 🔬 معماری آزمایش ایرانی

آزمایش ایرانی توسط یک **کاوشگر جداگانه** انجام می‌شود که باید داخل ایران اجرا شود:

```bash
# روی میزبان داخل ایران:
export IRAN_PROBE_TOKEN="یک-کلید-مشترک-قوی"
python3 probe/probe_agent.py --port 8787
```

سپس موتور مرکزی با این متغیرها اجرا می‌شود:

```bash
export IRAN_RADAR_PROBE_MODE=remote
export IRAN_PROBE_URL="https://probe.example.ir:8787"
export IRAN_PROBE_TOKEN="همان-کلید-مشترک"
```

آزمایش‌های واقعی شامل این مراحل است: DNS، دسترسی به سرور، دست‌دادن پروتکل، برقراری تونل، دسترسی به اینترنت از طریق تونل، تأخیر، سرعت دانلود محدود، و پایداری کوتاه‌مدت.

اگر کاوشگر موجود نباشد، هیچ آزمایش ایرانی جعل نمی‌شود.

## 🚨 گزارش کانفیگ خراب

از طریق [Issues](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/issues) گزارش دهید. لطفاً **هیچ‌گاه** اطلاعات خصوصی، رمز عبور یا لینک اشتراک شخصی خود را در Issues قرار ندهید.

## 🤝 مشارکت

* پیشنهاد منابع عمومی جدید
* گزارش کانفیگ خراب
* بهبود کد
* ترجمهٔ مستندات

راهنمای کامل: [CONTRIBUTING.md](CONTRIBUTING.md)

## 🔒 امنیت و حریم خصوصی

* تمام کانفیگ‌ها **عمومی** هستند و ممکن است ناامن، ناپایدار یا متعلق به شخص دیگری باشند.
* این پروژه هیچ‌گاه رمز عبور، توکن یا کلید خصوصی را ذخیره یا منتشر نمی‌کند.
* برای جزئیات به [SECURITY.md](SECURITY.md) مراجعه کنید.

## 📜 مجوز

[MIT](LICENSE)

</div>
