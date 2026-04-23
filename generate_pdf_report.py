#!/usr/bin/env python3
"""
OSANKA.health — Генератор PDF-отчёта диагностики.
Макет: Figma "Variant A — Card-based".
"""

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")


# ========== ПАЛИТРА (из Figma) ==========
COLOR_BRAND = "#c7db5e"      # лайм — шапка, норма
COLOR_NORM = "#62db5e"       # насыщенный зелёный — индикатор нормы
COLOR_OUT = "#ff7348"        # оранжевый — вне нормы
COLOR_CRIT = "#f9435e"       # красный — критично
COLOR_TEXT = "#1e2123"       # основной текст
COLOR_MUTED = "#8c8e93"      # подписи
COLOR_BG = "#f7f7f4"         # фон страницы
COLOR_CARD = "#ffffff"       # карточки
COLOR_BORDER = "#ededea"     # рамки
COLOR_TRACK = "#f1f1f1"      # трек прогресс-бара вне сегментов


# ========== ДАННЫЕ ДИАГНОСТИКИ ==========

# 1) Зоны мышечного напряжения из WebApp (index.html)
sample_zones = {
    "head": 1, "trap_l": 3, "trap_r": 2, "shoulder_l": 3, "shoulder_r": 2,
    "chest_l": 2, "chest_r": 1, "biceps_l": 1, "biceps_r": 1,
    "forearm_l": 1, "forearm_r": 1, "hand_l": 1, "hand_r": 1,
    "abs_l": 1, "abs_r": 1, "oblique_l": 2, "oblique_r": 1,
    "side_leg_l": 2, "side_leg_r": 1, "adductor_l": 1, "adductor_r": 1,
    "quad_l": 2, "quad_r": 1, "knee_l": 3, "knee_r": 1,
    "calf_l": 1, "calf_r": 1, "foot_l": 1, "foot_r": 1,
    "back_head": 2, "back_trap_l": 3, "back_trap_r": 2,
    "back_shoulder_l": 3, "back_shoulder_r": 2,
    "back_scapula_l": 4, "back_scapula_r": 2,
    "back_erector_l_new": 3, "back_erector_r_new": 2,
    "back_quadratus_l": 3, "back_quadratus_r": 2,
    "back_lowerback_l": 4, "back_lowerback_r": 2,
    "back_side_l": 2, "back_side_r": 1,
    "back_glute_l": 3, "back_glute_r": 1,
    "back_abductor_l": 2, "back_abductor_r": 1,
    "back_adductor_l_new": 1, "back_adductor_r_new": 1,
    "back_triceps_l": 1, "back_triceps_r": 1,
    "back_forearm_l": 1, "back_forearm_r": 1,
    "back_hand_l": 1, "back_hand_r": 1,
    "back_side_calf_l": 1, "back_side_calf_r": 1,
    "back_calf_l": 1, "back_calf_r": 1,
    "back_foot_l_new": 1, "back_foot_r_new": 1,
}

# 2) Метрики (формат: лейбл, значение, единица, min, max, norm_min, norm_max)
# min/max — границы шкалы; norm_min/max — норма
body_composition = [
    ("Рост",                    175.0, "см",  150, 200, 160, 190),
    ("Вес",                      78.0, "кг",  50,  120, 65,  85),
    ("ИМТ",                      25.5, "",    15,  40,  18.5, 24.9),
    ("Жировая масса",            22.0, "%",   5,   40,  15,  25),
    ("Масса скел. мускулатуры",  35.0, "кг",  20,  50,  36,  45),
]

strength = [
    ("Динамометрия правая",     42.0, "кг",  10,  70,  45,  65),
    ("Динамометрия левая",      38.0, "кг",  10,  70,  40,  60),
]

breathing = [
    ("Спирометрия",             4.2, "л",   2.0, 6.0, 3.5, 5.5),
]

posture_signs = [
    "Гипермобильность грудного отдела",
    "Сутулость",
]

complaints = "Боли в шейном отделе, периодические головные боли, дискомфорт в пояснице."

recommendations = [
    "ЛФК 3 раза в неделю",
    "Массаж курсом 10 сеансов",
]

# Оценки секций специалистом (0..max). Максимумы задаются здесь же.
# Общий балл = сумма / 100.
sections_ok = {
    "comp":     24,   # Состав тела
    "strength": 20,   # Сила
    "breath":   15,   # Дыхание
    "posture":  13,   # Осанка
}
sections_max = {"comp": 30, "strength": 25, "breath": 15, "posture": 30}

