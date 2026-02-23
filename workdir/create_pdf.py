import matplotlib.pyplot as plt

from textwrap import fill
from matplotlib import rcParams
from matplotlib.backends.backend_pdf import PdfPages

def make_pages(items, per_page):
    for i in range(0, len(items), per_page):
        yield items[i:i+per_page]

def render_page(ax, entries, title, show_meaning=False, cols=2, font_size=12, lines_per_word=1):
    ax.axis("off")
    ax.text(0.5, 0.97, title, ha="center", va="top", fontsize=font_size+4, fontweight="bold")
    margin_x, margin_top, margin_bottom = 0.06, 0.12, 0.08
    x0, x1 = margin_x, 1 - margin_x
    y_top, y_bottom = 1 - margin_top, margin_bottom
    width, height = x1 - x0, y_top - y_bottom
    col_w = width / cols

    # 1ページに載せる行数（見やすさ重視で調整可）
    rows_per_col = 24
    row_h = height / rows_per_col
    idx = 0
    for c in range(cols):
        x_left = x0 + c * col_w + 0.01
        for r in range(rows_per_col):
            if idx >= len(entries): break
            word, meaning = entries[idx]
            y = y_top - r * row_h
            ax.text(x_left, y-0.004, f"{idx+1}. {word}", ha="left", va="top", fontsize=font_size)
            if show_meaning:
                ax.text(x_left + 0.3, y-0.004, fill(meaning, 40), ha="left", va="top", fontsize=font_size-1)
            else:
                # 解答を隠す代わりに横線を引いて記入欄に
                for k in range(lines_per_word):
                    y_line = y - (k+0.6)*row_h/lines_per_word
                    ax.plot([x_left, x_left + col_w - 0.02], [y_line, y_line], linewidth=0.8)
            idx += 1

def save_pdf(entries, filepath, title, show_meaning, cols=2, font_size=12, lines_per_word=1):
    per_page = 24 * cols  # rows_per_col * cols
    with PdfPages(filepath) as pdf:
        for page_items in make_pages(entries, per_page):
            fig = plt.figure(figsize=(8.27, 11.69))  # A4縦
            ax = fig.add_axes([0, 0, 1, 1])
            render_page(ax, page_items, title, show_meaning, cols, font_size, lines_per_word)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

