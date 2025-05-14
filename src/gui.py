import customtkinter as ctk

class AppGui:
    def __init__(self, parent, select_callback, process_callback):
        self.parent = parent
        
        # Configure appearance
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # Configure main window
        parent.title("Processador de Fatura")
        parent.geometry("800x600")
        parent.minsize(600, 400)
        
        # Configure grid
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)
        
        # Title frame
        self.title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        self.title_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self.title_frame, 
            text="Processador de Fatura",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=10)
        
        # Controls frame
        self.controls_frame = ctk.CTkFrame(parent)
        self.controls_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure(0, weight=1)
        
        # File selection frame
        self.file_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.file_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)
        
        self.file_label = ctk.CTkLabel(
            self.file_frame, 
            text="Nenhum arquivo selecionado",
            font=ctk.CTkFont(size=12)
        )
        self.file_label.grid(row=0, column=0, padx=5, sticky="w")
        
        self.select_button = ctk.CTkButton(
            self.file_frame,
            text="Selecionar Fatura",
            command=select_callback,
            width=150
        )
        self.select_button.grid(row=0, column=1, padx=5)
        
        # Options frame
        self.options_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.options_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Add toggles
        self.auto_close_var = ctk.BooleanVar(value=True)
        self.auto_open_var = ctk.BooleanVar(value=True)
        
        self.auto_close_toggle = ctk.CTkSwitch(
            self.options_frame,
            text="Fechar ao finalizar",
            variable=self.auto_close_var,
            font=ctk.CTkFont(size=12)
        )
        self.auto_close_toggle.grid(row=0, column=0, padx=5)
        
        self.auto_open_toggle = ctk.CTkSwitch(
            self.options_frame,
            text="Abrir arquivo ao finalizar",
            variable=self.auto_open_var,
            font=ctk.CTkFont(size=12)
        )
        self.auto_open_toggle.grid(row=0, column=1, padx=5)
        
        self.process_button = ctk.CTkButton(
            self.options_frame,
            text="Processar",
            command=process_callback,
            width=150
        )
        self.process_button.grid(row=0, column=2, padx=5)
        
        # Log frame
        self.log_frame = ctk.CTkFrame(parent)
        self.log_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)
        
        self.log_label = ctk.CTkLabel(
            self.log_frame,
            text="Log de Processamento",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.log_label.grid(row=0, column=0, pady=5)
        
        self.text_area = ctk.CTkTextbox(
            self.log_frame,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.text_area.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")

    def get_auto_close(self):
        return self.auto_close_var.get()
        
    def get_auto_open(self):
        return self.auto_open_var.get()
