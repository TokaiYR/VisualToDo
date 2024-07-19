import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import shutil
import ctypes
from ctypes import wintypes

# デスクトップパス取得関数
def desktop_path():
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 0x0000, None, 0, buf)
    return buf.value

# デスクトップパス取得
desktop_path = desktop_path()
visual_todo_path = os.path.join(desktop_path, "ビジュアルToDo")
data_folder_path = os.path.join(visual_todo_path, "データ")

# ファイル作成数とタイトル文字数制限
MAX_FILES = 15
MAX_TITLE_LENGTH = 10

current_image_index = 0
image_files = []
buttons = []

# フォルダとテキストの作成
def make_file(entry_name):
    if len(entry_name) > MAX_TITLE_LENGTH:
        messagebox.showerror("エラー", f"タイトルは {MAX_TITLE_LENGTH} 文字以内で入力してください")
        return

    if not entry_name.isalnum() and not entry_name.isspace():
        messagebox.showerror("エラー", "タイトルに記号は使用できません")
        return

    folder_path = os.path.join(data_folder_path, entry_name)
    file_path = os.path.join(folder_path, f"{entry_name}.txt")

    if os.path.exists(folder_path):
        messagebox.showerror("エラー", "その名前は既に使用されています")
    else:
        os.makedirs(folder_path)
        with open(file_path, "w") as f:
            f.write("")
        add_new_button(entry_name)

# 予定ボタン作成
def add_new_button(entry_name):
    new_button = tk.Button(root, text=entry_name, command=lambda: edit_file(entry_name))
    new_button.place(x=10, y=110 + 30 * len(buttons))
    buttons.append(new_button)

# テキストファイル表示と画像表示
def edit_file(entry_name):
    global current_image_index, image_files

    folder_path = os.path.join(data_folder_path, entry_name)
    text_file_path = os.path.join(folder_path, f"{entry_name}.txt")
    
    # フォルダ内の画像ファイルを取得
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    current_image_index = 0

    # テキスト表示
    with open(text_file_path, "r") as f:
        content = f.read()
    text.delete("1.0", tk.END)
    text.insert(tk.END, content)
    current_file.set(text_file_path)

    # タイトル表示の更新
    title_label.config(text=entry_name)

    # 画像表示
    if image_files:
        load_image(os.path.join(folder_path, image_files[current_image_index]))
    else:
        show_image_placeholder()

# 画像ファイルのロード
def load_image(image_path):
    global image_label, img
    if image_label:
        image_label.destroy()

    img = Image.open(image_path).resize((250, 250), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)
    image_label = tk.Label(root, image=img)
    image_label.place(x=500, y=100)

    update_buttons_state()

# 画像がない場合のメッセージ
def show_image_placeholder():
    global image_label
    if image_label:
        image_label.destroy()

    image_label = tk.Label(root, text="画像を追加できます", font=("Arial", 20), bg="#e0ffff")
    image_label.place(x=520, y=200)

    update_buttons_state()

