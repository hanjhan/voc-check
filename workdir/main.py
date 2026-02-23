import csv
import math
import os
import sys
from datetime import date
from datetime import datetime
from textwrap import fill

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from matplotlib.backends.backend_pdf import PdfPages

import create_pdf

rcParams['font.family'] = 'IPAPGothic'

ROOT_PATH = '/workdir/data/'

word_dict = {}
word_dict_basic = {}
word_dict_standard = {}
word_dict_advance = {}

word_list = []
word_list_basic = []
word_list_standard = []
word_list_advance = []

weights_all = []
weights_basic = []
weights_standard = []
weights_advance = []

def add_word_to_each_dict(word, meaning, trimmed_filename):
    if len(trimmed_filename) >= 5 and trimmed_filename[-5:] == 'basic':
        word_dict_basic[word] = meaning
    elif len(trimmed_filename) >= 8 and trimmed_filename[-8:] == 'standard':
        word_dict_standard[word] = meaning
    else:
        word_dict_advance[word] = meaning

def add_word(csv_row, trimmed_filename):
    if len(csv_row) >= 2:
        word = csv_row[0].strip()
        meaning = csv_row[1].strip()
        word_dict[word] = meaning
        add_word_to_each_dict(word, meaning, trimmed_filename)

def days_since(datestr):
    if not datestr:
        return 9999
    return (date.today() - datetime.strptime(datestr, "%Y-%m-%d").date()).days


def add_weight(weight, trimmed_filename):
    weights_all.append(weight)
    if len(trimmed_filename) >= 5 and trimmed_filename[-5:] == 'basic':
        weights_basic.append(weight)
    elif len(trimmed_filename) >= 8 and trimmed_filename[-8:] == 'standard':
        weights_standard.append(weight)
    else:
        weights_advance.append(weight)


def calc_weight(csv_row, trimmed_filename):
    if len(csv_row) >= 6:
        try:
            weight = float(csv_row[2].strip())
        except ValueError:
            print(f"Failed to convert {csv_row[2].strip()} to float")
            print(f"Target word: \"{csv_row[0].strip()}\"")
            sys.exit(1)
        last_seen = csv_row[3].strip()
        last_correct = csv_row[4].strip()
        try:
            streak = int(csv_row[5].strip())
        except ValueError:
            print("Failed to convert the streak number to int")
            print(f"Target word: \"{csv_row[0].strip()}\"")
            sys.exit(1)
        day_boost = min(days_since(last_seen)/7, 8)
        correct_boost = min(days_since(last_correct)/7, 8)
        weight *= (day_boost + correct_boost * 0.5) * math.pow(0.8, streak)
        print(f"word: {csv_row[0]}, weight: {weight}")
        add_weight(weight, trimmed_filename)

def load_csv(csv_file):
    print(f"Loading {csv_file}")
    trimmed_filename = csv_file[:-4]
    with open(csv_file, newline="", encoding="utf-8") as f:
        header_check = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)
        reader = csv.reader(f)
        for row in reader:
            if header_check:
                header_check = False
                continue
            add_word(row, trimmed_filename)
            calc_weight(row, trimmed_filename)

def check_file(path):
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if filename[-3:] == 'csv':
                load_csv(os.path.join(dirpath,filename))

def create_word_dict(path):
    check_file(path)

def pick_words_from_basic():
    nums = 9
    picked = np.random.choice(word_list_basic, size=nums, replace=False, p=np.array(weights_basic)/sum(weights_basic))
    return picked

def pick_words_from_standard():
    nums = 8
    picked = np.random.choice(word_list_standard, size=nums, replace=False, p=np.array(weights_standard)/sum(weights_standard))
    return picked

def pick_words_from_advance():
    nums = 3
    picked = np.random.choice(word_list_advance, size=nums, replace=False, p=np.array(weights_advance)/sum(weights_advance))
    return picked

def pick_words():
    picked_words = []

    picked_from_basic = pick_words_from_basic()
    picked_from_standard = pick_words_from_standard()
    picked_from_advance = pick_words_from_advance()

    for word in picked_from_basic:
        picked_words.append(word)
    for word in picked_from_standard:
        picked_words.append(word)
    for word in picked_from_advance:
        picked_words.append(word)

    return picked_words

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

    rows_per_col = 24
    row_h = height / rows_per_col
    idx = 0
    for c in range(cols):
        x_left = x0 + c * col_w + 0.01
        for r in range(rows_per_col):
            if idx >= len(entries):
                break
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

if __name__ == "__main__":
    create_word_dict(ROOT_PATH)
    word_list_basic = list(word_dict_basic.keys())
    word_list_standard = list(word_dict_standard.keys())
    word_list_advance = list(word_dict_advance.keys())
    voc_test_words = pick_words()

    for w in voc_test_words:
        print(f"{w}\n{word_dict[w]}")
    to_pdf = list((w, word_dict[w]) for w in voc_test_words)
    create_pdf.save_pdf(to_pdf, "test.pdf", title="Vocabulary Test", show_meaning=False, cols=2, lines_per_word=1)
    create_pdf.save_pdf(to_pdf, "answer.pdf", title="Vocabulary Test", show_meaning=True, cols=2, lines_per_word=1)
