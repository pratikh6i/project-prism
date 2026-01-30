"""
Project Prism - SCC Data Processor
==================================
Processes Security Command Center exports and generates cleaned Excel reports.
"""

import io
import re
from typing import Optional

import pandas as pd

from utils.logger import logger


def normalize_column_name(name: str) -> str:
    """
    Normalize column names to a consistent format.
    
    Args:
        name: Original column name
    
    Returns:
        Normalized column name (lowercase, underscores)
    """
    # Remove leading/trailing whitespace
    name = str(name).strip()
    
    # Replace spaces and special characters with underscores
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)
    
    # Remove leading/trailing underscores
    name = name.strip('_')
    
    return name


def process_scc_export(
    raw_df: pd.DataFrame,
    rules_df: Optional[pd.DataFrame] = None
) -> io.BytesIO:
    """
    Process SCC export data and generate a multi-tab Excel file.
    
    Args:
        raw_df: Raw DataFrame from SCC export
        rules_df: Optional DataFrame with filtering rules
                  Expected columns: 'category', 'columns_to_keep'
    
    Returns:
        BytesIO object containing the Excel file
    """
    logger.info(f"Processing SCC export with {len(raw_df)} rows...")
    
    # Create a copy and normalize column names
    df = raw_df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]
    
    logger.debug(f"Normalized columns: {list(df.columns)}")
    
    # Identify the category column (common variations)
    category_col = None
    for col in ['category', 'finding_category', 'type', 'finding_type', 'class']:
        if col in df.columns:
            category_col = col
            break
    
    if category_col is None:
        # If no category column found, create a default one
        logger.warning("No category column found. Using 'All Findings' as default.")
        df['category'] = 'All Findings'
        category_col = 'category'
    
    # Get unique categories
    categories = df[category_col].unique()
    logger.info(f"Found {len(categories)} unique categories")
    
    # Create output Excel file in memory
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Process each category
        for category in categories:
            # Filter data for this category
            category_df = df[df[category_col] == category].copy()
            
            # Apply column filtering rules if provided
            if rules_df is not None and not rules_df.empty:
                category_df = apply_column_rules(category_df, category, rules_df)
            
            # Clean the sheet name (Excel has restrictions)
            sheet_name = clean_sheet_name(str(category))
            
            # Write to Excel
            category_df.to_excel(writer, sheet_name=sheet_name, index=False)
            logger.debug(f"Written sheet '{sheet_name}' with {len(category_df)} rows")
        
        # Add a summary sheet
        summary_data = []
        for category in categories:
            count = len(df[df[category_col] == category])
            summary_data.append({'Category': category, 'Finding Count': count})
        
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values('Finding Count', ascending=False)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    output.seek(0)
    logger.info("SCC export processing complete!")
    
    return output


def apply_column_rules(
    df: pd.DataFrame,
    category: str,
    rules_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Apply column filtering rules to a DataFrame.
    
    Args:
        df: DataFrame to filter
        category: Current category being processed
        rules_df: DataFrame with rules (columns: 'category', 'columns_to_keep')
    
    Returns:
        Filtered DataFrame with only specified columns
    """
    # Normalize category for matching
    normalized_category = normalize_column_name(category)
    
    # Find matching rule
    rules_df_normalized = rules_df.copy()
    if 'category' in rules_df_normalized.columns:
        rules_df_normalized['category_normalized'] = rules_df_normalized['category'].apply(
            lambda x: normalize_column_name(str(x))
        )
        
        matching_rules = rules_df_normalized[
            rules_df_normalized['category_normalized'] == normalized_category
        ]
        
        if not matching_rules.empty and 'columns_to_keep' in matching_rules.columns:
            columns_to_keep = matching_rules.iloc[0]['columns_to_keep']
            
            if isinstance(columns_to_keep, str):
                # Parse comma-separated column list
                columns_list = [
                    normalize_column_name(col.strip())
                    for col in columns_to_keep.split(',')
                ]
                
                # Keep only columns that exist in the DataFrame
                valid_columns = [col for col in columns_list if col in df.columns]
                
                if valid_columns:
                    return df[valid_columns]
    
    return df


def clean_sheet_name(name: str) -> str:
    """
    Clean a string to be used as an Excel sheet name.
    Excel sheet names have restrictions:
    - Max 31 characters
    - Cannot contain: [ ] : * ? / \
    
    Args:
        name: Original name
    
    Returns:
        Cleaned sheet name
    """
    # Remove invalid characters
    invalid_chars = r'[\[\]:*?/\\]'
    name = re.sub(invalid_chars, '', name)
    
    # Truncate to 31 characters
    if len(name) > 31:
        name = name[:28] + '...'
    
    # Handle empty names
    if not name.strip():
        name = 'Sheet'
    
    return name


def validate_scc_file(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Validate that an uploaded file is a valid SCC export.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if df.empty:
        return False, "The uploaded file is empty."
    
    if len(df.columns) < 2:
        return False, "The file has too few columns. Expected an SCC export with multiple columns."
    
    # Check for common SCC export columns (case-insensitive)
    normalized_cols = [normalize_column_name(col) for col in df.columns]
    
    # Common SCC columns
    common_scc_cols = [
        'finding', 'severity', 'resource', 'project', 'category',
        'state', 'source', 'description', 'recommendation'
    ]
    
    matches = sum(1 for col in common_scc_cols if col in normalized_cols)
    
    if matches < 2:
        logger.warning("Uploaded file may not be an SCC export. Proceeding anyway.")
        return True, "Warning: This file may not be a standard SCC export, but we'll try to process it."
    
    return True, "Valid SCC export file detected."
