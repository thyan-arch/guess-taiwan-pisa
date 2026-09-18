# -*- coding: utf-8 -*-
"""PISA 科學主測年（2006 / 2015 / 2025）資料庫建置
來源：OECD PISA 官方 Annex B 資料表（見 raw/SOURCES.md）
輸出：data/pisa_long.csv, data/pisa.json, data/indicators.json
"""
import os, json, csv, math, re
import openpyxl, xlrd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW  = os.path.join(ROOT, 'raw')
OUT  = os.path.join(ROOT, 'data')

# ---------------------------------------------------------------- 讀表工具
_cache = {}
def _rows_xlsx(fn, sheet):
    key = ('x', fn, sheet)
    if key not in _cache:
        wb = openpyxl.load_workbook(os.path.join(RAW, fn), read_only=True, data_only=True)
        _cache[key] = [list(r) for r in wb[sheet].iter_rows(values_only=True)]
    return _cache[key]

def _rows_xls(fn, sheet):
    key = ('o', fn, sheet)
    if key not in _cache:
        b = xlrd.open_workbook(os.path.join(RAW, fn))
        sh = b.sheet_by_name(sheet)
        _cache[key] = [[sh.cell_value(i, j) for j in range(sh.ncols)] for i in range(sh.nrows)]
    return _cache[key]

SKIP = {'oecd', 'partners', 'oecd total', 'oecd average', 'oecd average-30',
        'oecd average-35', 'partner countries/economies', ''}
NOTE_HINTS = ('note', 'source', 'informa', '*', '1.', '2.', 'symbol', 'a note',
              'c:', 'm:', 'w:', 'countries and econ', 'for all tables',
              'kosovo:', 'this designation')
AGGREGATES = {'oecd total', 'oecd average', 'eu total', 'european union total',
              'eu average', 'oecd average-30', 'oecd average-35', 'total'}
_FOOT = re.compile(r'[\u00b9\u00b2\u00b3\u2070-\u209f]|\s*\d(?:\s*,\s*\d)*$')

def _num(v):
    if v is None: return None
    if isinstance(v, (int, float)):
        return None if (isinstance(v, float) and math.isnan(v)) else float(v)
    s = str(v).strip()
    if s in ('', 'm', 'c', 'w', 'a', '†', '..'): return None
    try: return float(s.replace(',', ''))
    except ValueError: return None

def read_table(fn, sheet, cols, anchor_names=('OECD average', 'Australia', 'Argentina', 'OECD')):
    """回傳 {country: {colname: value}} 及 oecd_average。cols = {name: col_index}"""
    rows = _rows_xls(fn, sheet) if fn.endswith('.xls') else _rows_xlsx(fn, sheet)
    start = None
    for i, r in enumerate(rows):
        a = str(r[0]).strip() if r and r[0] is not None else ''
        if a in anchor_names:
            start = i; break
    if start is None:
        raise RuntimeError(f'找不到起始列: {fn}/{sheet}')
    data, oecd = {}, {}
    for r in rows[start:]:
        if not r or r[0] is None: continue
        name = str(r[0]).strip()
        low = name.lower()
        if not name: continue
        if low.startswith(NOTE_HINTS) and low != 'oecd average': break
        if len(name) > 45 or ':' in name: break
        name = _FOOT.sub('', name).strip()
        low = name.lower()
        if low in AGGREGATES and low != 'oecd average': continue
        vals = {}
        for cn, ci in cols.items():
            vals[cn] = _num(r[ci]) if ci < len(r) else None
        if low == 'oecd average':
            oecd = vals; continue
        if low in SKIP: continue
        if all(v is None for v in vals.values()): continue
        data[name] = vals
    return data, oecd

