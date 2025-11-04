# kilitli_pdf_sec_ve_ac.py
# Çalıştır: python kilitli_pdf_sec_ve_ac.py
# Açıklama: GUI ile PDF seçtirir; eğer şifreliyse parola ister; şifre çözülürse
# aynı isimle (aynı klasörde) geçici dosya kullanarak üzerine yazar.
# Başarı/başarısızlık mesajı gösterir.

import os
import tempfile
import shutil
import traceback
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

from PyPDF2 import PdfReader, PdfWriter

def unlock_and_replace(path: str, password: str = ""):
    reader = PdfReader(path)

    if reader.is_encrypted:
        # önce boş parola dene
        try:
            reader.decrypt("")
        except Exception:
            pass
        if reader.is_encrypted and password:
            try:
                reader.decrypt(password)
            except Exception:
                pass

    writer = PdfWriter()

    # sayfaları ekle
    for p in reader.pages:
        writer.add_page(p)

    # metadata kopyala (varsa)
    try:
        if reader.metadata:
            writer.add_metadata(reader.metadata)
    except Exception:
        pass

    # geçici dosya aynı klasörde
    dirname = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(prefix="._tmp_", suffix=".pdf", dir=dirname)
    os.close(fd)

    with open(tmp_path, "wb") as f:
        writer.write(f)

    # yedeğini almak istersen comment kaldır:
    # shutil.copy2(path, path + ".bak")

    os.replace(tmp_path, path)  # atomik değiştir

def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Kilitli PDF seçin",
        filetypes=[("PDF dosyaları", "*.pdf"), ("Tüm dosyalar", "*.*")],
    )
    if not file_path:
        return  # kullanıcı iptal etti

    # Eğer dosya okunamıyorsa kullanıcıyı bilgilendir
    if not os.path.isfile(file_path):
        messagebox.showerror("Hata", "Seçilen dosya bulunamadı.")
        return

    # Eğer şifreliyse parola sor
    try:
        reader = PdfReader(file_path)
    except Exception as e:
        messagebox.showerror("Hata", f"PDF açılırken hata: {e}")
        return

    pwd = ""
    if reader.is_encrypted:
        pwd = simpledialog.askstring("Parola", "PDF şifresi varsa girin (iptal = deneme yok):", show="*")
        if pwd is None:
            # kullanıcı iptal etti; yine denemek istiyorsan boş bırak
            pwd = ""

    # Deneme ve işlem
    try:
        unlock_and_replace(file_path, pwd)
        messagebox.showinfo("Tamamlandı", "PDF başarıyla yeniden kaydedildi (aynı isimle).")
    except Exception as e:
        tb = traceback.format_exc()
        # hata ayrıntısını istersen logla; kullanıcıya kısa bilgi ver
        messagebox.showerror("Başarısız", f"İşlem başarısız: {e}")

if __name__ == "__main__":
    main()
