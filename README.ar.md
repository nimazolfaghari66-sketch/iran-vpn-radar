<div align="center" dir="rtl">

# 📡 رادار VPN إيران

**الاكتشاف والاختبار والنشر التلقائي لاشتراكات VPN المجانية لمستخدمي إيران**

</div>

<div dir="rtl">

**اللغات:** [فارسی (الأساسية)](README.md) · [English](README.en.md) · **العربية** · [中文](README.zh.md) · [Русский](README.ru.md) · [Español](README.es.md)

> ⚠️ **ترجمة.** اللغة الأساسية للمشروع هي الفارسية ([README.md](README.md)). هذا الملف ترجمة موثّقة.

## ⚠️ حالة الاختبار الإيراني

لا يُنشَر أي إعداد على أنه «موثَّق من إيران» إلا إذا اختُبِر فعلياً بواسطة مجسّ موجود داخل إيران. وإلى أن يتم ربط المجسّ:

* تبقى جميع الإعدادات في حالة `PENDING_IRAN_TEST`.
* تبقى ملفات الاشتراك المنشورة **فارغة**.
* لا يتم أبداً تقديم نتيجة أجنبية أو مصطنعة كاختبار إيراني.

## ما هذا المشروع؟

نظام مفتوح المصدر وآلي يقوم بما يلي:

1. **يكتشف** المصادر العامة التي تنشر إعدادات VPN مجانية.
2. **يستخرج** الإعدادات ويوحّدها و**يزيل التكرار**.
3. **يختبرها من داخل إيران** باستخدام عملاء بروتوكول حقيقيين.
4. **يحذف** الإعدادات المعطوبة والمكررة.
5. **ينشر** ملفات اشتراك منفصلة لكل بروتوكول.
6. **يكرر** هذه الدورة **كل ساعتين**.

## البروتوكولات المدعومة

| البروتوكول | ملف الاشتراك |
|-----------|--------------|
| الكل | `subscriptions/all` |
| VLESS | `subscriptions/vless` |
| VMess | `subscriptions/vmess` |
| Trojan | `subscriptions/trojan` |
| Shadowsocks | `subscriptions/shadowsocks` |
| Hysteria2 | `subscriptions/hysteria2` |
| TUIC | `subscriptions/tuic` |
| SOCKS | `subscriptions/socks` |
| HTTP/HTTPS | `subscriptions/http` |

## روابط الاشتراك

```
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/all
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vmess
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/trojan
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/shadowsocks
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/hysteria2
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/tuic
```

يتوفر إصدار Base64 من كل ملف باللاحقة `.b64`.

## الاختبار الإيراني

يجب تشغيل المجسّ على مضيف داخل إيران:

```bash
export IRAN_PROBE_TOKEN="سر-مشترك-قوي"
python3 probe/probe_agent.py --port 8787
```

ثم المحرك المركزي:

```bash
export IRAN_RADAR_PROBE_MODE=remote
export IRAN_PROBE_URL="https://probe.example.ir:8787"
export IRAN_PROBE_TOKEN="نفس-السر"
```

مراحل الاختبار: DNS، الوصول إلى الخادم، المصافحة، النفق، الإنترنت عبر النفق، زمن الاستجابة، تنزيل محدود، الاستقرار.

## سياسة الجودة

`DISCOVERED` → `PENDING_IRAN_TEST` → `TESTING` → `WORKING` / `DEGRADED` / `FAILED` / `EXPIRED` / `DUPLICATE`

فشل واحد: `DEGRADED` (يُبقى). فشلان متتاليان: يُحذف من الناتج.

## الأمن والخصوصية

جميع الإعدادات **عامة** وقد تكون غير آمنة أو غير مستقرة. لا يخزّن هذا المشروع أو ينشر كلمات مرور أو رموزاً أو مفاتيح خاصة. راجع [SECURITY.md](SECURITY.md).

## المساهمة

[CONTRIBUTING.md](CONTRIBUTING.md) — اقترح مصادر عامة جديدة، أبلغ عن إعداد معطوب، حسّن الكود، ترجم الوثائق.

## الترخيص

[MIT](LICENSE)

</div>