# ---------------------------------------------------------------- 國名正規化
ALIAS = {
    'Chinese Taipei': 'Chinese Taipei', 'Chinese Taipei ': 'Chinese Taipei',
    'Czech Republic': 'Czechia', 'Slovak Republic': 'Slovak Republic',
    'Korea': 'Korea', 'Republic of Korea': 'Korea',
    'Hong Kong-China': 'Hong Kong (China)', 'Hong Kong (China)': 'Hong Kong (China)',
    'Macao-China': 'Macao (China)', 'Macao (China)': 'Macao (China)',
    'B-S-J-G (China)': 'B-S-J-Z (China)', 'B-S-J-Z (China)': 'B-S-J-Z (China)',
    'Shanghai-China': 'Shanghai (China)',
    'Russian Federation': 'Russia', 'Russia': 'Russia',
    'Turkey': 'Türkiye', 'Türkiye': 'Türkiye',
    'United States*': 'United States', 'United States': 'United States',
    'Canada*': 'Canada', 'Netherlands*': 'Netherlands', 'New Zealand*': 'New Zealand',
    'Norway*': 'Norway', 'Albania*': 'Albania',
    'Viet Nam': 'Viet Nam', 'Vietnam': 'Viet Nam',
    'Serbia': 'Serbia', 'Republic of Serbia': 'Serbia',
    'Moldova': 'Moldova', 'Republic of Moldova': 'Moldova',
    'North Macedonia': 'North Macedonia', 'FYROM': 'North Macedonia',
    'Macedonia': 'North Macedonia',
    'Slovenia': 'Slovenia', 'Chile': 'Chile',
    'United Kingdom': 'United Kingdom', 'Great Britain': 'United Kingdom',
    'Brunei Darussalam': 'Brunei Darussalam',
    'Dominican Republic': 'Dominican Republic',
    'United Arab Emirates': 'United Arab Emirates',
    'Baku (Azerbaijan)': 'Baku (Azerbaijan)',
}
def canon(name):
    n = str(name).strip()
    if n in ALIAS: return ALIAS[n]
    n = n.rstrip('*').strip()          # 抽樣警示標記
    return ALIAS.get(n, n)

ZH = {
 'Chinese Taipei':'臺灣','Japan':'日本','Korea':'韓國','Singapore':'新加坡',
 'Hong Kong (China)':'香港','Macao (China)':'澳門','B-S-J-Z (China)':'中國四省市',
 'Shanghai (China)':'上海','Viet Nam':'越南','Thailand':'泰國','Malaysia':'馬來西亞',
 'Indonesia':'印尼','Philippines':'菲律賓','Cambodia':'柬埔寨','Brunei Darussalam':'汶萊',
 'Mongolia':'蒙古','Kazakhstan':'哈薩克','Uzbekistan':'烏茲別克','Kyrgyzstan':'吉爾吉斯',
 'Azerbaijan':'亞塞拜然','Georgia':'喬治亞','Armenia':'亞美尼亞','Israel':'以色列',
 'Türkiye':'土耳其','Jordan':'約旦','Qatar':'卡達','United Arab Emirates':'阿聯',
 'Saudi Arabia':'沙烏地阿拉伯','Lebanon':'黎巴嫩','Palestinian Authority':'巴勒斯坦',
 'Morocco':'摩洛哥','Tunisia':'突尼西亞','Egypt':'埃及','Kenya':'肯亞','Rwanda':'盧安達',
 'Zambia':'尚比亞','Mauritius':'模里西斯','Australia':'澳洲','New Zealand':'紐西蘭',
 'United States':'美國','Canada':'加拿大','United Kingdom':'英國','Ireland':'愛爾蘭',
 'France':'法國','Germany':'德國','Netherlands':'荷蘭','Belgium':'比利時',
 'Switzerland':'瑞士','Austria':'奧地利','Luxembourg':'盧森堡','Denmark':'丹麥',
 'Sweden':'瑞典','Norway':'挪威','Finland':'芬蘭','Iceland':'冰島','Estonia':'愛沙尼亞',
 'Latvia':'拉脫維亞','Lithuania':'立陶宛','Poland':'波蘭','Czechia':'捷克',
 'Slovak Republic':'斯洛伐克','Hungary':'匈牙利','Slovenia':'斯洛維尼亞',
 'Croatia':'克羅埃西亞','Serbia':'塞爾維亞','Montenegro':'蒙特內哥羅','Albania':'阿爾巴尼亞',
 'North Macedonia':'北馬其頓','Bulgaria':'保加利亞','Romania':'羅馬尼亞','Greece':'希臘',
 'Italy':'義大利','Spain':'西班牙','Portugal':'葡萄牙','Malta':'馬爾他','Cyprus':'賽普勒斯',
 'Moldova':'摩爾多瓦','Ukraine':'烏克蘭','Ukrainian regions (17 of 27)':'烏克蘭（17區）',
 'Russia':'俄羅斯','Kosovo':'科索沃','Chile':'智利','Uruguay':'烏拉圭','Brazil':'巴西',
 'Argentina':'阿根廷','Colombia':'哥倫比亞','Peru':'秘魯','Mexico':'墨西哥',
 'Costa Rica':'哥斯大黎加','Panama':'巴拿馬','Paraguay':'巴拉圭','Ecuador':'厄瓜多',
 'Dominican Republic':'多明尼加','El Salvador':'薩爾瓦多','Guatemala':'瓜地馬拉',
 'Jamaica':'牙買加','Trinidad and Tobago':'千里達','Liechtenstein':'列支敦斯登',
 'Dushanbe (Tajikistan)':'杜尚別（塔吉克）','Kurdistan Region (Iraq)':'伊拉克庫德斯坦',
 'Baku (Azerbaijan)':'巴庫（亞塞拜然）','Algeria':'阿爾及利亞',
 'CABA (Argentina)':'布宜諾斯艾利斯市','Massachusetts (USA)':'麻州（美國）',
 'North Carolina (USA)':'北卡羅來納州（美國）','Puerto Rico (USA)':'波多黎各',
 'Miranda-Venezuela':'米蘭達（委內瑞拉）','Perm(Russian Federation)':'彼爾姆（俄羅斯）',
 'Chinese Taipei ':'臺灣','Hong Kong':'香港','Macao':'澳門',
}

