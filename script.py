#!/usr/bin/env python3
"""
Web Server Log Analysis Tool
Step 1: Project setup, imports, and basic script skeleton

This script sets up the basic structure for analyzing Apache/Nginx log files.
It handles input/output file paths and prepares the project for incremental
development of log parsing and statistics generation.

Author: Your Name
Date: 2025-10-18
"""

import os
import sys

from issues_detector import detect_issues
from parser import parse_arguments, print_summary, read_log_file, write_json_report
from statistics_calculator import (
    generate_endpoint_metrics,
    generate_ip_metrics,
    generate_overall_statistics,
)


def main():
    """
    Main function to initialize log analysis tool.
    """
    try:
        args = parse_arguments()

        input_file = args.input
        output_file = args.output
        verbose = args.verbose

        # Check if input file exists
        if not os.path.isfile(input_file):
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)

        if verbose:
            print(f"[INFO] Input file: {input_file}")
            print(f"[INFO] Output file: {output_file}")

        # Step 2: Parse log file
        log_entries = read_log_file(file_path=input_file, verbose=verbose)

        # Step 3: Generate overall statistics
        overall_stats = generate_overall_statistics(log_entries=log_entries)

        # Step 4: Generate per-endpoint and per-IP metrics
        endpoint_metrics = generate_endpoint_metrics(log_entries=log_entries)
        ip_metrics = generate_ip_metrics(log_entries=log_entries)

        if verbose:
            print("[INFO] Overall Statistics:")
            for key, value in overall_stats.items():
                print(f"  {key}: {value}")

            print("\n[INFO] Per Endpoint Metrics:")
            for endpoint, metrics in endpoint_metrics.items():
                print(f"  {endpoint}: {metrics}")

            print("\n[INFO] Per IP Metrics:")
            for ip, metrics in ip_metrics.items():
                print(f"  {ip}: {metrics}")

        # Step 5: Detect potential issues
        issues = detect_issues(endpoint_metrics=endpoint_metrics, ip_metrics=ip_metrics)

        if verbose:
            print("\n[INFO] High Error Endpoints:")
            for item in issues["high_error_endpoints"]:
                print(f"  {item}")

            print("\n[INFO] Suspicious IPs:")
            for item in issues["suspicious_ips"]:
                print(f"  {item}")

        # Step 6: Output results
        print_summary(overall_stats=overall_stats, endpoint_metrics=endpoint_metrics, ip_metrics=ip_metrics, issues=issues)
        write_json_report(
            output_file=output_file,
            overall_stats=overall_stats,
            endpoint_metrics=endpoint_metrics,
            ip_metrics=ip_metrics,
            issues=issues,
        )

        if verbose:
            print(f"[INFO] Analysis report written to '{output_file}'")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
