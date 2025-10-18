from datetime import datetime
import json
import re
import argparse
from typing import Dict, List


# Argument parser for command-line interface


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments including input and output file paths.

    Raises:
        Exception: If argument parsing fails.
    """
    try:
        parser = argparse.ArgumentParser(description="Web Server Log Analysis Tool")
        parser.add_argument(
            "-i", "--input", required=True, help="Path to the input web server log file"
        )
        parser.add_argument(
            "-o",
            "--output",
            required=False,
            default="report.json",
            help="Path to output JSON report file (default: report.json)",
        )
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Enable verbose output"
        )
        return parser.parse_args()
    except Exception as e:
        raise Exception(f"Error parsing arguments: {e}")


# Log line parser
def parse_log_line(line: str) -> Dict:
    """
    Parse a single log line into structured data.

    Args:
        line (str): A single line from the log file.

    Returns:
        dict or None: Parsed log entry with fields or None if line is malformed.

    Raises:
        Exception: If an error occurs during parsing.
    """
    try:
        # Regular expression for common Apache/Nginx log format
        LOG_PATTERN = re.compile(
            r'(?P<ip>\S+) - - \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<endpoint>\S+) (?P<protocol>[^"]+)" (?P<status>\d{3}) (?P<size>\d+|-)'
        )

        match = LOG_PATTERN.match(line)
        if not match:
            return None

        data = match.groupdict()

        # Parse timestamp to datetime object
        try:
            data["timestamp"] = datetime.strptime(
                data["timestamp"], "%d/%b/%Y:%H:%M:%S %z"
            )
        except ValueError:
            return None

        # Convert numeric fields
        data["status"] = int(data["status"])
        data["size"] = int(data["size"]) if data["size"].isdigit() else 0

        return data
    except Exception:
        return Exception("Error parsing log line")


def read_log_file(file_path: str, verbose: bool = False) -> List:
    """
    Read a log file line by line and parse entries.

    Args:
        file_path (str): Path to the log file.
        verbose (bool): If True, print parsing progress and warnings.

    Returns:
        list: List of parsed log entries (dicts).

    Raises:
        Exception: If an error occurs during file reading.
    """
    try:
        parsed_entries = []
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                entry = parse_log_line(line)
                if entry:
                    parsed_entries.append(entry)
                else:
                    if verbose:
                        print(f"[WARNING] Malformed line {i}: {line}")
        if verbose:
            print(
                f"[INFO] Parsed {len(parsed_entries)} valid log entries from {file_path}"
            )
        return parsed_entries
    except Exception as e:
        raise Exception(f"Error reading log file: {e}")


## Output parser


def print_summary(
    overall_stats: Dict, endpoint_metrics: Dict, ip_metrics: Dict, issues: Dict
) -> None:
    """
    Print a summary report to the console.

    Args:
        overall_stats (dict): Overall statistics.
        endpoint_metrics (dict): Metrics per endpoint.
        ip_metrics (dict): Metrics per IP.
        issues (dict): Detected issues including high error endpoints and suspicious IPs.

    Raises:
        Exception: If an error occurs during printing.
    """
    try:
        print("\n===== Final Report =====")
        print("\n===== Overall Statistics =====")
        for key, value in overall_stats.items():
            print(f"{key}: {value}")

        print("\n=====  Per Endpoint Metrics =====")
        for endpoint, metrics in endpoint_metrics.items():
            print(f"{endpoint}: {metrics}")

        print("\n=====  Per IP Metrics =====")
        for ip, metrics in ip_metrics.items():
            print(f"{ip}: {metrics}")

        print("\n===== High Error Endpoints =====")
        if issues["high_error_endpoints"]:
            for item in issues["high_error_endpoints"]:
                print(
                    f"{item['endpoint']}: {item['failed_requests']}/{item['total_requests']} failed ({item['failed_percentage']}%)"
                )
        else:
            print("None")

        print("\n===== Suspicious IPs =====")
        if issues["suspicious_ips"]:
            for item in issues["suspicious_ips"]:
                print(
                    f"{item['ip']}: {item['reason']} (Failed: {item['failed_percentage']}%)"
                )
        else:
            print("None")
    except Exception as e:
        raise Exception(f"Error printing summary: {e}")


def write_json_report(
    output_file: str,
    overall_stats: Dict,
    endpoint_metrics: Dict,
    ip_metrics: Dict,
    issues: Dict,
) -> None:
    """
    Write the analysis report to a JSON file.

    Args:
        output_file (str): Path to the output JSON file.
        overall_stats (dict): Overall statistics.
        endpoint_metrics (dict): Metrics per endpoint.
        ip_metrics (dict): Metrics per IP.
        issues (dict): Detected issues.

    Raises:
        Exception: If an error occurs during file writing.
    """
    try:
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "overall_statistics": overall_stats,
            "endpoint_metrics": endpoint_metrics,
            "ip_metrics": ip_metrics,
            "detected_issues": issues,
        }
        print("------------")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        raise Exception(f"Error writing JSON report: {e}")