# ---------------------------------------------------------------- 指標定義
# kind: index=標準化指數(OECD=0,SD=1) / score=PISA分數 / pct=百分比 / hours / points10
# hib (higher is better)：True/False/None(中性)
S = []   # spec list
def spec(**kw): S.append(kw); return kw

# ===== 2025 =====
F25P, F25S, F25G, F25A, F25C4, F25C5 = ('b1_2_2025.xlsx','b1_3_2025.xlsx',
    'b1_4_2025.xlsx','b1_6_2025.xlsx','b1_7_2025.xlsx','b1_8_2025.xlsx')
spec(id='sci_mean', cycle=2025, file=F25P, sheet='Table I.B1.2a.1', col=1, kind='score',
     group='成績', en='Science mean score', zh='科學平均分數', hib=True)
spec(id='sci_sd', cycle=2025, file=F25P, sheet='Table I.B1.2a.1', col=3, kind='score',
     group='成績', en='Science score standard deviation', zh='科學分數標準差（分數落差）', hib=None)
spec(id='sci_p10', cycle=2025, file=F25P, sheet='Table I.B1.2a.1', col=5, kind='score',
     group='成績', en='Science 10th percentile', zh='科學後段（第10百分位）分數', hib=True)
spec(id='sci_p90', cycle=2025, file=F25P, sheet='Table I.B1.2a.1', col=13, kind='score',
     group='成績', en='Science 90th percentile', zh='科學前段（第90百分位）分數', hib=True)
spec(id='sci_spread', cycle=2025, file=F25P, sheet='Table I.B1.2a.1', col=15, kind='score',
     group='成績', en='Science inter-decile range (P90-P10)', zh='科學高低分差距（P90−P10）', hib=False)
spec(id='read_mean', cycle=2025, file=F25P, sheet='Table I.B1.2a.2', col=1, kind='score',
     group='成績', en='Reading mean score', zh='閱讀平均分數', hib=True)
spec(id='math_mean', cycle=2025, file=F25P, sheet='Table I.B1.2a.3', col=1, kind='score',
     group='成績', en='Mathematics mean score', zh='數學平均分數', hib=True)
spec(id='cps_mean', cycle=2025, file=F25P, sheet='Table I.B1.2a.4', col=1, kind='score',
     group='成績', en='Computational problem solving mean', zh='運算問題解決平均分數', hib=True)
spec(id='sub_explain', cycle=2025, file=F25P, sheet='Table I.B1.2a.5', col=1, kind='score',
     group='成績', en='Subscale: explain phenomena scientifically', zh='科學子項：科學地解釋現象', hib=True)
spec(id='sub_enquiry', cycle=2025, file=F25P, sheet='Table I.B1.2a.6', col=1, kind='score',
     group='成績', en='Subscale: evaluate designs for scientific enquiry', zh='科學子項：評估探究設計', hib=True)
spec(id='sub_infodecision', cycle=2025, file=F25P, sheet='Table I.B1.2a.7', col=1, kind='score',
     group='成績', en='Subscale: evaluate scientific information for decision making', zh='科學子項：評估科學資訊做決策', hib=True)
spec(id='pct_below2', cycle=2025, file=F25P, sheet='Table I.B1.2a.10', cols_sum=[1,3,5], kind='pct',
     group='成績', en='% low performers in science (below Level 2)', zh='科學未達基礎水準（L2以下）比例', hib=False)
spec(id='pct_top', cycle=2025, file=F25P, sheet='Table I.B1.2a.10', cols_sum=[13,15], kind='pct',
     group='成績', en='% top performers in science (Level 5-6)', zh='科學頂尖學生（L5–6）比例', hib=True)
