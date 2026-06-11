#!/usr/bin/env python3
import re, sys, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PUBLIC_SCOPES=[ROOT/'src', ROOT/'public', ROOT/'index.html', ROOT/'README.md']
HAN=re.compile(r'[\u4e00-\u9fff]')
CAVEAT=re.compile(r'Caveats|方法限制|not actual|individual-level|household-level|no individual|vendor-confirmed|must be confirmed|Data limitations|Method limitations|Disclaimer|Privacy caveat',re.I)
OLD_POS=["art enrichment studio","kids art class provider","creative learning studio","interest-training school","ordinary art training school","generic art class provider"]
def files(scope):
    if scope.is_file(): return [scope]
    if not scope.exists(): return []
    return [p for p in scope.rglob('*') if p.is_file() and p.suffix.lower() not in ['.png','.jpg','.jpeg','.gif','.zip','.map']]
def main():
    errors=[]; changed=[]
    for scope in PUBLIC_SCOPES:
        for p in files(scope):
            txt=p.read_text(encoding='utf-8',errors='ignore')
            rel=str(p.relative_to(ROOT))
            if HAN.search(txt): errors.append(f'Chinese text in {rel}')
            if CAVEAT.search(txt): errors.append(f'Visible caveat/method limitation term in {rel}')
            low=txt.lower()
            for term in OLD_POS:
                if term in low: errors.append(f'Old HGL positioning term in {rel}: {term}')
    for f in ['docs/internal_methodology.md','docs/internal_data_notes.md','docs/internal_public_safety_notes.md']:
        if not (ROOT/f).exists(): errors.append(f'Missing internal doc {f}')
    try:
        status=subprocess.run(['git','status','--short'],cwd=ROOT,text=True,capture_output=True,timeout=30).stdout.splitlines()
        changed=[x for x in status if x.strip()]
    except Exception:
        changed=[]
    report=['# V5.3 Public UI Cleanup QA','']
    if errors:
        report+=['## Status: FAIL','']+[f'- {e}' for e in errors]
    else:
        report+=['## Status: PASS','','- Chinese text scan result: PASS for src/, public/, index.html, README.md.','- Caveat UI scan result: PASS for visible public UI/assets.','- Old HGL positioning scan: PASS.','- Internal methodology/data/public-safety notes preserved in docs/internal_*.md.','- Build result: see logs/v5_3_build.log and logs/v5_3_final_command_status.log.','','## Files changed']+[f'- {x}' for x in changed[:200]]
    (ROOT/'docs/v5_3_public_ui_cleanup_qa.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    if errors:
        print('\n'.join(errors)); sys.exit(1)
    print('V5.3 public UI cleanup validation PASS')
if __name__=='__main__': main()
