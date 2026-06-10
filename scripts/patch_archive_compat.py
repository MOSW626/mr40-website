"""옛 홈페이지 아카이브의 최신 브라우저 호환 패치 (멱등).

실행 순서: build_archive.py → fix_archive_links.py → 이 스크립트

패치 내용:
1. 2002 레이어 메뉴: `document.all(...)` → getElementById (모던 브라우저에서
   document.all이 falsy라 메뉴 레이어가 동작하지 않던 문제)
2. 2002 롤오버: appName 분기 eval → document.images[name] (안전·범용)
3. PPT 내보내기 진입 페이지 5종: 원본 .pptx를 옆에 복사하고, 페이지 상단에
   "슬라이드 프레임으로 보기 / 원본 다운로드" 배너 주입 (cp949 인코딩 유지)
"""
import re
import shutil
from pathlib import Path

WS = Path(__file__).resolve().parents[2]
SITE = Path(__file__).resolve().parents[1]
AR = SITE / "archive"


def patch_bytes(path: Path, old: bytes, new: bytes, label: str):
    data = path.read_bytes()
    if new in data:
        print(f"  · {label}: 이미 적용됨")
        return
    if old not in data:
        print(f"  ! {label}: 패턴 없음 (원본 변경됨?)")
        return
    path.write_bytes(data.replace(old, new))
    print(f"  ✓ {label}")


def patch_2002():
    print("[2002] 레이어 메뉴·롤오버")
    main = AR / "2002" / "main.htm"
    data = main.read_bytes()
    new = re.sub(
        rb"if\s*\(document\.all\)\s*[\r\n]+\s*document\.all\(lname\)\.style\.visibility\s*=\s*'(hidden|visible)'",
        rb"var el = document.getElementById(lname); if (el) el.style.visibility = '\1'",
        data)
    if new != data:
        main.write_bytes(new)
        print("  ✓ 레이어 show/hide 패치")
    else:
        print("  · 레이어 패치 불필요 또는 이미 적용")
    wnb = AR / "2002" / "wnb" / "wnb.htm"
    patch_bytes(
        wnb,
        b"var img = eval((navigator.appName.indexOf('Netscape', 0) != -1) ? nsdoc+'.'+name : 'document.all.'+name);",
        b"var img = document.images[name];",
        "rollover eval x2",
    )
    # 두 함수 모두 같은 라인 — replace는 전체 치환이 아니므로 한 번 더
    data = wnb.read_bytes()
    old = b"var img = eval((navigator.appName.indexOf('Netscape', 0) != -1) ? nsdoc+'.'+name : 'document.all.'+name);"
    if old in data:
        wnb.write_bytes(data.replace(old, b"var img = document.images[name];"))
        print("  ✓ rollover eval 잔여 치환")


# PPT 진입 페이지: (아카이브 경로, 원본 pptx)
PPTS = [
    ("2009/PPT/불낙로봇.htm",
     "cd files/2009 MR/PPT/불낙로봇.pptx"),
    ("2009/PPT/사과 깎는 로봇.htm",
     "cd files/2009 MR/PPT/사과 깎는 로봇.pptx"),
    ("2009/PPT/2009 큐브로봇 프로젝트.htm",
     "cd files/2009 MR/PPT/2009 큐브로봇 프로젝트.pptx"),
    ("2008/MR/menu3/목표추적로보트.htm",
     "cd files/2008 MR/MR/menu3/원본 PPT 파일/목표추적로보트.pptx"),
    ("2008/MR/menu3/제작 동기.htm",
     "cd files/2008 MR/MR/menu3/원본 PPT 파일/제작 동기.pptx"),
]

BANNER_MARK = b"mr40-ppt-banner"


def patch_ppt():
    print("[PPT] 진입 배너 + 원본 pptx")
    from urllib.parse import quote
    for rel, src_rel in PPTS:
        page = AR / rel
        src = WS / src_rel
        if not page.exists():
            print(f"  ! 없음: {rel}")
            continue
        # 원본 pptx 복사 (원본은 읽기만)
        dst = page.with_suffix(".pptx")
        if not dst.exists() and src.exists():
            shutil.copy2(src, dst)
        data = page.read_bytes()
        if BANNER_MARK in data:
            print(f"  · 배너 이미 적용: {rel}")
            continue
        frame = quote(page.stem) + ".files/frame.htm"
        pptx = quote(dst.name)
        banner_html = (
            '<div id="mr40-ppt-banner" style="position:fixed;top:0;left:0;right:0;'
            'z-index:99999;background:#15275c;color:#fff;padding:10px 14px;'
            "font-family:sans-serif;font-size:14px;line-height:1.5;\">"
            "이 문서는 옛 PowerPoint 웹 내보내기라 일부만 표시될 수 있어요. "
            f'<a href="{frame}" style="color:#9db9ff;font-weight:bold;">슬라이드 프레임으로 보기</a> | '
            f'<a href="{pptx}" style="color:#9db9ff;font-weight:bold;" download>원본 PPT 내려받기</a>'
            "</div><div style=\"height:46px\"></div>"
        )
        banner = banner_html.encode("cp949")
        low = data.lower()
        idx = low.find(b"<body")
        if idx >= 0:
            end = low.find(b">", idx)
            data = data[:end + 1] + banner + data[end + 1:]
        else:
            data = banner + data
        page.write_bytes(data)
        print(f"  ✓ {rel}")


if __name__ == "__main__":
    patch_2002()
    patch_ppt()