spec(id='escs_strength', cycle=2025, file=F25S, sheet='Table I.B1.2b.2', col=1, kind='pct',
     group='公平性', en='% of science variance explained by socio-economic status', zh='社經地位可解釋的科學成績變異％', hib=False)
spec(id='escs_gap', cycle=2025, file=F25S, sheet='Table I.B1.2b.2', col=19, kind='score',
     group='公平性', en='Science score gap: top vs bottom ESCS quarter', zh='社經前後四分之一的科學分數差', hib=False)
spec(id='sci_girls', cycle=2025, file=F25G, sheet='Table I.B1.2c.1', col=1, kind='score',
     group='性別', en='Science mean, girls', zh='科學平均分數（女生）', hib=True)
spec(id='sci_boys', cycle=2025, file=F25G, sheet='Table I.B1.2c.1', col=16, kind='score',
     group='性別', en='Science mean, boys', zh='科學平均分數（男生）', hib=True)
# 態度（第3章）
A25 = [('curiosity','Table I.B1.3.1','好奇心','Curiosity'),
       ('perseverance','Table I.B1.3.9','毅力','Perseverance'),
       ('nature_of_science','Table I.B1.3.30','對科學本質的信念','Beliefs about the nature of science'),
       ('cognitive_adaptability','Table I.B1.3.40','認知彈性','Cognitive adaptability'),
       ('help_seeking','Table I.B1.3.44','主動求助','Self-regulated help seeking'),
       ('goal_setting','Table I.B1.3.49','目標設定','Goal setting'),
       ('enjoyment','Table I.B1.3.53','享受科學（樂趣）','Enjoyment of science'),
       ('cognitive_activation','Table I.B1.3.57','科學課的認知啟動','Cognitive activation in science classes'),
       ('belonging','Table I.B1.3.62','學校歸屬感','Sense of belonging'),
       ]
for i,(iid,sh,zh,en) in enumerate(A25):
    spec(id=iid, cycle=2025, file=F25A, sheet=sh, col=1, kind='index',
         group='態度', en=en, zh=zh, hib=True)
spec(id='life_satisfaction', cycle=2025, file=F25A, sheet='Table I.B1.3.79', col=1, kind='points10',
     group='態度', en='Life satisfaction (0-10)', zh='生活滿意度（0–10分）', hib=True)
spec(id='growth_mindset', cycle=2025, file=F25A, sheet='Table I.B1.3.16', cols_sum=[1,4], kind='pct',
     group='態度', en='% disagreeing that intelligence is fixed (growth mindset)',
     zh='成長心態：不認同「智力天生無法改變」的比例', hib=True)
spec(id='school_waste', cycle=2025, file=F25A, sheet='Table I.B1.3.70', cols_sum=[19,22], kind='pct',
     group='態度', en='% agreeing school has been a waste of time', zh='認為「上學是浪費時間」的比例', hib=False)
spec(id='school_unprepared', cycle=2025, file=F25A, sheet='Table I.B1.3.70', cols_sum=[7,10], kind='pct',
     group='態度', en='% agreeing school did little to prepare them for adult life',
     zh='認為「學校沒讓我為成年生活做好準備」的比例', hib=False)
# 第4章 學校生活
spec(id='teacher_support', cycle=2025, file=F25C4, sheet='Table I.B1.4.113', col=1, kind='index',
     group='學校', en='Teacher support in science lessons', zh='科學課的教師支持', hib=True)
spec(id='family_support', cycle=2025, file=F25C4, sheet='Table I.B1.4.120', col=1, kind='index',
     group='學校', en='Family support', zh='家庭支持', hib=True)
spec(id='ai_use', cycle=2025, file=F25C4, sheet='Table I.B1.4.53', col=1, kind='index',
     group='學校', en='Use of AI for schoolwork', zh='用 AI 做功課的程度', hib=None)
spec(id='homework_hours', cycle=2025, file=F25C4, sheet='Table I.B1.4.93', col=1, kind='hours',
     group='學校', en='Hours of homework per day (all subjects)', zh='每天做功課時數（所有科目）', hib=None)
spec(id='digital_distraction', cycle=2025, file=F25C4, sheet='Table I.B1.4.43', col=1, kind='pct',
     group='學校', en='% distracted by digital devices in science lessons', zh='科學課被數位裝置干擾的比例', hib=False)
# 第5章 環境
spec(id='env_sci_mean', cycle=2025, file=F25C5, sheet='Table I.B1.5.1', col=1, kind='score',
     group='環境', en='Environmental science subscale mean', zh='環境科學子量表平均分數', hib=True)
