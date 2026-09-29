"""
Plan Anual de Seguridad y Salud en el Trabajo - DARTE CUERO
Versión de escritorio (Python + Tkinter + Pillow) del index.html original.

Requisitos:  pip install pillow
Ejecutar:    python main.py
"""
import os
import sys
import webbrowser
import tkinter as tk
from tkinter import font as tkfont

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk

# --------------------------------------------------------------------------
# RUTAS (funciona también empaquetado con PyInstaller)
# --------------------------------------------------------------------------
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE_DIR, "assets")


def asset(name):
    return os.path.join(ASSETS, name)


# --------------------------------------------------------------------------
# CONTENIDO (todo lo que estaba en el HTML)
# --------------------------------------------------------------------------
HEADER = "UNIVERSIDAD NACIONAL MAYOR DE SAN MARCOS"
TITULO = "Plan Anual de Seguridad y Salud en el Trabajo en la Empresa DARTE CUERO"
GRUPO = "GRUPO 02 - GRUPO SIN RIESGO"

# Documentos: siguen siendo enlaces en la nube (Google Drive / Docs)
ENLACES = [
    ("Ver Informe Plan SST",
     "https://docs.google.com/document/d/1q9u7a5X8_yykWOSJ-_2w05BWbgyeljc3/edit?usp=drive_link&ouid=103372542418574148131&rtpof=true&sd=true"),
    ("Ver plano en Autocad",
     "https://drive.google.com/file/d/1GIKtDY1sNT71hsjdHU_Cyee8kjhP2xOv/view?usp=drive_link"),
    ("Ver Informe Plan Ambiental",
     "https://docs.google.com/document/d/15xGYxPpscOl8J3mmY8ovO1BturmwCW36/edit"),
    ("Ver IPERC",
     "https://docs.google.com/spreadsheets/d/11jwKxj_S10IKPW5bfASo9WT2s2qzRnXW/edit?gid=1484855919#gid=1484855919"),
]

INTEGRANTES = [
    ("Jahir Piero Borja Infantes", "jahir_borja.jpg"),
    ("Armijo Aldoradin Vicky Valery", "vicky_armijo.jpg"),
    ("Diego Samuel Clavijo Sotelo", "diego_clavijo.jpg"),
    ("Do Baruc Peña Domínguez", "baruc_pena.jpg"),
    ("Terrones Fuentes Rivera Bryan", "bryan_terrones.jpg"),
]
DOCENTE = "Dr. Mg. Ing. Edito Luis Rojas Linares"

UNIV = "Universidad Nacional Mayor de San Marcos"
FACULTAD = "Facultad de Ingeniería Industrial"
ESCUELA = "Escuela Profesional de Ingeniería de Seguridad y Salud en el Trabajo"
CURSO = "Prevención y Control de Riesgos Laborales y Ambientales"
FOOTER = "Lima – Perú\n2026"

ROJO = "#8b0000"


# --------------------------------------------------------------------------
# UTILIDADES DE IMAGEN
# --------------------------------------------------------------------------
def load_font(size, bold=False):
    candidates = (["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
                  if bold else
                  ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"])
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            continue
    return ImageFont.load_default()


def cover(img, w, h):
    """Equivalente a background-size: cover; background-position: center."""
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale) + 1, int(ih * scale) + 1
    img = img.resize((nw, nh), Image.LANCZOS)
    x, y = (nw - w) // 2, (nh - h) // 2
    return img.crop((x, y, x + w, y + h))


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=255)
    return m


def glass_panel(bg, box, radius, tint, blur=6):
    """Panel translúcido con desenfoque (backdrop-filter: blur)."""
    x0, y0, x1, y1 = box
    region = bg.crop(box).filter(ImageFilter.GaussianBlur(blur)).convert("RGBA")
    region = Image.alpha_composite(region, Image.new("RGBA", region.size, tint))
    out = Image.new("RGBA", region.size, (0, 0, 0, 0))
    out.paste(region, (0, 0), rounded_mask(region.size, radius))
    return out


