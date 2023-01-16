def escribaExcel(writer, sheetName, df):
    df.to_excel(writer, sheet_name=sheetName, index=False, na_rep='NaN')

# Auto-adjust columns' width
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets[sheetName].set_column(col_idx, col_idx, column_width+2)