# Клиент
client_name = "Иванов Иван Иванович"
client_age = 27
specialist_name = "Кузнецов Иван"
diagnosis_date = "15.03.2026"


# ========== ПОДГОТОВКА SVG С РАСКРАШЕННЫМИ ЗОНАМИ ==========
with open(os.path.join(BASE_DIR, "index.html"), "r") as f:
    html_src = f.read()
svg_match = re.search(r'(<svg id="svg".*?</svg>)', html_src, re.DOTALL)
svg_raw = svg_match.group(1) if svg_match else ""


def svg_zone_style(lvl):
    """Цвет зоны по уровню 1..4."""
    return {
        1: ("rgba(199,219,94,0.55)", COLOR_BRAND),
        2: ("rgba(224,183,51,0.55)", "#e0b733"),
        3: ("rgba(255,115,72,0.55)", COLOR_OUT),
        4: ("rgba(249,67,94,0.55)", COLOR_CRIT),
    }[lvl]


def make_body_svg(zones_data, view="front"):
    out = svg_raw
    for zid, lvl in zones_data.items():
        fill, stroke = svg_zone_style(lvl)
        pattern = rf'<g id="{re.escape(zid)}" class="zone"'
        repl = f'<g id="{zid}" class="zone" style="fill:{fill};stroke:{stroke};stroke-width:1.2"'
        out = re.sub(pattern, repl, out)
    if view == "front":
        out = out.replace('viewBox="-250 0 900 700"', 'viewBox="-250 0 450 700"')
    else:
        out = out.replace('viewBox="-250 0 900 700"', 'viewBox="280 0 450 700"')
    return out


# ========== СТАТИСТИКА ==========
def calc_stats(data):
    by_level = {1: 0, 2: 0, 3: 0, 4: 0}
    for v in data.values():
        by_level[v] += 1
    return by_level


by_level = calc_stats(sample_zones)
total_zones = sum(by_level.values())


# ========== ПОДСЧЁТ ОБЩЕЙ ОЦЕНКИ ==========
def metric_in_norm(value, norm_min, norm_max):
    return norm_min <= value <= norm_max


total_ok = sum(sections_ok.values())
total_max = sum(sections_max.values())
overall_percent = round(total_ok / total_max * 100)

if overall_percent >= 85:
    overall_label = "Отличное"
elif overall_percent >= 70:
    overall_label = "Хорошее"
elif overall_percent >= 50:
    overall_label = "Удовлетворительное"
else:
    overall_label = "Требует внимания"


# ========== РЕНДЕР SVG-ПРОГРЕСС-БАРА ==========
def render_metric_bar(value, vmin, vmax, norm_min, norm_max, width=260, height=18):
    """SVG: трек с 3 зонами (оранж|зелёный|оранж) + кружок на позиции value.
    Цвет кружка зависит от того, в норме ли значение."""
    if vmax <= vmin:
        return ""
    in_norm = metric_in_norm(value, norm_min, norm_max)
    dot_color = COLOR_BRAND if in_norm else COLOR_OUT
    dot_stroke = "#8fa939" if in_norm else "#c85a33"

    track_h = 6
    track_y = (height - track_h) / 2
    track_r = track_h / 2

    # Позиции границ нормы (x-координаты)
    norm_x1 = (norm_min - vmin) / (vmax - vmin) * width
    norm_x2 = (norm_max - vmin) / (vmax - vmin) * width
    value_x = max(0, min(width, (value - vmin) / (vmax - vmin) * width))

    dot_r = 7

    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
      <!-- левый оранжевый сегмент -->
      <rect x="0" y="{track_y}" width="{norm_x1}" height="{track_h}" rx="{track_r}" fill="{COLOR_OUT}"/>
      <!-- зелёный (норма) -->
      <rect x="{norm_x1}" y="{track_y}" width="{norm_x2 - norm_x1}" height="{track_h}" rx="{track_r}" fill="{COLOR_BRAND}"/>
      <!-- правый оранжевый -->
      <rect x="{norm_x2}" y="{track_y}" width="{width - norm_x2}" height="{track_h}" rx="{track_r}" fill="{COLOR_OUT}"/>
      <!-- вертикальные разделители нормы -->
      <line x1="{norm_x1}" y1="2" x2="{norm_x1}" y2="{height - 2}" stroke="#b8bac0" stroke-width="1"/>
      <line x1="{norm_x2}" y1="2" x2="{norm_x2}" y2="{height - 2}" stroke="#b8bac0" stroke-width="1"/>
      <!-- кружок-маркер -->
      <circle cx="{value_x}" cy="{height/2}" r="{dot_r}" fill="{dot_color}" stroke="{dot_stroke}" stroke-width="1.5"/>
    </svg>'''


# ========== РЕНДЕР СТРОК МЕТРИК ==========
def render_metric_rows(metrics):
    rows = []
    for label, value, unit, vmin, vmax, nmin, nmax in metrics:
        in_norm = metric_in_norm(value, nmin, nmax)
        if in_norm:
            badge = f'<span class="badge badge-ok">норма</span>'
        elif value < nmin:
            badge = f'<span class="badge badge-warn">ниже нормы</span>'
        else:
            badge = f'<span class="badge badge-warn">выше нормы</span>'

        bar = render_metric_bar(value, vmin, vmax, nmin, nmax)
        value_str = f"{value:g}"
        if unit:
            value_str += f" {unit}"

        rows.append(f'''
        <div class="metric-row">
          <div class="metric-label">{label}</div>
          <div class="metric-bar">{bar}</div>
          <div class="metric-value">{value_str}</div>
          <div class="metric-badge">{badge}</div>
        </div>''')
    return "".join(rows)


# ========== РЕНДЕР ОБЩЕЙ ПРОГРЕСС-ПОЛОСКИ ==========
def render_overall_bar(percent):
    width = 540
    height = 12
    filled = width * percent / 100
    r = height / 2
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="0" width="{width}" height="{height}" rx="{r}" fill="{COLOR_TRACK}"/>
      <rect x="0" y="0" width="{filled}" height="{height}" rx="{r}" fill="{COLOR_BRAND}"/>
    </svg>'''


