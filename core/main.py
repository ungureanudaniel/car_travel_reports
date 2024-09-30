import pandas as pd
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from kivy.app import App
from kivy.uix.textinput import TextInput
from reportlab.lib.units import cm
from datetime import datetime
import re


def generate_datetime():
    x = datetime.now().strftime("%Y%m%d_%H%M%S")
    return x

def extract_floats_from_string(input_string):
    # Define a regex pattern to find floating point numbers
    pattern = r'[-+]?\d*\.\d+|\d+'  # Matches numbers with optional sign and decimal
        
    # Find all matches in the input string
    match = re.findall(pattern, input_string)
        
    # Convert matches to float
    float_number = float(match[0])
        
    return float_number

# create the layout class
class CarReportApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pdf_save_path = None  # Initialize the pdf_save_path
        self.csv_file_path = None  # Initialize the csv_file_path
        self.vehicle_title = None  # Initialize the vehicle title
        self.default_cols = ["Durată","Vmed","Vmax","Scop deplasare","Consum total","Alimentări măsurate"]  # default columns to delete
        self.start_date = None  # Initialize the start_date
        self.end_date = None  # Initialize the end_date
        self.filechooser = None  # Initialize filechooser as an instance variable

    def build(self):
        # Layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Creating a sub-layout to control the width of elements (centered with horizontal alignment)
        centered_layout = BoxLayout(orientation='vertical', size_hint=(0.6, None), pos_hint={"center_y":0.5, "center_x": 0.5}, spacing=40)

        # Adjusting the height dynamically based on the number of widgets
        centered_layout.bind(minimum_height=centered_layout.setter('height'))

        # Fuel Difference label (Decimal only)
        self.input_fuel_label = Label(
            text="Pasul 1. Introduceți combustibilul din luna precedentă (numar cu 2 zecimale, ex: 12.50)",
            size_hint=(1, None),
            size_hint_y=None,
            markup=True,
            pos_hint={"center_y": 0.1},
            height=30,
            halign='left',
            valign='top'
            )
        centered_layout.add_widget(self.input_fuel_label)

        # Fuel Difference input (Decimal only)
        self.fuel_float_input = TextInput(
            text="",
            size_hint=(1, None),
            height=50,
            input_filter='float'  # Restrict input to decimal numbers
            )
        centered_layout.add_widget(self.fuel_float_input)

        # CSV File Input label
        self.select_file_label = Label(
            text="Pasul 2. Selectați fișierul .csv cu datele din aplicația GPS",
            size_hint=(1, None),
            height=30,
            markup=True,
            halign='left',
            valign='middle'
            )
        centered_layout.add_widget(self.select_file_label)

        # Button to select CSV file
        self.select_file_button = Button(
            text="Apăsați pentru selecție fișier .csv",
            size_hint=(1, None),
            height=40,
            valign='middle'
            )
        self.select_file_button.bind(on_press=self.select_csv_file)
        centered_layout.add_widget(self.select_file_button)

        # Label to show the selected CSV file path
        self.file_path_label = Label(
            text="Nu ați selectat un fișier!",
            size_hint=(1, None),
            height=30,
            color=(1, 0, 0, 1)  # Set the text color to red (R, G, B, A) 
            )
        centered_layout.add_widget(self.file_path_label)

        # Label for columns to delete
        self.columns_to_delete_label = Label(
            text=f"Coloanele care se vor elimina din tabel:  {self.default_cols}",
            size_hint=(1, 0.5),
            height=30,
            markup=True,
            halign='left',
            valign='middle'
        )
        centered_layout.add_widget(self.columns_to_delete_label)

        # Button to edit columns to exclude
        self.edit_columns = Button(
            text="Editează coloanele de exclus din tabel",
            size_hint=(1, None),
            height=50,
            background_color=(1, 0, 0, 1)
        )
        # Bind to the set_columns_to_delete method
        self.edit_columns.bind(on_press=self.set_columns_to_delete)
        centered_layout.add_widget(self.edit_columns)

        # PDF File save label
        self.select_savelocation_label = Label(
            text="Pasul 3. Selectați folderul în care doriți să salvați Foaia de Parcurs",
            size_hint=(1, 0.5),
            height=30,
            markup=True,
            halign='left',
            valign='middle'
            )
        centered_layout.add_widget(self.select_savelocation_label)

        # Button to select save location file
        self.select_savelocation_button = Button(
            text="Apăsați pentru alege folderul",
            size_hint=(1, None),
            height=40,
            valign='middle'
            )
        self.select_savelocation_button.bind(on_press=self.save_location_popup)
        centered_layout.add_widget(self.select_savelocation_button)

        # Label to show the selected generated pdf file path
        self.pdf_path_label = Label(
            text="Nu ați selectat un folder pentru salvare pdf!",
            size_hint=(1, None),
            height=30,
            color=(1, 0, 0, 1)  # Set the text color to red (R, G, B, A) 
            )
        centered_layout.add_widget(self.pdf_path_label)

        # Button to generate report
        self.generate_report_button = Button(
            text="Generați raportul",
            size_hint=(1, None),
            height=70,
            )
        self.generate_report_button.bind(on_press=self.generate_report)
        centered_layout.add_widget(self.generate_report_button)

        # Status label to display messages
        self.status_label = Label(
            text="",
            size_hint=(1, None),
            height=30,
            )
        centered_layout.add_widget(self.status_label)
        
        # Adding the centered layout to the main layout
        main_layout.add_widget(centered_layout)

        return main_layout

    def _set_csv_path(self, selection):
        if selection:
            self.csv_file_path = selection[0]
            self.file_path_label.text = f"Fișier selectat: {self.csv_file_path}"
            self.file_path_label.color = (0, 1, 0, 1)  # set color to green
        else:
            self.file_path_label.text = "Nu ați selectat fișierul .csv"
        self.popup.dismiss()

    def select_csv_file(self, instance):
        # set the downloads folder dinamically with os
        # Set default path to the user's Downloads directory
        csv_folder = os.path.join(os.path.expanduser("~"), "Desktop", "rapoarte_itrack")

        # create FAZ folder on desktop if not there 
        if not os.path.exists(csv_folder):
            os.makedirs(csv_folder)

        # Create a FileChooser popup
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(path=csv_folder, filters=['*.csv'], dirselect=True, size_hint=(1, 0.9))
        content.add_widget(filechooser)

        # Add buttons to confirm or cancel
        btn_layout = BoxLayout(size_hint_y=None, height=50)

        select_btn = Button(text="Select", size_hint=(0.5, 1))
        select_btn.bind(on_press=lambda x: self._set_csv_path(filechooser.selection))

        cancel_btn = Button(text="Cancel", size_hint=(0.5, 1))
        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())

        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)

        content.add_widget(btn_layout)

        # Create and open the popup
        self.popup = Popup(title="Selectați fișierul de tip .csv", content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def add_remaining_fuel(self, *args):
        # Layout
        layout = BoxLayout(orientation='vertical', spacing=10)

        # Source Folder Input
        self.source_input = TextInput(hint_text='Diferență combustibil luna precedentă')
        layout.add_widget(self.source_input)

    # open pop up for saving location    
    def save_location_popup(self, instance):
        # Set default path to the user's Downloads directory
        save_folder = os.path.join(os.path.expanduser("~\\Desktop"))

        # create FAZ folder on desktop if not there 
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # Create a FileChooser popup for selecting the save location
        content = BoxLayout(orientation='vertical')
        self.filechooser = FileChooserListView(path=save_folder, size_hint=(1, 0.9), dirselect=True)
        content.add_widget(self.filechooser)

        # Add buttons to confirm or cancel
        btn_layout = BoxLayout(size_hint_y=None, height=50)

        select_btn = Button(text="Select", size_hint=(0.5, 1))
        select_btn.bind(on_press=lambda x: self.set_save_location(x))


        cancel_btn = Button(text="Anulare", size_hint=(0.5, 1))
        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())

        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)

        content.add_widget(btn_layout)

        # Create and open the popup
        self.popup = Popup(title="Selectați folderul pentru salvare", content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    
    # set the save location
    def set_save_location(self, instance):
        selection = self.filechooser.selection  # Get the selected directory from filechooser

        if selection:  # Ensure a directory was selected
            self.pdf_save_path = selection[0]  # Set the save location
            self.popup.dismiss()  # Close the popup

            # set succes label text
            self.pdf_path_label.text = f"Folder selectat: {self.pdf_save_path}"
            self.pdf_path_label.color = (0, 1, 0, 1)  # Set the label text color to green
        else:
            # Show error if no selection made
            error_popup = Popup(title="Error!",
                                content=Label(text="Nici un folder selectat."),
                                size_hint=(0.6, 0.4))
            error_popup.open()
            self.pdf_path_label.text = "Nu ați selectat fișierul .csv"

    # set columns to delete
    def set_columns_to_delete(self, instance):

        content = BoxLayout(orientation='vertical')
        # Convert the default columns list into a comma-separated string
        columns_str = ', '.join(self.default_cols)  # Convert list to string
        self.columns_editor = TextInput(
            text=columns_str,
            multiline=True,
            size_hint_y=None,
            height=200
            )
        content.add_widget(self.columns_editor)

        # Add buttons to confirm or cancel
        btn_layout = BoxLayout(size_hint_y=None, height=50)

        select_btn = Button(text="Salvare", size_hint=(0.5, 1))
        select_btn.bind(on_press=lambda x: self.save_columns(instance))


        cancel_btn = Button(text="Anulare", size_hint=(0.5, 1))
        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())

        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)

        content.add_widget(btn_layout)
        # Create and open the popup
        self.popup = Popup(title="Selectați coloanele de șters, scriindu-le pe rând exact cum apar în tabel, cu virgulă între ele, fără spații",
                           content=content,
                           size_hint=(0.8, 0.8))
        self.popup.open()

    def save_columns(self, instance):
        # Extract text input and split by commas to create a list
        columns_str = self.columns_editor.text
        self.default_cols = [col.strip() for col in columns_str.split(",") if col.strip()]
        
        # Update the main label
        self.columns_to_delete_label.text = f"Coloanele care se elimină din tabel: {', '.join(self.default_cols)}"

        # Close the popup
        self.popup.dismiss()


    def generate_report(self, instance=None):
        try:
            # Retrieve value from remaining fuel input field
            remaining_fuel_difference = self.fuel_float_input.text.strip()
            
            # retrieve filtered columns
            deleted_columns = self.default_cols
            # Convert the input to appropriate types
            remaining_fuel_difference = float(remaining_fuel_difference)
            
            # Validate that the pdf_save_path is defined
            if not hasattr(self, 'pdf_save_path') or not self.pdf_save_path:
                self.status_label.text = "Nu ați selectat încă locul de salvare."
                self.set_save_location(instance)
                return

            self.process_csv_to_pdf(self.csv_file_path, self.pdf_save_path, remaining_fuel_difference, deleted_columns)

            # # Create the main layout for the popup content
            # content = Label(text=f"Raport generat cu succes și salvat la:\n{self.pdf_save_path}")

            # # Create a header layout to contain the close button
            # header_layout = BoxLayout(size_hint_y=None, height=40)

            # # Create the close button ("X") and add functionality to close the popup
            # close_btn = Button(text="X", size_hint=(None, 1), width=40, background_normal='', background_color=(1, 0, 0, 1))
            # close_btn.bind(on_press=lambda x: self.popup.dismiss())
            
            # # Add the close button to the header layout and align it to the right
            # header_layout.add_widget(Widget())  # Adds a spacer to push the button to the right
            # header_layout.add_widget(close_btn)
            
            # # Add the header layout to the popup content
            # content.add_widget(header_layout)

            # Show confirmation of report generation
            confirmation_popup = Popup(title="Succes!",
                                       content=Label(text=f"Raport generat cu succes și salvat la:\n{self.pdf_save_path}"),
                                       size_hint=(0.6, 0.4))
            confirmation_popup.open()
            self.status_label.text = f"Raport generat cu succes! Salvat la: {self.pdf_save_path}"
        except ValueError:
            self.status_label.text = "Asigurați-vă că datele introduse sunt corecte."
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"

    # processing the csv data into a pdf table
    def process_csv_to_pdf(self, csv_file_path, pdf_file_path, previous_month_fuel, deleted_columns):
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
                df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Eroare de citire fișier .csv: {str(e)}")
            return
        
        try:
            summary_data = df.iloc[1:25].copy() if df.shape[0] > 25 else df.iloc[1:].copy()
            # keep only the first two columns
            summary_data = summary_data.iloc[:, :2]

            summary_data.columns = ["Parametri", "Date"]
            # Fetch gps data header
            header = df.iloc[26].tolist()  # Extract the 28th row as the header (index 27)
            gps_data = df.iloc[27:].copy()

            # Strip any leading/trailing whitespaces from the column names
            gps_data.columns = header    
        except Exception as e:
            print(f"Eroare de copiere dataframes: {str(e)}")

        try:
            # convert all necessary column data to float
            columns_to_convert_float = ["Distanță", "Consum mediu", "Alimentări importate"]
            gps_data[columns_to_convert_float] = gps_data[columns_to_convert_float].apply(pd.to_numeric, errors='coerce')
            # fill all NaN cells with 0 in Alimentări măsurate column
            gps_data["Alimentări importate"] = gps_data["Alimentări importate"].fillna(0)        

            # Fetch vehicle name, total consumption, distance, start date, end date with safe conversion to string
            self.vehicle_title = str(summary_data.iloc[0, 1]) if pd.notna(summary_data.iloc[0, 1]) else "-"
            self.total_consumption = str(summary_data.iloc[20, 1]) if pd.notna(summary_data.iloc[20, 1]) else "-"
            self.total_km = str(summary_data.iloc[14, 1]) if pd.notna(summary_data.iloc[14, 1]) else "-"
            self.start_date = summary_data.iloc[2, 1] if pd.notna(summary_data.iloc[3, 1]) else "-"
            self.end_date = summary_data.iloc[3, 1] if pd.notna(summary_data.iloc[3, 1]) else "-"

            try:
                total_fills = gps_data['Alimentări importate'].sum()
            except Exception as e:
                print(f"Eroare la însumarea numerelor din coloana 'Alimentari importate'! {e}")

            # Register the 'DejaVu Sans' font
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'C:/Users/PNB-IT/Documents/code/FAZ_PNB/Font/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf'))

            # Prepare the document
            path = pdf_file_path
            doc = SimpleDocTemplate(path, pagesize=landscape(A4), leftMargin=0.3*cm, rightMargin=0.3*cm, topMargin=0.5*cm, bottomMargin=0.5*cm)
            elements = []

            # set the generic styles from kivy
            styles = getSampleStyleSheet()

            # Create a custom style for title using the registered DejaVuSans font
            title_style = ParagraphStyle(
                name='TitleStyle',
                parent=styles['Normal'],
                fontName='DejaVuSans',
                fontSize=14,
                leading=12
            )

            # Create a custom style using the registered DejaVuSans font
            custom_style = ParagraphStyle(
                name='CustomStyle',
                parent=styles['Normal'],
                fontName='DejaVuSans',
                fontSize=7,
                leading=12
            )

            # Create a title
            title_text = f"Foaie de Parcurs - {self.vehicle_title} (Perioada: {self.start_date[:10]} - {self.end_date[:10]})"
            title = Paragraph(title_text, title_style)
            elements.append(title)
            elements.append(Spacer(1, 20))

            # Add the remaining fuel difference information
            previous_fuel = Paragraph(f"Combustibil rămas din luna precedentă: {previous_month_fuel} lit", custom_style)
            elements.append(previous_fuel)
            elements.append(Spacer(5, 1))

            # Add the total fills in current month
            fills = Paragraph(f"Alimentări combustibil luna curentă: {total_fills} lit", custom_style)
            elements.append(fills)
            elements.append(Spacer(5, 1))

            # Add the total consumption
            consumption = Paragraph(f"Consum total combustibil luna curentă: {self.total_consumption}", custom_style)
            elements.append(consumption)
            elements.append(Spacer(5, 1))

            # Add the remaining fuel difference information
            remaining_fuel = float(total_fills) + float(previous_month_fuel) - extract_floats_from_string(self.total_consumption)
            current_remaining_fuel = Paragraph(f"Diferență rămasă de combustibil în luna curentă: {remaining_fuel} lit", custom_style)
            elements.append(current_remaining_fuel)
            elements.append(Spacer(5, 1))

            # Add the total distance in km
            distance = Paragraph(f"Distanță parcursă în luna curentă: {self.total_km}", custom_style)
            elements.append(distance)
            elements.append(Spacer(5, 1))

            # Define specific widths for certain columns
            specific_column_widths = [1 * cm, 3.2 * cm, 2.7 * cm, 2.7 * cm, 6.5 * cm, 6.5 * cm, 1.5 * cm, 1.6 * cm, 1.7 * cm, 1.8 * cm]  # Example: first and fifth columns are 2 cm wide

            # cols to delete
            columns_to_delete = deleted_columns

            # Drop the specified columns from gps_data
            gps_data_filtered = gps_data.drop(columns=columns_to_delete, errors='ignore')

            # Convert all columns back to string and strip spaces
            gps_data_filtered = gps_data_filtered.astype(str).map(str.strip)

            # Create table data from the filtered DataFrame
            header = gps_data_filtered.columns.tolist()  # Get the new header after filtering
            data = [header] + gps_data_filtered.values.tolist()  # Include header row explicitly

            # Wrap cell contents in Paragraph to ensure text doesn't overflow
            wrapped_data = []
            for row in data:
                wrapped_row = []
                for cell in row:
                    if isinstance(cell, str):
                        cell = Paragraph(cell, custom_style)
                    wrapped_row.append(cell)
                wrapped_data.append(wrapped_row)

            # Create the table
            table = Table(wrapped_data, colWidths=specific_column_widths)
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),  # Use the DejaVuSans font for the table
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            # Add the table to the document
            elements.append(table)
            
            # Build the PDF document
            doc.build(elements)
            return self.vehicle_title, self.start_date, self.end_date
        except Exception as e:
            print(f"Eroare: {str(e)}")
# run the App
if __name__ == '__main__':
    CarReportApp().run()