spec(id='env_awareness', cycle=2025, file=F25C5, sheet='Table I.B1.5.6', col=1, kind='index',
     group='環境', en='Environmental awareness', zh='環境議題認識程度', hib=True)
spec(id='env_agency', cycle=2025, file=F25C5, sheet='Table I.B1.5.11', col=1, kind='index',
     group='環境', en='Belief in own capacity to generate environmental change', zh='相信自己能帶來環境改變', hib=True)
spec(id='env_collective', cycle=2025, file=F25C5, sheet='Table I.B1.5.18', col=1, kind='index',
     group='環境', en='Belief in collective environmental efficacy', zh='相信集體行動能改變環境', hib=True)
spec(id='env_career', cycle=2025, file=F25C5, sheet='Table I.B1.5.41', cols_sum=[7,10], kind='pct',
     group='環境', en='% expecting an environment-related career (to some/large extent)',
     zh='期待從事與環境相關工作的比例', hib=True)

# --- 診斷型指標（城鄉、學校落差、補習、班級、校園氛圍）
spec(id='sci_rural', cycle=2025, file=F25C5, sheet='Table I.B1.5.4', col=39, kind='score',
     group='城鄉', en='Science score, rural schools (env. science subscale)', zh='鄉村學校的科學分數', hib=True)
spec(id='sci_city', cycle=2025, file=F25C5, sheet='Table I.B1.5.4', col=43, kind='score',
     group='城鄉', en='Science score, city schools (env. science subscale)', zh='城市學校的科學分數', hib=True)
spec(id='urban_rural_gap', cycle=2025, file=F25C5, sheet='Table I.B1.5.4', col=45, kind='score',
     group='城鄉', en='City minus rural science score gap (env. science subscale)', zh='城鄉科學分數差（城市−鄉村）', hib=False)
spec(id='school_ses_gap', cycle=2025, file=F25C5, sheet='Table I.B1.5.4', col=37, kind='score',
     group='城鄉', en='Advantaged minus disadvantaged school score gap', zh='優勢校與弱勢校的科學分數差', hib=False)
spec(id='between_school_var', cycle=2025, file=F25P, sheet='Table I.B1.2a.25', col=12, kind='pct',
     group='城鄉', en='% of science score variation that lies between schools', zh='科學成績差異來自「學校之間」的比例', hib=False)
spec(id='cram_science', cycle=2025, file=F25C4, sheet='Table I.B1.4.105', col=1, kind='pct',
     group='學校', en='% taking additional science instruction', zh='有上額外科學課／補習的比例', hib=None)
spec(id='cram_ses_gap', cycle=2025, file=F25C4, sheet='Table I.B1.4.105', col=19, kind='pct',
     group='城鄉', en='Advantaged minus disadvantaged gap in extra science instruction', zh='補習的社經落差（優勢−弱勢，百分點）', hib=False)
spec(id='class_size_sci', cycle=2025, file=F25C4, sheet='Table I.B1.4.109', col=1, kind='count',
     group='學校', en='Science class size', zh='科學課班級人數', hib=False)
spec(id='class_size_city_rural', cycle=2025, file=F25C4, sheet='Table I.B1.4.109', col=25, kind='count',
     group='城鄉', en='City minus rural science class size', zh='城鄉班級人數差（城市−鄉村）', hib=False)
spec(id='discipline', cycle=2025, file=F25C4, sheet='Table I.B1.4.132', col=1, kind='index',
     group='學校', en='Disciplinary climate in science lessons', zh='科學課的秩序與紀律', hib=True)
spec(id='bullying', cycle=2025, file=F25C4, sheet='Table I.B1.4.138', col=1, kind='index',
     group='學校', en='Exposure to bullying', zh='遭受霸凌的程度', hib=False)
spec(id='feel_safe', cycle=2025, file=F25C4, sheet='Table I.B1.4.149', col=1, kind='index',
     group='學校', en='Feeling safe at school', zh='在學校感到安全', hib=True)
spec(id='truancy', cycle=2025, file=F25C4, sheet='Table I.B1.4.158', col=1, kind='pct',
     group='學校', en='% who skipped a whole school day', zh='曾整天蹺課的比例', hib=False)

# ===== 2015 =====
F15A, F15B = 'pisa2015_ch2.xlsx', 'pisa2015_ch3.xlsx'
spec(id='sci_mean', cycle=2015, file=F15A, sheet='Table I.2.3', col=1, kind='score',
     group='成績', en='Science mean score', zh='科學平均分數', hib=True)
