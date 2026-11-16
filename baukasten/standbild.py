"""Standbild aus einem Video als Hintergrund fürs Titelbild (1080 x 1920 PNG).

Aufruf:  py baukasten/standbild.py <video> <sekunde> <ausgabe.png> [--vf "crop=1017:1808:32:0"] [--blatt]
  --vf     zusätzlicher ffmpeg-Filter vor dem Skalieren (z. B. Ausschnitt)
  --blatt  statt eines Bildes einen Kontaktbogen von sekunde-1 bis sekunde+1 in 0,2-s-Schritten (Augen prüfen:
           offen, Blick in die Linse, keine übertriebene Mimik) -> <ausgabe>-blatt.jpg

Das Bild darf keine eingebrannten Texte haben (Untertitel, Hook). Darum aus dem Rohschnitt oder der Aufnahme nehmen,
nicht aus dem fertigen Reel.
"""
import io, subprocess, sys, pathlib
from PIL import Image, ImageDraw

W, H = 1080, 1920


def bild(video, t, vf=None):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', str(video), '-frames:v', '1']
    if vf:
        cmd += ['-vf', vf]
    roh = subprocess.run(cmd + ['-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True, check=True).stdout
    b = Image.open(io.BytesIO(roh)).convert('RGB')
    if b.size != (W, H):
        # Seitenverhältnis erhalten: auf 9:16 zuschneiden, dann skalieren (nie verzerren)
        bw, bh = b.size
        if bw / bh > W / H:
            nw = bh * W / H
            b = b.crop(((bw - nw) / 2, 0, (bw + nw) / 2, bh))
        else:
            nh = bw * H / W
            b = b.crop((0, (bh - nh) / 2, bw, (bh + nh) / 2))
        b = b.resize((W, H), Image.LANCZOS)
    return b


def main():
    a = sys.argv[1:]
    vf = a[a.index('--vf') + 1] if '--vf' in a else None
    pos = [x for i, x in enumerate(a) if not x.startswith('--') and (i == 0 or a[i - 1] != '--vf')]
    if len(pos) < 3:
        sys.exit(__doc__)
    video, t, aus = pathlib.Path(pos[0]), float(pos[1]), pathlib.Path(pos[2])
    aus.parent.mkdir(parents=True, exist_ok=True)
    if '--blatt' in a:
        zeiten = [round(t - 1 + i * .2, 2) for i in range(11) if t - 1 + i * .2 >= 0]
        kw, kh = 270, 480
        blatt = Image.new('RGB', (kw * 6, kh * 2), 'white')
        for k, z in enumerate(zeiten):
            b = bild(video, z, vf).resize((kw, kh), Image.LANCZOS)
            ImageDraw.Draw(b).text((8, 8), f'{z:.2f}', fill='yellow')
            blatt.paste(b, ((k % 6) * kw, (k // 6) * kh))
        ziel = aus.with_name(aus.stem + '-blatt.jpg')
        blatt.save(ziel, quality=88)
        print('Kontaktbogen ->', ziel)
        return
    bild(video, t, vf).save(aus)
    print('Standbild ->', aus)


if __name__ == '__main__':
    main()
