<div align="center" dir="rtl">

# 📡 ایران وی‌پی‌ان رادار

**کشف، آزمایش و انتشار خودکار اشتراک‌های رایگان وی‌پی‌ان برای کاربران ایران**

</div>

<div dir="rtl">

**زبان‌ها:** [فارسی (اصلی)](README.md) · [English](README.en.md) · [العربية](README.ar.md) · [中文](README.zh.md) · [Русский](README.ru.md) · [Español](README.es.md)

> این پرونده نسخهٔ کامل فارسی است. صفحهٔ اصلی پروژه نیز فارسی‌محور است: [README.md](README.md)

## ⚠️ وضعیت آزمایش ایرانی

هیچ کانفیگی به‌عنوان «تأییدشده از ایران» منتشر نمی‌شود مگر آنکه واقعاً توسط کاوشگری داخل ایران آزمایش شده باشد. تا اتصال کاوشگر:

* همهٔ کانفیگ‌ها در وضعیت `PENDING_IRAN_TEST` می‌مانند.
* فایل‌های اشتراک منتشرشده **خالی** هستند.
* هیچ نتیجهٔ خارجی یا ساختگی به‌عنوان آزمایش ایرانی گزارش نمی‌شود.

## این پروژه چیست؟

سیستمی خودکار و متن‌باز که منابع عمومی انتشار کانفیگ را کشف می‌کند، آن‌ها را استخراج و یکتاسازی می‌کند، از داخل ایران آزمایش می‌کند، خرابی‌ها را حذف می‌کند و فایل‌های اشتراک تفکیک‌شده را هر ۲ ساعت منتشر می‌کند.

## پروتکل‌های پشتیبانی‌شده

VLESS · VMess · Trojan · Shadowsocks · Hysteria2 · TUIC · SOCKS · HTTP/HTTPS

## لینک‌های اشتراک

```
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/all
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vmess
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/trojan
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/shadowsocks
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/hysteria2
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/tuic
```

نسخهٔ Base64 با پسوند `.b64` در دسترس است.

## آزمایش ایرانی

کاوشگر باید روی میزبانی داخل ایران اجرا شود:

```bash
export IRAN_PROBE_TOKEN="یک-کلید-مشترک-قوی"
python3 probe/probe_agent.py --port 8787
```

سپس موتور مرکزی:

```bash
export IRAN_RADAR_PROBE_MODE=remote
export IRAN_PROBE_URL="https://probe.example.ir:8787"
export IRAN_PROBE_TOKEN="همان-کلید"
```

مراحل آزمایش: DNS، دسترسی به سرور، دست‌دادن پروتکل، تونل، اینترنت از طریق تونل، تأخیر، دانلود محدود، پایداری.

### تشخیص دسترسی از داخل ایران (Check-Host)

علاوه بر کاوشگر اصلی، پروژه از سرویس عمومی [Check-Host](https://check-host.net) برای سنجش «دسترسی‌پذیری از داخل ایران» (تهران، اصفهان، شیراز، قم) استفاده می‌کند. گره‌های Check-Host کاوشگر تشخیصی از راه دور هستند؛ می‌توان نام دامنه را resolve کرد یا یک سوکت TCP/UDP باز کرد، اما نمی‌توان روی آن‌ها کلاینت VPN اجرا کرد.

بنابراین Check-Host فقط نشان می‌دهد که سرور از ایران «در دسترس» است، اما هرگز اثبات نمی‌کند که «تونل کار می‌کند». این نتایج تنها تشخیصی هستند، هرگز منتشر نمی‌شوند و هیچ کانفیگی را به خروجی منتشرشده اضافه نمی‌کنند. این کار فقط از عهدهٔ کاوشگر ایران برمی‌آید. جزئیات: [docs/CHECKHOST.md](docs/CHECKHOST.md)

### کاوشگرهای ISP ایران از طریق Globalping

پروژه همچنین از شبکهٔ عمومی و رایگان [Globalping](https://globalping.io) استفاده می‌کند که کاوشگرهای داوطلبانه‌ای روی خطوط واقعی ISP ایران دارد — از جمله تهران و یک کاوشگر در تبریز روی شبکهٔ موبایل همراه اول (MCI).

Globalping یک کلاینت HTTP واقعی روی کاوشگر اجرا می‌کند، بنابراین می‌توانیم از داخل ایران شاهد resolve واقعی DNS، اتصال TCP، **دست‌دادن TLS** و پاسخ HTTP باشیم. برای کانفیگ‌های TLS این شاهد قوی‌تر از یک بررسی سادهٔ پورت است.

با این حال نمی‌تواند کلاینت VLESS/VMess/Trojan/Shadowsocks/Hysteria2/TUIC را اجرا کند، پس هرگز اثبات نمی‌کند تونل کار می‌کند و IP خروجی تونل را نمی‌بیند. نتایج آن نیز تنها تشخیصی و هرگز منتشرشدنی نیستند. جزئیات: [docs/GLOBALPING.md](docs/GLOBALPING.md)

## سیاست کیفیت

`DISCOVERED` → `PENDING_IRAN_TEST` → `TESTING` → `WORKING` / `DEGRADED` / `FAILED` / `EXPIRED` / `DUPLICATE`

یک شکست: `DEGRADED` (هنوز منتشر می‌شود). دو شکست: حذف از خروجی.

## امنیت و حریم خصوصی

تمام کانفیگ‌ها عمومی هستند و ممکن است ناامن یا ناپایدار باشند. این پروژه هرگز رمز، توکن یا کلید خصوصی ذخیره نمی‌کند. جزئیات: [SECURITY.md](SECURITY.md)

## مشارکت

[CONTRIBUTING.md](CONTRIBUTING.md) — پیشنهاد منبع عمومی، گزارش کانفیگ خراب، بهبود کد، ترجمه.

## مجوز

[MIT](LICENSE)

</div>