# ========== ЛОГОТИП (иконка-листок) ==========
LOGO_ICON = f'''<svg width="22" height="22" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
  <path d="M26 4c-8 0-18 4-18 16 0 5 3 8 8 8 10 0 14-10 14-20 0-2 0-4-1-4h-3zM11 26c1-4 4-9 9-12-3 5-6 9-9 12z"
        fill="{COLOR_TEXT}"/>
</svg>'''


# ========== HTML ==========
overall_bar = render_overall_bar(overall_percent)
front_svg = make_body_svg(sample_zones, "front")
back_svg = make_body_svg(sample_zones, "back")

html_report = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<style>
  @font-face {{
    font-family: 'Inter';
    font-weight: 300;
    src: url('file://{FONT_DIR}/Inter-Light.ttf') format('truetype');
  }}
  @font-face {{
    font-family: 'Inter';
    font-weight: 400;
    src: url('file://{FONT_DIR}/Inter-Regular.ttf') format('truetype');
  }}
  @font-face {{
    font-family: 'Inter';
    font-weight: 500;
    src: url('file://{FONT_DIR}/Inter-Medium.ttf') format('truetype');
  }}
  @font-face {{
    font-family: 'Inter';
    font-weight: 600;
    src: url('file://{FONT_DIR}/Inter-SemiBold.ttf') format('truetype');
  }}
  @font-face {{
    font-family: 'Inter';
    font-weight: 700;
    src: url('file://{FONT_DIR}/Inter-Bold.ttf') format('truetype');
  }}

  @page {{
    size: A4;
    margin: 20mm 16mm;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  html, body {{
    font-family: 'Inter', sans-serif;
    color: {COLOR_TEXT};
    background: white;
    font-size: 10px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}

  /* ===== ШАПКА ===== */
  .top-banner {{
    background: {COLOR_BRAND};
    border-radius: 14px;
    padding: 14px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }}

  .brand {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: {COLOR_TEXT};
  }}

  .top-banner .meta {{
    text-align: right;
    font-size: 9px;
    line-height: 1.5;
    color: {COLOR_TEXT};
  }}

  .top-banner .meta .title {{
    font-weight: 700;
    font-size: 10px;
  }}

  .client-info {{
    display: flex;
    justify-content: space-between;
    padding: 4px 20px 16px;
    font-size: 10px;
  }}

  .client-info .role {{
    color: {COLOR_MUTED};
    font-weight: 400;
    margin-right: 4px;
  }}

  .client-info .name {{
    color: {COLOR_TEXT};
    font-weight: 600;
  }}

  /* ===== КАРТОЧКА ===== */
  .card {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
  }}

  .card-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }}

  .card-title {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: {COLOR_TEXT};
  }}

  .card-score {{
    font-size: 10px;
    color: {COLOR_MUTED};
    font-weight: 500;
  }}

  /* ===== ОБЩАЯ ОЦЕНКА ===== */
  .overall {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 8px;
  }}

  .overall-head {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }}

  .overall-left .label {{
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: {COLOR_MUTED};
    margin-bottom: 4px;
  }}

  .overall-left .value {{
    font-size: 44px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -1.5px;
    color: {COLOR_TEXT};
  }}

  .overall-left .value .max {{
    font-size: 18px;
    font-weight: 300;
    color: {COLOR_MUTED};
    margin-left: 2px;
  }}

  .badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 9px;
    font-weight: 600;
    line-height: 1.2;
  }}

  .badge-ok {{
    background: rgba(199,219,94,0.35);
    color: #4d5c1a;
  }}

  .badge-warn {{
    background: rgba(255,115,72,0.18);
    color: #b84a1e;
  }}

  .badge-crit {{
    background: rgba(249,67,94,0.15);
    color: #b22233;
  }}

  .overall-bar {{
    margin-top: 14px;
  }}

  /* ===== СТРОКА МЕТРИКИ ===== */
  .metric-row {{
    display: flex;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #f4f4f1;
  }}

  .metric-row:last-child {{
    border-bottom: none;
  }}

  .metric-label {{
    flex: 0 0 36%;
    font-size: 10px;
    font-weight: 500;
    color: {COLOR_TEXT};
  }}

  .metric-bar {{
    flex: 1;
    display: flex;
    align-items: center;
  }}

  .metric-value {{
    flex: 0 0 70px;
    text-align: right;
    font-size: 11px;
    font-weight: 600;
    color: {COLOR_TEXT};
    padding: 0 12px 0 8px;
  }}

  .metric-badge {{
    flex: 0 0 95px;
    text-align: right;
  }}

  /* ===== ОСАНКА (список признаков) ===== */
  .posture-list {{
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}

  .posture-row {{
    display: flex;
    align-items: center;
    padding: 8px 12px;
    background: {COLOR_BG};
    border-radius: 8px;
  }}

  .posture-row .dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: {COLOR_OUT};
    margin-right: 10px;
  }}

  .posture-row .text {{
    font-size: 10px;
    color: {COLOR_TEXT};
    font-weight: 500;
  }}

  /* ===== ЖАЛОБЫ / РЕКОМЕНДАЦИИ ===== */
  .text-section {{
    text-align: center;
    margin: 12px 0 8px;
  }}

  .text-section .label {{
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {COLOR_MUTED};
    margin-bottom: 8px;
  }}

  .text-section .body {{
    font-size: 10px;
    color: {COLOR_TEXT};
    font-weight: 400;
    max-width: 80%;
    margin: 0 auto;
  }}

  .rec-list {{
    text-align: left;
    max-width: 80%;
    margin: 0 auto;
    font-size: 10px;
    color: {COLOR_TEXT};
  }}

  .rec-list li {{
    margin-bottom: 4px;
  }}

  /* ===== КАРТА ТЕЛА ===== */
  .body-map-wrap {{
    text-align: center;
    margin-top: 8px;
  }}

  .body-map-wrap .label {{
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {COLOR_MUTED};
    margin-bottom: 10px;
  }}

  .body-map-row {{
    display: flex;
    justify-content: center;
    gap: 8px;
  }}

  .body-map-row svg.body {{
    width: 110px;
    height: auto;
    background: {COLOR_BG};
    border-radius: 10px;
    padding: 6px;
  }}

  /* ===== ФОТО ===== */
  .photos {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    margin-top: 10px;
  }}

  .photo {{
    aspect-ratio: 3 / 4;
    background: {COLOR_TRACK};
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: {COLOR_MUTED};
    font-size: 10px;
    font-weight: 500;
    min-height: 180px;
  }}

  /* ===== ПОДВАЛ ===== */
  .footer {{
    display: flex;
    justify-content: space-between;
    padding: 14px 6px 0;
    border-top: 1px solid {COLOR_BORDER};
    margin-top: 14px;
    font-size: 8px;
    color: {COLOR_MUTED};
    font-weight: 400;
  }}
