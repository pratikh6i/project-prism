"""
SCC Data Processor
==================
Processes Security Command Center CSV exports.
Filters columns based on reference list and outputs clean Excel.
"""

import pandas as pd
from io import BytesIO
from typing import Tuple

from utils.logger import logger

# Reference columns to keep (from SCC Reference Sheet)
REFERENCE_COLUMNS = [
    "resource.gcp_metadata.project_display_name",
    "resource.display_name",
    "resource.type",
    "finding.state",
    "finding.category",
    "finding.event_time",
    "finding.create_time",
    "finding.property_data_types",
    "finding.severity",
    "finding.mute",
    "finding.mute_info.static_mute.state",
    "finding.mute_info.static_mute.apply_time",
    "finding.finding_class",
    "finding.vulnerability.cve.id",
    "finding.vulnerability.cve.references",
    "finding.vulnerability.cve.cvssv3",
    "finding.vulnerability.cve.upstream_fix_available",
    "finding.vulnerability.cve.zero_day",
    "finding.vulnerability.cve.impact",
    "finding.vulnerability.cve.exploitation_activity",
    "finding.vulnerability.cve.exploit_release_date",
    "finding.vulnerability.cve.first_exploitation_date",
    "finding.vulnerability.offending_package.package_name",
    "finding.vulnerability.offending_package.cpe_uri",
    "finding.vulnerability.offending_package.package_type",
    "finding.vulnerability.offending_package.package_version",
    "finding.vulnerability.fixed_package.package_name",
    "finding.vulnerability.fixed_package.cpe_uri",
    "finding.vulnerability.fixed_package.package_type",
    "finding.vulnerability.fixed_package.package_version",
    "finding.contacts",
    "finding.compliances",
    "finding.original_provider_id",
    "finding.access.principal_subject",
    "finding.source_properties",
    "finding.parent_display_name",
    "finding.description",
    "finding.iam_bindings",
    "finding.next_steps",
    "finding.kubernetes.objects",
    "finding.attack_exposure.score",
    "finding.attack_exposure.latest_calculation_time",
    "finding.attack_exposure.attack_exposure_result",
    "finding.attack_exposure.state",
    "finding.attack_exposure.exposed_low_value_resources_count",
    "finding.toxic_combination.attack_exposure_score",
    "finding.toxic_combination.related_findings",
    "finding.group_memberships",
    "resource.name",
    "resource.cloud_provider",
    "resource.service",
    "resource.location",
    "resource.gcp_metadata.project",
    "resource.gcp_metadata.parent",
    "resource.gcp_metadata.parent_display_name",
    "resource.gcp_metadata.folders",
    "resource.gcp_metadata.organization",
    "resource.resource_path.nodes",
    "resource.resource_path_string",
    "finding.cloud_armor.security_policy.name",
]


def validate_file(uploaded_file) -> Tuple[bool, str]:
    """
    Validate the uploaded file is a valid SCC CSV export.
    
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        # Check file size (max 50MB)
        uploaded_file.seek(0, 2)
        size = uploaded_file.tell()
        uploaded_file.seek(0)
        
        if size > 50 * 1024 * 1024:
            return False, "File too large. Maximum size is 50MB."
        
        if size == 0:
            return False, "File is empty."
        
        # Try to read as CSV
        df = pd.read_csv(uploaded_file, nrows=5)
        uploaded_file.seek(0)
        
        if df.empty:
            return False, "CSV file has no data."
        
        # Check if it has at least some expected SCC columns
        scc_indicators = ['finding.', 'resource.']
        has_scc_columns = any(
            any(indicator in col for indicator in scc_indicators)
            for col in df.columns
        )
        
        if not has_scc_columns:
            return False, "This doesn't look like an SCC export. Expected columns like 'finding.*' or 'resource.*'."
        
        return True, "Valid SCC export file."
        
    except Exception as e:
        logger.error(f"File validation error: {e}")
        return False, f"Could not read file: {str(e)}"


def process_scc_export(uploaded_file) -> Tuple[BytesIO, dict]:
    """
    Process SCC CSV export and filter to reference columns only.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        Tuple of (Excel file as BytesIO, stats dict)
    """
    logger.info("Starting SCC export processing")
    
    # Read the full CSV
    df = pd.read_csv(uploaded_file)
    original_rows = len(df)
    original_cols = len(df.columns)
    
    logger.info(f"Loaded CSV: {original_rows} rows, {original_cols} columns")
    
    # Find matching columns from reference list
    existing_cols = df.columns.tolist()
    matched_columns = [col for col in REFERENCE_COLUMNS if col in existing_cols]
    missing_columns = [col for col in REFERENCE_COLUMNS if col not in existing_cols]
    
    logger.info(f"Matched {len(matched_columns)} of {len(REFERENCE_COLUMNS)} reference columns")
    
    if not matched_columns:
        raise ValueError("No matching columns found. Please check if this is a valid SCC export.")
    
    # Filter to only matched columns
    df_clean = df[matched_columns].copy()
    
    # Rename first column to "Project Name" for readability
    if matched_columns and matched_columns[0] == "resource.gcp_metadata.project_display_name":
        df_clean = df_clean.rename(columns={"resource.gcp_metadata.project_display_name": "Project Name"})
    
    # Create Excel output
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_clean.to_excel(writer, sheet_name='Cleaned Findings', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Cleaned Findings']
        for idx, col in enumerate(df_clean.columns):
            max_length = max(
                df_clean[col].astype(str).map(len).max() if len(df_clean) > 0 else 0,
                len(str(col))
            )
            # Cap at 50 characters width
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[chr(65 + idx) if idx < 26 else f"A{chr(65 + idx - 26)}"].width = adjusted_width
    
    output.seek(0)
    
    # Collect stats
    stats = {
        "original_rows": original_rows,
        "original_columns": original_cols,
        "cleaned_columns": len(matched_columns),
        "missing_columns": len(missing_columns),
        "matched_column_names": matched_columns[:5],  # First 5 for display
    }
    
    logger.info(f"Processing complete: {len(matched_columns)} columns retained")
    
    return output, stats


def get_project_summary(uploaded_file) -> pd.DataFrame:
    """
    Get a summary of findings by project.
    
    Returns:
        DataFrame with project name and finding count
    """
    df = pd.read_csv(uploaded_file)
    uploaded_file.seek(0)
    
    project_col = "resource.gcp_metadata.project_display_name"
    
    if project_col not in df.columns:
        # Try alternate column names
        for col in df.columns:
            if 'project' in col.lower() and 'display' in col.lower():
                project_col = col
                break
    
    if project_col not in df.columns:
        return pd.DataFrame(columns=['Project Name', 'Finding Count'])
    
    summary = df.groupby(project_col).size().reset_index(name='Finding Count')
    summary = summary.rename(columns={project_col: 'Project Name'})
    summary = summary.sort_values('Finding Count', ascending=False)
    
    return summary
