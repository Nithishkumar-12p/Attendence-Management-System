import os
from datetime import datetime
from fpdf import FPDF
from backend.models.attendance import AttendanceModel

class ReportModel(FPDF):
    def header(self):
        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 25)
        
        # Logo/Branding
        self.set_x(40) # Push text to the right of logo
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(249, 115, 22) # Amber/Orange (Matches #f97316)
        self.cell(0, 10, 'VIDVAT SOLUTIONS', border=False, align='L', new_x="LMARGIN", new_y="NEXT")
        
        self.set_x(40)
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Industrial Attendance Portal - Official Export', border=False, align='L', new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Generated On: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', align='C')

    @staticmethod
    def _create_pdf_instance():
        pdf = ReportModel()
        pdf.alias_nb_pages()
        return pdf

    @staticmethod
    def generate_daily_pdf(date_str):
        records = AttendanceModel.get_attendance_for_date(date_str)
        pdf = ReportModel._create_pdf_instance()
        pdf.add_page()
        
        pdf.set_font('helvetica', 'B', 14)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, f'Daily Attendance Report: {date_str}', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        # ... (rest of method same)

    # ... keeping other static methods ...

    @staticmethod
    def _draw_invoice_slip(pdf, r, month_name, year):
        # Corporate Colors
        TEAL = (30, 83, 107)
        DARK = (30, 41, 59)
        LIGHT_BG = (245, 247, 249)
        
        # 0. Global Setup
        pdf.set_auto_page_break(auto=True, margin=20)
        
        # 1. Header Bar (Teal Primary)
        pdf.set_fill_color(*TEAL)
        pdf.rect(0, 0, 210, 45, 'F')
        
        # Logo on the left
        logo_path = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            pdf.image(logo_path, 15, 8, 25)
            
        # Revert "INVOICE" as the main large centered title
        pdf.set_xy(0, 8)
        pdf.set_font('helvetica', 'B', 40)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 30, 'INVOICE', align='C', new_x="LMARGIN", new_y="NEXT")
        
        # Company Info on Right (Making Name Large and Bold)
        pdf.set_xy(135, 10)
        pdf.set_font('helvetica', 'B', 12) # Prominent size 12 bold
        pdf.set_text_color(255, 255, 255)
        pdf.cell(65, 6, 'VIDVAT SOLUTIONS', align='R', new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('helvetica', '', 8.5)
        pdf.set_x(135)
        pdf.cell(65, 4.5, '4, 261, BN Reddy Nagar', align='R', new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(135)
        pdf.cell(65, 4.5, 'Cherlapalli, Hyderabad, Telangana 500051', align='R', new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(135)
        pdf.cell(65, 4.5, 'Phone: +91 79010 05402', align='R', new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(135)
        pdf.cell(65, 4.5, 'https://www.indiamart.com/vidvat-solutions', align='R', new_x="LMARGIN", new_y="NEXT")

        pdf.set_y(52)
        
        # 2. Invoice Meta & Bill To Info
        # Left side: Invoice Details
        pdf.set_font('helvetica', 'B', 10)
        pdf.set_text_color(*DARK)
        pdf.cell(40, 6, 'Reference No:') # Renaming Invoice No to Reference No as company name is now title
        pdf.set_font('helvetica', '', 10)
        # Use Month Shorthand and Year from the salary record
        pdf.cell(50, 6, f'VS-{year}{month_name[:3].upper()}-{r[1]}')
        
        # Right side: Bill To Header
        pdf.set_x(140)
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(60, 6, 'Bill To', align='R', new_x="LMARGIN", new_y="NEXT")
        
        # Row 2
        pdf.set_x(10)
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(40, 6, 'Date of Issue:')
        pdf.set_font('helvetica', '', 10)
        pdf.cell(50, 6, datetime.now().strftime("%d %b %Y"))
        
        # Right side: Employee Name
        pdf.set_x(140)
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(60, 6, str(r[11]), align='R', new_x="LMARGIN", new_y="NEXT")
        
        # Row 3
        pdf.set_x(10)
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(40, 6, 'Period:')
        pdf.set_font('helvetica', '', 10)
        pdf.cell(50, 6, f'{month_name} {year}')
        
        # Right side: Designation/Phone
        pdf.set_x(140)
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(60, 5, str(r[12] or 'Worker'), align='R', new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(140)
        pdf.cell(60, 5, f'Ph: {r[14] or "-"}', align='R', new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(10)

        # 3. Main Itemized Table
        pdf.set_font('helvetica', 'B', 9)
        pdf.set_fill_color(*TEAL)
        pdf.set_text_color(255, 255, 255)
        
        # New Columns: ID, Name, Work Type, Daily Wage, Pres., Absnt., Amount
        col_widths = [10, 30, 45, 25, 18, 18, 44] 
        headers = ['ID', 'Name', 'Work Type', 'Daily Wage', 'Pres.', 'Absnt.', 'Total Earned']
        
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 10, h, fill=True, align='C' if i > 2 else 'L')
        pdf.ln()

        # Table Row 1
        pdf.set_font('helvetica', '', 9)
        pdf.set_text_color(*DARK)
        pdf.set_fill_color(*LIGHT_BG)
        
        present_days = float(r[5] or 0)
        absent_days = float(r[6] or 0)
        final_sal = float(r[9] or 0)
        daily_wage = float(r[13] or 0)
        designation = str(r[12] or 'General Work')
        
        pdf.cell(col_widths[0], 12, str(r[1]), border='B', align='L', fill=True)
        pdf.cell(col_widths[1], 12, str(r[11]), border='B', fill=True)
        # Just the Work Type
        pdf.cell(col_widths[2], 12, designation, border='B', fill=True)
        pdf.cell(col_widths[3], 12, f'Rs. {daily_wage:,.2f}', border='B', align='C', fill=True)
        pdf.cell(col_widths[4], 12, str(present_days), border='B', align='C', fill=True)
        pdf.cell(col_widths[5], 12, str(absent_days), border='B', align='C', fill=True)
        pdf.cell(col_widths[6], 12, f'Rs. {final_sal:,.2f}', border='B', align='R', fill=True)
        pdf.ln()
        pdf.ln()

        pdf.ln(3)

        # 4. Totals
        deductions = float(r[8] or 0)
        subtotal = final_sal + deductions
        
        pdf.set_x(120)
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(50, 7, 'Gross Salary:')
        pdf.set_font('helvetica', '', 10)
        pdf.cell(30, 7, f'Rs. {subtotal:,.2f}', align='R', new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_x(120)
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(50, 7, 'Deductions:')
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(220, 38, 38) # Red
        pdf.cell(30, 7, f'- Rs. {deductions:,.2f}', align='R', new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(1)
        pdf.set_x(120)
        pdf.set_fill_color(*LIGHT_BG)
        pdf.set_font('helvetica', 'B', 12)
        pdf.set_text_color(*TEAL)
        pdf.cell(80, 10, f'NET PAYABLE: Rs. {final_sal:,.2f}', align='R', fill=True, border='T')
        
        pdf.set_y(-50)
        
        # 5. Signatures Section
        pdf.set_font('helvetica', 'B', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(95, 10, '', border='B')
        pdf.cell(10, 10, '')
        pdf.cell(85, 10, '', border='B', new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('helvetica', 'I', 9)
        pdf.cell(95, 8, 'Employee Signature', align='C')
        pdf.cell(10, 8, '')
        pdf.cell(85, 8, 'Authorized Signatory', align='C')

        # 6. Bottom Banner Footer
        pdf.set_y(-15)
        pdf.set_fill_color(*TEAL)
        pdf.rect(0, 282, 210, 15, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(0, 10, 'Thank you for your business!', align='C')

    @staticmethod
    def generate_filtered_invoices_pdf(emp_ids, month, year):
        from backend.database.db_connection import db
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[int(month)]

        pdf = ReportModel._create_pdf_instance()
        
        for emp_id in emp_ids:
            # Fetch Salary and Employee details
            query = """
                SELECT s.*, e.name, e.designation, e.basic_salary as master_basic, e.phone_number
                FROM salaries s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE s.employee_id = %s AND s.month = %s AND s.year = %s
            """
            row = db.execute_query(query, (emp_id, month, year), fetch=True)
            if not row: continue

            pdf.add_page()
            ReportModel._draw_invoice_slip(pdf, row[0], month_name, year)

        output_path = os.path.join(os.path.dirname(__file__), '..', '..', f'payroll_invoices_{month_name}_{year}.pdf')
        pdf.output(output_path)
        return output_path

    @staticmethod
    def generate_salary_slip_pdf(emp_id, month, year):
        return ReportModel.generate_filtered_invoices_pdf([emp_id], month, year)
