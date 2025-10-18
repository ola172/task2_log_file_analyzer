from constants import ERROR_THRESHOLD_PERCENTAGE, EXCESSIVE_REQUESTS_PER_MINUTE, FAILED_REQUESTS_PERCENTAGE_IP


def detect_high_error_endpoints(endpoint_metrics, threshold=ERROR_THRESHOLD_PERCENTAGE):
    """
    Detect endpoints with high error rates.

    Args:
        endpoint_metrics (dict): Metrics per endpoint.
        threshold (float): Failure percentage threshold to flag an endpoint.

    Returns:
        list: List of endpoints exceeding the failure threshold.
    """
    high_error_endpoints = []
    for endpoint, metrics in endpoint_metrics.items():
        if metrics["failed_percentage"] > threshold:
            high_error_endpoints.append({
                "endpoint": endpoint,
                **metrics
            })
    return high_error_endpoints

def detect_suspicious_ips(ip_metrics, request_threshold=EXCESSIVE_REQUESTS_PER_MINUTE, failed_threshold=FAILED_REQUESTS_PERCENTAGE_IP):
    """
    Detect suspicious IPs based on excessive requests or high failure percentage.

    Args:
        ip_metrics (dict): Metrics per IP.
        request_threshold (int): Requests per minute threshold to flag excessive activity.
        failed_threshold (float): Failed request percentage threshold.

    Returns:
        list: List of suspicious IPs with reasons.
    """
    suspicious_ips = []
    for ip, metrics in ip_metrics.items():
        if metrics["failed_percentage"] > failed_threshold:
            suspicious_ips.append({
                "ip": ip,
                **metrics,
                "reason": "High failed requests percentage"
            })
        for minute, count in metrics["requests_per_minute"].items():
            if count > request_threshold:
                suspicious_ips.append({
                    "ip": ip,
                    **metrics,
                    "reason": f"Excessive requests in minute {minute}"
                })
                break  # Only flag once per IP
    return suspicious_ips

def detect_issues(endpoint_metrics, ip_metrics):
    """
    Aggregate detected issues from high error endpoints and suspicious IPs.

    Args:
        endpoint_metrics (dict): Metrics per endpoint.
        ip_metrics (dict): Metrics per IP.

    Returns:
        dict: Detected issues.
    """
    return {
        "high_error_endpoints": detect_high_error_endpoints(endpoint_metrics),
        "suspicious_ips": detect_suspicious_ips(ip_metrics)
    }
