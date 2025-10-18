
from collections import defaultdict, Counter


def generate_overall_statistics(log_entries):
    """
    Generate overall statistics from parsed log entries.

    Args:
        log_entries (list): List of parsed log entries.

    Returns:
        dict: Overall metrics including total, passed, and failed requests.
    """
    total_requests = len(log_entries)
    passed_requests = sum(1 for e in log_entries if 200 <= e['status'] < 300)
    failed_requests = sum(1 for e in log_entries if 400 <= e['status'] < 600)

    overall_stats = {
        "total_requests": total_requests,
        "passed_requests": passed_requests,
        "passed_percentage": round((passed_requests / total_requests * 100), 2) if total_requests else 0.0,
        "failed_requests": failed_requests,
        "failed_percentage": round((failed_requests / total_requests * 100), 2) if total_requests else 0.0
    }

    return overall_stats

def generate_endpoint_metrics(log_entries):
    """
    Generate metrics per endpoint.

    Args:
        log_entries (list): List of parsed log entries.

    Returns:
        dict: Metrics per endpoint including total, failed, and failure percentage.
    """
    endpoint_counter = Counter()
    endpoint_failed = Counter()

    for entry in log_entries:
        endpoint = entry['endpoint']
        endpoint_counter[endpoint] += 1
        if 400 <= entry['status'] < 600:
            endpoint_failed[endpoint] += 1

    endpoint_metrics = {}
    for endpoint in endpoint_counter:
        total = endpoint_counter[endpoint]
        failed = endpoint_failed[endpoint]
        endpoint_metrics[endpoint] = {
            "total_requests": total,
            "failed_requests": failed,
            "failed_percentage": round((failed / total * 100), 2) if total else 0.0
        }

    return endpoint_metrics


def generate_ip_metrics(log_entries):
    """
    Generate metrics per IP.

    Args:
        log_entries (list): List of parsed log entries.

    Returns:
        dict: Metrics per IP including total requests, per-minute requests, passed/failed counts.
    """
    ip_counter = Counter()
    ip_failed = Counter()
    ip_per_minute = defaultdict(lambda: defaultdict(int))  # ip -> minute -> count

    for entry in log_entries:
        ip = entry['ip']
        ip_counter[ip] += 1
        if 400 <= entry['status'] < 600:
            ip_failed[ip] += 1

        minute = entry['timestamp'].strftime("%Y-%m-%d %H:%M")
        ip_per_minute[ip][minute] += 1

    ip_metrics = {}
    for ip in ip_counter:
        total = ip_counter[ip]
        failed = ip_failed[ip]
        ip_metrics[ip] = {
            "total_requests": total,
            "failed_requests": failed,
            "failed_percentage": round((failed / total * 100), 2) if total else 0.0,
            "requests_per_minute": dict(ip_per_minute[ip])
        }

    return ip_metrics


