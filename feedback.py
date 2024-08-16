import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re

admin_login_win = None  # Global variable to store admin login window
admin_win = None  # Global variable to store admin window

def submit_feedback():
    name = name_entry.get()
    email = email_entry.get()
    feedback = feedback_text.get("1.0", tk.END)
    phone_number = phone_number_entry.get()
    rating = rating_var.get()

    # Validate Name
    if not name:
        messagebox.showerror("Error", "Name cannot be empty.")
        return
    
    if name.isdigit():
        messagebox.showerror("Error", "Name cannot contain numbers.")
        return
    if any(char == '-' for char in name):
        messagebox.showerror("Error", "Name cannot contain negative numbers.")
        return
    if name.isspace():
        messagebox.showerror("Error", "Name cannot contain spaces.")
        return
    if not re.match(r"^[a-zA-Z\s]*$", name):
        messagebox.showerror("Error", "Name cannot contain special characters.")
        return
    if len(name) < 2 or len(name) > 20:
        messagebox.showerror("Error", "Name length should be between 2 to 20 characters.")
        return
        
    # Validate Phone Number
    if not phone_number:
        messagebox.showerror("Error", "Phone Number cannot be empty.")
        return

    if phone_number.isspace():
        messagebox.showerror("Error", "Phone number cannot contain spaces.")
        return
    
    if any(char == '-' for char in phone_number):
        messagebox.showerror("Error", "Phone Number cannot contain negative numbers.")
        return
    if not phone_number.isdigit():
        messagebox.showerror("Error", "Phone number should contain only numbers.")
        return
    elif len(phone_number) != 10:
        messagebox.showerror("Error", "Phone number should be exactly 10 digits long.")
        return
    

    # Validate Email
    if not email:
        messagebox.showerror("Error", "Email cannot be empty.")
        return
    if email.isspace():
        messagebox.showerror("Error", "Email cannot contain spaces.")
        return
    if email.isdigit() or email.isspace():
        messagebox.showerror("Error", "Email cannot be all numbers or contain spaces.")
        return
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showerror("Error", "Invalid email format.")
        return

    try:
        conn = sqlite3.connect('fback.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feedbacks WHERE email=?", (email,))
        count = cursor.fetchone()[0]
        conn.close()

        if count > 0:
            messagebox.showerror("Error", "Email already exists.")
            return
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Database error: {e}")
    
    if feedback.isspace():
        messagebox.showerror("Error", "Feedback cannot be empty.")
        return
    if len(feedback) < 10 or len(feedback) > 50:
        messagebox.showerror("Error", "Feedback length should be between 10 to 50 characters.")
        return

    # Validate Rating
    if rating == 0:
        messagebox.showerror("Error", "Please select a rating.")
        return
    
    # processing validations pass
    try:
        conn = sqlite3.connect('fback.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedbacks (name, email, feedback, rating, phone_number) VALUES (?, ?, ?, ?, ?)",
                       (name, email, feedback, rating, phone_number))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Feedback submitted successfully.")
        clear_feedback()  # Clear the entered feedback content after submission
        name_entry.focus()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error submitting feedback: {e}")

def clear_feedback():
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    feedback_text.delete("1.0", tk.END)
    rating_var.set(0)
    phone_number_entry.delete(0, tk.END)

def create_rating_buttons():
    ratings_frame = tk.Frame(root)
    ratings_frame.pack(pady=5)

    for i in range(1, 6):
        rating_button = tk.Radiobutton(ratings_frame, text=f"{i} Star", variable=rating_var, value=i,
                                       font=("Helvetica", 12))
        rating_button.pack(side=tk.LEFT, padx=5)

def admin_login():
    global admin_login_win

    if admin_login_win and admin_login_win.winfo_exists():
        messagebox.showinfo("Info", "Admin login window is already open.")
        return

    admin_login_win = tk.Toplevel(root)
    admin_login_win.title("Admin Login")
    admin_login_win.geometry("500x200")     
    
    tk.Label(admin_login_win, text="Username:", font=("Helvetica", 12)).pack(pady=5)
    username_entry = tk.Entry(admin_login_win, font=("Helvetica", 12))
    username_entry.pack()

    tk.Label(admin_login_win, text="Password:", font=("Helvetica", 12)).pack(pady=5)
    password_entry = tk.Entry(admin_login_win, show="*", font=("Helvetica", 12))
    password_entry.pack()

    def authenticate():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        try:
            conn = sqlite3.connect('fback.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password))
            admin = cursor.fetchone()
            conn.close()

            if admin:
                admin_window()
                admin_login_win.destroy()
            else:
                messagebox.showerror("Error", "Invalid credentials.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

    login_button = tk.Button(admin_login_win, text="Login", command=authenticate, font=("Helvetica", 12))
    login_button.pack(pady=10)

def admin_window():
    global admin_win

    if admin_win and admin_win.winfo_exists():
        messagebox.showinfo("Info", "Admin panel is already open.")
        return

    admin_win = tk.Toplevel(root)
    admin_win.title("Admin Panel")
    admin_win.geometry("800x600")

    welcome_label = ttk.Label(admin_win, text="WELCOME ADMIN", style='Header.TLabel')
    welcome_label.pack(pady=5)

    columns = ('ID', 'Name', 'Email', 'Phone Number', 'Feedback', 'Rating')
    feedback_tree = ttk.Treeview(admin_win, columns=columns, show='headings')
    feedback_tree.heading('ID', text='ID')
    feedback_tree.heading('Name', text='Name')
    feedback_tree.heading('Email', text='Email')
    feedback_tree.heading('Phone Number', text='Phone Number')
    feedback_tree.heading('Feedback', text='Feedback')
    feedback_tree.heading('Rating', text='Rating')

    feedback_tree.column('ID', width=50)
    feedback_tree.column('Name', width=100)
    feedback_tree.column('Email', width=150)
    feedback_tree.column('Phone Number', width=100)
    feedback_tree.column('Feedback', width=200)
    feedback_tree.column('Rating', width=50)

    feedback_tree.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def view_feedbacks():
        for row in feedback_tree.get_children():
            feedback_tree.delete(row)
        
        try:
            conn = sqlite3.connect('fback.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedbacks")
            feedbacks = cursor.fetchall()
            conn.close()

            for feedback in feedbacks:
                # Ensure the order of values matches the Treeview columns
                feedback_tree.insert('', tk.END, values=(feedback[0], feedback[1], feedback[2], feedback[5], feedback[3], feedback[4]))
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error fetching feedbacks: {e}")

    view_button = ttk.Button(admin_win, text="View", command=view_feedbacks)
    view_button.pack(pady=5)

    def delete_feedback():
        selected_item = feedback_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a feedback to delete.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this feedback?"):
            feedback_id = feedback_tree.item(selected_item)['values'][0]
            try:
                conn = sqlite3.connect('fback.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM feedbacks WHERE id=?", (feedback_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Feedback deleted successfully.")
                view_feedbacks()  # Refresh the feedback list
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error deleting feedback: {e}")

    delete_button = ttk.Button(admin_win, text="Delete", command=delete_feedback)
    delete_button.pack(pady=5)

    def exit_admin_panel():
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit the admin panel?"):
            admin_win.destroy()

    exit_button = ttk.Button(admin_win, text="Exit", command=exit_admin_panel)
    exit_button.pack(pady=10)

root = tk.Tk()
root.title("Feedback System")
root.geometry("500x600")

tk.Label(root, text="Submit your feedback", font=("Helvetica", 16)).pack(pady=10)

tk.Label(root, text="Name:", font=("Helvetica", 12)).pack(pady=5)
name_entry = tk.Entry(root, font=("Helvetica", 12))
name_entry.pack()

tk.Label(root, text="Email:", font=("Helvetica", 12)).pack(pady=5)
email_entry = tk.Entry(root, font=("Helvetica", 12))
email_entry.pack()

tk.Label(root, text="Phone Number:", font=("Helvetica", 12)).pack(pady=5)
phone_number_entry = tk.Entry(root, font=("Helvetica", 12))
phone_number_entry.pack()

tk.Label(root, text="Feedback:", font=("Helvetica", 12)).pack(pady=5)
feedback_text = tk.Text(root, height=5, font=("Helvetica", 12))
feedback_text.pack(pady=5)

tk.Label(root, text="Rating:", font=("Helvetica", 12)).pack(pady=5)
rating_var = tk.IntVar()
create_rating_buttons()

submit_button = tk.Button(root, text="Submit", command=submit_feedback, font=("Helvetica", 12))
submit_button.pack(pady=10)

clear_button = tk.Button(root, text="Clear", command=clear_feedback, font=("Helvetica", 12))
clear_button.pack(pady=5)

admin_button = tk.Button(root, text="Admin Login", command=admin_login, font=("Helvetica", 12))
admin_button.pack(pady=20)

root.mainloop()