spec(id='sci_sd', cycle=2015, file=F15A, sheet='Table I.2.3', col=3, kind='score',
     group='成績', en='Science score standard deviation', zh='科學分數標準差（分數落差）', hib=None)
spec(id='epistemic', cycle=2015, file=F15A, sheet='Table I.2.12a', col=1, kind='index',
     group='態度', en='Epistemic beliefs about science', zh='科學知識論信念（相信科學怎麼運作）', hib=True)
spec(id='enjoyment', cycle=2015, file=F15B, sheet='Table I.3.1a', col=1, kind='index',
     group='態度', en='Enjoyment of science', zh='享受科學（樂趣）', hib=True)
spec(id='interest_broad', cycle=2015, file=F15B, sheet='Table I.3.2a', col=1, kind='index',
     group='態度', en='Interest in broad science topics', zh='對各類科學主題的興趣', hib=True)
spec(id='instrumental', cycle=2015, file=F15B, sheet='Table I.3.3a', col=1, kind='index',
     group='態度', en='Instrumental motivation to learn science', zh='工具性動機（學科學有用）', hib=True)
spec(id='self_efficacy', cycle=2015, file=F15B, sheet='Table I.3.4a', col=1, kind='index',
     group='態度', en='Science self-efficacy', zh='科學自我效能（我做得到）', hib=True)
spec(id='sci_activities', cycle=2015, file=F15B, sheet='Table I.3.5a', col=1, kind='index',
     group='態度', en='Science activities outside school', zh='課外科學活動參與', hib=True)
spec(id='career_sci', cycle=2015, file=F15B, sheet='Table I.3.10a', cols_sum=[1,3,5,7], kind='pct',
     group='職涯', en='% expecting a science-related career at 30', zh='30歲想從事科學相關工作的比例', hib=True)
spec(id='career_sci_eng', cycle=2015, file=F15B, sheet='Table I.3.10a', col=1, kind='pct',
     group='職涯', en='% expecting to be science/engineering professionals', zh='想當科學家／工程師的比例', hib=True)
spec(id='career_health', cycle=2015, file=F15B, sheet='Table I.3.10a', col=3, kind='pct',
     group='職涯', en='% expecting to be health professionals', zh='想當醫療專業人員的比例', hib=True)
spec(id='career_ict', cycle=2015, file=F15B, sheet='Table I.3.10a', col=5, kind='pct',
     group='職涯', en='% expecting to be ICT professionals', zh='想當資通訊專業人員的比例', hib=True)
spec(id='career_vague', cycle=2015, file=F15B, sheet='Table I.3.10a', col=11, kind='pct',
     group='職涯', en='% with vague career expectations', zh='對未來職業沒有明確想法的比例', hib=False)
# 2006 的職涯數字取自同一張 2015 表（定義與 2015 完全一致，可直接比較）
spec(id='career_sci', cycle=2006, file=F15B, sheet='Table I.3.10a', cols_sum=[13,15,17,19], kind='pct',
     group='職涯', en='% expecting a science-related career at 30', zh='30歲想從事科學相關工作的比例', hib=True)
spec(id='career_sci_eng', cycle=2006, file=F15B, sheet='Table I.3.10a', col=13, kind='pct',
     group='職涯', en='% expecting to be science/engineering professionals', zh='想當科學家／工程師的比例', hib=True)
spec(id='career_health', cycle=2006, file=F15B, sheet='Table I.3.10a', col=15, kind='pct',
     group='職涯', en='% expecting to be health professionals', zh='想當醫療專業人員的比例', hib=True)
spec(id='career_ict', cycle=2006, file=F15B, sheet='Table I.3.10a', col=17, kind='pct',
     group='職涯', en='% expecting to be ICT professionals', zh='想當資通訊專業人員的比例', hib=True)
spec(id='career_vague', cycle=2006, file=F15B, sheet='Table I.3.10a', col=23, kind='pct',
     group='職涯', en='% with vague career expectations', zh='對未來職業沒有明確想法的比例', hib=False)

# ===== 2006 =====
F06A, F06B = 'pisa2006_ch2.xls', 'pisa2006_ch3.xls'
spec(id='sci_mean', cycle=2006, file=F06A, sheet='T2.1c', col=1, kind='score',
     group='成績', en='Science mean score', zh='科學平均分數', hib=True)
spec(id='sci_sd', cycle=2006, file=F06A, sheet='T2.1c', col=3, kind='score',
     group='成績', en='Science score standard deviation', zh='科學分數標準差（分數落差）', hib=None)
