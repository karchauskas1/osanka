#!/usr/bin/env python3
"""
OSANKA.health — Генератор PDF-отчёта диагностики.
Пример: как может выглядеть выгрузка результатов диагностики в PDF.
"""

from weasyprint import HTML
from datetime import datetime

# ========== ПРИМЕР ДАННЫХ ДИАГНОСТИКИ ==========
# Это данные, которые приходят из WebApp (index.html) при сохранении.
# Уровни: 1 = норма (зелёный), 2 = лёгкое (жёлтый), 3 = среднее (оранжевый), 4 = выраженное (красный)

sample_diagnosis = {
    # --- ПЕРЕД ---
    "head": 1,
    "trap_l": 3, "trap_r": 2,
    "shoulder_l": 3, "shoulder_r": 2,
    "chest_l": 2, "chest_r": 1,
    "biceps_l": 1, "biceps_r": 1,
    "forearm_l": 1, "forearm_r": 1,
    "hand_l": 1, "hand_r": 1,
    "abs_l": 1, "abs_r": 1,
    "oblique_l": 2, "oblique_r": 1,
    "side_leg_l": 2, "side_leg_r": 1,
    "adductor_l": 1, "adductor_r": 1,
    "quad_l": 2, "quad_r": 1,
    "knee_l": 3, "knee_r": 1,
    "calf_l": 1, "calf_r": 1,
    "foot_l": 1, "foot_r": 1,
    # --- СПИНА ---
    "back_head": 2,
    "back_trap_l": 3, "back_trap_r": 2,
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

# Читаемые названия зон
zone_names = {
    "head": "Голова", "trap_l": "Трапеция Л", "trap_r": "Трапеция П",
    "shoulder_l": "Плечо Л", "shoulder_r": "Плечо П",
    "chest_l": "Грудная Л", "chest_r": "Грудная П",
    "biceps_l": "Бицепс Л", "biceps_r": "Бицепс П",
    "forearm_l": "Предплечье Л", "forearm_r": "Предплечье П",
    "hand_l": "Кисть Л", "hand_r": "Кисть П",
    "abs_l": "Пресс Л", "abs_r": "Пресс П",
    "oblique_l": "Косые Л", "oblique_r": "Косые П",
    "side_leg_l": "Бок бедра Л", "side_leg_r": "Бок бедра П",
    "adductor_l": "Аддуктор Л", "adductor_r": "Аддуктор П",
    "quad_l": "Квадрицепс Л", "quad_r": "Квадрицепс П",
    "knee_l": "Колено Л", "knee_r": "Колено П",
    "calf_l": "Голень Л", "calf_r": "Голень П",
    "foot_l": "Стопа Л", "foot_r": "Стопа П",
    "back_head": "Затылок",
    "back_trap_l": "Трапеция Л (спина)", "back_trap_r": "Трапеция П (спина)",
    "back_shoulder_l": "Плечо Л (спина)", "back_shoulder_r": "Плечо П (спина)",
    "back_scapula_l": "Лопатка Л", "back_scapula_r": "Лопатка П",
    "back_erector_l_new": "Разгибатель Л", "back_erector_r_new": "Разгибатель П",
    "back_quadratus_l": "Квадратная Л", "back_quadratus_r": "Квадратная П",
    "back_lowerback_l": "Поясница Л", "back_lowerback_r": "Поясница П",
    "back_side_l": "Бок Л (спина)", "back_side_r": "Бок П (спина)",
    "back_glute_l": "Ягодица Л", "back_glute_r": "Ягодица П",
    "back_abductor_l": "Абдуктор Л", "back_abductor_r": "Абдуктор П",
    "back_adductor_l_new": "Аддуктор Л (спина)", "back_adductor_r_new": "Аддуктор П (спина)",
    "back_triceps_l": "Трицепс Л", "back_triceps_r": "Трицепс П",
    "back_forearm_l": "Предплечье Л (спина)", "back_forearm_r": "Предплечье П (спина)",
    "back_hand_l": "Кисть Л (спина)", "back_hand_r": "Кисть П (спина)",
    "back_side_calf_l": "Бок голени Л", "back_side_calf_r": "Бок голени П",
    "back_calf_l": "Голень Л (спина)", "back_calf_r": "Голень П (спина)",
    "back_foot_l_new": "Стопа Л (спина)", "back_foot_r_new": "Стопа П (спина)",
}

level_labels = {1: "Норма", 2: "Лёгкое напряжение", 3: "Умеренное напряжение", 4: "Выраженное напряжение"}
level_colors = {1: "#2ECC71", 2: "#F1C40F", 3: "#E67E22", 4: "#E74C3C"}
level_bg = {1: "#E8F8F0", 2: "#FEF9E7", 3: "#FDF2E9", 4: "#FDEDEC"}

# SVG fill/stroke по уровню
def svg_fill(lvl):
    return {
        1: ("rgba(46,204,113,0.45)", "#2ECC71"),
        2: ("rgba(241,196,15,0.45)", "#F1C40F"),
        3: ("rgba(230,126,34,0.45)", "#E67E22"),
        4: ("rgba(231,76,60,0.45)", "#E74C3C"),
    }[lvl]


# ========== ПОДГОТОВКА SVG С РАСКРАШЕННЫМИ ЗОНАМИ ==========
# Читаем оригинальный SVG из index.html
with open("/home/user/osanka/index.html", "r") as f:
    html_content = f.read()

import re

# Извлекаем SVG
svg_match = re.search(r'(<svg id="svg".*?</svg>)', html_content, re.DOTALL)
svg_raw = svg_match.group(1) if svg_match else ""

# Функция: создаём отдельные SVG для переда и спины
def make_body_svg(zones_data, side="front"):
    """Строим SVG только с нужными зонами, раскрашенными по уровням."""

    # Фронтальные зоны (без back_ префикса)
    front_ids = [k for k in zones_data if not k.startswith("back_")]
    back_ids = [k for k in zones_data if k.startswith("back_")]

    target_ids = front_ids if side == "front" else back_ids

    # Для каждой зоны подставляем цвет
    svg_out = svg_raw
    for zone_id, lvl in zones_data.items():
        fill, stroke = svg_fill(lvl)
        # Заменяем стиль зоны по id
        pattern = rf'(<g id="{re.escape(zone_id)}" class="zone")'
        replacement = rf'<g id="{zone_id}" class="zone" style="fill:{fill};stroke:{stroke};stroke-width:1.5"'
        svg_out = re.sub(pattern, replacement, svg_out)

    return svg_out


# Разделяем SVG на два: перед (viewBox для левой части) и спина (viewBox для правой)
def get_front_svg(zones_data):
    svg = make_body_svg(zones_data, "front")
    # Фронт: viewBox фокус на левую часть SVG
    svg = svg.replace('viewBox="-250 0 900 700"', 'viewBox="-250 0 450 700"')
    return svg

def get_back_svg(zones_data):
    svg = make_body_svg(zones_data, "back")
    # Спина: viewBox фокус на правую часть SVG
    svg = svg.replace('viewBox="-250 0 900 700"', 'viewBox="280 0 450 700"')
    return svg


# ========== СТАТИСТИКА ==========
def calc_stats(data):
    total = len(data)
    by_level = {1: 0, 2: 0, 3: 0, 4: 0}
    for v in data.values():
        by_level[v] += 1

    problem_zones = {k: v for k, v in data.items() if v >= 3}
    attention_zones = {k: v for k, v in data.items() if v == 2}

    return total, by_level, problem_zones, attention_zones

total, by_level, problem_zones, attention_zones = calc_stats(sample_diagnosis)

# ========== ТАБЛИЦА ПРОБЛЕМНЫХ ЗОН ==========
def make_problem_table(zones, data, compact=False):
    if not zones:
        return '<p style="color:#999;font-style:italic;font-size:9px;">Проблемных зон не обнаружено</p>'

    items = sorted(zones.items(), key=lambda x: -x[1])
    pad = "4px 8px" if compact else "5px 10px"
    fs = "9px" if compact else "10px"

    if compact and len(items) > 6:
        # Две колонки для компактности
        mid = (len(items) + 1) // 2
        col1 = items[:mid]
        col2 = items[mid:]

        def make_col(items_list):
            rows = ""
            for zone_id, lvl in items_list:
                name = zone_names.get(zone_id, zone_id)
                color = level_colors[lvl]
                bg = level_bg[lvl]
                dot = f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{color};margin-right:4px;"></span>'
                rows += f'<tr style="background:{bg};"><td style="padding:{pad};border-bottom:1px solid #eee;font-size:{fs};">{dot}{name}</td></tr>'
            return f'<table style="width:100%;border-collapse:collapse;">{rows}</table>'

        return f'<div style="display:flex;gap:12px;"><div style="flex:1;">{make_col(col1)}</div><div style="flex:1;">{make_col(col2)}</div></div>'

    rows = ""
    for zone_id, lvl in items:
        name = zone_names.get(zone_id, zone_id)
        color = level_colors[lvl]
        bg = level_bg[lvl]
        label = level_labels[lvl]
        dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};margin-right:5px;"></span>'
        rows += f'''
        <tr style="background:{bg};">
            <td style="padding:{pad};border-bottom:1px solid #eee;font-size:{fs};">{name}</td>
            <td style="padding:{pad};border-bottom:1px solid #eee;font-size:{fs};">{dot}{label}</td>
        </tr>'''

    return f'''
    <table style="width:100%;border-collapse:collapse;">
        <thead>
            <tr style="background:#f7f7f7;">
                <th style="padding:{pad};text-align:left;border-bottom:2px solid #ddd;font-weight:600;font-size:{fs};">Зона</th>
                <th style="padding:{pad};text-align:left;border-bottom:2px solid #ddd;font-weight:600;font-size:{fs};">Статус</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>'''