def shadow_for(size, radius, blur=14, alpha=90, pad=24):
    sh = Image.new("RGBA", (size[0] + pad * 2, size[1] + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        (pad, pad + 6, pad + size[0], pad + size[1] + 6), radius, fill=(0, 0, 0, alpha))
    return sh.filter(ImageFilter.GaussianBlur(blur)), pad


def gradient_pill(w, h, c1, c2, text, font, text_color="white", radius=None):
    """Botón con degradado diagonal y esquinas redondeadas."""
    radius = h // 2 if radius is None else radius
    xs = Image.linear_gradient("L").resize((w, h))             # vertical 0->255
    xs_h = xs.rotate(90, expand=True).resize((w, h))
    t = Image.blend(xs_h, xs, 0.5)                              # diagonal
    c1i = Image.new("RGB", (w, h), c1)
    c2i = Image.new("RGB", (w, h), c2)
    grad = Image.composite(c2i, c1i, t)
    btn = grad.convert("RGBA")
    d = ImageDraw.Draw(btn)
    d.text((w / 2, h / 2), text, font=font, fill=text_color, anchor="mm")
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(btn, (0, 0), rounded_mask((w, h), radius))
    return out


def flat_button(w, h, color, text, font, radius=6):
    btn = Image.new("RGBA", (w, h), color)
    ImageDraw.Draw(btn).text((w / 2, h / 2), text, font=font, fill="white", anchor="mm")
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(btn, (0, 0), rounded_mask((w, h), radius))
    return out


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# --------------------------------------------------------------------------
# APLICACIÓN
# Para que no se trabe: cada página se "aplana" en UNA sola imagen opaca
# (fondo + panel + sombras + fotos). Encima solo van textos y los parches
# opacos de botones/tarjetas que cambian al pasar el mouse.
# --------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Plan Anual de SST - DARTE CUERO")
        self.geometry("1000x780")
        self.minsize(720, 560)
        self._icon()

        tk.Label(self, text=HEADER, bg=ROJO, fg="white",
                 font=("Arial", 13, "bold"), pady=12).pack(fill="x")

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.raw = {
            "fondo_principal": Image.open(asset("fondo_principal.jpg")).convert("RGB"),
            "fondo_integrantes": Image.open(asset("fondo_integrantes.jpg")).convert("RGB"),
            "portada": Image.open(asset("portada_darte_cuero.jpg")).convert("RGB"),
            "logo": Image.open(asset("logo_unmsm.png")).convert("RGBA"),
            "docente": Image.open(asset("docente.jpg")).convert("RGB"),
        }
        self.fotos = [(n, Image.open(asset(f)).convert("RGB")) for n, f in INTEGRANTES]

        self.page = "principal"
        self.cache = {}      # páginas ya aplanadas (PhotoImage)
        self.pil = {}        # sprites PIL reutilizables (independientes del tamaño)
        self.deco = []       # (imagen RGBA, x, y) que se pegan en el fondo aplanado
        self.sprites = []    # elementos interactivos (botones / tarjetas)
        self._size = None
        self._after = None
        self._content_h = 0
        self._hits = []      # zonas interactivas de la página actual
        self._hover = None

        self.canvas.bind("<Configure>", self._on_resize)
        # El hover se calcula por POSICIÓN del mouse (no por Enter/Leave de cada
        # elemento): así el texto que va encima de las tarjetas no provoca un
        # ciclo infinito entrar/salir que congelaba la ventana.
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda e: self._set_hover(None))
        self.canvas.bind("<Button-1>", self._on_click)
        self.bind_all("<MouseWheel>", self._on_wheel)
        self.bind_all("<Button-4>", lambda e: self._scroll(-3))
        self.bind_all("<Button-5>", lambda e: self._scroll(3))
        self.after(600, self._prewarm)

    def _icon(self):
        try:
            self.iconphoto(True, ImageTk.PhotoImage(
                Image.open(asset("logo_unmsm.png")).convert("RGBA").resize((64, 64))))
        except Exception:
            pass

    def _prewarm(self):
        actual = self.page
        self.page = "integrantes" if actual == "principal" else "principal"
        self.render()
        self.page = actual
        self.render()

    # ---------------- navegación ----------------
    def mostrar_integrantes(self):
        self.page = "integrantes"
        self.render()

    def volver_principal(self):
        self.page = "principal"
        self.render()

    # ---------------- scroll ----------------
    def _scroll(self, units):
        if self._content_h > self.canvas.winfo_height():
            self.canvas.yview_scroll(units, "units")
            self.after_idle(self._refresh_hover)

    def _on_wheel(self, e):
        step = e.delta // 120 if abs(e.delta) >= 120 else (1 if e.delta > 0 else -1)
        self._scroll(-step * 3)

    def _on_resize(self, e):
        if self._size == (e.width, e.height):
            return
        if self._after:
            self.after_cancel(self._after)
        self._after = self.after(250, self.render)

    # ---------------- helpers ----------------
    def sprite(self, key, make, dim=None):
        if key not in self.pil:
            self.pil[key] = make()
        return self.pil[key]

    def add_button(self, x, y, key, make_n, make_h, command):
        self.sprites.append(dict(
            x=x, y=y, cursor="hand2", cmd=command,
            n=lambda: self.sprite(key + ":n", make_n),
            h=lambda: self.sprite(key + ":h", make_h)))

    def text(self, x, y, s, size, bold=False, italic=False, color="#222",
             width=None, justify="center", anchor="n"):
        f = tkfont.Font(family="Arial", size=-size, weight="bold" if bold else "normal",
                        slant="italic" if italic else "roman")
        item = self.canvas.create_text(x, y, text=s, font=f, fill=color, width=width,
                                       justify=justify, anchor=anchor, tags=("content",))
        return item, self.canvas.bbox(item)[3]

    # ---------------- render ----------------
    def render(self):
        c = self.canvas
        W, H = max(c.winfo_width(), 400), max(c.winfo_height(), 300)
        if self._size != (W, H):
            self._size = (W, H)
            self.cache.clear()
        c.delete("all")
        c.yview_moveto(0)
        self._hits, self._hover = [], None
        self.deco, self.sprites = [], []
        if self.page == "principal":
            self._render_principal(W, H)
        else:
            self._render_integrantes(W, H)

    def _finish(self, W, H, bg_key, box, radius, tint, dark):
        c = self.canvas
        self._content_h = box[3] + 40
        total_h = max(H, self._content_h)
        key = f"{self.page}:{W}:{total_h}"

        if key not in self.cache:
            bg = cover(self.raw[bg_key], W, total_h).convert("RGBA")
            bg = Image.alpha_composite(bg, Image.new("RGBA", bg.size, dark))
            panel = glass_panel(bg, box, radius, tint)
            sh, pad = shadow_for((box[2] - box[0], box[3] - box[1]), radius)
            flat = bg.convert("RGB")
            flat.paste(sh, (box[0] - pad, box[1] - pad), sh)
            flat.paste(panel, (box[0], box[1]), panel)
            for img, x, y in self.deco:
                flat.paste(img, (x, y), img)

            def patch(img, sp):
                reg = flat.crop((sp["x"], sp["y"], sp["x"] + img.width, sp["y"] + img.height))
                reg.paste(img, (0, 0), img)
                return ImageTk.PhotoImage(reg)          # RGB opaco = rápido de pintar

            patches = [(patch(sp["n"](), sp), patch(sp["h"](), sp)) for sp in self.sprites]
            self.cache[key] = (ImageTk.PhotoImage(flat), patches)

        flat_tk, patches = self.cache[key]
        c.create_image(0, 0, image=flat_tk, anchor="nw", tags=("bg",))
        for sp, (n_tk, h_tk) in zip(self.sprites, patches):
            item = c.create_image(sp["x"], sp["y"], image=n_tk, anchor="nw", tags=("patch",))
            self._hits.append(dict(sp=sp, item=item, n=n_tk, h=h_tk,
                                   rect=(sp["x"], sp["y"], sp["x"] + n_tk.width(), sp["y"] + n_tk.height())))
        c.tag_lower("patch")
        c.tag_lower("bg")
        c.config(scrollregion=(0, 0, W, total_h))

    # ---------------- hover / clic por posición ----------------
    def _hit_at(self, x, y):
        for hit in self._hits:
            x0, y0, x1, y1 = hit["rect"]
            if x0 <= x < x1 and y0 <= y < y1:
                return hit
        return None

    def _set_hover(self, hit):
        if hit is self._hover:
            return
        c = self.canvas
        old = self._hover
        if old:
            c.itemconfig(old["item"], image=old["n"])
            if old["sp"].get("leave"):
                old["sp"]["leave"]()
        self._hover = hit
        if hit:
            c.itemconfig(hit["item"], image=hit["h"])
            if hit["sp"].get("enter"):
                hit["sp"]["enter"]()
        c.config(cursor=hit["sp"]["cursor"] if hit and hit["sp"]["cursor"] else "")

    def _on_motion(self, e):
        self._set_hover(self._hit_at(e.x, self.canvas.canvasy(e.y)))

    def _refresh_hover(self):
        c = self.canvas
        px, py = c.winfo_pointerx() - c.winfo_rootx(), c.winfo_pointery() - c.winfo_rooty()
        if 0 <= px < c.winfo_width() and 0 <= py < c.winfo_height():
            self._set_hover(self._hit_at(px, c.canvasy(py)))
        else:
            self._set_hover(None)

    def _on_click(self, e):
        hit = self._hit_at(e.x, self.canvas.canvasy(e.y))
        if hit and hit["sp"].get("cmd"):
            hit["sp"]["cmd"]()

    # ---------- Página principal ----------
    def _render_principal(self, W, H):
        pw = min(780, W - 40)
        x0 = (W - pw) // 2
        cx = W // 2
        y0 = 40
        y = y0 + 34

        _, y = self.text(cx, y, TITULO, 20, bold=True, color="#000", width=pw - 100)
        _, y = self.text(cx, y + 8, GRUPO, 13, bold=True, color="#000")
        y += 22

        iw = min(480, pw - 80)
        ih = int(iw * 300 / 480)
        portada = cover(self.raw["portada"], iw, ih).convert("RGBA")
        ImageDraw.Draw(portada).rectangle((0, 0, iw - 1, ih - 1), outline="#aaaaaa", width=2)
        self.deco.append((portada, cx - iw // 2, y))
        y += ih + 28

        f = load_font(18, bold=True)
        bw, bh = 260, 48
        self.add_button(
            cx - bw // 2, y, "btn_integrantes",
            lambda: gradient_pill(bw, bh, (46, 139, 46), (63, 174, 63), "Integrantes", f),
            lambda: gradient_pill(bw, bh, (36, 107, 36), (46, 139, 46), "Integrantes", f),
            self.mostrar_integrantes)
        y += bh + 24

        f2 = load_font(15)
        cols = 2 if pw >= 640 else 1
        bw2, bh2, gap = 250, 40, 16
        rows = (len(ENLACES) + cols - 1) // cols
        for i, (label, url) in enumerate(ENLACES):
            r, col = divmod(i, cols)
            in_row = min(cols, len(ENLACES) - r * cols)
            row_w = in_row * bw2 + (in_row - 1) * gap
            bx = cx - row_w // 2 + col * (bw2 + gap)
            by = y + r * (bh2 + gap)
            self.add_button(
                bx, by, f"link{i}",
                lambda l=label: flat_button(bw2, bh2, "#4a90c4", l, f2),
                lambda l=label: flat_button(bw2, bh2, "#357aab", l, f2),
                lambda u=url: webbrowser.open(u))
        y += rows * (bh2 + gap) - gap + 36

        self._finish(W, H, "fondo_principal", (x0, y0, x0 + pw, y), 12,
                     tint=(220, 240, 250, 165), dark=(30, 50, 70, 60))

    # ---------- Página de integrantes ----------
    def _render_integrantes(self, W, H):
        pw = min(700, W - 40)
        x0 = (W - pw) // 2
        cx = W // 2
        y0 = 40
        y = y0 + 34
        inner = pw - 84

        logo = self.raw["logo"]
        lw = 90
        lh = int(logo.height * lw / logo.width)
        self.deco.append((self.sprite("logo", lambda: logo.resize((lw, lh), Image.LANCZOS)),
                          cx - lw // 2, y))
        y += lh + 10

        _, y = self.text(cx, y, UNIV.upper(), 15, bold=True, color=ROJO)
        _, y = self.text(cx, y + 2, FACULTAD, 12, bold=True, color="#222")
        _, y = self.text(cx, y + 2, ESCUELA, 12, color="#333", width=inner)
        y += 18

        # Recuadro del título
        tid, tb_bottom = self.text(cx, y + 12, f'"{TITULO}"', 13, bold=True, italic=True,
                                   color="#4a0000", width=inner - 40)
        bx0, by0, bx1, by1 = x0 + 42, y, x0 + pw - 42, tb_bottom + 12
        bw_, bh_ = bx1 - bx0, by1 - by0
        box_img = Image.new("RGBA", (bw_, bh_), (0, 0, 0, 0))
        fill = Image.new("RGBA", (bw_, bh_), (255, 245, 245, 255))
        d = ImageDraw.Draw(fill)
        d.rectangle((0, 0, bw_, bh_), outline=(227, 184, 184, 255), width=1)
        d.rectangle((0, 0, 3, bh_), fill=hex_rgb(ROJO) + (255,))
        box_img.paste(fill, (0, 0), rounded_mask((bw_, bh_), 6))
        self.deco.append((box_img, bx0, by0))
        y = by1 + 24

        _, y = self.text(cx, y, "INTEGRANTES:", 13, bold=True, color=ROJO)
        y += 12

        cw, ch, r_gap, c_gap, size = 150, 178, 36, 18, 92
        per_row = max(1, (inner + c_gap) // (cw + c_gap))
        for i, (nombre, foto) in enumerate(self.fotos):
            r, col = divmod(i, per_row)
            in_row = min(per_row, len(self.fotos) - r * per_row)
            row_w = in_row * cw + (in_row - 1) * c_gap
            self._card(cx - row_w // 2 + col * (cw + c_gap), y + r * (ch + r_gap),
                       cw, ch, size, nombre, foto)
        rows = (len(self.fotos) + per_row - 1) // per_row
        y += rows * (ch + r_gap) - r_gap + 22

        tx = x0 + 42
        _, y = self.text(tx, y, "CURSO:", 13, bold=True, color=ROJO, anchor="nw", justify="left")
        _, y = self.text(tx + 10, y + 8, CURSO, 12, anchor="nw", justify="left", width=inner - 10)
        y += 18
        _, y = self.text(tx, y, "DOCENTE:", 13, bold=True, color=ROJO, anchor="nw", justify="left")
        _, y = self.text(tx + 10, y + 8, DOCENTE, 12, anchor="nw", justify="left", width=inner - 10)

        doc = self.raw["docente"]
        dw = 150
        dh = int(doc.height * dw / doc.width)

        def mk_doc():
            im = doc.resize((dw, dh), Image.LANCZOS).convert("RGBA")
            ImageDraw.Draw(im).rectangle((0, 0, dw - 1, dh - 1), outline="#aaaaaa", width=2)
            out = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
            out.paste(im, (0, 0), rounded_mask((dw, dh), 8))
            return out
        self.deco.append((self.sprite("docente", mk_doc), cx - dw // 2, y + 12))
        y += dh + 12 + 20

        _, y = self.text(cx, y, FOOTER, 12, bold=True, color="#333")
        y += 20

        f = load_font(14, bold=True)
        bw, bh = 150, 38
        self.add_button(
            cx - bw // 2, y, "btn_volver",
            lambda: gradient_pill(bw, bh, (139, 0, 0), (179, 0, 0), "←  Volver", f),
            lambda: gradient_pill(bw, bh, (163, 0, 0), (211, 47, 47), "←  Volver", f),
            self.volver_principal)
        y += bh + 34

        # franja roja superior del panel
        self.deco.append((self.sprite("stripe:%d" % pw, lambda: gradient_pill(
            pw, 8, (139, 0, 0), (198, 40, 40), "", load_font(8), radius=4)), x0, y0))

        self._finish(W, H, "fondo_integrantes", (x0, y0, x0 + pw, y), 18,
                     tint=(255, 250, 250, 185), dark=(20, 20, 30, 150))

    def _card(self, x, y, w, h, size, nombre, foto):
        """Tarjeta con foto circular. Hover: se levanta y el nombre se pone rojo."""
        def build(hover):
            lift = -6 if hover else 0
            card = Image.new("RGBA", (w, h), (255, 240, 240, 240) if hover else (255, 255, 255, 200))
            sh, _ = shadow_for((w, h), 16, blur=6, alpha=110 if hover else 70, pad=10)
            base = Image.new("RGBA", (w + 20, h + 32), (0, 0, 0, 0))
            base.alpha_composite(sh, (0, 12 + lift))
            base.paste(card, (10, 10 + lift), rounded_mask((w, h), 16))
            if hover:
                ImageDraw.Draw(base).rounded_rectangle(
                    (10, 10 + lift, 10 + w - 1, 10 + lift + h - 1), 16, outline=ROJO, width=2)
            ss = 4
            circ = foto.resize((size * ss, size * ss), Image.LANCZOS).convert("RGBA")
            mask = Image.new("L", circ.size, 0)
            ImageDraw.Draw(mask).ellipse((0, 0, circ.width - 1, circ.height - 1), fill=255)
            ring = Image.new("RGBA", ((size + 6) * ss, (size + 6) * ss), (0, 0, 0, 0))
            ImageDraw.Draw(ring).ellipse((0, 0, ring.width - 1, ring.height - 1), fill=hex_rgb(ROJO) + (255,))
            ring.paste(circ, (3 * ss, 3 * ss), mask)
            ring = ring.resize((size + 6, size + 6), Image.LANCZOS)
            base.alpha_composite(ring, (10 + (w - size - 6) // 2, 10 + lift + 18))
            return base

        f = tkfont.Font(family="Arial", size=-13, weight="bold")
        t = self.canvas.create_text(x + w // 2, y + 18 + size + 6 + 12, text=nombre, font=f,
                                    fill="#222", width=w - 20, justify="center", anchor="n",
                                    tags=("content",))
        c = self.canvas
        self.sprites.append(dict(
            x=x - 10, y=y - 10, cursor=None, cmd=None,
            n=lambda: self.sprite(f"card:{nombre}:n", lambda: build(False)),
            h=lambda: self.sprite(f"card:{nombre}:h", lambda: build(True)),
            enter=lambda: (c.itemconfig(t, fill=ROJO), c.move(t, 0, -6)),
            leave=lambda: (c.itemconfig(t, fill="#222"), c.move(t, 0, 6))))


if __name__ == "__main__":
    try:  # nitidez en pantallas HiDPI de Windows
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    App().mainloop()