spec(id='sub_identify', cycle=2006, file=F06A, sheet='T2.2c', col=1, kind='score',
     group='成績', en='Subscale: identifying scientific issues', zh='科學子項：辨識科學議題', hib=True)
spec(id='sub_explain', cycle=2006, file=F06A, sheet='T2.3c', col=1, kind='score',
     group='成績', en='Subscale: explaining phenomena scientifically', zh='科學子項：科學地解釋現象', hib=True)
spec(id='sub_evidence', cycle=2006, file=F06A, sheet='T2.4c', col=1, kind='score',
     group='成績', en='Subscale: using scientific evidence', zh='科學子項：運用科學證據', hib=True)
spec(id='interest_learning', cycle=2006, file=F06B, sheet='T3.1', col=1, kind='score',
     group='態度', en='Interest in learning science topics (scale, OECD=500)', zh='對學習科學主題的興趣（量尺分數）', hib=True)
spec(id='support_enquiry', cycle=2006, file=F06B, sheet='T3.2', col=1, kind='score',
     group='態度', en='Support for scientific enquiry (scale, OECD=500)', zh='支持科學探究的態度（量尺分數）', hib=True)
A06 = [('self_efficacy','T3.3','科學自我效能（我做得到）','Science self-efficacy'),
       ('self_concept','T3.4','科學自我概念（我是不是讀科學的料）','Science self-concept'),
       ('general_value','T3.5','科學的一般價值（對社會有用）','General value of science'),
       ('personal_value','T3.6','科學的個人價值（對我有用）','Personal value of science'),
       ('general_interest','T3.8','對科學的一般興趣','General interest in science'),
       ('enjoyment','T3.9','享受科學（樂趣）','Enjoyment of science'),
       ('instrumental','T3.10','工具性動機（學科學有用）','Instrumental motivation'),
       ('future_motivation','T3.11','未來導向動機（想繼續走科學）','Future-oriented science motivation'),
       ('sci_activities','T3.15','課外科學活動參與','Science-related activities'),
       ('env_awareness','T3.16','環境議題認識程度','Awareness of environmental issues'),
       ('env_concern','T3.17','對環境議題的擔憂','Concern for environmental issues'),
       ('env_optimism','T3.18','對環境問題的樂觀程度','Optimism about environmental issues'),
       ('env_responsibility','T3.19','對永續發展的責任感','Responsibility for sustainable development'),
       ]
for iid, sh, zh, en in A06:
    g = '環境' if iid.startswith('env_') else '態度'
    spec(id=iid, cycle=2006, file=F06B, sheet=sh, col=1, kind='index', group=g, en=en, zh=zh,
         hib=(None if iid=='env_optimism' else True))
spec(id='parent_sci_career', cycle=2006, file=F06B, sheet='T3.13', col=1, kind='pct',
     group='職涯', en='% with at least one parent in a science-related career', zh='至少一位家長從事科學相關工作的比例', hib=None)

# ---------------------------------------------------------------- 執行抽取
records = []      # cycle, indicator, country, value
oecd_avgs = {}
meta = {}
errors = []
for sp in S:
    if 'cols_sum' in sp:
        cols = {f'c{c}': c for c in sp['cols_sum']}
    else:
        cols = {'v': sp['col']}
    try:
        data, oecd = read_table(sp['file'], sp['sheet'], cols)
    except Exception as e:
        errors.append(f"{sp['cycle']} {sp['id']}: {e}"); continue

    def combine(d):
        if 'cols_sum' in sp:
            vs = [d[f'c{c}'] for c in sp['cols_sum']]
            return None if any(v is None for v in vs) else round(sum(vs), 5)
        return d['v']

    key = (sp['cycle'], sp['id'])
    meta[f"{sp['cycle']}|{sp['id']}"] = {k: sp[k] for k in ('id','cycle','group','en','zh','kind','hib')}
    meta[f"{sp['cycle']}|{sp['id']}"]['source'] = f"{sp['file']} / {sp['sheet']}"
    ov = combine(oecd) if oecd else None
    if ov is not None: oecd_avgs[f"{sp['cycle']}|{sp['id']}"] = ov
    n = 0
    for cname, d in data.items():
        v = combine(d)
        if v is None: continue
        records.append({'cycle': sp['cycle'], 'indicator': sp['id'],
                        'country': canon(cname), 'value': round(v, 5)})
        n += 1
    meta[f"{sp['cycle']}|{sp['id']}"]['n_countries'] = n
    print(f"  ✓ {sp['cycle']} {sp['id']:<22} n={n:<3} OECD={ov}")

