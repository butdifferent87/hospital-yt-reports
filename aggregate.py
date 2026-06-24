#!/usr/bin/env python3
"""
병원 유튜브 월간 리포트 집계 스크립트.

매달 YouTube Studio CSV를 받아 리포트에 필요한 숫자를 한 번에 뽑는다.
손계산 오류 방지 + 매번 파이썬 재작성 방지용.

사용법:
  python3 aggregate.py \
    --this  "콘텐츠 2026-06-01_.../표 데이터.csv" --this-days 21 \
    --last  "콘텐츠 2026-05-01_.../표 데이터.csv" --last-days 31 \
    [--this-total "...6월.../총계.csv" --last-total "...5월.../총계.csv"]  # 같은창 비교
    [--lifetime "콘텐츠 2024-..._.../표 데이터.csv"]                        # 카테고리·에버그린
    [--channel hwang]                                                      # 카테고리 규칙 선택

출력: 하루평균 스냅샷 / 형식별(쇼츠·롱폼) 끝까지 본 비율 / (lifetime 시) 카테고리·에버그린.
"""
import csv, argparse, sys
from collections import defaultdict

# ── 카테고리 분류 규칙 (채널별). 새 채널은 여기 추가. ──
CHEJIL = ['소음인','소양인','태음인','태양인','사상체질','체질','다이어트','살이','살찌','감기',
          '기침','수면','잠이','잠은','못 일어','피로','무기력','우울','욱할','멘탈','난방','겨울',
          '식탐','추위','냉증의','스트레스','면역력','소화','삼계탕','보약','수험생','속이','속쓰림','피곤','몸보신']
def cat_hwang(t):
    if '쇼그렌' in t: return '쇼그렌'
    if '말초신경병' in t: return '말초신경병증'
    if '중증근무력' in t: return '중증근무력증'
    if any(k in t for k in ['대상포진','신경통','람세이헌트','안면마비','신경차단']): return '대상포진'
    if any(k in t for k in CHEJIL): return '체질·건강일반'
    return '기타질환'
CAT_RULES = {'hwang': cat_hwang}  # 'mun' 등 추가 가능. 없으면 카테고리 생략.

def load(path):
    """표 데이터.csv → [(title, pub_year, length_s, views, watch_h, subs, imp, ctr), ...], 합계행"""
    rows, total = [], None
    with open(path, encoding='utf-8') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if not row: continue
            if row[0] == '합계': total = row; continue
            try:
                L = int(row[3]) if row[3].strip() else 9999
                v = int(row[4] or 0); w = float(row[5] or 0); s = int(row[6] or 0)
                imp = int(row[7] or 0); ctr = float(row[8] or 0)
            except (ValueError, IndexError):
                continue
            pub = row[2].strip().strip('"')
            yr = pub.split(', ')[-1] if ',' in pub else '?'
            rows.append((row[1], yr, L, v, w, s, imp, ctr))
    return rows, total

def daily_total(path):
    d = {}
    with open(path, encoding='utf-8') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) >= 2:
                try: d[row[0]] = int(row[1])
                except ValueError: pass
    return d

def fmt_split(rows, days, label):
    print(f"\n=== {label} (÷{days}일, 하루평균) ===")
    cats = {'쇼츠': [], '롱폼': []}
    for (_, _, L, v, w, s, imp, ctr) in rows:
        cats['쇼츠' if L <= 90 else '롱폼'].append((v, w, s, imp, ctr, L))
    for fm in ['쇼츠', '롱폼']:
        vs = cats[fm]
        if not vs: continue
        v = sum(x[0] for x in vs); w = sum(x[1] for x in vs); s = sum(x[2] for x in vs)
        imp = sum(x[3] for x in vs)
        den = sum(x[0]*x[5] for x in vs if x[5] < 9999)         # 조회×길이
        watched = w*3600/den*100 if den else 0                  # 끝까지 본 비율 근사
        print(f"  {fm}: 조회/일 {v/days:.0f} | 끝까지 {watched:.0f}% | 신규구독/일 {s/days:.2f} | 노출/일 {imp/days:.0f}")

