"""Automatic README subscription section.

The landing READMEs publish one canonical subscription table whose "Active
configs" column must always match the real contents of the files under
``subscriptions/iran-priority/``. Counting is therefore derived from the files
themselves, using the *same* de-duplication and validity rules as the generator
(``normalize.parse_uri`` -> ``Config.fingerprint``), so a displayed number can
never drift from what a client would actually download.

Each README carries a marker-delimited block. Only the text between the markers
is rewritten, so unrelated edits elsewhere in a README are never touched.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import config as cfg
from .normalize import parse_uri

TIER = "iran-priority"
START = "<!-- radar:subscriptions:start -->"
END = "<!-- radar:subscriptions:end -->"

# Protocol order shown in the table, with the display names used in every language.
ROWS: tuple[tuple[str, str], ...] = (
    ("vless", "VLESS"),
    ("vmess", "VMess"),
    ("trojan", "Trojan"),
    ("shadowsocks", "Shadowsocks"),
    ("hysteria2", "Hysteria2"),
    ("tuic", "TUIC"),
    ("socks", "SOCKS"),
    ("http", "HTTP"),
)

# README file -> language code. Persian is the primary language (README.md).
README_LANGS: tuple[tuple[str, str], ...] = (
    ("README.md", "fa"),
    ("README.fa.md", "fa"),
    ("README.en.md", "en"),
    ("README.ar.md", "ar"),
    ("README.zh.md", "zh"),
    ("README.ru.md", "ru"),
    ("README.es.md", "es"),
)

L = {
    "fa": {
        "heading": "## 📥 لینک‌های اشتراک",
        "intro": "لینک زیر را کپی کنید و در کلاینت وی‌پی‌ان خود اضافه کنید. تمام شد.",
        "all_label": "همهٔ پروتکل‌ها (all)",
        "headers": ("پروتکل", "لینک اشتراک", "تعداد فعال"),
        "b64": "نسخهٔ Base64 هر فایل با پسوند `.b64` در دسترس است. اگر کلاینت شما لینک Base64 می‌خواهد، از این نسخه استفاده کنید.",
        "tier": "این لینک‌ها از ردهٔ «اولویت ایران» هستند: تونل واقعی برقرار شده و شواهد دسترسی از شبکهٔ ایران وجود دارد؛ اما از داخل ایران تأیید نشده‌اند.",
        "unavailable": "⚠️ ناموجود",
    },
    "en": {
        "heading": "## 📥 Subscription links",
        "intro": "Copy a link below and add it to your VPN client. That's it.",
        "all_label": "All protocols (all)",
        "headers": ("Protocol", "Subscription link", "Active configs"),
        "b64": "A Base64 variant of each file is available with a `.b64` suffix. Use it if your client expects a Base64 subscription.",
        "tier": "These links are the Iran-priority tier: a real tunnel was established and there is Iranian network reachability evidence, but they are not verified from inside Iran.",
        "unavailable": "⚠️ unavailable",
    },
    "ar": {
        "heading": "## 📥 روابط الاشتراك",
        "intro": "انسخ الرابط وأضفه إلى عميل VPN الخاص بك. هذا كل شيء.",
        "all_label": "جميع البروتوكولات (all)",
        "headers": ("البروتوكول", "رابط الاشتراك", "التهيئات النشطة"),
        "b64": "يتوفر إصدار Base64 من كل ملف باللاحقة `.b64`.",
        "tier": "هذه الروابط من فئة «أولوية إيران»: تم إنشاء نفق حقيقي وتوجد أدلة على إمكانية الوصول من شبكة إيرانية، لكنها غير مُتحقَّق منها من داخل إيران.",
        "unavailable": "⚠️ غير متاح",
    },
    "zh": {
        "heading": "## 📥 订阅链接",
        "intro": "复制下面的链接，添加到你的 VPN 客户端即可。",
        "all_label": "所有协议（all）",
        "headers": ("协议", "订阅链接", "有效配置数"),
        "b64": "每个文件的 Base64 版本带有 `.b64` 后缀。",
        "tier": "这些链接属于「伊朗优先」层级：已建立真实隧道并有伊朗网络可达性证据，但未在伊朗境内验证。",
        "unavailable": "⚠️ 不可用",
    },
    "ru": {
        "heading": "## 📥 Ссылки на подписки",
        "intro": "Скопируйте ссылку и добавьте её в свой VPN-клиент. Готово.",
        "all_label": "Все протоколы (all)",
        "headers": ("Протокол", "Ссылка на подписку", "Активных конфигураций"),
        "b64": "Версия в Base64 доступна с суффиксом `.b64`.",
        "tier": "Эти ссылки относятся к уровню «приоритет Ирана»: реальный туннель установлен и есть свидетельства доступности из иранской сети, но они не проверены изнутри Ирана.",
        "unavailable": "⚠️ недоступно",
    },
    "es": {
        "heading": "## 📥 Enlaces de suscripción",
        "intro": "Copia un enlace y añádelo a tu cliente VPN. Eso es todo.",
        "all_label": "Todos los protocolos (all)",
        "headers": ("Protocolo", "Enlace de suscripción", "Configuraciones activas"),
        "b64": "Cada archivo tiene una variante Base64 con el sufijo `.b64`.",
        "tier": "Estos enlaces son del nivel «prioridad Irán»: se estableció un túnel real y hay evidencia de accesibilidad desde una red iraní, pero no están verificados desde dentro de Irán.",
        "unavailable": "⚠️ no disponible",
    },
}


@dataclass
class CountReport:
    """Result of counting one subscription file."""

    count: int = 0
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class ReadmeResult:
    counts: dict[str, int] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    updated: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems

    def to_dict(self) -> dict:
        return {
            "counts": self.counts,
            "errors": self.errors,
            "updated": self.updated,
            "skipped": self.skipped,
            "problems": self.problems,
        }


def count_file(path: Path) -> CountReport:
    """Count unique, valid configurations in a subscription file.

    A file that exists but is empty is a valid ``0``. A file that is missing or
    unreadable is reported as an error instead of a misleading number.
    """
    if not path.exists():
        return CountReport(0, "file is missing")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return CountReport(0, f"file is unreadable: {exc}")
    seen: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        conf = parse_uri(line)
        if conf is None:
            continue
        seen.add(conf.fingerprint)
    return CountReport(len(seen), None)


def count_tier(sub_dir: Path, tier: str = TIER) -> tuple[dict[str, int], dict[str, str]]:
    """Count the ``all`` file plus each protocol file under ``<sub_dir>/<tier>``."""
    tier_dir = Path(sub_dir) / tier
    counts: dict[str, int] = {}
    errors: dict[str, str] = {}

    all_report = count_file(tier_dir / "all")
    counts["all"] = all_report.count
    if not all_report.ok:
        errors["all"] = all_report.error or "unavailable"

    for proto, _display in ROWS:
        report = count_file(tier_dir / proto)
        counts[proto] = report.count
        if not report.ok:
            errors[proto] = report.error or "unavailable"
    return counts, errors


def render_block(
    lang: str,
    raw_base: str,
    counts: dict[str, int],
    errors: dict[str, str],
) -> str:
    """Render the marker-delimited subscription section for one language."""
    strings = L[lang]
    tier_base = f"{raw_base}/subscriptions/{TIER}"

    def link(name: str) -> str:
        url = f"{tier_base}/{name}"
        return f"[{url}]({url})"

    def cell(name: str) -> str:
        if name in errors:
            return strings["unavailable"]
        return str(counts.get(name, 0))

    lines: list[str] = [START, strings["heading"], "", strings["intro"], ""]
    lines.append(f"**{strings['all_label']}:** {link('all')}")
    lines.append("")
    header = strings["headers"]
    lines.append(f"| {header[0]} | {header[1]} | {header[2]} |")
    lines.append("|---|---|---|")
    for proto, display in ROWS:
        lines.append(f"| **{display}** | {link(proto)} | {cell(proto)} |")
    lines.append("")
    lines.append(f"> {strings['b64']}")
    lines.append("")
    lines.append(f"> {strings['tier']}")
    lines.append(END)
    return "\n".join(lines)


def update_readme_text(text: str, block: str) -> tuple[str, str]:
    """Replace the marker block in ``text``.

    Returns ``(new_text, status)`` where status is ``updated``, ``unchanged`` or
    ``no-markers``. A README without markers is left untouched so unrelated
    content is never clobbered.
    """
    start = text.find(START)
    end = text.find(END)
    if start == -1 or end == -1 or end < start:
        return text, "no-markers"
    end += len(END)
    new_text = text[:start] + block + text[end:]
    if new_text == text:
        return text, "unchanged"
    return new_text, "updated"


def update_readmes(settings) -> ReadmeResult:
    """Recount the iran-priority files and refresh every landing README."""
    result = ReadmeResult()
    counts, errors = count_tier(settings.sub_dir)
    result.counts = counts
    result.errors = errors
    for name, message in errors.items():
        result.problems.append(f"{TIER}/{name}: {message}")

    raw_base = settings.raw_base
    for filename, lang in README_LANGS:
        path = Path(settings.root) / filename
        if not path.exists():
            result.problems.append(f"{filename}: missing")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            result.problems.append(f"{filename}: unreadable ({exc})")
            continue
        block = render_block(lang, raw_base, counts, errors)
        new_text, status = update_readme_text(text, block)
        if status == "no-markers":
            result.problems.append(f"{filename}: subscription markers not found")
            continue
        if status == "updated":
            path.write_text(new_text, encoding="utf-8", newline="\n")
            result.updated.append(filename)
        else:
            result.skipped.append(filename)
    return result


def readme_files(root: Path) -> list[Path]:
    """Existing landing README files (for publishing)."""
    return [Path(root) / name for name, _lang in README_LANGS if (Path(root) / name).exists()]
