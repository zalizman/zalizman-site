"""FTP-verktyg för zalizman.se hos Loopia.

Användning:
  python tools/ftp_upload.py list                 # lista rotkatalogen på servern
  python tools/ftp_upload.py upload               # ladda upp allt i site/ (spegla)
  python tools/ftp_upload.py upload --dry         # visa vad som SKULLE laddas upp

Lösenordet läses ur ftp_credentials.txt(.txt) i projektroten — lämnas utanför git.
Vinkla parenteser <> i filen ignoreras automatiskt.
"""
import ftplib
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(ROOT, "site")


def read_credentials():
    for name in ("ftp_credentials.txt", "ftp_credentials.txt.txt"):
        path = os.path.join(ROOT, name)
        if os.path.exists(path):
            creds = {}
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if "=" in line:
                        key, val = line.split("=", 1)
                        # strippalau <> om användaren lämnat platshållarna kvar
                        creds[key.strip().lower()] = val.strip().strip("<>").strip()
            return creds
    raise SystemExit("Hittar inte ftp_credentials.txt i " + ROOT)


def connect():
    creds = read_credentials()
    host = creds.get("host", "ftp.loopia.se")
    user, password = creds["user"], creds["password"]
    print(f"Ansluter till {host} som {user} ...")
    ftp = ftplib.FTP_TLS(host)
    ftp.connect(timeout=30)
    ftp.auth()
    ftp.login(user, password)
    ftp.prot_p()  # kryptera även datakanalen
    print("Inloggad OK (FTPS)")
    return ftp


def cmd_list():
    ftp = connect()
    print("\n--- rotkatalogen ---")
    ftp.retrlines("LIST")
    ftp.quit()


def walk_local(base):
    for dirpath, _dirnames, filenames in os.walk(base):
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, base).replace("\\", "/")
            yield rel, full


def cmd_upload(remote_root, dry=False):
    ftp = connect()
    uploads = list(walk_local(SITE_DIR))
    print(f"\n{len(uploads)} filer att spegla till {remote_root}", flush=True)
    remote_root = remote_root.rstrip("/")
    made_dirs = set()
    ok = 0
    for rel, full in uploads:
        remote_path = remote_root + "/" + rel
        # skapa underkataloger (MKD absolute; ignorerar om de redan finns)
        cur = remote_root
        for d in rel.split("/")[:-1]:
            cur = cur + "/" + d
            if cur not in made_dirs:
                try:
                    ftp.mkd(cur)
                except ftplib.error_perm:
                    pass  # finns redan
                made_dirs.add(cur)
        size = os.path.getsize(full)
        if dry:
            print(f"  [DRY] {rel} ({size//1024} kB)", flush=True)
            continue
        for attempt in (1, 2):
            try:
                with open(full, "rb") as fh:
                    ftp.storbinary("STOR " + remote_path, fh, blocksize=32768)
                ok += 1
                print(f"  uppladdad: {rel} ({size//1024} kB)", flush=True)
                break
            except (ftplib.error_temp, ftplib.error_proto, OSError) as exc:
                if attempt == 1:
                    print(f"  retry {rel}: {exc}", flush=True)
                    ftp = connect()
                else:
                    raise
    if not dry:
        print(f"\nKlart! {ok}/{len(uploads)} filer uppladdade.", flush=True)
        print("Verifiera forhandsgranskningen i webblasaren.", flush=True)
    ftp.quit()


def cmd_move(remote_from_dir, remote_to_dir):
    """Flytta ALLA poster i remote_from_dir till remote_to_dir (skapar mappen)."""
    ftp = connect()
    try:
        ftp.mkd(remote_to_dir)
    except ftplib.error_perm:
        pass  # finns redan
    entries = []
    ftp.retrlines("LIST " + remote_from_dir, lambda line: entries.append(line))
    # LIST-format: perms links owner group size month day year-or-time NAME
    names = []
    for e in entries:
        parts = e.split(None, 8)
        if len(parts) >= 9:
            name = parts[8].strip()
            if name not in (".", ".."):
                names.append(name)
    print(f"Flyttar {len(names)} poster: {remote_from_dir} -> {remote_to_dir}", flush=True)
    moved = 0
    for name in names:
        src = remote_from_dir.rstrip("/") + "/" + name
        dst = remote_to_dir.rstrip("/") + "/" + name
        try:
            ftp.rename(src, dst)  # RNFR + RNTO
            moved += 1
            print(f"  flyttad: {name}", flush=True)
        except ftplib.error_perm as exc:
            print(f"  FEL {name}: {exc}", flush=True)
    print(f"Klart: {moved}/{len(names)} flyttade.", flush=True)
    ftp.quit()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        cmd_list()
    elif cmd == "upload":
        remote_root = sys.argv[3] if len(sys.argv) > 3 else "/zalizman.se/public_html"
        cmd_upload(remote_root, dry="--dry" in sys.argv)
    elif cmd == "move":
        # python ftp_upload.py move /fran/katalog /till/katalog
        cmd_move(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