def channel_snapshot(total, days, label):
    # 합계행: [_,_,_,_, 조회, 시청h, 구독, 노출, CTR]
    v = int(total[4]); w = float(total[5]); s = int(total[6]); imp = int(total[7])
    print(f"  [{label}] 조회/일 {v/days:.0f} | 신규구독/일 {s/days:.2f} | 노출/일 {imp/days:.0f} | 시청/일 {w/days:.1f}h | CTR {total[8]}%")

def category_breakdown(rows, catfn):
    print("\n=== 카테고리 (누적 전체) ===")
    ag = defaultdict(lambda: [0,0,0,0,0.0])  # n, views, subs, imp, clicks
    for (t,_,L,v,w,s,imp,ctr) in rows:
        a = ag[(catfn(t), '쇼츠' if L<=90 else '롱폼')]; a[0]+=1; a[1]+=v; a[2]+=s; a[3]+=imp; a[4]+=imp*ctr/100
    totv = sum(a[1] for a in ag.values())
    print(f"{'주제':14}{'형식':5}{'편':>4}{'조회':>8}{'조회%':>6}{'CTR':>6}{'노출/편':>8}{'구독/편':>7}")
    for (c,fm), a in sorted(ag.items(), key=lambda x:-x[1][1]):
        n,v,s,imp,cl = a; ctr = cl/imp*100 if imp else 0
        print(f"{c:14}{fm:5}{n:>4}{v:>8,}{v/totv*100:>5.0f}%{ctr:>5.1f}%{imp/n:>8.0f}{s/n:>7.1f}")

def evergreen(rows, catfn=None):
    print("\n=== 에버그린 (게시 연도별 누적 조회) ===")
    byyr = defaultdict(int); tot = 0
    for (_,yr,_,v,_,_,_,_) in rows:
        byyr[yr]+=v; tot+=v
    for yr in sorted(byyr, reverse=True):
        print(f"  {yr}: {byyr[yr]:,} ({byyr[yr]/tot*100:.0f}%)")

def same_window(this_total, last_total):
    if not (this_total and last_total): return
    t = daily_total(this_total); l = daily_total(last_total)
    this_days = sorted(int(k[8:10]) for k in t)
    if not this_days: return
    cutoff = max(this_days)
    tv = sum(t.values())
    lv = sum(v for k,v in l.items() if int(k[8:10]) <= cutoff)
    print(f"\n=== 같은 창 비교 (1~{cutoff}일) ===")
    print(f"  지난달 {lv:,} → 이번달 {tv:,} = {(tv-lv)/lv*100:+.1f}%" if lv else "  (지난달 데이터 부족)")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--this', required=True); p.add_argument('--this-days', type=int, required=True)
    p.add_argument('--last'); p.add_argument('--last-days', type=int)
    p.add_argument('--this-total'); p.add_argument('--last-total')
    p.add_argument('--lifetime'); p.add_argument('--channel')
    a = p.parse_args()

    this_rows, this_total = load(a.this)
    print("="*52)
    if this_total: channel_snapshot(this_total, a.this_days, "이번달 채널전체")
    fmt_split(this_rows, a.this_days, "이번달")
    if a.last:
        last_rows, last_total = load(a.last)
        if last_total: channel_snapshot(last_total, a.last_days, "지난달 채널전체")
        fmt_split(last_rows, a.last_days, "지난달")
    same_window(a.this_total, a.last_total)
    if a.lifetime:
        life_rows, _ = load(a.lifetime)
        catfn = CAT_RULES.get(a.channel)
        if catfn: category_breakdown(life_rows, catfn)
        evergreen(life_rows)
    print("="*52)

if __name__ == '__main__':
    main()
