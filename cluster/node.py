import polars as pl
from prettytable import PrettyTable

from cluster.query_slurm import get_slurm_node_df, get_slurm_job_df
from utils.log import get_logger

logger = get_logger(__name__)


def get_node_info():
    """
    Gets basic Slurm node information.

    Returns:
        A string containing formatted node information.
    """
    node_df = get_slurm_node_df()
    if node_df.is_empty():
        logger.warning("No Nodes found!")
        return "No nodes found."
    
    pretty_column_names = {"partitions": "Partitions", "cpus_status": "CPUs", "mem_status": "Memory", "gres_status": "GPUs"}
    
    node_df_selection = node_df.select("partitions", "cpus_status", "mem_status", "gres_status")
    
    table = PrettyTable()
    table.field_names = [pretty_column_names.get(col) for col in node_df_selection.columns]
    for row in node_df_selection.iter_rows():
        table.add_row(list(row))

    output = "Slurm Node Information:\n\n"
    output += table.get_string()
    
    return output