import ttkbootstrap as ttkb
from ttkbootstrap import Combobox
from tkinter import messagebox,StringVar,filedialog

class UserView:
    def __init__(self, master, db_service):
        self.master = master
        self.db_service = db_service

        self.frame = ttkb.Frame(self.master, padding=5)
        self.frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.setup_ui()

    def setup_ui(self):
        """Create the user section with a dropdown filter for user type."""
        user_frame = ttkb.Frame(self.master, padding=5)
        user_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Allow the user_frame to expand in height
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        
        user_frame.grid_rowconfigure(1, weight=1)  # Make row with TreeView expandable
        user_frame.grid_columnconfigure(0, weight=1)

        # Dropdown Filter Frame
        filter_frame = ttkb.Frame(user_frame)
        filter_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Label for Filter
        ttkb.Label(filter_frame, text="Filter by Type:", font="TkFixedFont 10").pack(side="left", padx=5)

        # Dropdown for User Type Filter
        self.user_type_var = StringVar()
        self.user_type_dropdown = Combobox(filter_frame, textvariable=self.user_type_var, state="readonly")
        self.user_type_dropdown.pack(side="left", padx=5)

        # Load Button to Apply Filter
        filter_button = ttkb.Button(filter_frame, text="Apply Filter", command=self.load_users)
        filter_button.pack(side="left", padx=5)
        
        # Check Live Button
        check_live_button = ttkb.Button(filter_frame, text="Check Live")
        check_live_button.pack(side="left", padx=5)

        # Delete Button
        delete_button = ttkb.Button(filter_frame, text="Delete", style="danger.TButton", command=self.delete_user_by_type)
        delete_button.pack(side="left", padx=5)

        # Refresh Button (Reloads Data from Server)
        refresh_button = ttkb.Button(filter_frame, text="Refresh", command=self.refresh_data, style="info.TButton")
        refresh_button.pack(side="left", padx=5)

        # Export Button (Exports Data to TXT)
        export_button = ttkb.Button(filter_frame, text="Export", command=self.export_to_txt, style="success.TButton")
        export_button.pack(side="left", padx=5)

        # User Treeview
        self.user_tree = ttkb.Treeview(
            user_frame,
            columns=("No", "UID", "Password", "2FA", "Email", "PassMail", "Type", "Status", "CreatedDate"),
            show="headings",
            height=10
        )
        
        # Set Table Headers (Must match MySQL Query Order)
        self.user_tree.heading("No", text="No")
        self.user_tree.heading("UID", text="UID")
        self.user_tree.heading("Password", text="Password")
        self.user_tree.heading("2FA", text="2FA")
        self.user_tree.heading("Email", text="Email")
        self.user_tree.heading("PassMail", text="PassMail")
        self.user_tree.heading("Type", text="Type")  # ✅ Matches "acc_type" from MySQL
        self.user_tree.heading("Status", text="Status")
        self.user_tree.heading("CreatedDate", text="Created Date")

        # Adjust Column Width
        self.user_tree.column("No", width=50, anchor="center")
        self.user_tree.column("UID", width=100, anchor="center")
        self.user_tree.column("Password", width=100, anchor="center")
        self.user_tree.column("2FA", width=280, anchor="center")
        self.user_tree.column("Email", width=250, anchor="center")
        self.user_tree.column("PassMail", width=150, anchor="center")
        self.user_tree.column("Type", width=50, anchor="center")
        self.user_tree.column("Status", width=50, anchor="center")
        self.user_tree.column("CreatedDate", width=100, anchor="center")

        # Expand TreeView to fill available space
        self.user_tree.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Scrollbar for User Treeview
        user_scrollbar = ttkb.Scrollbar(user_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=user_scrollbar.set)
        user_scrollbar.grid(row=1, column=1, sticky="ns")

        # Load Available User Types in Dropdown
        self.load_user_types()
        self.load_users()  # Load users from MySQL


    def load_users(self):
        """Fetch and display users from MySQL in the TreeView with filtering."""
        self.user_tree.delete(*self.user_tree.get_children())  # Clear existing rows

        selected_type = self.user_type_var.get()  # Get selected type from dropdown
        users = self.db_service.get_users(selected_type)  # ✅ Fetch filtered users from MySQL

        for idx, user in enumerate(users, start=1):
            user_id, uid, password, two_factor, email, pass_mail, acc_type, status, created_at = user
            self.user_tree.insert(
                "", "end",
                values=(idx, uid, password, two_factor, email, pass_mail, acc_type, status, created_at)
            )

    def load_user_types(self):
        """Fetch unique user types from MySQL and populate dropdown."""
        user_types = self.db_service.get_user_types()
        user_types.insert(0, "All")
        self.user_type_dropdown["values"] = user_types
        self.user_type_dropdown.current(0)

    def delete_user_by_type(self):
        """Delete selected user type from the database."""
        selected_type = self.user_type_var.get()
        if selected_type == "All":
            messagebox.showwarning("Warning", "Please select a specific user type to delete.")
            return

        confirmation = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete all users of type '{selected_type}'?"
        )
        
        if confirmation:
            self.db_service.delete_user_by_type(selected_type)
            #reload the user list
            self.load_users()
            #change the dropdown to "All"
            self.user_type_var.set("All")
            
            

    def refresh_data(self):
        """Reload user data from the database."""
        self.load_users()
        messagebox.showinfo("Refresh Complete", "✅ Data has been refreshed from the server.")

    def export_to_txt(self):
        """Export user data to a TXT file in 'uid|pass|2fa|mail|passmail' format with a save dialog."""
        
        # Ask user where to save the file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Exported Users"
        )

        # If the user cancels, return
        if not file_path:
            return

        # Write data to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("uid|pass|2fa|mail|passmail\n")  # Header line

            for item in self.user_tree.get_children():
                values = self.user_tree.item(item, "values")
                uid = values[1]
                password = values[2]
                two_factor = values[3]
                email = values[4]
                passmail = values[5]

                file.write(f"{uid}|{password}|{two_factor}|{email}|{passmail}\n")  # Export format

        messagebox.showinfo("Export Complete", f"✅ Data exported to:\n{file_path}")
