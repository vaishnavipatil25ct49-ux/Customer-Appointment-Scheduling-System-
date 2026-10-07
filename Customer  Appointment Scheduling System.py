import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


# ---------- MYSQL CONNECTION ----------
def connect_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="pydroid",
        password="1234",
        database="appointment_db"
    )


# ---------- CREATE TABLES ----------
db = connect_db()
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(50)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    service VARCHAR(100),
    appointment_date VARCHAR(20),
    appointment_time VARCHAR(20),
    status VARCHAR(30)
)
""")

cur.execute("""
INSERT IGNORE INTO users(username, password)
VALUES ('admin', '1234')
""")

db.commit()
cur.close()
db.close()


# ---------- LOGIN ----------
def login():
    username = username_entry.get()
    password = password_entry.get()

    db = connect_db()
    cur = db.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    result = cur.fetchone()

    cur.close()
    db.close()

    if result:
        login_window.destroy()
        open_main_window()
    else:
        messagebox.showerror(
            "Login",
            "Invalid username or password"
        )


# ---------- MAIN WINDOW ----------
def open_main_window():

    root = tk.Tk()
    root.title("Customer Appointment Scheduling System")
    root.geometry("1000x650")

    # ---------- VARIABLES ----------
    customer = tk.StringVar()
    phone = tk.StringVar()
    email = tk.StringVar()
    service = tk.StringVar()
    date = tk.StringVar()
    time = tk.StringVar()
    status = tk.StringVar(value="Booked")
    search = tk.StringVar()

    # ---------- CLEAR ----------
    def clear():
        customer.set("")
        phone.set("")
        email.set("")
        service.set("")
        date.set("")
        time.set("")
        status.set("Booked")
        tree.selection_remove(tree.selection())

    # ---------- SHOW ----------
    def show():
        for item in tree.get_children():
            tree.delete(item)

        db = connect_db()
        cur = db.cursor()

        cur.execute("SELECT * FROM appointments ORDER BY id")

        for row in cur.fetchall():
            tree.insert("", tk.END, values=row)

        cur.close()
        db.close()

    # ---------- ADD ----------
    def add():
        if customer.get() == "" or phone.get() == "" or date.get() == "":
            messagebox.showwarning(
                "Warning",
                "Customer name, phone and date are required"
            )
            return

        db = connect_db()
        cur = db.cursor()

        cur.execute("""
        INSERT INTO appointments
        (customer_name, phone, email, service,
         appointment_date, appointment_time, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            customer.get(),
            phone.get(),
            email.get(),
            service.get(),
            date.get(),
            time.get(),
            status.get()
        ))

        db.commit()
        cur.close()
        db.close()

        messagebox.showinfo(
            "Success",
            "Appointment booked successfully"
        )

        clear()
        show()

    # ---------- SELECT ----------
    def select_record(event):
        selected = tree.focus()

        if not selected:
            return

        values = tree.item(selected, "values")

        customer.set(values[1])
        phone.set(values[2])
        email.set(values[3])
        service.set(values[4])
        date.set(values[5])
        time.set(values[6])
        status.set(values[7])

    # ---------- UPDATE ----------
    def update():
        selected = tree.focus()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Select an appointment"
            )
            return

        values = tree.item(selected, "values")
        appointment_id = values[0]

        db = connect_db()
        cur = db.cursor()

        cur.execute("""
        UPDATE appointments
        SET customer_name=%s,
            phone=%s,
            email=%s,
            service=%s,
            appointment_date=%s,
            appointment_time=%s,
            status=%s
        WHERE id=%s
        """, (
            customer.get(),
            phone.get(),
            email.get(),
            service.get(),
            date.get(),
            time.get(),
            status.get(),
            appointment_id
        ))

        db.commit()
        cur.close()
        db.close()

        messagebox.showinfo(
            "Success",
            "Appointment updated"
        )

        clear()
        show()

    # ---------- DELETE ----------
    def delete():
        selected = tree.focus()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Select an appointment"
            )
            return

        values = tree.item(selected, "values")
        appointment_id = values[0]

        answer = messagebox.askyesno(
            "Delete",
            "Delete this appointment?"
        )

        if answer:
            db = connect_db()
            cur = db.cursor()

            cur.execute(
                "DELETE FROM appointments WHERE id=%s",
                (appointment_id,)
            )

            db.commit()
            cur.close()
            db.close()

            messagebox.showinfo(
                "Success",
                "Appointment deleted"
            )

            clear()
            show()

    # ---------- SEARCH ----------
    def search_record():
        for item in tree.get_children():
            tree.delete(item)

        db = connect_db()
        cur = db.cursor()

        text = "%" + search.get() + "%"

        cur.execute("""
        SELECT * FROM appointments
        WHERE customer_name LIKE %s
           OR phone LIKE %s
           OR service LIKE %s
        """, (text, text, text))

        for row in cur.fetchall():
            tree.insert("", tk.END, values=row)

        cur.close()
        db.close()

    # ---------- TITLE ----------
    tk.Label(
        root,
        text="CUSTOMER APPOINTMENT SCHEDULING SYSTEM",
        font=("Arial", 12, "bold")
    ).pack(pady=10)

    # ---------- FORM ----------
    form = tk.Frame(root)
    form.pack(pady=5)

    tk.Label(
        form,
        text="Customer Name"
    ).grid(row=0, column=0, padx=5, pady=5)

    tk.Entry(
        form,
        textvariable=customer,
        width=25
    ).grid(row=0, column=1)

    tk.Label(
        form,
        text="Phone"
    ).grid(row=0, column=2, padx=5)

    tk.Entry(
        form,
        textvariable=phone,
        width=20
    ).grid(row=0, column=3)

    tk.Label(
        form,
        text="Email"
    ).grid(row=1, column=0, padx=5, pady=5)

    tk.Entry(
        form,
        textvariable=email,
        width=25
    ).grid(row=1, column=1)

    tk.Label(
        form,
        text="Service"
    ).grid(row=1, column=2, padx=5)

    ttk.Combobox(
        form,
        textvariable=service,
        values=[
            "Consultation",
            "Service",
            "Meeting",
            "Repair",
            "Other"
        ],
        width=18
    ).grid(row=1, column=3)

    tk.Label(
        form,
        text="Date"
    ).grid(row=2, column=0, padx=5, pady=5)

    tk.Entry(
        form,
        textvariable=date,
        width=25
    ).grid(row=2, column=1)

    tk.Label(
        form,
        text="Time"
    ).grid(row=2, column=2, padx=5)

    tk.Entry(
        form,
        textvariable=time,
        width=20
    ).grid(row=2, column=3)

    tk.Label(
        form,
        text="Status"
    ).grid(row=3, column=0, padx=5, pady=5)

    ttk.Combobox(
        form,
        textvariable=status,
        values=[
            "Booked",
            "Completed",
            "Cancelled"
        ],
        state="readonly",
        width=22
    ).grid(row=3, column=1)

    # ---------- BUTTONS ----------
    buttons = tk.Frame(root)
    buttons.pack(pady=10)

    tk.Button(
        buttons,
        text="Book Appointment",
        command=add,
        width=17
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        buttons,
        text="Update",
        command=update,
        width=12
    ).grid(row=0, column=1, padx=5)

    tk.Button(
        buttons,
        text="Delete",
        command=delete,
        width=12
    ).grid(row=0, column=2, padx=5)

    tk.Button(
        buttons,
        text="Clear",
        command=clear,
        width=12
    ).grid(row=0, column=3, padx=5)

    # ---------- SEARCH ----------
    search_frame = tk.Frame(root)
    search_frame.pack(pady=5)

    tk.Label(
        search_frame,
        text="Search"
    ).pack(side=tk.LEFT)

    tk.Entry(
        search_frame,
        textvariable=search,
        width=30
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        search_frame,
        text="Search",
        command=search_record
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        search_frame,
        text="Show All",
        command=show
    ).pack(side=tk.LEFT)

    # ---------- TREEVIEW ----------
    table_frame = tk.Frame(root)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    columns = (
        "ID",
        "Customer",
        "Phone",
        "Email",
        "Service",
        "Date",
        "Time",
        "Status"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(
            col,
            width=130,
            minwidth=100
        )

    # ---------- VERTICAL SCROLLBAR ----------
    v_scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    # ---------- HORIZONTAL SCROLLBAR ----------
    h_scrollbar = ttk.Scrollbar(
        table_frame,
        orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set
    )

    tree.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    v_scrollbar.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    h_scrollbar.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    table_frame.grid_rowconfigure(
        0,
        weight=1
    )

    table_frame.grid_columnconfigure(
        0,
        weight=1
    )

    tree.bind(
        "<ButtonRelease-1>",
        select_record
    )

    show()

    root.mainloop()


# ---------- LOGIN WINDOW ----------
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("400x300")

tk.Label(
    login_window,
    text="LOGIN",
    font=("Arial", 20, "bold")
).pack(pady=30)

tk.Label(
    login_window,
    text="Username"
).pack()

username_entry = tk.Entry(login_window)
username_entry.pack(pady=5)

tk.Label(
    login_window,
    text="Password"
).pack()

password_entry = tk.Entry(
    login_window,
    show="*"
)
password_entry.pack(pady=5)

tk.Button(
    login_window,
    text="Login",
    command=login,
    width=15
).pack(pady=20)

login_window.mainloop()