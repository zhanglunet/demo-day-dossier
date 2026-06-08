#!/usr/bin/env python3
"""Generate batch-4.json from output/projects.json.

batch-4 is the auto-derived wiki batch:
- Each of 54 projects → 1 entity
- Each named founder → 1 person

merge.py dedupes by slug, so:
- Project entity slug matches an existing entity (e.g. 'rustfs') → merged (longest wins)
- Founder name matches existing person slug → merged

Pure transform from projects.json. Idempotent.
"""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_JSON = REPO_ROOT / 'output' / 'projects.json'
BATCH4_OUT = REPO_ROOT / 'output' / 'wiki' / 'data' / 'raw' / 'batch-4.json'

# ===== Project ID → wiki entity slug =====
# Map first to existing entity slugs where applicable (so merge dedupes).
PROJECT_SLUG = {
    # 已有 wiki entity 的项目 (会合并更新)
    'A07': 'rustfs',
    'A10': 'molplus-ai',
    'A11': 'shuyu-keji',
    'B02': 'ying-kong-ji-qi-ren',
    'B11': 'oki-home',
    'E04': 'insightsec',
    'F11': 'memova-ai',
    'F12': 'thennote',
    # 新项目 (新建 entity)
    'A01': 'vibechip',
    'A02': 'honghu-fusion',
    'A03': 'lorentz-kracht',
    'A04': 'shidai-zhongchu',
    'A05': 'insightchemy',
    'A06': 'xinpian-tech',
    'A08': 'lynnreal',
    'A09': 'liuchang-sampling',
    'B01': 'hivemind',
    'B03': 'softsync',
    'B04': 'xingying-tech',
    'B05': 'snow-origin',
    'B06': 'xiaoying-vision',
    'B07': 'elecholic-tech',
    'B08': 'mirrorspace',
    'B09': 'xiaoxiang-zhikong',
    'B10': 'kynooe',
    'B12': 'zengyuan-zaowu',
    'B13': 'gedu-tech',
    'B14': 'monako-glass',
    'B15': 'suhui-zhineng',
    'B16': 'sportix-ai',
    'B17': 'siai-tech',
    'B18': 'oryn-tech',
    'B19': 'lynook',
    'E01': 'dianyang-tech',
    'E02': 'singularity-engine',
    'E03': 'feika',
    'E05': 'archersmart-ai',
    'E06': 'meridian-ai',
    'E07': 'nextbanker',
    'E08': 'toclean',
    'E09': 'shuwei-zhineng',
    'E10': 'tianqiong-zhisuan',
    'E11': 'shuyu-tech-eda',
    'E12': 'herui-zhixin',
    'F01': 'ksanadock',
    'F02': 'useit-ai',
    'F03': 'lulula-ai',
    'F04': 'humanify',
    'F05': 'all-our-broken-parts',
    'F06': 'stack-anyway',
    'F07': 'helens-kitchen',
    'F08': 'xiang-tongle',
    'F09': 'kuku',
    'F10': 'skardi-ai',
}

# ===== Person name → wiki slug (existing canonical) =====
PERSON_SLUG = {
    '陆奇': 'lu-qi',
    '陈洛飞': 'chen-luofei',
    '王子峣': 'wang-ziyao',
    '刘雅': 'liu-ya',
    '王俊毅': 'wang-junyi',
    '沈明航': 'shen-minghang',
    '陆伟然': 'lu-weiran',
    '杜天蔚': 'du-tianwei',
    '陈晨': 'chen-chen-memova',
    '程漾': 'cheng-yang',
    '孙明雨': 'sun-mingyu',
    '刘荣轩': 'liu-rongxuan',
    '徐晨曦': 'xu-chenxi',
    '路昕瞳': 'lu-xintong',
    '彭向达': 'peng-xiangda',
    '田阳': 'tian-yang',
    '曹瑞鹏': 'cao-ruipeng',
    '王新宇': 'wang-xinyu',
    '金依力': 'jin-yili',
    '邓泰华': 'deng-taihua',
    '彭志辉': 'peng-zhihui-zhihuijun',
    '稚晖君': 'peng-zhihui-zhihuijun',
    '杨植麟': 'yang-zhilin',
    '王小川': 'wang-xiaochuan',
    '许晋诚': 'xu-jincheng',
    '王永锟': 'wang-yongkun',
    '胡效赫': 'hu-xiaohe',
    # New founders from project cards
    '梁进帆': 'liang-jinfan',
    '戴立忠': 'dai-lizhong',
    '曾健安': 'zeng-jianan',
    '唐霄汉': 'tang-xiaohan',
    '欧阳倩': 'ouyang-qian',
    '刘玖阳': 'liu-jiuyang',
    '李文凯': 'li-wenkai',
    '马炜杰': 'ma-weijie',
    '陈明': 'chen-ming',
    '林森源': 'lin-senyuan',
    '陈博宇': 'chen-boyu',
    '秦旭': 'qin-xu',
    '王智林': 'wang-zhilin',
    '付际': 'fu-ji',
    '卢子寅': 'lu-ziyin',
    '计昊天': 'ji-haotian',
    '蓝国伟': 'lan-guowei',
    '许康瑞': 'xu-kangrui',
    '白纯歌': 'bai-chunge',
    '薛来': 'xue-lai',
    '刘欢': 'liu-huan-suhui',
    '沈书涵': 'shen-shuhan',
    '张哲宁': 'zhang-zhening',
    '杨思敏': 'yang-simin',
    '罗镜民': 'luo-jingmin',
    '孔德超': 'kong-dechao',
    '王哲': 'wang-zhe-feika',
    '陈广博': 'chen-guangbo',
    '周玉林': 'zhou-yulin',
    '夏乐冰': 'xia-lebing',
    '张鑫': 'zhang-xin-shuwei',
    '徐子谏': 'xu-zijian',
    '汪嘉成': 'wang-jiacheng',
    '王瑞': 'wang-rui',
    '李豪': 'li-hao',
    '郜迪飞': 'gao-difei',
    '孙长昊': 'sun-changhao',
    '易和阳': 'yi-heyang-aaron',
    '班春晖': 'ban-chunhui',
    '徐世哲': 'xu-shizhe',
    '邓牧雨': 'deng-muyu',
    '韩瑜': 'han-yu',
    '魏鑫': 'wei-xin-bt',
    'Aaron Yee': 'yi-heyang-aaron',
}


