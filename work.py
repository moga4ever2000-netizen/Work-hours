import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime 
import os 

DATA_FILE = "employees_data.json"
class WorkTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامج حساب اجر عمال ابو وائل")
        self.root.geometry("850x550")
        #load last data
        self.data = self.load_data()
        #add new employ
        add_frame = tk.LabelFrame(root, text="ضيف عامل جديد يا وليد",font=("Arial",11,"bold"),padx=10,pady=10)
        add_frame.pack(fill="x",padx=15,pady=5)
    

        tk.Label(add_frame, text="اسم العامل:", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.name_entry = tk.Entry(add_frame, font=("Arial", 10))
        self.name_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(add_frame, text="أجر الساعة:", font=("Arial", 10)).grid(row=0, column=2, padx=5)
        self.rate_entry = tk.Entry(add_frame, font=("Arial", 10))
        self.rate_entry.grid(row=0, column=3, padx=5)
        
        add_btn = tk.Button(add_frame, text="إضافة العامل", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), command=self.add_employee)
        add_btn.grid(row=0, column=4, padx=10)

        self.delete_btn = tk.Button(
            add_frame,
            text="حذف العامل",
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.delete_employee
        )
        self.delete_btn.grid(row=0, column=5, padx=5)

        #display employ
        table_frame = tk.Frame(root)
        table_frame.pack(fill="both",expand=True,padx=15,pady=10)

        columns=("name","rate","status","start_time","total_hours","total_salary")
        self.tree=ttk.Treeview(table_frame,columns=columns,show="headings",height=10)


        self.tree.heading("name",text="اسم العامل")
        self.tree.heading("rate",text="اجر الساعة")
        self.tree.heading("status", text="الحالة الحالية")
        self.tree.heading("start_time",text="وقت الدخول")
        self.tree.heading("total_hours",text="كل عدد الساعات بالشهر")
        self.tree.heading("total_salary",text="المستحق حتى الان")

        for col in columns:
            self.tree.column(col, anchor="center", width=120)
            
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.refresh_table()
        
        # --- لوحة التحكم في الحضور والانصراف ---
        control_frame = tk.Frame(root, pady=10)
        control_frame.pack(fill="x", padx=15)
        
        btn_start = tk.Button(control_frame, text="▶ العامل وصل (تسجيل الدخول)", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), command=self.check_in)
        btn_start.pack(side="left", padx=10)
        
        btn_stop = tk.Button(control_frame, text="⏹ كده مشى (حساب الساعات)", bg="#f44336", fg="white", font=("Arial", 11, "bold"), command=self.check_out)
        btn_stop.pack(side="left", padx=10)

        btn_reset = tk.Button(control_frame, text="🔄 تصفير الشهر (تصفير الأجور)", bg="#FF9800", fg="white", font=("Arial", 11, "bold"), command=self.reset_month)
        btn_reset.pack(side="right", padx=10)
    def delete_employee(self):
        # التأكد من تحديد عنصر من الجدول
        selected_item = self.tree.selection()
        
        if not selected_item:
            messagebox.showwarning("تنبيه", "يرجى تحديد عامل من القائمة لحذفه")
            return

        # تأكيد الحذف من المستخدم
        confirm = messagebox.askyesno("تأكيد الحذف", "هل أنت متاكد من رغبتك في حذف هذا العامل؟")
        if confirm:
            # حذف العامل من البيانات والجدول
            emp_name = self.tree.item(selected_item[0])["values"][0]
            if emp_name not in self.data:
                messagebox.showerror("خطأ", "تعذر العثور على بيانات العامل")
                return
            del self.data[emp_name]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("نجاح", "تم حذف العامل بنجاح")


    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def add_employee(self):
        name = self.name_entry.get().strip()
        rate = self.rate_entry.get().strip()
        
        if not name or not rate:
            messagebox.showwarning("تنبيه", "يرجى إدخال اسم العامل وأجر الساعة")
            return
            
        try:
            rate = float(rate)
        except ValueError:
            messagebox.showerror("خطأ", "أجر الساعة لازم يكون رقم")
            return
            
        if name in self.data:
            messagebox.showwarning("تنبيه", "العامل موجود بالفعل")
            return
            
        self.data[name] = {
            "rate": rate,
            "is_working": False,
            "start_time": None,
            "total_hours": 0.0,
            "total_salary": 0.0
        }
        self.save_data()
        self.refresh_table()
        self.name_entry.delete(0, tk.END)
        self.rate_entry.delete(0, tk.END)

    def check_in(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("تنبيه", "اختر عامل أولاً من الجدول")
            return
            
        emp_name = self.tree.item(selected_item)["values"][0]
        emp = self.data[emp_name]
        
        if emp["is_working"]:
            messagebox.showwarning("تنبيه", "العامل في حالة عمل بالفعل!")
            return
            
        emp["is_working"] = True
        emp["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_data()
        self.refresh_table()

    def check_out(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("تنبيه", "اختر عامل أولاً من الجدول")
            return
            
        emp_name = self.tree.item(selected_item)["values"][0]
        emp = self.data[emp_name]
        
        if not emp["is_working"]:
            messagebox.showwarning("تنبيه", "العامل ليس في حالة عمل لحساب الانصراف!")
            return
            
        # حساب الساعات المنقضية
        start_dt = datetime.strptime(emp["start_time"], "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.now()
        
        duration_seconds = (end_dt - start_dt).total_seconds()
        worked_hours = duration_seconds / 3600.0  # تحويل من ثواني إلى ساعات
        
        earned_salary = worked_hours * emp["rate"]
        
        # تحديث البيانات
        emp["is_working"] = False
        emp["start_time"] = None
        emp["total_hours"] += round(worked_hours, 2)
        emp["total_salary"] += round(earned_salary, 2)
        
        self.save_data()
        self.refresh_table()
        
        messagebox.showinfo("تم التسجيل", f"تم تسجيل الانصراف لـ {emp_name}\n"
                                         f"ساعات الشيفت: {worked_hours:.2f} ساعة\n"
                                         f"أجر الشيفت: {earned_salary:.2f} جنيه")

    def reset_month(self):
        if messagebox.askyesno("تأكيد", "هل أنت تأكد من تصفير سِجل الساعات والمرتبات لجميع العمال لبدء شهر جديد؟"):
            for emp in self.data.values():
                emp["total_hours"] = 0.0
                emp["total_salary"] = 0.0
                emp["is_working"] = False
                emp["start_time"] = None
            self.save_data()
            self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for name, emp in self.data.items():
            status = "يعمل الآن 🟢" if emp["is_working"] else "متوقف 🔴"
            start = emp["start_time"] if emp["start_time"] else "-"
            
            self.tree.insert("", "end", values=(
                name,
                f"{emp['rate']:.2f}",
                status,
                start,
                f"{emp['total_hours']:.2f} ساعة",
                f"{emp['total_salary']:.2f} جنيه"
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkTrackerApp(root)
    root.mainloop()
    