import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# ===== KẾT NỐI SQL SERVER =====
def get_conn():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=NguyenQuangAnh;"
        "DATABASE=ShopThoiTrang_Python;"
        "Trusted_Connection=yes;"
    )

def giao_dien_khachhang(frame):

    for w in frame.winfo_children():
        w.destroy()

    tk.Label(frame, text="KHÁCH HÀNG", font=("Arial", 16)).pack()

    form = tk.Frame(frame)
    form.pack()

    labels = ["Tài khoản", "Tên", "SĐT", "Địa chỉ", "SL mua", "Tổng tiền"]
    entries = []

    for i, text in enumerate(labels):
        tk.Label(form, text=text).grid(row=i, column=0, padx=5, pady=5)
        e = tk.Entry(form)
        e.grid(row=i, column=1, padx=5, pady=5)
        entries.append(e)

    tree = ttk.Treeview(frame)
    tree["columns"] = ("tk", "ten", "sdt", "dc", "sl", "tong")

    tree.heading("#0", text="ID")
    tree.heading("tk", text="TK")
    tree.heading("ten", text="Tên")
    tree.heading("sdt", text="SĐT")
    tree.heading("dc", text="Địa chỉ")
    tree.heading("sl", text="SL")
    tree.heading("tong", text="Tổng")

    tree.column("#0", width=50)
    tree.pack(fill="both", expand=True)

    # =============================
    # LOAD DATA TỪ DATABASE
    # =============================
    def load():
        conn = get_conn()
        cursor = conn.cursor()

        tree.delete(*tree.get_children())

        cursor.execute("SELECT * FROM KhachHang")
        for row in cursor.fetchall():
            tree.insert("", "end", text=row[0], values=row[1:])

        conn.close()

    # =============================
    def clear():
        for e in entries:
            e.delete(0, tk.END)

    # =============================
    # THÊM
    # =============================
    def them():
        data = [e.get() for e in entries]

        if "" in data:
            messagebox.showwarning("Lỗi", "Nhập đầy đủ thông tin")
            return

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO KhachHang (TaiKhoan, Ten, SDT, DiaChi, SoLuongMua, TongTien)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)

        conn.commit()
        conn.close()

        load()
        clear()

    # =============================
    # CHỌN DÒNG
    # =============================
    def chon_dong(event):
        item = tree.selection()
        if item:
            values = tree.item(item)["values"]
            for i in range(len(entries)):
                entries[i].delete(0, tk.END)
                entries[i].insert(0, values[i])

    # =============================
    # SỬA
    # =============================
    def sua():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Lỗi", "Chọn dòng cần sửa")
            return

        id_selected = tree.item(item)["text"]
        data = [e.get() for e in entries]

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE KhachHang
            SET TaiKhoan=?, Ten=?, SDT=?, DiaChi=?, SoLuongMua=?, TongTien=?
            WHERE MaKH=?
        """, data + [id_selected])

        conn.commit()
        conn.close()

        load()
        clear()

    # =============================
    # XÓA
    # =============================
    def xoa():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Lỗi", "Chọn dòng cần xóa")
            return

        id_selected = tree.item(item)["text"]

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM KhachHang WHERE MaKH=?", id_selected)

        conn.commit()
        conn.close()

        load()
        clear()

    tree.bind("<<TreeviewSelect>>", chon_dong)

    btn_frame = tk.Frame(frame)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Thêm", command=them).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Sửa", command=sua).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Xóa", command=xoa).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Clear", command=clear).grid(row=0, column=3, padx=5)

    # LOAD LẦN ĐẦU
    load()
