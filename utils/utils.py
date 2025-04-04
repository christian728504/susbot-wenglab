import functools
import time
import subprocess
from dataclasses import dataclass

# https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix="", with_unit=True):
    for unit in ["M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return (int(num), f"{unit}{suffix}") if with_unit else int(num)
        num /= 1024.0
    return (int(num), f"Y{suffix}") if with_unit else int(num)

def cache_for_n_seconds(seconds=1800):
    def decorator_cache_for_n_seconds(func):
        @functools.wraps(func)
        def wrapper_cache_for_n_seconds(*args, **kwargs):
            if not hasattr(wrapper_cache_for_n_seconds, "last_call_value") or len(wrapper_cache_for_n_seconds.last_call_value) == 0 or time.time() - wrapper_cache_for_n_seconds.last_call_time >= seconds:
                wrapper_cache_for_n_seconds.last_call_time = time.time()
                wrapper_cache_for_n_seconds.last_call_value = func(*args, **kwargs)
            return wrapper_cache_for_n_seconds.last_call_value
        return wrapper_cache_for_n_seconds
    return decorator_cache_for_n_seconds

def _format_time(seconds):
    days = int(seconds / (24 * 60 * 60))
    hours = int((seconds % (24 * 60 * 60)) / (60 * 60))
    mins = int((seconds % (60 * 60)) / 60)
    secs = int(seconds % 60)

    parts = []
    if days > 0:
        parts.append(f"{days}-")
    if hours > 0:
        parts.append(f"{hours}:")
    parts.append(f"{mins}:")
    parts.append(f"{secs}")

    return "".join(parts)

@dataclass
class User:
    username: str = None
    unix_uid: str = None
    real_name: str = None

def _get_users():
    user_groups = ["xusers", "zusers", "tusers", "rusers", "musers"]
    result = ""
    for user_group in user_groups:
        result += (subprocess.run(['getent', 'group', f"{user_group}"], capture_output=True, text=True)).stdout

    users_groups = result.strip().split('\n')

    members = []
    for user_group in users_groups:
        fields = user_group.split(':')
        members.extend(fields[-1].split(','))

    user_info = []
    for member in set(members):
        result = subprocess.run(['getent', 'passwd', f"{member}"], capture_output=True, text=True)
        users_data = result.stdout.strip().split('\n')

        for user_line in users_data:
            fields = user_line.split(':')
            username, _, unix_uid, _, real_name = fields[:5]
            user_info.append(User(str(username), str(unix_uid), str(real_name)))
            
    return user_info
