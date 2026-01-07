import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# =========================
# Color Palette - Forest Green & White
# =========================
COLORS = {
    "forest_dark": "#1B4D3E",
    "forest_medium": "#2D6A4F",
    "forest_light": "#40916C",
    "forest_lighter": "#52B788",
    "forest_pale": "#74C69D",
    "bg_white": "#FFFFFF",
    "bg_light": "#F0F9F7",
    "text_dark": "#1B4D3E",
    "text_light": "#5A8E7A",
    "border_subtle": "#D4E8E1",
    "accent_gold": "#D4AF37",
    "success": "#52B788",
    "danger": "#E63946",
    "table_alt": "#E8F5F1",
}

FONTS = {
    "title": ("Segoe UI", 22, "bold"),
    "subtitle": ("Segoe UI", 12, "normal"),
    "heading": ("Segoe UI", 13, "bold"),
    "label": ("Segoe UI", 10, "normal"),
    "button": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9, "normal"),
}

# =========================
# Database Connection
# =========================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="PK12345678",
        database="webgui"
    )

# =========================
# Animation Helper
# =========================
class AnimatedButton(tk.Button):
    def __init__(self, parent, **kwargs):
        self.normal_bg = kwargs.get('bg', COLORS["forest_light"])
        self.hover_bg = kwargs.get('activebackground', COLORS["forest_lighter"])
        super().__init__(parent, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(bg=self.hover_bg)

    def on_leave(self, event):
        self.config(bg=self.normal_bg)

# =========================
# CRUD Operations
# =========================
def add_student():
    studentname = e_name.get().strip()
    coursename = e_course.get().strip()
    fee = e_fee.get().strip()

    if not studentname or not coursename or not fee:
        show_notification("Input Error", "All fields must be filled.", "error")
        return

    try:
        fee = int(fee)
    except ValueError:
        show_notification("Input Error", "Fee must be a valid number.", "error")
        return

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO students (name, course, fee) VALUES (%s, %s, %s)"
        cursor.execute(sql, (studentname, coursename, fee))
        conn.commit()
        show_notification("Success", "Student added successfully!", "success")
        clear_form()
        load_students()
    except mysql.connector.Error as err:
        show_notification("Database Error", str(err), "error")
    finally:
        if conn:
            conn.close()

def update_student():
    student_id = e_id.get().strip()
    if not student_id:
        show_notification("Selection Error", "Please select a student to update.", "error")
        return

    studentname = e_name.get().strip()
    coursename = e_course.get().strip()
    fee = e_fee.get().strip()

    if not studentname or not coursename or not fee:
        show_notification("Input Error", "All fields must be filled.", "error")
        return

    try:
        fee = int(fee)
    except ValueError:
        show_notification("Input Error", "Fee must be a valid number.", "error")
        return

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE students SET name=%s, course=%s, fee=%s WHERE id=%s"
        cursor.execute(sql, (studentname, coursename, fee, student_id))
        conn.commit()
        show_notification("Success", "Student updated successfully!", "success")
        clear_form()
        load_students()
    except mysql.connector.Error as err:
        show_notification("Database Error", str(err), "error")
    finally:
        if conn:
            conn.close()

def delete_student():
    student_id = e_id.get().strip()
    if not student_id:
        show_notification("Selection Error", "Please select a student to delete.", "error")
        return

    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=%s", (student_id,))
            conn.commit()
            show_notification("Success", "Student deleted successfully!", "success")
            clear_form()
            load_students()
        except mysql.connector.Error as err:
            show_notification("Database Error", str(err), "error")
        finally:
            if conn:
                conn.close()

def view_student_details():
    student_id = e_id.get().strip()
    if not student_id:
        messagebox.showwarning("Selection Error", "Please select a student to view details.")
        return

    studentname = e_name.get()
    coursename = e_course.get()
    fee = e_fee.get()

    details = f"""
╔════════════════════════════════╗
║     STUDENT DETAILS            ║
╠════════════════════════════════╣
║ ID:      {student_id:<24} ║
║ Name:    {studentname:<24} ║
║ Course:  {coursename:<24} ║
║ Fee:     ₹{fee:<23} ║
╚════════════════════════════════╝
"""
    messagebox.showinfo("Student Details", details)

def load_students():
    for row in treeview.get_children():
        treeview.delete(row)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()

        for idx, row in enumerate(rows):
            tag = "oddrow" if idx % 2 == 0 else "evenrow"
            treeview.insert("", "end", values=row, tags=(tag,))
    except mysql.connector.Error as err:
        show_notification("Database Error", str(err), "error")
    finally:
        if conn:
            conn.close()

    update_button_states()

def on_treeview_select(event):
    selected = treeview.selection()
    if selected:
        values = treeview.item(selected[0], "values")
        e_id.config(state="normal")
        e_id.delete(0, tk.END)
        e_id.insert(0, values[0])
        e_id.config(state="disabled")
        e_name.delete(0, tk.END)
        e_name.insert(0, values[1])
        e_course.delete(0, tk.END)
        e_course.insert(0, values[2])
        e_fee.delete(0, tk.END)
        e_fee.insert(0, values[3])
        update_button_states()

def clear_form():
    e_id.config(state="normal")
    e_id.delete(0, tk.END)
    e_id.config(state="disabled")
    e_name.delete(0, tk.END)
    e_course.delete(0, tk.END)
    e_fee.delete(0, tk.END)
    treeview.selection_remove(treeview.selection())
    update_button_states()

def update_button_states():
    if 'btn_update' not in globals() or 'btn_delete' not in globals() or 'btn_view_details' not in globals():
        return
    has_selection = len(treeview.selection()) > 0
    btn_update.config(state="normal" if has_selection else "disabled", bg=COLORS["forest_light"] if has_selection else COLORS["text_light"])
    btn_delete.config(state="normal" if has_selection else "disabled", bg=COLORS["danger"] if has_selection else COLORS["text_light"])
    btn_view_details.config(state="normal" if has_selection else "disabled", bg=COLORS["forest_pale"] if has_selection else COLORS["text_light"])

def show_notification(title, message, type_="info"):
    if type_ == "success":
        messagebox.showinfo(title, message)
    elif type_ == "error":
        messagebox.showerror(title, message)
    else:
        messagebox.showinfo(title, message)

# =========================
# GUI Setup
# =========================
root = tk.Tk()
root.title("Student Management System")
root.geometry("1000x650")
root.resizable(False, False)
root.config(bg=COLORS["bg_white"])

style = ttk.Style()
style.theme_use("clam")

# Treeview styling
style.configure(
    "Treeview",
    background=COLORS["bg_white"],
    foreground=COLORS["text_dark"],
    rowheight=32,
    font=FONTS["label"],
    fieldbackground=COLORS["bg_white"],
    borderwidth=0,
)
style.map("Treeview", background=[("selected", COLORS["forest_light"])])
style.configure(
    "Treeview.Heading",
    background=COLORS["forest_dark"],
    foreground=COLORS["bg_white"],
    font=FONTS["heading"],
    borderwidth=0,
)
style.map("Treeview.Heading", background=[("active", COLORS["forest_medium"])])

# ==================== SIDEBAR ====================
sidebar = tk.Frame(root, bg=COLORS["forest_dark"], width=220)
sidebar.pack(side="left", fill="y", padx=0, pady=0)
sidebar.pack_propagate(False)

# Gradient-like effect with frame layers
top_accent = tk.Frame(sidebar, bg=COLORS["forest_light"], height=4)
top_accent.pack(fill="x")

# Logo/Title section
logo_frame = tk.Frame(sidebar, bg=COLORS["forest_dark"])
logo_frame.pack(fill="x", padx=25, pady=30)

tk.Label(
    logo_frame,
    text="🌿",
    font=("Arial", 40),
    bg=COLORS["forest_dark"],
    fg=COLORS["forest_lighter"],
).pack(pady=(0, 12))

tk.Label(
    logo_frame,
    text="Student",
    font=("Segoe UI", 18, "bold"),
    bg=COLORS["forest_dark"],
    fg=COLORS["bg_white"],
    justify="center",
).pack()

tk.Label(
    logo_frame,
    text="Management",
    font=("Segoe UI", 18, "bold"),
    bg=COLORS["forest_dark"],
    fg=COLORS["forest_lighter"],
    justify="center",
).pack()

tk.Label(
    logo_frame,
    text="━━━━━━━━━━",
    font=("Segoe UI", 8),
    bg=COLORS["forest_dark"],
    fg=COLORS["forest_pale"],
).pack(pady=8)

tk.Label(
    logo_frame,
    text="Admin Panel",
    font=("Segoe UI", 10),
    bg=COLORS["forest_dark"],
    fg=COLORS["forest_pale"],
).pack(pady=(0, 5))

# Divider with accent
divider = tk.Frame(sidebar, bg=COLORS["forest_lighter"], height=2)
divider.pack(fill="x", pady=20)

# Button container
button_frame = tk.Frame(sidebar, bg=COLORS["forest_dark"])
button_frame.pack(fill="both", expand=True, padx=12, pady=15)

def create_sidebar_button(parent, text, icon, command, color=COLORS["forest_lighter"]):
    btn = AnimatedButton(
        parent,
        text=f"{icon}\n{text}",
        command=command,
        bg=color,
        fg=COLORS["bg_white"],
        font=("Segoe UI", 9, "bold"),
        border=0,
        activebackground=COLORS["forest_light"],
        activeforeground=COLORS["bg_white"],
        relief="flat",
        pady=14,
        cursor="hand2",
        wraplength=100,
    )
    btn.pack(fill="x", pady=8)
    return btn

btn_add = create_sidebar_button(button_frame, "Add\nStudent", "➕", add_student, COLORS["forest_lighter"])

# Placeholder buttons to be configured
btn_update = tk.Button(button_frame, text="placeholder", bg=COLORS["forest_light"])
btn_delete = tk.Button(button_frame, text="placeholder", bg=COLORS["danger"])
btn_view_details = tk.Button(button_frame, text="placeholder", bg=COLORS["forest_pale"])

# Configure update button
btn_update = AnimatedButton(
    button_frame,
    text="✏️\nUpdate",
    command=update_student,
    bg=COLORS["forest_light"],
    fg=COLORS["bg_white"],
    font=("Segoe UI", 9, "bold"),
    border=0,
    activebackground=COLORS["forest_lighter"],
    activeforeground=COLORS["bg_white"],
    relief="flat",
    pady=14,
    cursor="hand2",
    wraplength=100,
)
btn_update.pack(fill="x", pady=8)

# Configure delete button
btn_delete = AnimatedButton(
    button_frame,
    text="🗑️\nDelete",
    command=delete_student,
    bg=COLORS["danger"],
    fg=COLORS["bg_white"],
    font=("Segoe UI", 9, "bold"),
    border=0,
    activebackground=COLORS["danger"],
    activeforeground=COLORS["bg_white"],
    relief="flat",
    pady=14,
    cursor="hand2",
    wraplength=100,
)
btn_delete.pack(fill="x", pady=8)

# Configure view details button
btn_view_details = AnimatedButton(
    button_frame,
    text="👁️\nView",
    command=view_student_details,
    bg=COLORS["forest_pale"],
    fg=COLORS["bg_white"],
    font=("Segoe UI", 9, "bold"),
    border=0,
    activebackground=COLORS["forest_lighter"],
    activeforeground=COLORS["bg_white"],
    relief="flat",
    pady=14,
    cursor="hand2",
    wraplength=100,
)
btn_view_details.pack(fill="x", pady=8)

# Now we can safely call load_students which uses update_button_states
# Load students is moved after button definitions

btn_clear = AnimatedButton(
    button_frame,
    text="🔄 Clear Form",
    command=clear_form,
    bg=COLORS["forest_medium"],
    fg=COLORS["bg_white"],
    font=("Segoe UI", 9, "bold"),
    border=0,
    activebackground=COLORS["forest_light"],
    activeforeground=COLORS["bg_white"],
    relief="flat",
    pady=12,
    cursor="hand2",
)
btn_clear.pack(fill="x", pady=8)

# ==================== MAIN CONTENT ====================
main_content = tk.Frame(root, bg=COLORS["bg_light"])
main_content.pack(side="right", fill="both", expand=True, padx=0, pady=0)

# Top accent bar
accent_bar = tk.Frame(main_content, bg=COLORS["forest_lighter"], height=3)
accent_bar.pack(fill="x")

# Header section with shadow effect
header_frame = tk.Frame(main_content, bg=COLORS["bg_white"], highlightbackground=COLORS["border_subtle"], highlightthickness=1)
header_frame.pack(fill="x", padx=25, pady=(20, 15))

tk.Label(
    header_frame,
    text="📋 Student Records",
    font=FONTS["title"],
    bg=COLORS["bg_white"],
    fg=COLORS["forest_dark"],
).pack(anchor="w", padx=15, pady=(12, 5))

tk.Label(
    header_frame,
    text="Manage and organize student information efficiently",
    font=FONTS["small"],
    bg=COLORS["bg_white"],
    fg=COLORS["text_light"],
).pack(anchor="w", padx=15, pady=(0, 12))

# Form section with subtle shadow
form_frame = tk.Frame(main_content, bg=COLORS["bg_white"], highlightbackground=COLORS["border_subtle"], highlightthickness=1)
form_frame.pack(fill="x", padx=25, pady=(0, 15))

form_inner = tk.Frame(form_frame, bg=COLORS["bg_white"])
form_inner.pack(fill="x", padx=15, pady=12)

tk.Label(
    form_frame,
    text="Input Form",
    font=("Segoe UI", 10, "bold"),
    bg=COLORS["bg_white"],
    fg=COLORS["forest_dark"],
).pack(anchor="w", padx=15, pady=(8, 0))

def create_form_field(parent, label_text):
    field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
    field_frame.pack(fill="x", pady=8)

    tk.Label(
        field_frame,
        text=label_text,
        font=FONTS["label"],
        bg=COLORS["bg_white"],
        fg=COLORS["forest_dark"],
    ).pack(anchor="w", pady=(0, 5))

    entry = tk.Entry(
        field_frame,
        font=FONTS["label"],
        bg=COLORS["bg_light"],
        fg=COLORS["text_dark"],
        border=1,
        relief="solid",
        borderwidth=1,
    )
    entry.pack(fill="x", ipady=9)
    entry.config(highlightbackground=COLORS["forest_pale"], highlightthickness=1)
    return entry

e_id = create_form_field(form_inner, "Student ID")
e_id.config(state="disabled", bg=COLORS["table_alt"])

e_name = create_form_field(form_inner, "Full Name")
e_course = create_form_field(form_inner, "Course")
e_fee = create_form_field(form_inner, "Fee (₹)")

# Table section with shadow
table_frame = tk.Frame(main_content, bg=COLORS["bg_white"], highlightbackground=COLORS["border_subtle"], highlightthickness=1)
table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))

tk.Label(
    table_frame,
    text="📊 All Students",
    font=("Segoe UI", 11, "bold"),
    bg=COLORS["bg_white"],
    fg=COLORS["forest_dark"],
).pack(anchor="w", padx=15, pady=(12, 10))

cols = ("id", "name", "course", "fee")
treeview = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
treeview.tag_configure("oddrow", background=COLORS["bg_white"])
treeview.tag_configure("evenrow", background=COLORS["table_alt"])
treeview.pack(fill="both", expand=True, padx=15, pady=(0, 15))

treeview.column("id", width=60, anchor="center")
treeview.column("name", width=200, anchor="w")
treeview.column("course", width=150, anchor="w")
treeview.column("fee", width=100, anchor="e")

for col in cols:
    treeview.heading(col, text=col.upper())

# Scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=treeview.yview)
scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=(0, 15))
treeview.config(yscroll=scrollbar.set)

treeview.bind("<ButtonRelease-1>", on_treeview_select)

# Initialize - NOW safe to call after all buttons are defined
load_students()
root.mainloop()