import pandas as pd
import os
from IPython.display import display

class DataFrameMerger:
    """
    A class to facilitate merging a user-provided Pandas DataFrame with an external file
    (CSV, TSV, XLS, XLSX). It handles:
    
    1. Reading the external file.
    2. Displaying a preview of the external file.
    3. Merging the two DataFrames on user-specified columns.
    4. Handling multiple comma-separated IDs in the external file.
    5. Checking for potential "double-merge" scenarios, i.e. if the external file's
       columns already exist in the main DataFrame.
    """
    
    def __init__(self, df):
        """
        Initialize the DataFrameMerger with the current in-memory DataFrame.
        
        Parameters
        ----------
        df : pd.DataFrame
            The in-memory DataFrame that we want to merge onto.
        """
        self.df = df
        self.external_df = None
        self.file_path = None
        self.df_merge_col = None
        self.external_merge_col = None
        self.multiple_id_delimiter = None

    def set_file_path(self, file_path):
        """
        Set the file path to the external file (csv, tsv, xls, xlsx).
        
        Parameters
        ----------
        file_path : str
            The path to the file on disk.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        self.file_path = file_path
        self._read_file()

    def _read_file(self):
        """
        Internal method to read the external file and store it in self.external_df.
        Auto-detects format based on file extension.
        """
        ext = os.path.splitext(self.file_path)[-1].lower()

        if ext == '.csv':
            self.external_df = pd.read_csv(self.file_path)
        elif ext == '.tsv':
            self.external_df = pd.read_csv(self.file_path, sep='\t')
        elif ext in ['.xls', '.xlsx']:
            self.external_df = pd.read_excel(self.file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
            
        print(f"Successfully read file: {self.file_path}")
        print(f"External DataFrame shape: {self.external_df.shape}")

    def preview_file(self, n=5):
        """
        Display a preview of the external file (first n rows).
        
        Parameters
        ----------
        n : int, optional
            Number of rows to display. Default is 5.
        """
        if self.external_df is None:
            raise ValueError("No file has been loaded. Use `set_file_path` first.")
        
        print(f"Showing first {n} rows of external DataFrame:")
        display(self.external_df.head(n))

    def set_merge_columns(self, df_col, external_col, multiple_id_delimiter=None):
        """
        Set the column names for merging the DataFrame (self.df) and the external file (self.external_df).
        Optionally specify a delimiter if the external column has multiple IDs separated by a delimiter.
        
        Parameters
        ----------
        df_col : str
            The column name in the current df to merge on.
        external_col : str
            The column name in the external file to merge on.
        multiple_id_delimiter : str, optional
            If the external_col contains multiple IDs separated by a delimiter, specify it here.
            Example: ',' if the IDs are comma-separated.
        """
        if df_col not in self.df.columns:
            raise ValueError(f"Column '{df_col}' not found in the current DataFrame.")
        if external_col not in self.external_df.columns:
            raise ValueError(f"Column '{external_col}' not found in the external DataFrame.")
        
        self.df_merge_col = df_col
        self.external_merge_col = external_col
        self.multiple_id_delimiter = multiple_id_delimiter
        
        print(f"Merging on:\n- Current DF column: {df_col}\n- External DF column: {external_col}")
        if multiple_id_delimiter:
            print(f"Handling multiple IDs in the external file with delimiter: '{multiple_id_delimiter}'")

    def merge_data(self, how='left'):
        """
        Merge the current DataFrame (self.df) with the external DataFrame (self.external_df) using
        the specified columns. If multiple_id_delimiter is set, the external column is split and
        expanded before merging. Includes a check to see if all columns already exist in self.df
        (i.e. double merge scenario) before proceeding.
        
        Parameters
        ----------
        how : str, optional
            Type of merge to perform. One of 'left', 'right', 'inner', 'outer'.
            Default is 'left'.
        
        Returns
        -------
        pd.DataFrame
            The merged DataFrame.
        """
        if self.df_merge_col is None or self.external_merge_col is None:
            raise ValueError("Merge columns not set. Use `set_merge_columns` first.")

        # Double-merge check: Are all external columns (besides the merge col) already in the main DataFrame?
        self._check_for_double_merge()

        if self.multiple_id_delimiter is not None:
            # Expand the external dataframe so that rows with multiple IDs become multiple rows
            expanded_df = self._expand_multiple_ids(
                self.external_df,
                self.external_merge_col,
                self.multiple_id_delimiter
            )
            merged_df = pd.merge(
                self.df,
                expanded_df,
                left_on=self.df_merge_col,
                right_on=self.external_merge_col,
                how=how
            )
        else:
            merged_df = pd.merge(
                self.df,
                self.external_df,
                left_on=self.df_merge_col,
                right_on=self.external_merge_col,
                how=how
            )
        
        print(f"Merged DataFrame shape: {merged_df.shape} using how='{how}'")
        return merged_df

    def _expand_multiple_ids(self, df, col, delimiter):
        """
        Internal helper to split rows on a column containing multiple delimiter-separated IDs,
        then explode them into multiple rows, each with a single ID in 'col'.
        
        Parameters
        ----------
        df : pd.DataFrame
            The external DataFrame with the column containing multiple IDs.
        col : str
            The column name that has the multiple IDs.
        delimiter : str
            The delimiter used to split the IDs (e.g. ',').
            
        Returns
        -------
        pd.DataFrame
            A DataFrame with exploded IDs in the specified column.
        """
        df_copy = df.copy()
        # Convert column to string and split on the delimiter -> list of IDs
        df_copy[col] = df_copy[col].astype(str).apply(lambda x: x.split(delimiter))
        # Explode the lists into multiple rows
        df_exploded = df_copy.explode(col)
        # Strip whitespace if any
        df_exploded[col] = df_exploded[col].str.strip()
        return df_exploded
    
    def _check_for_double_merge(self):
        """
        Internal helper to check if all columns from the external DataFrame
        (excluding the merge column) are already present in the main DataFrame.
        If so, ask the user for confirmation before proceeding.
        """
        external_cols = set(self.external_df.columns)
        df_cols = set(self.df.columns)

        # Exclude the external merge column from consideration, since it may be in both already
        external_cols_to_check = external_cols - {self.external_merge_col}

        # If all these columns are already in df, it's likely a double merge scenario
        if external_cols_to_check.issubset(df_cols):
            print("\nWARNING: All columns from the external file (except the merge column) "
                  "already exist in the main DataFrame. This might be a double merge.\n")
            confirm = input("All columns from the external file (except the merge column) "
                  "already exist in the main DataFrame. This might be a double merge. Do you want to proceed with the merge? (y/n): ").strip().lower()
            if confirm not in ["y", "yes"]:
                print("Merge operation canceled.")
                # Raise an exception or return None to stop the merge
                raise RuntimeError("Merge canceled by user.")