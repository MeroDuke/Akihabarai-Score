from PyQt6.QtGui import QPainter, QPixmap


def trim_pixmap(pm: QPixmap, bg_color, pad: int = 12) -> QPixmap:
    img = pm.toImage().convertToFormat(pm.toImage().Format.Format_ARGB32)
    w, h = img.width(), img.height()

    br, bgc, bb = bg_color.red(), bg_color.green(), bg_color.blue()

    left, right = w, -1
    top, bottom = h, -1
    tol = 8

    for y in range(h):
        for x in range(w):
            c = img.pixelColor(x, y)
            if (
                abs(c.red() - br) > tol
                or abs(c.green() - bgc) > tol
                or abs(c.blue() - bb) > tol
            ):
                if x < left:
                    left = x
                if x > right:
                    right = x
                if y < top:
                    top = y
                if y > bottom:
                    bottom = y

    if right < left or bottom < top:
        out = QPixmap(w + pad * 2, h + pad * 2)
        out.fill(bg_color)
        p = QPainter(out)
        p.drawPixmap(pad, pad, pm)
        p.end()
        return out

    cropped = pm.copy(left, top, (right - left + 1), (bottom - top + 1))

    out = QPixmap(cropped.width() + pad * 2, cropped.height() + pad * 2)
    out.fill(bg_color)
    p = QPainter(out)
    p.drawPixmap(pad, pad, cropped)
    p.end()
    return out