# 画像ファイルの追加
def add_image():
    file_path = current_file.get()
    if not file_path:
        messagebox.showerror("エラー", "ファイルが選択されていません")
        return

    image_path = filedialog.askopenfilename(title="画像ファイルを選択", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if not image_path:
        return

    image_filename = os.path.basename(image_path)
    destination_folder = os.path.dirname(file_path)

    try:
        shutil.copy(image_path, os.path.join(destination_folder, image_filename))
        edit_file(os.path.basename(destination_folder))
    except Exception:
        pass

# テキスト保存
def save_file():
    file_path = current_file.get()
    if file_path:
        with open(file_path, "w") as f:
            f.write(text.get("1.0", tk.END).strip())

# 予定追加時の入力欄
def newfile_window():
    entry_window = tk.Toplevel(root)
    entry_window.title("予定の追加")
    tk.Label(entry_window, text="タイトルを入力").pack(pady=10)
    entry = tk.Entry(entry_window)
    entry.pack(pady=10)
    tk.Button(entry_window, text="作成", command=lambda: [make_file(entry.get()), entry_window.destroy()]).pack(pady=10)

# 「データ」フォルダ内のファイル読込とボタンを作成
def load_existing_files():
    if os.path.exists(data_folder_path):
        for folder_name in os.listdir(data_folder_path):
            folder_path = os.path.join(data_folder_path, folder_name)
            if os.path.isdir(folder_path):
                add_new_button(folder_name)

# 「前」ボタン処理
def previous_image():
    global current_image_index
    if current_image_index > 0:
        current_image_index -= 1
        load_image(os.path.join(os.path.dirname(current_file.get()), image_files[current_image_index]))

# 「次」ボタン処理
def next_image():
    global current_image_index
    if current_image_index < len(image_files) - 1:
        current_image_index += 1
        load_image(os.path.join(os.path.dirname(current_file.get()), image_files[current_image_index]))

# 画像削除の処理
def delete_image():
    global current_image_index
    if image_files:
        file_path = os.path.join(os.path.dirname(current_file.get()), image_files[current_image_index])
        try:
            os.remove(file_path)
            del image_files[current_image_index]

            if current_image_index >= len(image_files):
                current_image_index -= 1
            
            if image_files:
                load_image(os.path.join(os.path.dirname(current_file.get()), image_files[current_image_index]))
            else:
                show_image_placeholder()
            
        except Exception:
            pass

# 予定削除の処理
def delete_schedule():
    file_path = current_file.get()
    if not file_path:
        messagebox.showerror("エラー", "ファイルが選択されていません")
        return

    result = messagebox.askquestion("確認", "本当に削除しますか？", icon='warning')
    if result == 'yes':
        try:
            folder_path = os.path.dirname(file_path)
            shutil.rmtree(folder_path)
            messagebox.showinfo("完了", "予定を削除しました\n更新してください")
            current_file.set("")
            text.delete("1.0", tk.END)
            title_label.config(text="")
            show_image_placeholder()
            load_existing_files()

        except Exception:
            pass

# ボタンの有効/無効
def update_buttons_state():
    prev_button.config(state=tk.NORMAL if current_image_index > 0 else tk.DISABLED)
    next_button.config(state=tk.NORMAL if current_image_index < len(image_files) - 1 else tk.DISABLED)
    delete_button.config(state=tk.NORMAL if image_files else tk.DISABLED)

# ウィンドウ表示
root = tk.Tk()
root.title("ビジュアルToDo")
root.geometry("800x600")
root.configure(bg="#e0ffff")

# ロゴ表示
tk.Label(root, text="VisualToDo", font=("Bauhaus 93", 24), fg="#32cd32", bg="#e0ffff").place(x=10, y=10)

# 横線
tk.Canvas(root, width=780, height=2, bg="#00bfff", highlightthickness=0).place(x=10, y=50)

# 予定一覧背景
tk.Canvas(root, width=180, height=545, bg="#b0c4de", highlightthickness=0).place(x=0, y=55)

# 「予定を追加」ボタン
tk.Button(root, text="予定を追加", command=newfile_window).place(x=10, y=70)

# 「画像を追加」ボタン
tk.Button(root, text="画像を追加", command=add_image).place(x=600, y=70)

# 「予定を削除」ボタン
tk.Button(root, text="予定を削除", command=delete_schedule).place(x=100, y=70)

# テキスト編集エリア
text = tk.Text(root, width=40, height=37)
text.place(x=190, y=100)

# テキストファイルのタイトル表示
title_label = tk.Label(root, text="", font=("Arial", 16), bg="#e0ffff")
title_label.place(x=200, y=60)

# 保存ボタン
tk.Button(root, text="保存", width=5, height=2, command=save_file).place(x=430, y=55)

# 画像表示用のラベルと画像オブジェクト
image_label = None

# 「前」ボタン
tk.Button(root, text="前", command=previous_image).place(x=550, y=360)

# 「次」ボタン
tk.Button(root, text="次", command=next_image).place(x=600, y=360)

# 「画像を削除」ボタン
tk.Button(root, text="画像を削除", command=delete_image).place(x=690, y=360)

current_file = tk.StringVar()

# プログラム起動時に既存のファイル読込
load_existing_files()

root.mainloop()