</style>
</head>
<body>

  <!-- ==== ШАПКА ==== -->
  <div class="top-banner">
    <div class="brand">{LOGO_ICON}<span>ОСАНКА</span></div>
    <div class="meta">
      <div class="title">Диагностический осмотр</div>
      <div>Диагност: {specialist_name}</div>
    </div>
  </div>

  <div class="client-info">
    <div>
      <span class="role">Клиент</span>
      <span class="name">{client_name} · {client_age} лет</span>
    </div>
    <div>
      <span class="role">Дата</span>
      <span class="name">{diagnosis_date}</span>
    </div>
  </div>

  <!-- ==== ОБЩАЯ ОЦЕНКА ==== -->
  <div class="overall">
    <div class="overall-head">
      <div class="overall-left">
        <div class="label">Общая оценка</div>
        <div class="value">{total_ok}<span class="max"> / {total_max}</span></div>
      </div>
      <div style="padding-top: 20px;">
        <span class="badge {'badge-ok' if overall_percent >= 70 else 'badge-warn'}">{overall_label}</span>
      </div>
    </div>
    <div class="overall-bar">{overall_bar}</div>
  </div>

  <!-- ==== СОСТАВ ТЕЛА ==== -->
  <div class="card">
    <div class="card-head">
      <div class="card-title">Состав тела</div>
      <div class="card-score">{sections_ok["comp"]} / {sections_max["comp"]}</div>
    </div>
    {render_metric_rows(body_composition)}
  </div>

  <!-- ==== СИЛА ==== -->
  <div class="card">
    <div class="card-head">
      <div class="card-title">Сила</div>
      <div class="card-score">{sections_ok["strength"]} / {sections_max["strength"]}</div>
    </div>
    {render_metric_rows(strength)}
  </div>

  <!-- ==== ДЫХАНИЕ ==== -->
  <div class="card">
    <div class="card-head">
      <div class="card-title">Дыхание</div>
      <div class="card-score">{sections_ok["breath"]} / {sections_max["breath"]}</div>
    </div>
    {render_metric_rows(breathing)}
  </div>

  <!-- ==== ОСАНКА ==== -->
  <div class="card">
    <div class="card-head">
      <div class="card-title">Осанка</div>
      <div class="card-score">{sections_ok["posture"]} / {sections_max["posture"]}</div>
    </div>
    <div class="posture-list">
      {''.join(f'<div class="posture-row"><span class="dot"></span><span class="text">{s}</span></div>' for s in posture_signs)}
    </div>
  </div>

  <!-- ==== ЖАЛОБЫ ==== -->
  <div class="text-section">
    <div class="label">Жалобы</div>
    <div class="body">{complaints}</div>
  </div>

  <!-- ==== РЕКОМЕНДАЦИИ ==== -->
  <div class="text-section">
    <div class="label">Рекомендации</div>
    <ol class="rec-list">
      {''.join(f'<li>{r}</li>' for r in recommendations)}
    </ol>
  </div>

  <!-- ==== КАРТА ПРОБЛЕМНЫХ ЗОН ==== -->
  <div class="body-map-wrap">
    <div class="label">Карта проблемных зон</div>
    <div class="body-map-row">
      <div class="body svg-wrap">{front_svg.replace('<svg id="svg"', '<svg class="body"')}</div>
      <div class="body svg-wrap">{back_svg.replace('<svg id="svg"', '<svg class="body"')}</div>
    </div>
  </div>

  <!-- ==== ФОТО ДИАГНОСТИКИ ==== -->
  <div class="text-section" style="margin-top: 18px;">
    <div class="label">Фото диагностики</div>
  </div>
  <div class="photos">
    <div class="photo">Фото 1</div>
    <div class="photo">Фото 2</div>
    <div class="photo">Фото 3</div>
    <div class="photo">Фото 4</div>
  </div>

  <!-- ==== ПОДВАЛ ==== -->
  <div class="footer">
    <span>Программа здорового тела · osanka.health</span>
    <span>Диагност: {specialist_name}</span>
  </div>

</body>
</html>'''

# ========== ГЕНЕРАЦИЯ PDF ==========
font_config = FontConfiguration()
output_path = os.path.join(BASE_DIR, "report_example.pdf")
HTML(string=html_report, base_url=BASE_DIR).write_pdf(output_path, font_config=font_config)
print(f"PDF создан: {output_path}")

html_path = os.path.join(BASE_DIR, "report_example.html")
with open(html_path, "w") as f:
    f.write(html_report)
print(f"HTML сохранён: {html_path}")
