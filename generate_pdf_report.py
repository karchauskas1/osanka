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
        return '<p style="color:#b0b8c4;font-style:italic;font-size:9px;">Проблемных зон не обнаружено</p>'

    items = sorted(zones.items(), key=lambda x: -x[1])
    pad = "3px 8px" if compact else "4px 10px"
    fs = "8px" if compact else "9px"

    if compact and len(items) > 6:
        mid = (len(items) + 1) // 2
        col1 = items[:mid]
        col2 = items[mid:]

        def make_col(items_list):
            rows = ""
            for i, (zone_id, lvl) in enumerate(items_list):
                name = zone_names.get(zone_id, zone_id)
                color = level_colors[lvl]
                bg = "#ffffff" if i % 2 == 0 else "#f9fafb"
                dot = f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{color};margin-right:6px;box-shadow:0 1px 2px rgba(0,0,0,0.15);"></span>'
                rows += f'<tr style="background:{bg};"><td style="padding:{pad};border-bottom:1px solid #eef0f2;font-size:{fs};color:#3d4852;font-weight:500;">{dot}{name}</td></tr>'
            return f'<table style="width:100%;border-collapse:collapse;border-radius:8px;overflow:hidden;border:1px solid #eef0f2;">{rows}</table>'

        return f'<div style="display:flex;gap:12px;"><div style="flex:1;">{make_col(col1)}</div><div style="flex:1;">{make_col(col2)}</div></div>'

    rows = ""
    for i, (zone_id, lvl) in enumerate(items):
        name = zone_names.get(zone_id, zone_id)
        color = level_colors[lvl]
        label = level_labels[lvl]
        bg = "#ffffff" if i % 2 == 0 else "#f9fafb"
        dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};margin-right:6px;box-shadow:0 1px 2px rgba(0,0,0,0.15);"></span>'
        rows += f'''
        <tr style="background:{bg};">
            <td style="padding:{pad};border-bottom:1px solid #eef0f2;font-size:{fs};color:#1a1a2e;font-weight:600;">{name}</td>
            <td style="padding:{pad};border-bottom:1px solid #eef0f2;font-size:{fs};color:#3d4852;font-weight:500;">{dot}{label}</td>
        </tr>'''

    return f'''
    <table style="width:100%;border-collapse:collapse;border-radius:10px;overflow:hidden;border:1.5px solid #e4e8ec;">
        <thead>
            <tr style="background:linear-gradient(180deg,#f6f8fa,#eef0f2);">
                <th style="padding:{pad};text-align:left;border-bottom:2px solid #d0d4d8;font-weight:700;font-size:{fs};color:#555;letter-spacing:0.3px;">Зона</th>
                <th style="padding:{pad};text-align:left;border-bottom:2px solid #d0d4d8;font-weight:700;font-size:{fs};color:#555;letter-spacing:0.3px;">Статус</th>
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

# Расчёт общего балла здоровья (0-100)
health_score = round(100 - ((by_level[2] * 1 + by_level[3] * 3 + by_level[4] * 5) / total) * 20)
score_color = "#2ECC71" if health_score >= 80 else "#F1C40F" if health_score >= 60 else "#E67E22" if health_score >= 40 else "#E74C3C"
score_label = "Отлично" if health_score >= 80 else "Хорошо" if health_score >= 60 else "Требует внимания" if health_score >= 40 else "Критично"

# SVG для кругового индикатора
def make_score_ring(score, color):
    r = 40
    circ = 2 * 3.14159 * r
    offset = circ * (1 - score / 100)
    return f'''<svg width="100" height="100" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="{r}" fill="none" stroke="#eef2f7" stroke-width="8"/>
      <circle cx="50" cy="50" r="{r}" fill="none" stroke="{color}" stroke-width="8"
        stroke-dasharray="{circ}" stroke-dashoffset="{offset}"
        stroke-linecap="round" transform="rotate(-90 50 50)"/>
      <text x="50" y="46" text-anchor="middle" font-size="22" font-weight="800" fill="{color}">{score}</text>
      <text x="50" y="60" text-anchor="middle" font-size="8" fill="#999">баллов</text>
    </svg>'''

score_ring = make_score_ring(health_score, score_color)

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
    background: linear-gradient(135deg, #0d1117 0%, #161b22 40%, #1a2332 100%);
    color: white;
    padding: 30px 40px 26px;
    position: relative;
  }}

  .header::before {{
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 200px;
    height: 100%;
    background: radial-gradient(ellipse at top right, rgba(46,204,113,0.15), transparent 70%);
  }}

  .header::after {{
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #2ECC71 0%, #2ECC71 60%, #F1C40F 75%, #E67E22 88%, #E74C3C 100%);
  }}

  .logo {{
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -0.5px;
    position: relative;
  }}

  .logo span {{
    color: #2ECC71;
  }}

  .logo-sub {{
    font-size: 10px;
    color: rgba(255,255,255,0.45);
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: 3px;
    font-weight: 500;
  }}

  .doc-title {{
    font-size: 14px;
    color: rgba(255,255,255,0.9);
    margin-top: 14px;
    font-weight: 400;
    letter-spacing: 0.3px;
  }}

  /* ===== CLIENT INFO ===== */
  .client-info {{
    display: flex;
    justify-content: space-between;
    padding: 18px 40px;
    background: linear-gradient(180deg, #f6f8fa 0%, #ffffff 100%);
    border-bottom: 1px solid #e8ecf0;
    font-size: 11.5px;
  }}

  .client-info .label {{
    color: #a0a8b4;
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 3px;
    font-weight: 600;
  }}

  .client-info .value {{
    font-weight: 700;
    color: #1a1a2e;
    font-size: 12px;
  }}

  /* ===== CONTENT ===== */
  .content {{
    padding: 22px 40px;
  }}

  .section-title {{
    font-size: 14px;
    font-weight: 700;
    color: #0d1117;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 3px solid #2ECC71;
    display: inline-block;
    letter-spacing: -0.2px;
  }}

  /* ===== SCORE + STATS ===== */
  .score-stats-row {{
    display: flex;
    gap: 16px;
    margin: 8px 0 22px;
    align-items: stretch;
  }}

  .score-card {{
    background: linear-gradient(145deg, #f8fffe, #edf7f0);
    border: 1.5px solid #d4edda;
    border-radius: 14px;
    padding: 16px 20px;
    text-align: center;
    min-width: 130px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }}

  .score-card .score-title {{
    font-size: 9px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
    font-weight: 600;
  }}

  .score-card .score-verdict {{
    font-size: 11px;
    font-weight: 700;
    margin-top: 4px;
  }}

  .stats-grid {{
    flex: 1;
    display: flex;
    gap: 10px;
  }}

  .stat-card {{
    flex: 1;
    text-align: center;
    padding: 14px 8px 12px;
    border-radius: 12px;
    position: relative;
    overflow: hidden;
  }}

  .stat-card::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
  }}

  .stat-number {{
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -1px;
  }}

  .stat-label {{
    font-size: 8px;
    color: #777;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 2px;
    font-weight: 600;
  }}

  .stat-sublabel {{
    font-size: 7px;
    color: #bbb;
    margin-top: 1px;
  }}

  /* ===== BODY MAP ===== */
  .body-map-container {{
    display: flex;
    justify-content: center;
    align-items: flex-start;
    gap: 16px;
    margin: 10px 0 16px;
  }}

  .body-map {{
    text-align: center;
  }}

  .body-map-label {{
    font-size: 9px;
    font-weight: 700;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 6px;
  }}

  .body-map svg {{
    width: 210px;
    height: auto;
    background: linear-gradient(180deg, #fafbfc 0%, #f0f2f5 100%);
    border-radius: 14px;
    border: 1.5px solid #e4e8ec;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  }}

  /* ===== LEGEND ===== */
  .legend {{
    display: flex;
    justify-content: center;
    gap: 24px;
    margin: 14px 0 0;
    padding: 10px 16px;
    background: #f6f8fa;
    border-radius: 10px;
    border: 1px solid #eef0f2;
  }}

  .legend-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 9px;
    color: #555;
    font-weight: 500;
  }}

  .legend-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.15);
  }}

  /* ===== FOOTER ===== */
  .footer {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 10px 40px;
    background: #f6f8fa;
    border-top: 1px solid #e8ecf0;
    font-size: 8px;
    color: #b0b8c4;
    display: flex;
    justify-content: space-between;
    letter-spacing: 0.3px;
  }}

  /* ===== PAGE 2 ===== */
  .zone-group {{
    margin-bottom: 10px;
  }}

  .recommendations {{
    background: linear-gradient(145deg, #f8fffe, #edf7f0);
    border: 1.5px solid #d4edda;
    border-radius: 12px;
    padding: 12px 16px;
    margin-top: 10px;
    position: relative;
  }}

  .recommendations::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: #2ECC71;
    border-radius: 12px 12px 0 0;
  }}

  .recommendations h3 {{
    font-size: 11px;
    font-weight: 700;
    color: #0d1117;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .recommendations li {{
    font-size: 9px;
    color: #3d4852;
    margin-bottom: 5px;
    padding-left: 2px;
    line-height: 1.45;
  }}

  .signature-block {{
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1.5px solid #e4e8ec;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}

  .signature-line {{
    width: 150px;
    border-bottom: 1.5px solid #c0c8d0;
    margin-bottom: 4px;
  }}

  .signature-label {{
    font-size: 7.5px;
    color: #a0a8b4;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600;
  }}

  .qr-placeholder {{
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #f0f2f5, #e4e8ec);
    border: 1.5px solid #d0d4d8;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 6.5px;
    color: #b0b8c4;
    text-align: center;
    font-weight: 600;
  }}

  .watermark {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 90px;
    font-weight: 900;
    color: rgba(46, 204, 113, 0.03);
    letter-spacing: 12px;
    pointer-events: none;
    white-space: nowrap;
  }}

  /* ===== DISCLAIMER ===== */
  .disclaimer {{
    margin-top: 6px;
    padding: 6px 10px;
    background: #f6f8fa;
    border-radius: 8px;
    border-left: 3px solid #d0d4d8;
  }}

  .disclaimer p {{
    font-size: 7px;
    color: #a0a8b4;
    line-height: 1.5;
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

  <div class="content">
    <!-- Общий балл + статистика -->
    <div class="score-stats-row">
      <div class="score-card">
        <div class="score-title">Общий балл</div>
        {score_ring}
        <div class="score-verdict" style="color:{score_color};">{score_label}</div>
      </div>
      <div class="stats-grid">
        <div class="stat-card" style="background:linear-gradient(180deg,#e8f8f0,#d4edda);border:1.5px solid #c3e6cb;">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;background:#2ECC71;border-radius:12px 12px 0 0;"></div>
          <div class="stat-number" style="color:#27ae60;">{by_level[1]}</div>
          <div class="stat-label">Норма</div>
          <div class="stat-sublabel">{round(by_level[1]/total*100)}%</div>
        </div>
        <div class="stat-card" style="background:linear-gradient(180deg,#fef9e7,#fdebd0);border:1.5px solid #f9e79f;">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;background:#F1C40F;border-radius:12px 12px 0 0;"></div>
          <div class="stat-number" style="color:#d4a017;">{by_level[2]}</div>
          <div class="stat-label">Лёгкое</div>
          <div class="stat-sublabel">{round(by_level[2]/total*100)}%</div>
        </div>
        <div class="stat-card" style="background:linear-gradient(180deg,#fdf2e9,#fbe0c4);border:1.5px solid #f5cba7;">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;background:#E67E22;border-radius:12px 12px 0 0;"></div>
          <div class="stat-number" style="color:#d35400;">{by_level[3]}</div>
          <div class="stat-label">Умеренное</div>
          <div class="stat-sublabel">{round(by_level[3]/total*100)}%</div>
        </div>
        <div class="stat-card" style="background:linear-gradient(180deg,#fdedec,#f5c6cb);border:1.5px solid #f1948a;">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;background:#E74C3C;border-radius:12px 12px 0 0;"></div>
          <div class="stat-number" style="color:#c0392b;">{by_level[4]}</div>
          <div class="stat-label">Выраженное</div>
          <div class="stat-sublabel">{round(by_level[4]/total*100)}%</div>
        </div>
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
        Лёгкое
      </div>
      <div class="legend-item">
        <div class="legend-dot" style="background:#E67E22;"></div>
        Умеренное
      </div>
      <div class="legend-item">
        <div class="legend-dot" style="background:#E74C3C;"></div>
        Выраженное
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

  <div class="header" style="padding:12px 40px 10px;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div class="logo" style="font-size:18px;">OSANKA<span>.health</span></div>
      <div style="text-align:right;font-size:10px;opacity:0.6;font-weight:400;">{client_name} · {diagnosis_date}</div>
    </div>
  </div>

  <div class="content" style="padding:16px 40px;">
    <!-- Проблемные зоны -->
    <div class="zone-group">
      <div class="section-title" style="border-color:#E74C3C;font-size:12px;margin-bottom:6px;padding-bottom:4px;">Зоны повышенного внимания</div>
      <p style="font-size:8px;color:#888;margin-bottom:5px;font-weight:500;">
        Зоны с умеренным и выраженным напряжением, требующие приоритетной работы
      </p>
      {make_problem_table(problem_zones, sample_diagnosis)}
    </div>

    <!-- Зоны с лёгким напряжением -->
    <div class="zone-group" style="margin-top:8px;">
      <div class="section-title" style="border-color:#F1C40F;font-size:12px;margin-bottom:6px;padding-bottom:4px;">Зоны с лёгким напряжением</div>
      <p style="font-size:8px;color:#888;margin-bottom:5px;font-weight:500;">
        Области для мониторинга — без активного вмешательства
      </p>
      {make_problem_table(attention_zones, sample_diagnosis, compact=True)}
    </div>

    <!-- Рекомендации -->
    <div class="recommendations">
      <h3>Рекомендации специалиста</h3>
      <ol style="padding-left:18px;">
        <li><strong>Левая лопатка и поясница</strong> — выраженное напряжение. Рекомендуется курс миофасциального релиза 2 раза в неделю, акцент на левую сторону.</li>
        <li><strong>Трапециевидная мышца</strong> — асимметрия между правой и левой стороной. Необходима работа с шейно-воротниковой зоной.</li>
        <li><strong>Левое колено</strong> — умеренное напряжение, возможна компенсаторная нагрузка из-за перекоса таза. Контроль через 2 недели.</li>
        <li><strong>Общая рекомендация:</strong> ежедневная утренняя разминка 10–15 мин, акцент на мобильность грудного отдела и растяжку левой стороны тела.</li>
      </ol>
    </div>

    <!-- Подпись -->
    <div class="signature-block">
      <div>
        <div class="signature-line"></div>
        <div class="signature-label">Подпись специалиста</div>
        <div style="font-size:10px;margin-top:4px;font-weight:700;color:#0d1117;">{specialist_name}</div>
      </div>
      <div style="text-align:center;">
        <div class="qr-placeholder">
          QR<br>Запись
        </div>
      </div>
      <div>
        <div class="signature-line"></div>
        <div class="signature-label">Подпись клиента</div>
      </div>
    </div>

    <!-- Дисклеймер -->
    <div class="disclaimer">
      <p>
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