# ========== ГЕНЕРАЦИЯ HTML ==========
client_name = "Иванова Мария Сергеевна"
specialist_name = "Александр Карчаускас"
diagnosis_date = "24 марта 2026"
session_number = "3"

front_svg = get_front_svg(sample_diagnosis)
back_svg = get_back_svg(sample_diagnosis)

html_report = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<style>
  @page {{
    size: A4;
    margin: 0;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #2D3436;
    background: white;
    line-height: 1.5;
  }}

  .page {{
    width: 210mm;
    min-height: 297mm;
    padding: 0;
    page-break-after: always;
    position: relative;
    overflow: hidden;
  }}

  .page:last-child {{
    page-break-after: avoid;
  }}

  /* ===== HEADER ===== */
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 28px 36px 24px;
    position: relative;
  }}

  .header::after {{
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #2ECC71, #F1C40F, #E67E22, #E74C3C);
  }}

  .logo {{
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
  }}

  .logo span {{
    color: #2ECC71;
  }}

  .logo-sub {{
    font-size: 11px;
    color: rgba(255,255,255,0.6);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 2px;
  }}

  .doc-title {{
    font-size: 13px;
    color: rgba(255,255,255,0.85);
    margin-top: 12px;
    font-weight: 500;
  }}

  /* ===== CLIENT INFO ===== */
  .client-info {{
    display: flex;
    justify-content: space-between;
    padding: 16px 36px;
    background: #f8f9fa;
    border-bottom: 1px solid #e9ecef;
    font-size: 11.5px;
  }}

  .client-info .label {{
    color: #999;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 2px;
  }}

  .client-info .value {{
    font-weight: 600;
    color: #2D3436;
  }}

  /* ===== CONTENT ===== */
  .content {{
    padding: 20px 36px;
  }}

  .section-title {{
    font-size: 14px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 2px solid #2ECC71;
    display: inline-block;
  }}

  /* ===== BODY MAP ===== */
  .body-map-container {{
    display: flex;
    justify-content: center;
    align-items: flex-start;
    gap: 10px;
    margin: 8px 0 16px;
  }}

  .body-map {{
    text-align: center;
  }}

  .body-map-label {{
    font-size: 10px;
    font-weight: 600;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 4px;
  }}

  .body-map svg {{
    width: 200px;
    height: auto;
    background: #fafafa;
    border-radius: 12px;
    border: 1px solid #eee;
  }}

  /* ===== LEGEND ===== */
  .legend {{
    display: flex;
    justify-content: center;
    gap: 20px;
    margin: 12px 0 16px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 8px;
  }}

  .legend-item {{
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    color: #555;
  }}

  .legend-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }}

  /* ===== STATS BAR ===== */
  .stats-bar {{
    display: flex;
    gap: 12px;
    margin: 12px 0 20px;
  }}

  .stat-card {{
    flex: 1;
    text-align: center;
    padding: 12px 8px;
    border-radius: 10px;
    border: 1px solid #eee;
  }}

  .stat-number {{
    font-size: 22px;
    font-weight: 800;
  }}

  .stat-label {{
    font-size: 9px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
  }}

  /* ===== FOOTER ===== */
  .footer {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 12px 36px;
    background: #f8f9fa;
    border-top: 1px solid #e9ecef;
    font-size: 9px;
    color: #aaa;
    display: flex;
    justify-content: space-between;
  }}

  /* ===== PAGE 2 SPECIFIC ===== */
  .zone-group {{
    margin-bottom: 16px;
  }}

  .zone-group-title {{
    font-size: 12px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 6px;
    padding-left: 8px;
    border-left: 3px solid #2ECC71;
  }}

  .recommendations {{
    background: linear-gradient(135deg, #f8f9fa, #e8f8f0);
    border-radius: 12px;
    padding: 16px 20px;
    margin-top: 16px;
  }}

  .recommendations h3 {{
    font-size: 13px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 10px;
  }}

  .recommendations li {{
    font-size: 11px;
    color: #444;
    margin-bottom: 6px;
    padding-left: 4px;
  }}

  .signature-block {{
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid #ddd;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}

  .signature-line {{
    width: 180px;
    border-bottom: 1px solid #999;
    margin-bottom: 4px;
  }}

  .signature-label {{
    font-size: 9px;
    color: #999;
  }}

  .qr-placeholder {{
    width: 60px;
    height: 60px;
    background: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 7px;
    color: #bbb;
    text-align: center;
  }}

  .watermark {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 80px;
    font-weight: 900;
    color: rgba(46, 204, 113, 0.04);
    letter-spacing: 10px;
    pointer-events: none;
    white-space: nowrap;
  }}
</style>
</head>
<body>

<!-- ==================== СТРАНИЦА 1 ==================== -->
<div class="page">
  <div class="watermark">OSANKA</div>

  <div class="header">
    <div class="logo">OSANKA<span>.health</span></div>
    <div class="logo-sub">Студия коррекции осанки</div>
    <div class="doc-title">Отчёт функциональной диагностики тела</div>
  </div>

  <div class="client-info">
    <div>
      <div class="label">Клиент</div>
      <div class="value">{client_name}</div>
    </div>
    <div>
      <div class="label">Дата диагностики</div>
      <div class="value">{diagnosis_date}</div>
    </div>
    <div>
      <div class="label">Сессия №</div>
      <div class="value">{session_number}</div>
    </div>
    <div>
      <div class="label">Специалист</div>
      <div class="value">{specialist_name}</div>
    </div>
  </div>

  <!-- Статистика -->
  <div class="content">
    <div class="stats-bar">
      <div class="stat-card" style="background:#E8F8F0;border-color:#2ECC71;">
        <div class="stat-number" style="color:#2ECC71;">{by_level[1]}</div>
        <div class="stat-label">Норма</div>
      </div>
      <div class="stat-card" style="background:#FEF9E7;border-color:#F1C40F;">
        <div class="stat-number" style="color:#F1C40F;">{by_level[2]}</div>
        <div class="stat-label">Лёгкое</div>
      </div>
      <div class="stat-card" style="background:#FDF2E9;border-color:#E67E22;">
        <div class="stat-number" style="color:#E67E22;">{by_level[3]}</div>
        <div class="stat-label">Умеренное</div>
      </div>
      <div class="stat-card" style="background:#FDEDEC;border-color:#E74C3C;">
        <div class="stat-number" style="color:#E74C3C;">{by_level[4]}</div>
        <div class="stat-label">Выраженное</div>
      </div>
    </div>

    <!-- Карта тела -->
    <div class="section-title">Карта тела — визуальная диагностика</div>

    <div class="body-map-container">
      <div class="body-map">
        <div class="body-map-label">Вид спереди</div>
        {front_svg}
      </div>
      <div class="body-map">
        <div class="body-map-label">Вид сзади</div>
        {back_svg}
      </div>
    </div>

    <div class="legend">
      <div class="legend-item">
        <div class="legend-dot" style="background:#2ECC71;"></div>
        Норма
      </div>
      <div class="legend-item">
        <div class="legend-dot" style="background:#F1C40F;"></div>
        Лёгкое напряжение
      </div>
      <div class="legend-item">
        <div class="legend-dot" style="background:#E67E22;"></div>
        Умеренное напряжение
      </div>
      <div class="legend-item">
        <div class="legend-dot" style="background:#E74C3C;"></div>
        Выраженное напряжение
      </div>
    </div>
  </div>

  <div class="footer">
    <span>OSANKA.health — Отчёт диагностики</span>
    <span>Страница 1 из 2</span>
    <span>Сгенерировано: {datetime.now().strftime("%d.%m.%Y %H:%M")}</span>
  </div>
</div>

<!-- ==================== СТРАНИЦА 2 ==================== -->
<div class="page">
  <div class="watermark">OSANKA</div>

  <div class="header" style="padding:18px 36px 16px;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div>
        <div class="logo" style="font-size:20px;">OSANKA<span>.health</span></div>
      </div>
      <div style="text-align:right;">
        <div style="font-size:11px;opacity:0.7;">{client_name} · {diagnosis_date}</div>
      </div>
    </div>
  </div>

  <div class="content">
    <!-- Проблемные зоны -->
    <div class="zone-group">
      <div class="section-title" style="border-color:#E74C3C;">Зоны повышенного внимания</div>
      <p style="font-size:9.5px;color:#666;margin-bottom:6px;">
        Зоны с умеренным и выраженным напряжением, требующие приоритетной работы
      </p>
      {make_problem_table(problem_zones, sample_diagnosis)}
    </div>

    <!-- Зоны с лёгким напряжением -->
    <div class="zone-group" style="margin-top:12px;">
      <div class="section-title" style="border-color:#F1C40F;">Зоны с лёгким напряжением</div>
      <p style="font-size:9.5px;color:#666;margin-bottom:6px;">
        Области, которые стоит мониторить — пока без активного вмешательства
      </p>
      {make_problem_table(attention_zones, sample_diagnosis, compact=True)}
    </div>

    <!-- Рекомендации -->
    <div class="recommendations" style="margin-top:12px;padding:12px 16px;">
      <h3 style="font-size:12px;">Рекомендации специалиста</h3>
      <ol style="padding-left:16px;">
        <li style="font-size:9.5px;margin-bottom:4px;"><strong>Левая лопатка и поясница</strong> — выраженное напряжение. Рекомендуется курс миофасциального релиза 2 раза в неделю, акцент на левую сторону.</li>
        <li style="font-size:9.5px;margin-bottom:4px;"><strong>Трапециевидная мышца</strong> — асимметрия между правой и левой стороной. Необходима работа с шейно-воротниковой зоной.</li>
        <li style="font-size:9.5px;margin-bottom:4px;"><strong>Левое колено</strong> — умеренное напряжение, возможна компенсаторная нагрузка из-за перекоса таза. Контроль через 2 недели.</li>
        <li style="font-size:9.5px;margin-bottom:4px;"><strong>Общая рекомендация:</strong> ежедневная утренняя разминка 10–15 мин, акцент на мобильность грудного отдела и растяжку левой стороны тела.</li>
      </ol>
    </div>

    <!-- Подпись -->
    <div class="signature-block" style="margin-top:16px;padding-top:12px;">
      <div>
        <div class="signature-line" style="width:150px;"></div>
        <div class="signature-label">Подпись специалиста</div>
        <div style="font-size:10px;margin-top:3px;font-weight:600;">{specialist_name}</div>
      </div>
      <div style="text-align:center;">
        <div class="qr-placeholder" style="width:50px;height:50px;">
          QR<br>Запись
        </div>
      </div>
      <div>
        <div class="signature-line" style="width:150px;"></div>
        <div class="signature-label">Подпись клиента</div>
      </div>
    </div>

    <!-- Дисклеймер -->
    <div style="margin-top:12px;padding:8px 12px;background:#f8f9fa;border-radius:6px;border-left:3px solid #ddd;">
      <p style="font-size:8px;color:#999;line-height:1.5;">
        Данный отчёт носит информационный характер и не является медицинским заключением.
        Результаты диагностики отражают состояние мышечного тонуса на момент осмотра.
        При наличии болевого синдрома рекомендуется консультация профильного врача.
        © {datetime.now().year} OSANKA.health — Студия коррекции осанки
      </p>
    </div>
  </div>

  <div class="footer">
    <span>OSANKA.health — Отчёт диагностики</span>
    <span>Страница 2 из 2</span>
    <span>Сгенерировано: {datetime.now().strftime("%d.%m.%Y %H:%M")}</span>
  </div>
</div>

</body>
</html>'''

# ========== ГЕНЕРАЦИЯ PDF ==========
output_path = "/home/user/osanka/report_example.pdf"
HTML(string=html_report).write_pdf(output_path)
print(f"PDF создан: {output_path}")

# Также сохраним HTML для просмотра
html_path = "/home/user/osanka/report_example.html"
with open(html_path, "w") as f:
    f.write(html_report)
print(f"HTML сохранён: {html_path}")
