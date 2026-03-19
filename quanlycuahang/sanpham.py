import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import pyodbc

# =========================================================
# ===== KẾT NỐI SQL SERVER =====
# =========================================================
def connect_db():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=NguyenQuangAnh;"
        "DATABASE=ShopThoiTrang_Python;"
        "Trusted_Connection=yes;"
    )
    return conn, conn.cursor()


def giao_dien_sanpham(frame):

    # ===== CLEAR UI =====
    for w in frame.winfo_children():
        w.destroy()

    # ===== TIÊU ĐỀ =====
    tk.Label(frame, text="QUẢN LÝ SẢN PHẨM",
             font=("Arial", 20, "bold"),
             bg="#ecf0f1").pack(pady=10)

    main = tk.Frame(frame, bg="#ecf0f1")
    main.pack(fill="both", expand=True, padx=20)

    # =========================================================
    # ===== FORM NHẬP (UI) =====
    # =========================================================
    form = tk.Frame(main, bg="#ecf0f1")
    form.pack(pady=10)

    def row(label, r):
        tk.Label(form, text=label, bg="#ecf0f1").grid(row=r, column=0, padx=5, pady=5, sticky="w")
        e = tk.Entry(form, width=25)
        e.grid(row=r, column=1, pady=5)
        return e

    ten = row("Tên", 0)
    gia = row("Giá", 1)
    sl = row("Số lượng", 2)

    # =========================================================
    # ===== ẢNH =====
    # =========================================================
    img_label = tk.Label(form, bg="#ecf0f1")
    img_label.grid(row=0, column=2, rowspan=4, padx=20)

    img_path = None

    def chon_anh():
        nonlocal img_path
        path = filedialog.askopenfilename(filetypes=[("Image", "*.png *.jpg *.jpeg")])
        if path:
            img_path = path
            img = Image.open(path)
            img = img.resize((100, 100))
            img = ImageTk.PhotoImage(img)

            img_label.config(image=img)
            img_label.image = img

    tk.Button(form, text="📷 Chọn ảnh",
              bg="#2980b9", fg="white",
              command=chon_anh).grid(row=3, column=2)

    # =========================================================
    # ===== KẾT NỐI DB =====
    # =========================================================
    conn, cursor = connect_db()

    # =========================================================
    # ===== TABLE =====
    # =========================================================
    tree = ttk.Treeview(main, columns=("id","ten","gia","sl"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("ten", text="Tên")
    tree.heading("gia", text="Giá")
    tree.heading("sl", text="Số lượng")

    tree.pack(fill="both", expand=True, pady=10)

    selected_id = None

    # =========================================================
    # ===== FUNCTIONS =====
    # =========================================================

    def load():
        tree.delete(*tree.get_children())
        cursor.execute("""
            SELECT MaSanPham, TenSanPham, Gia, SoLuong 
            FROM SanPham
        """)
        for row in cursor.fetchall():
            tree.insert("", "end", values=(
                int(row[0]),
                row[1],
                float(row[2]),
                int(row[3])
            ))

    def clear():
        nonlocal img_path, selected_id
        ten.delete(0, tk.END)
        gia.delete(0, tk.END)
        sl.delete(0, tk.END)
        img_label.config(image="")
        img_label.image = None
        img_path = None
        selected_id = None

    def on_select(event):
        nonlocal selected_id, img_path

        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            data = item["values"]

            selected_id = data[0]
            if isinstance(selected_id, tuple):
                selected_id = selected_id[0]

            selected_id = int(selected_id)

            ten.delete(0, tk.END)
            gia.delete(0, tk.END)
            sl.delete(0, tk.END)

            ten.insert(0, data[1])
            gia.insert(0, data[2])
            sl.insert(0, data[3])

            cursor.execute(
                "SELECT HinhAnh FROM SanPham WHERE MaSanPham=?",
                (selected_id,)
            )
            result = cursor.fetchone()

            if result and result[0]:
                img_path = result[0]
                try:
                    img = Image.open(img_path)
                    img = img.resize((100, 100))
                    img = ImageTk.PhotoImage(img)

                    img_label.config(image=img)
                    img_label.image = img
                except:
                    img_label.config(image="")

    tree.bind("<<TreeviewSelect>>", on_select)

    # ===== THÊM =====
    def them():
        if ten.get() == "" or gia.get() == "" or sl.get() == "":
            messagebox.showwarning("Lỗi", "Nhập đầy đủ thông tin")
            return

        cursor.execute("""
            INSERT INTO SanPham (TenSanPham, Gia, SoLuong, MaDanhMuc, HinhAnh)
            VALUES (?, ?, ?, NULL, ?)
        """, (ten.get(), float(gia.get()), int(sl.get()), img_path))

        conn.commit()
        load()
        clear()

    # ===== SỬA =====
    def sua():
        if selected_id is None:
            messagebox.showwarning("Lỗi", "Chọn sản phẩm cần sửa")
            return

        cursor.execute("""
            UPDATE SanPham
            SET TenSanPham=?, Gia=?, SoLuong=?, MaDanhMuc=NULL, HinhAnh=?
            WHERE MaSanPham=?
        """, (ten.get(), float(gia.get()), int(sl.get()), img_path, selected_id))

        conn.commit()
        load()
        clear()

    # ===== XÓA =====
    def xoa():
        if selected_id is None:
            messagebox.showwarning("Lỗi", "Chọn sản phẩm cần xóa")
            return

        cursor.execute("DELETE FROM SanPham WHERE MaSanPham=?", (selected_id,))
        conn.commit()
        load()
        clear()

    # =========================================================
    # ===== BUTTON =====
    # =========================================================
    btn_frame = tk.Frame(main, bg="#ecf0f1")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Thêm", bg="#27ae60", fg="white",
              width=12, command=them).pack(side="left", padx=5)

    tk.Button(btn_frame, text="Sửa", bg="#f39c12", fg="white",
              width=12, command=sua).pack(side="left", padx=5)

    tk.Button(btn_frame, text="Xóa", bg="red", fg="white",
              width=12, command=xoa).pack(side="left", padx=5)

    tk.Button(btn_frame, text="Clear",
              width=12, command=clear).pack(side="left", padx=5)

    load()
