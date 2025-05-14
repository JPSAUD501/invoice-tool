import pandas as pd

class DataProcessor:
    def __init__(self, logger):
        self.logger = logger

    def clean_dataframe(self, df):
        """Clean and prepare the dataframe"""
        if df is None or df.empty:
            return None
        
        # Create an explicit copy
        df = df.copy()
        
        # Clean Nome do Logon
        df.loc[:, 'Nome do Logon'] = df['Nome do Logon'].fillna('')
        df.loc[:, 'Nome do Logon'] = df['Nome do Logon'].astype(str).str.strip()
        df = df[df['Nome do Logon'] != ''].copy()
        
        # Clean Valor Total Produto if exists
        if 'Valor Total Produto' in df.columns:
            df.loc[:, 'Valor Total Produto'] = pd.to_numeric(df['Valor Total Produto'], errors='coerce')
            df.loc[:, 'Valor Total Produto'] = df['Valor Total Produto'].fillna(0)
            
        return df

    def validate_dataframes(self, df_fatura, df_depara):
        """Validate dataframes and return missing logons if any"""
        required_columns = ['Nome do Logon', 'Valor Total Produto']
        missing_columns = [col for col in required_columns if col not in df_fatura.columns]
        if missing_columns:
            self.logger(f"Erro: Colunas ausentes na fatura: {', '.join(missing_columns)}")
            return False, None
            
        if 'Nome do Logon' not in df_depara.columns:
            self.logger("Erro: Coluna 'Nome do Logon' ausente no arquivo DE-PARA.xlsx")
            return False, None
            
        logons_fatura = set(df_fatura['Nome do Logon'].str.upper().str.strip().unique())
        logons_depara = set(df_depara['Nome do Logon'].str.upper().str.strip().unique())
        missing_logons = logons_fatura - logons_depara
        
        return True, missing_logons

    def process_fatura(self, df_fatura, df_depara):
        """Process the fatura with the DE-PARA mapping"""
        # Create explicit copies to avoid warnings
        df_fatura = df_fatura.copy()
        
        site_mapping = df_depara.set_index('Nome do Logon')['Site'].to_dict()
        df_fatura.loc[:, 'Site'] = df_fatura['Nome do Logon'].map(site_mapping)
        df_consolidado = df_fatura.groupby('Site')['Valor Total Produto'].sum().reset_index()
        
        return df_fatura, df_consolidado
