import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

paths = [
    "src/in_game/events/tv_academy_join_events.txt",
    "src/in_game/common/international_organizations/tv_academy_of_sciences.txt",
]
for path in paths:
    content = open(path, "rb").read()
    if not content.startswith(b"\xef\xbb\xbf"):
        open(path, "wb").write(b"\xef\xbb\xbf" + content)
        print(f"BOM added: {path}")
    else:
        print(f"Already has BOM: {path}")