if errors:
    print('\n!! 抽取失敗：')
    for e in errors: print('  ', e)

# ---------------------------------------------------------------- 衍生指標
DERIVED = [
  # (cycle, new_id, a, b, zh, en, kind, group, hib)   value = a - b
  (2025,'gender_gap_sci','sci_girls','sci_boys','科學成績的性別差（女−男）',
   'Gender gap in science (girls - boys)','score','性別',None),
  (2025,'rel_explain','sub_explain','sci_mean','相對強弱：科學地解釋現象',
   'Relative strength: explain phenomena scientifically','score','診斷',None),
  (2025,'rel_enquiry','sub_enquiry','sci_mean','相對強弱：評估探究設計',
   'Relative strength: evaluate designs for scientific enquiry','score','診斷',None),
  (2025,'rel_infodecision','sub_infodecision','sci_mean','相對強弱：評估科學資訊做決策',
   'Relative strength: evaluate scientific information for decision making','score','診斷',None),
  (2006,'rel_identify','sub_identify','sci_mean','相對強弱：辨識科學議題',
   'Relative strength: identifying scientific issues','score','診斷',None),
  (2006,'rel_explain','sub_explain','sci_mean','相對強弱：科學地解釋現象',
   'Relative strength: explaining phenomena scientifically','score','診斷',None),
  (2006,'rel_evidence','sub_evidence','sci_mean','相對強弱：運用科學證據',
   'Relative strength: using scientific evidence','score','診斷',None),
]
_byci = {}
for r in records: _byci.setdefault((r['cycle'], r['indicator']), {})[r['country']] = r['value']
for cyc, nid, a, b, zh, en, kind, group, hib in DERIVED:
    A, B = _byci.get((cyc, a), {}), _byci.get((cyc, b), {})
    mk = f'{cyc}|{nid}'
    meta[mk] = {'id': nid, 'cycle': cyc, 'group': group, 'en': en, 'zh': zh,
                'kind': kind, 'hib': hib,
                'source': f"衍生：{meta[f'{cyc}|{a}']['source']} 減 {meta[f'{cyc}|{b}']['source']}"}
    n = 0
    for c in A:
        if c in B:
            records.append({'cycle': cyc, 'indicator': nid, 'country': c,
                            'value': round(A[c] - B[c], 5)})
            n += 1
    meta[mk]['n_countries'] = n
    oa, ob = oecd_avgs.get(f'{cyc}|{a}'), oecd_avgs.get(f'{cyc}|{b}')
    if oa is not None and ob is not None: oecd_avgs[mk] = round(oa - ob, 5)
    print(f'  + {cyc} {nid:<22} n={n}')

# ---------------------------------------------------------------- 排名
from collections import defaultdict
by_ind = defaultdict(list)
for r in records:
    by_ind[(r['cycle'], r['indicator'])].append(r)

for k, rows in by_ind.items():
    mk = f'{k[0]}|{k[1]}'
    hib = meta[mk]['hib']
    desc = False if hib is False else True   # hib None 也用高→低排，只是不詮釋好壞
    rows.sort(key=lambda r: r['value'], reverse=desc)
    n = len(rows)
    for i, r in enumerate(rows):
        r['rank'] = i + 1
        r['n'] = n
        r['pct_rank'] = round(100.0 * i / (n - 1), 1) if n > 1 else 0.0

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'pisa_long.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=['cycle','indicator','country','country_zh','value','rank','n','pct_rank'])
    w.writeheader()
    for r in sorted(records, key=lambda r: (r['cycle'], r['indicator'], r['rank'])):
        r2 = dict(r); r2['country_zh'] = ZH.get(r['country'], '')
        w.writerow(r2)

countries = sorted({r['country'] for r in records})
db = {
  'meta': {'built': '2026-09-18', 'cycles': [2006, 2015, 2025],
           'note': 'PISA 科學主測年資料庫。index 類指標為 OECD 標準化指數（OECD 平均=0，標準差=1）。'},
  'indicators': meta,
  'oecd_average': oecd_avgs,
  'countries': [{'en': c, 'zh': ZH.get(c, '')} for c in countries],
  'records': records,
}
with open(os.path.join(OUT, 'pisa.json'), 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=1)

print(f"\n完成：{len(records)} 筆、{len(by_ind)} 個指標-年度、{len(countries)} 個國家／經濟體")
missing_zh = [c for c in countries if c not in ZH]
if missing_zh: print('缺中文名：', missing_zh)
