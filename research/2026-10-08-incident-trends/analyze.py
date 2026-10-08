"""Reproduce the AIID snapshot study. Python 3.13; see requirements.txt."""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CATEGORIES = ['Negligible', 'Minor', 'Moderate', 'Severe', 'Critical']


def read(name, root=ROOT):
    with (root / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows, fields=None):
    with (ROOT / name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def prepare(source):
    """Keep factual fields only. Do not redistribute article text or names."""
    specs = [
        ('incidents.csv', 'data_incidents_october.csv', ['incident_id', 'date']),
        ('incidents-january.csv', 'data_incidents_january.csv', ['incident_id', 'date']),
        ('classifications_CSETv0.csv', 'data_csetv0.csv', ['Incident ID', 'Published', 'Severity']),
        ('classifications_CSETv1.csv', 'data_csetv1.csv', ['Incident ID', 'Published', 'AI System', 'AI Harm Level']),
    ]
    for src, dest, fields in specs:
        rows = read(src, source)
        key = 'incident_id' if 'incident_id' in fields else 'Incident ID'
        rows.sort(key=lambda r: int(r[key]))
        write(dest, [{k: r[k] for k in fields} for r in rows], fields)


def index(rows, key):
    ids = [int(r[key]) for r in rows]
    assert len(ids) == len(set(ids)), ('duplicate IDs', key)
    return dict(zip(ids, rows))


def pct(a, b):
    return round(100 * a / b, 6) if b else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, help='Optional original extracted CSV folder')
    args = parser.parse_args()
    if args.source_dir:
        prepare(args.source_dir)

    current = index(read('data_incidents_october.csv'), 'incident_id')
    earlier = index(read('data_incidents_january.csv'), 'incident_id')
    v0_all = index(read('data_csetv0.csv'), 'Incident ID')
    v1_all = index(read('data_csetv1.csv'), 'Incident ID')
    for records, cutoff in ((current, dt.date(2026, 10, 5)), (earlier, dt.date(2026, 1, 5))):
        for r in records.values():
            d = dt.date.fromisoformat(r['date'])
            assert d <= cutoff
    v0 = {i: r for i, r in v0_all.items() if r['Published'] == 'True'}
    v1 = {i: r for i, r in v1_all.items() if r['Published'] == 'True'}
    assert set(v0) <= set(current), 'Unmatched v0 IDs'
    assert set(v1) <= set(current), 'Unmatched v1 IDs'
    known = {i: r for i, r in v0.items() if r['Severity'] in CATEGORIES}
    high = {i for i, r in known.items() if r['Severity'] in ['Moderate', 'Severe', 'Critical']}
    assert all(r['Severity'] in CATEGORIES + ['Unclear/unknown', ''] for r in v0.values())
    count = collections.Counter(int(r['date'][:4]) for r in current.values())
    old_count = collections.Counter(int(r['date'][:4]) for r in earlier.values())
    annual = []
    for year in range(min(count), 2027):
        ids = {i for i, r in current.items() if int(r['date'][:4]) == year}
        annual.append({'year': year, 'incidents': len(ids), 'partial_year': year == 2026,
                       'v0_published': len(ids & set(v0)), 'v0_known_severity': len(ids & set(known)),
                       'v1_published': len(ids & set(v1)), 'v1_ai_no': sum(v1[i]['AI System'] == 'no' for i in ids & set(v1))})
    write('results_annual.csv', annual)

    periods = [('1983–2009', 1983, 2009), ('2010–2014', 2010, 2014), ('2015–2019', 2015, 2019),
               ('2020–2025', 2020, 2025), ('2026 partial', 2026, 2026)]
    bounds = []
    for label, lo, hi in periods:
        ids = {i for i, r in current.items() if lo <= int(r['date'][:4]) <= hi}
        n, k, h = len(ids), len(ids & set(known)), len(ids & high)
        bounds.append({'period': label, 'incidents': n, 'known_severity': k, 'moderate_or_higher': h,
                       'unclassified_or_unknown': n-k, 'coverage_pct': pct(k, n),
                       'classified_share_pct': pct(h, k), 'lower_bound_pct': pct(h, n),
                       'upper_bound_pct': pct(h+n-k, n)})
    write('results_severity_bounds.csv', bounds)
    severity_dist = [{'severity': c, 'count': sum(r['Severity'] == c for r in v0.values())}
                     for c in CATEGORIES + ['Unclear/unknown']]
    write('results_severity_distribution.csv', severity_dist)

    added = set(current) - set(earlier)
    removed = set(earlier) - set(current)
    common = set(current) & set(earlier)
    changed = {i for i in common if current[i]['date'] != earlier[i]['date']}
    drift = []
    for year in range(min(count), 2027):
        additions = sum(int(current[i]['date'][:4]) == year for i in added)
        removals = sum(int(earlier[i]['date'][:4]) == year for i in removed)
        moved_in = sum(int(current[i]['date'][:4]) == year and int(earlier[i]['date'][:4]) != year for i in changed)
        moved_out = sum(int(earlier[i]['date'][:4]) == year and int(current[i]['date'][:4]) != year for i in changed)
        delta = count[year] - old_count[year]
        assert delta == additions - removals + moved_in - moved_out
        drift.append({'year': year, 'january_count': old_count[year], 'october_count': count[year],
                      'net_change': delta, 'added_ids': additions, 'removed_ids': removals,
                      'changed_year_in': moved_in, 'changed_year_out': moved_out})
    write('results_snapshot_change.csv', drift)
    ytd = {year: sum(r['date'][:4] == str(year) and r['date'][5:] <= '09-28' for r in current.values())
           for year in [2025, 2026]}
    summary = {
        'current_records': len(current), 'january_records': len(earlier),
        'current_date_min': min(r['date'] for r in current.values()),
        'current_date_max': max(r['date'] for r in current.values()),
        'v0_published': len(v0), 'v0_known': len(known), 'v0_unknown': len(v0)-len(known),
        'v0_coverage_pct': pct(len(known), len(current)), 'v1_published': len(v1),
        'v1_coverage_pct': pct(len(v1), len(current)),
        'v0_latest_date': max(current[i]['date'] for i in v0),
        'v1_latest_date': max(current[i]['date'] for i in v1),
        'v1_not_ai': sum(r['AI System'] == 'no' for r in v1.values()),
        'v0_unpublished_excluded': len(v0_all)-len(v0), 'v1_unpublished_excluded': len(v1_all)-len(v1),
        'added_ids': len(added), 'removed_ids': len(removed), 'changed_date_ids': len(changed),
        'added_ids_with_pre2026_dates': sum(current[i]['date'] < '2026-01-01' for i in added),
        'count_2020': count[2020], 'count_2024': count[2024], 'count_2025': count[2025],
        'growth_2024_2025_pct': pct(count[2025]-count[2024], count[2024]),
        'multiple_2020_2025': count[2025]/count[2020],
        'ytd_to_september_28': ytd,
        'ytd_change_pct': pct(ytd[2026]-ytd[2025], ytd[2025]),
        'all_years_sum': sum(r['incidents'] for r in annual),
        'missing_dates': 0, 'duplicate_incident_ids': 0, 'unmatched_published_annotation_ids': 0,
    }
    assert summary['all_years_sum'] == len(current)
    assert sum(r['count'] for r in severity_dist) == len(v0)
    (ROOT/'results_summary.json').write_text(json.dumps(summary, indent=2)+'\n')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.titleweight': 'bold', 'savefig.dpi': 180})
    blue, gray, orange = '#176B87', '#8B98A5', '#D27623'
    fig, axes = plt.subplots(2, 1, figsize=(11, 8.4), gridspec_kw={'height_ratios': [1, 1.3]})
    for ax, start in zip(axes, [1983, 2015]):
        years = list(range(start, 2027))
        bars=ax.bar(years,[count[y] for y in years],color=[orange if y==2026 else blue for y in years],width=.8)
        bars[-1].set_hatch('///')
        ax.set_ylabel('Recorded incidents')
        ax.set_ylim(0,510)
        ax.set_xlim(start-1,2027)
        ax.grid(axis='y',alpha=.15)
        ax.set_axisbelow(True)
        if start==1983:
            ax.set_xticks([1983,1990,2000,2010,2020,2026])
            ax.set_title('All dated database records, 1983–2026',loc='left',pad=12)
        else:
            ax.set_xticks(years)
            ax.bar_label(bars,padding=3,fontsize=10)
            ax.set_title('Recent years: 2026 is incomplete',loc='left',pad=12)
    fig.suptitle('Recorded incident counts increased across recent full years',x=.09,ha='left',fontsize=16,fontweight='bold')
    fig.text(.09,.025,'AIID snapshot: October 5, 2026. Count by recorded incident year. Latest record: September 28, 2026.\nThese are database counts, not global incidence or risk per AI use. Blank early years mean no records in this snapshot.',fontsize=9,color='#43505B')
    fig.subplots_adjust(left=.09,right=.97,top=.90,bottom=.12,hspace=.40)
    fig.savefig(ROOT/'figure_counts.png');plt.close(fig)

    fig, ax=plt.subplots(figsize=(10.5,5.8))
    y=list(range(len(bounds)))
    ax.hlines(y,[r['lower_bound_pct'] for r in bounds],[r['upper_bound_pct'] for r in bounds],color=gray,lw=8,alpha=.65)
    for j,r in enumerate(bounds):
        if r['classified_share_pct'] is not None:
            ax.scatter(r['classified_share_pct'],j,color=blue,s=65,zorder=3)
        ax.text(102,j,f"{r['known_severity']}/{r['incidents']}",va='center',fontsize=10)
    ax.set_yticks(y,[r['period'] for r in bounds]);ax.invert_yaxis()
    ax.set_xlim(0,119);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Share with Moderate, Severe, or Critical legacy rating (%)')
    ax.set_title('Missing severity scores prevent a reliable trend estimate',loc='left',fontsize=15,pad=20)
    ax.text(102,-.55,'Known / all',fontsize=10,fontweight='bold')
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    fig.text(.08,.04,'Bars: bounds if every unknown record is low or high severity. Dots: share among known ratings only.\nThese are missing-data bounds, not confidence intervals. Published CSETv0 ratings only; definitions cannot be merged with CSETv1.',fontsize=9,color='#43505B')
    fig.subplots_adjust(left=.15,right=.97,top=.86,bottom=.20)
    fig.savefig(ROOT/'figure_severity.png');plt.close(fig)

    fig, ax=plt.subplots(figsize=(10.5,5.8))
    years=list(range(2020,2026));xs=years
    b1=ax.bar([x-.2 for x in xs],[old_count[y] for y in years],width=.38,color=gray,label='January 5, 2026 snapshot')
    b2=ax.bar([x+.2 for x in xs],[count[y] for y in years],width=.38,color=blue,label='October 5, 2026 snapshot')
    ax.bar_label(b1,padding=3,fontsize=10);ax.bar_label(b2,padding=3,fontsize=10)
    ax.set_xticks(xs,[str(y) for y in years]);ax.set_xlim(2019.4,2025.6);ax.set_ylim(0,525);ax.set_ylabel('Recorded incidents');ax.set_xlabel('Recorded incident year')
    ax.set_title('Counts for past years changed between database snapshots',loc='left',fontsize=15,pad=18)
    ax.legend(frameon=False,loc='upper left');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.text(.08,.035,'Both snapshots use the same distinct-ID count and incident-date field. Changes can include added IDs, removals, and date edits.\nThe comparison measures changes in the database. It does not measure new incidents occurring in these past years.',fontsize=9,color='#43505B')
    fig.subplots_adjust(left=.09,right=.97,top=.87,bottom=.19)
    fig.savefig(ROOT/'figure_snapshot_change.png');plt.close(fig)
    print(json.dumps(summary,indent=2))
    print('All data integrity and count reconciliation checks passed.')


if __name__ == '__main__':
    main()
