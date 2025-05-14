import customtkinter as ctk
import pandas as pd
from tkinter import filedialog
import sys
import os
from datetime import datetime

class FaturaProcessorApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Processador de Fatura")
        self.app.geometry("600x400")
        
        # Store whether we should auto-close
        self.auto_close = len(sys.argv) > 1
        
        # Configure grid
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(1, weight=1)
        
        # Frame for file selection
        self.file_frame = ctk.CTkFrame(self.app)
        self.file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Label to show selected file
        self.file_label = ctk.CTkLabel(self.file_frame, text="Nenhum arquivo selecionado")
        self.file_label.grid(row=0, column=0, padx=5, pady=5)
        
        # Button to select file
        self.select_button = ctk.CTkButton(self.file_frame, text="Selecionar Fatura", command=self.select_file)
        self.select_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Process button
        self.process_button = ctk.CTkButton(self.file_frame, text="Processar", command=self.process_file)
        self.process_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Text area for messages
        self.text_area = ctk.CTkTextbox(self.app, width=580, height=300)
        self.text_area.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.selected_file = None

        # Check if DE-PARA.xlsx exists first
        depara_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DE-PARA.xlsx")
        if not os.path.exists(depara_path):
            example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DE-PARA.example.xlsx")
            import shutil
            shutil.copy2(example_path, depara_path)
            from tkinter import messagebox
            # Use after to ensure the window is fully loaded before showing the message
            self.app.after(100, lambda: self.show_depara_warning(depara_path))
            return

        # Check if file was passed as argument
        if len(sys.argv) > 1:
            filepath = sys.argv[1]
            if os.path.exists(filepath):
                self.selected_file = filepath
                self.file_label.configure(text=os.path.basename(filepath))
                self.log_message(f"Arquivo carregado: {os.path.basename(filepath)}")
                # Auto-process the file
                self.app.after(100, self.process_file)

    def log_message(self, message):
        self.text_area.insert("end", f"{message}\n")
        self.text_area.see("end")

    def select_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filepath:
            self.selected_file = filepath
            self.file_label.configure(text=os.path.basename(filepath))
            self.log_message(f"Arquivo selecionado: {os.path.basename(filepath)}")

    def process_file(self):
        if not self.selected_file:
            self.log_message("Por favor, selecione um arquivo de fatura primeiro!")
            return
            
        try:
            # Read the fatura file

            # Read the fatura file
            df_fatura = pd.read_excel(self.selected_file)
            df_fatura['Nome do Logon'] = df_fatura['Nome do Logon'].astype(str).str.strip()
            df_fatura = df_fatura.replace('nan', pd.NA)
            df_fatura = df_fatura.dropna(subset=['Nome do Logon'])
            
            # Read the DE-PARA file
            df_depara = pd.read_excel(depara_path)
            df_depara['Nome do Logon'] = df_depara['Nome do Logon'].astype(str).str.strip()
            
            # Verify required columns in fatura
            required_columns = ['Nome do Logon', 'Valor Total Produto']
            missing_columns = [col for col in required_columns if col not in df_fatura.columns]
            if missing_columns:
                self.log_message(f"Erro: Colunas ausentes na fatura: {', '.join(missing_columns)}")
                return
                
            # Verify required columns in DE-PARA
            if 'Nome do Logon' not in df_depara.columns:
                self.log_message("Erro: Coluna 'Nome do Logon' ausente no arquivo DE-PARA.xlsx")
                return
                
            # Clean and standardize logons for comparison
            logons_fatura = set(df_fatura['Nome do Logon'].str.upper().str.strip().unique())
            logons_depara = set(df_depara['Nome do Logon'].str.upper().str.strip().unique())
            missing_logons = logons_fatura - logons_depara
            
            if missing_logons:
                self.log_message("\nAtenção: Os seguintes logons não foram encontrados no DE-PARA:")
                for logon in missing_logons:
                    self.log_message(f"- {logon}")
                self.log_message("\nPor favor, atualize o arquivo DE-PARA.xlsx com estes logons e tente novamente.")
                return
            
            # Create a mapping dictionary from DE-PARA
            site_mapping = df_depara.set_index('Nome do Logon')['Site'].to_dict()
            
            # Add the Site column to the fatura
            df_fatura['Site'] = df_fatura['Nome do Logon'].map(site_mapping)
            
            # Create the consolidated sheet
            df_consolidado = df_fatura.groupby('Site')['Valor Total Produto'].sum().reset_index()
            
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
                if self.auto_close:
                    self.app.after(1000, self.app.quit)
            else:
                self.log_message("\nOperação cancelada pelo usuário.")
                if self.auto_close:
                    self.app.after(1000, self.app.quit)
            
        except Exception as e:
            self.log_message(f"Erro durante o processamento: {str(e)}")
            if self.auto_close:
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