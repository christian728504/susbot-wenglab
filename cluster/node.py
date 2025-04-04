import polars as pl
from prettytable import PrettyTable

from cluster.query_slurm import get_slurm_node_df, get_slurm_job_df
from utils.log import get_logger
from utils.utils import _get_users

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
    
    pretty_column_names = {"partitions": "Partitions", "cpus": "CPUs", "cpus_usage": "CPU usage", "real_memory": "RAM", "mem_usage": "RAM usage", "gres": "GPUs", "gres_usage": "GPU usage"}
    
    node_df_selection = node_df.select("partitions", "cpus", "cpus_usage", "real_memory", "mem_usage", "gres", "gres_usage")
    
    table = PrettyTable()
    table.field_names = [pretty_column_names.get(col) for col in node_df_selection.columns]
    for row in node_df_selection.iter_rows():
        table.add_row(list(row))

    output = "Slurm Node Information:\n\n"
    output += table.get_string()
    
    return output

def get_squeue(real_name: str, username: str = None) -> pl.DataFrame:
    USERS = _get_users()
    
    job_df = get_slurm_job_df()
    if job_df.is_empty():
        logger.warning(f"No Jobs found for {real_name}!")
        return f"No Jobs found for {real_name}."
    
    if username:
        for user in USERS:
            if user.username == username:
                unix_uid = user.unix_uid
    else:
        for user in USERS:
            if user.real_name == real_name:
                unix_uid = user.unix_uid
                username = user.username
            
    pretty_column_names = {"id": "Job ID", "name": "Job Name", "partition": "Partition", "nodes": "Nodes", "num_nodes": "Num Nodes", "job_state": "State", "run_time_str": "Run Time", "username": "Username"}
    
    job_df = job_df.filter(pl.col("user_id") == unix_uid)
    job_df = job_df.with_columns(pl.col("user_id").replace(unix_uid, username).alias("username"))
    table = PrettyTable()
    table.field_names = [pretty_column_names.get(col) for col in job_df.columns]
    for row in job_df.iter_rows():
        table.add_row(list(row))
        
    output = "Squeue:\n\n"
    output += table.get_string()
    
    return output
    
    