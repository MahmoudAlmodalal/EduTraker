import openpyxl
from django.http import HttpResponse
from datetime import datetime

class ExportService:
    @staticmethod
    def export_to_excel(data, headers, filename="report"):
        """
        Generates an Excel file from a list of dictionaries.
        :param data: List of dictionaries containing the data.
        :param headers: List of column headers (keys in the dictionary).
        :param filename: Base filename for the download.
        :return: HttpResponse with the Excel file.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Report"

        # Write header
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_num, value=header.capitalize())

        # Write data
        for row_num, row_data in enumerate(data, 2):
            for col_num, header in enumerate(headers, 1):
                value = row_data.get(header, "")
                # Convert list/dict to string if necessary
                if isinstance(value, (list, dict)):
                    value = str(value)
                ws.cell(row=row_num, column=col_num, value=value)

        # Prepare response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response["Content-Disposition"] = f'attachment; filename="{filename}_{timestamp}.xlsx"'
        
        wb.save(response)
        return response

    @staticmethod
    def export_to_csv(data, headers, filename="report"):
        """
        Generates a CSV file from a list of dictionaries.
        """
        import csv
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response['Content-Disposition'] = f'attachment; filename="{filename}_{timestamp}.csv"'

        writer = csv.DictWriter(response, fieldnames=headers)
        writer.writeheader()
        for row in data:
            # Clean data (handle nested dicts/lists)
            clean_row = {}
            for header in headers:
                val = row.get(header, "")
                if isinstance(val, (list, dict)):
                    val = str(val)
                clean_row[header] = val
            writer.writerow(clean_row)
            
        return response

    @staticmethod
    def export_to_pdf(data, headers, filename="report"):
        """
        Generates a basic PDF file (Note: currently returns a placeholder or simple text if reportlab is missing).
        """
        # Since reportlab is not in requirements.txt, we will provide a simple implementation
        # or a message if we can't generate a full PDF here.
        # For now, let's try a very basic implementation if we can't use a library.
        # Alternatively, we can use a library if we want to be premium.
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            response = HttpResponse(content_type='application/pdf')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            response['Content-Disposition'] = f'attachment; filename="{filename}_{timestamp}.pdf"'
            
            p = canvas.Canvas(response, pagesize=letter)
            width, height = letter
            
            y = height - 50
            p.drawString(100, y, f"Report: {filename.capitalize()}")
            y -= 30
            
            # Simple table-like output
            header_str = " | ".join([h.capitalize() for h in headers])
            p.drawString(50, y, header_str)
            y -= 20
            p.line(50, y+15, width-50, y+15)
            
            for row in data:
                row_str = " | ".join([str(row.get(h, "")) for h in headers])
                p.drawString(50, y, row_str)
                y -= 20
                if y < 50:
                    p.showPage()
                    y = height - 50
                    
            p.showPage()
            p.save()
            return response
            
        except ImportError:
            # Fallback if reportlab is not installed
            response = HttpResponse("PDF generation requires 'reportlab' library.", content_type='text/plain')
            return response
