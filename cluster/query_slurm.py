import pyslurm
import polars as pl
import json
from datetime import datetime

from utils.log import get_logger
from utils.utils import cache_for_n_seconds

logger = get_logger(__name__)

@cache_for_n_seconds(seconds=2)
def get_slurm_node_df():
    try:
        json_string = json.dumps(pyslurm.node().get())
        json_object = json.loads(json_string)
        p = [v for v in json_object.values()]
        node_df = pl.DataFrame(p)
        node_df = node_df.drop(["core_spec_cnt", "cpu_spec_list", "core_spec_cnt", "extra", "features", "features_active", "mcs_label", "mem_spec_limit", "owner", "tmp_disk", "reason_time", "reason", "reason_uid", "power_mgmt", "energy"])
        node_df = node_df.with_columns(pl.col("last_busy", "slurmd_start_time").map_elements(lambda x: datetime.fromtimestamp(x), return_dtype=pl.Datetime))
        node_df = node_df.with_columns(pl.col("last_busy", "slurmd_start_time").map_elements(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"), return_dtype=pl.Utf8))
        node_df = node_df.with_columns(pl.col("gres", "gres_used").list.first())
        node_df = node_df.with_columns(pl.col("gres", "gres_used").map_elements(lambda x: int(x.split(":")[-1]) if isinstance(x, str) else x, return_dtype=pl.Int64))
        node_df = node_df.with_columns(pl.col("gres", "gres_used").fill_null(0))
        node_df = node_df.with_columns((pl.col("gres") - pl.col("gres_used")).alias("gres_available"))
        node_df = node_df.with_columns((pl.col("cpus") - pl.col("alloc_cpus")).alias("cpus_available"))
        node_df = node_df.with_columns([
            (pl.col("real_memory") / 1024).floor(),
            (pl.col("free_mem") / 1024).floor()
        ])
        node_df = node_df.filter(~pl.col("name").is_in([f"z0{i}" for i in range(10, 17)]))
        node_df = node_df.explode("partitions")
        node_df = node_df.group_by("partitions").agg(pl.col("name"), pl.col("state"), pl.col("cpus_available").sum(), pl.col("cpus").sum(), pl.col("gres_available").sum(), pl.col("gres").sum(), pl.col("free_mem").sum(), pl.col("real_memory").sum())
        node_df = node_df.with_columns(
            pl.concat_str([
                pl.col("gres_available").cast(pl.Utf8),
                pl.lit(" of "),
                pl.col("gres").cast(pl.Utf8)
            ]).alias("gres_status")
        )
        node_df = node_df.with_columns(
            pl.concat_str([
                pl.col("cpus_available").cast(pl.Utf8),
                pl.lit(" of "),
                pl.col("cpus").cast(pl.Utf8)
            ]).alias("cpus_status")
        )
        node_df = node_df.with_columns(
            pl.concat_str([
                pl.col("free_mem").cast(pl.Utf8),
                pl.lit(" GB of "),
                pl.col("real_memory").cast(pl.Utf8),
                pl.lit("GB")
            ]).alias("mem_status")
        )
        node_df = node_df.with_columns(pl.col("gres_status").replace("0 of 0", ""))
        custom_order = ["30mins", "4hours", "12hours", "5days", "gpu"]
        order_dict = {val: i for i, val in enumerate(custom_order)}
        node_df = (node_df
            .with_columns(
                pl.col("partitions").map_elements(lambda x: order_dict.get(x), return_dtype=pl.Int64).alias("__sort_key")
            )
            .sort("__sort_key")
            .drop("__sort_key")
        )
        return node_df
    except ValueError as e:
        logger.error(f"Error - {e.args[0]}")
        return pl.DataFrame()


@cache_for_n_seconds(seconds=2)
def get_slurm_job_df():
    try:
        jobs_json_string = json.dumps(pyslurm.job().get())
        jobs_json = json.loads(jobs_json_string)
        jobs = [dict for dict in jobs_json.values()]
        jobs_df = pl.DataFrame(jobs, infer_schema_length=None)
        jobs_df = jobs_df.drop(["cpus_allocated", "cpus_alloc_layout"])
        jobs_df = jobs_df.with_columns(pl.col("eligible_time", "end_time", "start_time", "submit_time").map_elements(lambda x: datetime.fromtimestamp(x), return_dtype=pl.Datetime))
        return jobs_df
    except ValueError as e:
        logger.error(f"Error - {e.args[0]}")
        return pl.DataFrame()


@cache_for_n_seconds(seconds=2)
def get_slurm_statistics_df():
    try:
        jobs_json_string = json.dumps(pyslurm.statistics().get())
        jobs_json = json.loads(jobs_json_string)
        jobs_json.pop("rpc_type_stats")
        jobs_json.pop("rpc_user_stats")
        statistics_df = pl.DataFrame(jobs_json, infer_schema_length=None)
        return statistics_df
    except ValueError as e:
        logger.error(f"Error - {e.args[0]}")
        return pl.DataFrame()