def parse_founders(founder_str):
    """Parse founder field into list of (chinese_name, role)."""
    if not founder_str or founder_str.strip() == '未公开':
        return []
    parts = re.split(r'[、+]', founder_str)
    out = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Pattern: "Name — role"
        m = re.match(r'^([一-龥]{2,4}(?:\s*\([^)]+\))?)\s*[—\-]+\s*(.+)$', part)
        if m:
            name_raw = m.group(1).strip()
            role = m.group(2).strip()
        else:
            # Pattern: "Name（role）"
            m = re.match(r'^([一-龥]{2,4})\s*[（(]\s*([^)）]+)\s*[)）]', part)
            if m:
                name_raw = m.group(1).strip()
                role = m.group(2).strip()
            else:
                m = re.match(r'^([一-龥]{2,4})', part)
                if m:
                    name_raw = m.group(1).strip()
                    role = '创始人'
                else:
                    continue
        chinese = re.match(r'^([一-龥]+)', name_raw)
        clean = chinese.group(1) if chinese else name_raw
        out.append((clean, role))
    return out


def build_entity_description(p, zone):
    """Multi-paragraph markdown for entity body."""
    secs = []
    secs.append(f"**项目 ID**: {p['id']} ({zone['zone']} · {zone['theme']})")
    for label, key in [
        ('一句话定位', 'tagline'),
        ('方向', 'direction'),
        ('创始人', 'founder'),
        ('团队', 'team'),
        ('主体', 'company'),
        ('融资', 'funding'),
        ('对标', 'benchmarks'),
        ('亮点', 'highlight'),
        ('展位', 'booth_no'),
        ('联系方式', 'contact'),
        ('项目卡披露融资', 'card_funding'),
        ('项目卡披露团队', 'card_team'),
        ('官网', 'site'),
        ('GitHub', 'github'),
    ]:
        if p.get(key):
            secs.append(f"**{label}**: {p[key]}")
    lp = p.get('live_pitch')
    if lp:
        secs.append(f"**2026-06-07 路演现场 pitch** (演讲人 {lp.get('presenter','')})")
        if lp.get('summary'):
            secs.append(lp['summary'])
    return '\n\n'.join(secs)


def main():
    projects = json.loads(PROJECTS_JSON.read_text(encoding='utf-8'))

    entities = []
    people = []
    seen = set()

    for zone in projects['zones']:
        for p in zone['projects']:
            pid = p['id']
            slug = PROJECT_SLUG.get(pid)
            if not slug:
                print(f'  ⚠ no slug for {pid} {p["name"]}')
                continue

            entities.append({
                "slug": slug,
                "name": p['name'],
                "type": "external-company",
                "description": build_entity_description(p, zone),
                "first_meeting": "kp-keynote-26-06-07",
            })

            for name, role in parse_founders(p.get('founder','')):
                pslug = PERSON_SLUG.get(name)
                if not pslug or pslug in seen:
                    continue
                seen.add(pslug)
                summary = f"{p['name']} ({pid}) {role}。"
                team = p.get('team','')
                if name in team:
                    rel = [s.strip() for s in re.split(r'[。；]', team) if name in s and len(s.strip()) > 5]
                    if rel:
                        summary += ' ' + '。'.join(rel[:2]) + '。'
                people.append({
                    "slug": pslug,
                    "name": name,
                    "aliases": [],
                    "role": f"{p['name']} ({pid}) {role}",
                    "department": None,
                    "first_seen_meeting": "kp-keynote-26-06-07",
                    "summary": summary,
                })

    batch = {
        "batch_id": "batch-4",
        "files_processed": ["output/projects.json"],
        "meetings": [],
        "people": people,
        "concepts": [],
        "entities": entities,
    }
    BATCH4_OUT.parent.mkdir(parents=True, exist_ok=True)
    BATCH4_OUT.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding='utf-8')
    return len(entities), len(people)


if __name__ == '__main__':
    n_ent, n_per = main()
    print(f'✓ batch-4.json: {n_ent} entities + {n_per} people')
