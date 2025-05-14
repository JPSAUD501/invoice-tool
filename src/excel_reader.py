import pandas as pd
import pythoncom
from win32com import client
import time
import numpy as np
import os

class ExcelReader:
    def __init__(self, logger):
        self.logger = logger

    def read_excel_com(self, filepath):
        """Read Excel file using COM object and return dataframe"""
        excel = None
        try:
            pythoncom.CoInitialize()
            
            excel = client.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            
            self.logger("Abrindo arquivo protegido...")
            wb = excel.Workbooks.Open(os.path.abspath(filepath))
            time.sleep(1)
            
            sheet = wb.Worksheets(1)
            last_row = sheet.UsedRange.Row + sheet.UsedRange.Rows.Count - 1
            last_col = sheet.UsedRange.Column + sheet.UsedRange.Columns.Count - 1
            
            # Leitura dos dados
            headers = [str(h) if h is not None else f"Column_{i+1}" 
                      for i, h in enumerate(sheet.Range(sheet.Cells(1, 1), sheet.Cells(1, last_col)).Value[0])]
            
            data = []
            chunk_size = 1000
            
            self.logger("Lendo dados...")
            for start_row in range(2, last_row + 1, chunk_size):
                end_row = min(start_row + chunk_size - 1, last_row)
                chunk = sheet.Range(sheet.Cells(start_row, 1), sheet.Cells(end_row, last_col)).Value
                if chunk:
                    for row in chunk:
                        processed_row = []
                        for value in row:
                            if value is None:
                                processed_row.append(np.nan)
                            elif isinstance(value, (int, float, str)):
                                processed_row.append(value)
                            else:
                                try:
                                    processed_row.append(str(value))
                                except:
                                    processed_row.append(np.nan)
                        data.append(processed_row)
            
            wb.Close(False)
            
            df = pd.DataFrame(data, columns=headers)
            self.logger(f"Dados carregados: {len(df)} linhas")
            return df
            
        except Exception as e:
            self.logger(f"Erro ao ler arquivo: {str(e)}")
            return None
        finally:
            if excel:
                excel.Quit()
            pythoncom.CoUninitialize()
