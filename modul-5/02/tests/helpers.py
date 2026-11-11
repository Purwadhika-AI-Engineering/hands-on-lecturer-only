"""Fungsi bantu bersama untuk semua test: membuat gambar uji dan memanggil Docker CLI."""
import io
import re
import shutil
import subprocess

from PIL import Image, ImageDraw

CIFAR10_CLASSES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck",
]


# --------------------------------------------------------------------------- images
def make_image(size=(224, 224), color=(200, 30, 30), mode="RGB", fmt="PNG", shapes=True) -> bytes:
    """Buat gambar sintetis (tanpa file eksternal) dan kembalikan sebagai bytes."""
    img = Image.new("RGB", size, color)
    if shapes:
        d = ImageDraw.Draw(img)
        w, h = size
        d.ellipse([w * 0.25, h * 0.25, w * 0.75, h * 0.75], fill=(240, 240, 240))
        d.rectangle([0, int(h * 0.8), w, h], fill=(30, 120, 30))
    if mode != "RGB":
        img = img.convert(mode)
    buf = io.BytesIO()
    # JPEG tidak mendukung alpha / palette -> simpan sebagai RGB bila perlu
    if fmt.upper() == "JPEG" and img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    img.save(buf, format=fmt)
    return buf.getvalue()


def png_files(name="test.png", **kw):
    return {"file": (name, make_image(fmt="PNG", **kw), "image/png")}


def jpeg_files(name="test.jpg", **kw):
    return {"file": (name, make_image(fmt="JPEG", **kw), "image/jpeg")}


# --------------------------------------------------------------------------- docker
def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=20)
        return r.returncode == 0
    except Exception:
        return False


def docker(*args, timeout=120):
    """Jalankan perintah docker, kembalikan CompletedProcess (stdout/stderr berupa teks)."""
    return subprocess.run(["docker", *args], capture_output=True, text=True, timeout=timeout)


def container_exists(name: str) -> bool:
    return docker("inspect", "--format", "{{.Id}}", name).returncode == 0


def inspect(name: str, fmt: str) -> str:
    r = docker("inspect", "--format", fmt, name)
    return r.stdout.strip() if r.returncode == 0 else ""


def logs(name: str) -> str:
    r = docker("logs", name)
    return (r.stdout or "") + (r.stderr or "")  # uvicorn menulis ke stderr


_UNITS = {"b": 1, "kib": 1024, "mib": 1024**2, "gib": 1024**3,
          "kb": 1000, "mb": 1000**2, "gb": 1000**3}


def parse_mem_usage(text: str) -> float:
    """'123.4MiB / 7.67GiB' -> jumlah byte yang dipakai (angka pertama)."""
    m = re.match(r"\s*([\d.]+)\s*([A-Za-z]+)", text)
    if not m:
        raise ValueError(f"Format memori tidak dikenal: {text!r}")
    return float(m.group(1)) * _UNITS[m.group(2).lower()]
