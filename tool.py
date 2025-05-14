import customtkinter as ctk
from tkinter import filedialog
import sys
import os
from datetime import datetime
from src.excel_reader import ExcelReader
from src.data_processor import DataProcessor
from src.gui import AppGui
import pandas as pd

class FaturaProcessorApp:
    def __init__(self):
        self.app = ctk.CTk()
        
        # Initialize modules
        self.excel_reader = ExcelReader(self.log_message)
        self.data_processor = DataProcessor(self.log_message)
        
        # Initialize GUI
        self.gui = AppGui(self.app, self.select_file, self.process_file)
        
        # Store whether we should auto-close from command line
        self.auto_close = len(sys.argv) > 1
        if self.auto_close:
            self.gui.auto_close_var.set(True)
        
        self.selected_file = None

        # Check if DE-PARA.xlsx exists first
        self.depara_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DE-PARA.xlsx")
        if not os.path.exists(self.depara_path):
            example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DE-PARA.example.xlsx")
            import shutil
            shutil.copy2(example_path, self.depara_path)
            from tkinter import messagebox
            self.app.after(100, lambda: self.show_depara_warning(self.depara_path))
            return

        # Check if file was passed as argument
        if len(sys.argv) > 1:
            filepath = sys.argv[1]
            if os.path.exists(filepath):
                self.selected_file = filepath
                self.gui.file_label.configure(text=os.path.basename(filepath))
                self.log_message(f"Arquivo carregado: {os.path.basename(filepath)}")
                self.app.after(100, self.process_file)

    def log_message(self, message):
        self.gui.text_area.insert("end", f"{message}\n")
        self.gui.text_area.see("end")

    def select_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filepath:
            self.selected_file = filepath
            self.gui.file_label.configure(text=os.path.basename(filepath))
            self.log_message(f"Arquivo selecionado: {os.path.basename(filepath)}")

    def process_file(self):
        if not self.selected_file:
            self.log_message("Por favor, selecione um arquivo de fatura primeiro!")
            return
            
        try:
            # Read files
            df_fatura = self.excel_reader.read_excel_com(self.selected_file)
            if df_fatura is None:
                return
                
            df_fatura = self.data_processor.clean_dataframe(df_fatura)
            df_depara = pd.read_excel(self.depara_path)
            df_depara = self.data_processor.clean_dataframe(df_depara)
            
            # Validate data
            valid, missing_logons = self.data_processor.validate_dataframes(df_fatura, df_depara)
            if not valid:
                return
                
            if missing_logons:
                self.log_message("\nAtenção: Os seguintes logons não foram encontrados no DE-PARA:")
                for logon in missing_logons:
                    self.log_message(f"- {logon}")
                self.log_message("\nPor favor, atualize o arquivo DE-PARA.xlsx com estes logons e tente novamente.")
                return
            
            # Process data
            df_fatura, df_consolidado = self.data_processor.process_fatura(df_fatura, df_depara)
            
            # Save results
            # Create default output filename
            default_filename = f"Fatura_Processada_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Open file save dialog
            output_filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=default_filename,
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if output_filename:
                # Save to new Excel file with both sheets
                with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
                    df_fatura.to_excel(writer, sheet_name='Fatura', index=False)
                    df_consolidado.to_excel(writer, sheet_name='Consolidado', index=False)
                
                self.log_message(f"\nProcessamento concluído com sucesso!")
                self.log_message(f"Arquivo salvo como: {output_filename}")
                
                # Handle auto-open
                if self.gui.get_auto_open():
                    os.startfile(output_filename)
                
                # Handle auto-close
                should_close = self.auto_close or self.gui.get_auto_close()
                if should_close:
                    self.app.after(1000, self.app.quit)
            else:
                self.log_message("\nOperação cancelada pelo usuário.")
                should_close = self.auto_close or self.gui.get_auto_close()
                if should_close:
                    self.app.after(1000, self.app.quit)
            
        except Exception as e:
            self.log_message(f"Erro durante o processamento: {str(e)}")
            should_close = self.auto_close or self.gui.get_auto_close()
            if should_close:
                self.app.after(3000, self.app.quit)

    def show_depara_warning(self, depara_path):
        """Show warning about DE-PARA configuration and open the file"""
        from tkinter import messagebox
        messagebox.showwarning("Configuração Necessária", 
            "O arquivo DE-PARA.xlsx ainda não foi configurado.\n\n" +
            "A planilha será aberta para você configurar o mapeamento de logons e sites.\n" +
            "Por favor, configure-a antes de processar faturas.")
        os.startfile(depara_path)
        self.app.quit()

def main():
    app = FaturaProcessorApp()
    app.app.mainloop()

if __name__ == "__main__":
    main()