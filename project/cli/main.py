#!/usr/bin/env python3
"""
Log Intelligence CLI — AI-Powered Security Operations Platform.

A modern interactive terminal for managing logs, running AI analysis,
and monitoring system health across the microservice ecosystem.
"""
import sys
import time
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

from api_client import APIClient
from ui import (
    console,
    print_banner,
    print_menu,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_section,
    print_kv,
    print_logs_table,
    print_health_status,
    print_ai_result,
    print_metrics,
    prompt,
    ACCENT,
    ACCENT_DIM,
    DIM,
    SUCCESS,
    ERROR,
)

client = APIClient()


# ─────────────────────────────────────────────────────────
#  Spinner helper
# ─────────────────────────────────────────────────────────
def with_spinner(label: str, fn, *args, **kwargs):
    """Run a function while showing a spinner."""
    with console.status(f"[{ACCENT}]{label}[/]", spinner="dots"):
        return fn(*args, **kwargs)


# ─────────────────────────────────────────────────────────
#  Command handlers
# ─────────────────────────────────────────────────────────
def cmd_login():
    print_section("Login")
    email = prompt("Email")
    password = prompt("Password")

    result = with_spinner("Authenticating...", client.login, email, password)

    if result.get("status") == "success":
        print_success("Logged in successfully!")
        print_kv("Token", client.token[:40] + "...")
    else:
        print_error(f"Login failed: {result.get('detail', result.get('error', 'Unknown error'))}")


def cmd_register():
    print_section("Register New User")
    username = prompt("Username")
    email = prompt("Email")
    password = prompt("Password")

    roles = ["writer", "reader", "admin"]
    print_info(f"Available roles: {', '.join(roles)}")
    role = prompt("Role (default: writer)") or "writer"

    result = with_spinner("Creating account...", client.register, username, email, password, role)

    if result.get("status") == "success":
        print_success(f"User '{username}' created!")
        data = result.get("data", {})
        print_kv("ID", str(data.get("id", "—")))
        print_kv("Role", data.get("role", "—"))
    else:
        print_error(f"Registration failed: {result.get('detail', result.get('error', 'Unknown'))}")


def cmd_whoami():
    if not client.token:
        print_warning("You must login first.")
        return

    result = with_spinner("Fetching profile...", client.get_me)
    if result.get("status") == "success":
        data = result["data"]
        print_section("Current User")
        print_kv("ID", str(data.get("id", "—")))
        print_kv("Username", data.get("username", "—"))
        print_kv("Email", data.get("email", "—"))
        print_kv("Role", data.get("role", "—"))
    else:
        print_error("Could not fetch profile.")


def cmd_ingest():
    if not client.token:
        print_warning("You must login first.")
        return

    print_section("Ingest Log Entry")
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    print_info(f"Levels: {', '.join(levels)}")
    level = prompt("Level").upper()
    if level not in levels:
        print_error(f"Invalid level. Choose from: {', '.join(levels)}")
        return

    message = prompt("Message")
    service_name = prompt("Service name (default: cli)") or "cli"

    result = with_spinner("Ingesting log...", client.ingest_log, level, message, service_name)

    if result.get("status") == "success":
        print_success("Log ingested successfully!")
        data = result.get("data", {})
        print_kv("ID", str(data.get("id", "—")))
        print_kv("AI Classification", data.get("ai_classification", "—"))
    else:
        print_error(f"Ingest failed: {result.get('detail', result.get('error', 'Unknown'))}")


def cmd_list_logs():
    if not client.token:
        print_warning("You must login first.")
        return

    print_section("Log Explorer")
    level = prompt("Filter by level (blank for all)") or None
    service = prompt("Filter by service (blank for all)") or None
    limit_str = prompt("Limit (default: 20)") or "20"

    result = with_spinner("Fetching logs...", client.list_logs, level, service, int(limit_str))

    if result.get("status") == "success":
        logs = result.get("data", [])
        print_logs_table(logs)
        print_info(f"Showing {len(logs)} log(s).")
    else:
        print_error("Failed to fetch logs.")


def cmd_analyze():
    if not client.token:
        print_warning("You must login first.")
        return

    print_section("AI Incident Analysis")
    print_info("Sending recent logs to Claude-3 for semantic analysis...")

    result = with_spinner("Running AI analysis (this may take a few seconds)...", client.analyze_logs)

    if result.get("status") == "success":
        print_ai_result("🧠 AI Incident Summary", result.get("data", {}))
    else:
        print_error(f"Analysis failed: {result.get('detail', result.get('error', 'Unknown'))}")


def cmd_anomalies():
    if not client.token:
        print_warning("You must login first.")
        return

    print_section("AI Anomaly Detection")
    print_info("Scanning logs with PyTorch + Claude-3 hybrid engine...")

    result = with_spinner("Detecting anomalies...", client.detect_anomalies)

    if result.get("status") == "success":
        print_ai_result("🔍 Anomaly Detection Report", result.get("data", {}))
    else:
        print_error(f"Detection failed: {result.get('detail', result.get('error', 'Unknown'))}")


def cmd_health():
    print_section("System Health Check")

    gw = with_spinner("Checking gateway...", client.health_gateway)

    services = {"API Gateway": gw}

    if client.token:
        log_health = with_spinner("Checking log service...", client.health_service, "api/v1/health")
        services["Log Service"] = log_health
    else:
        services["Log Service"] = {"status": "unknown", "error": "Login required"}
        services["Auth Service"] = {"status": "healthy" if gw.get("status") == "healthy" else "unknown"}

    print_health_status(services)


def cmd_metrics():
    if not client.token:
        print_warning("You must login first.")
        return

    result = with_spinner("Fetching metrics...", client.get_metrics)

    if result.get("status") == "success":
        print_metrics(result.get("data", {}))
    else:
        print_error("Failed to fetch metrics.")


def cmd_demo():
    """Run a full demo scenario."""
    if not client.token:
        print_warning("You must login first to run the demo.")
        return

    print_section("🎬 Live Demo — Simulated Attack Scenario")
    console.print()

    # Step 1: Ingest normal logs
    print_info("Step 1/4: Ingesting normal traffic logs...")
    normal_logs = [
        ("INFO", "User logged in successfully", "auth-service"),
        ("INFO", "Fetched dashboard data", "api-gateway"),
        ("DEBUG", "Cache hit for user preferences", "log-service"),
        ("INFO", "Payment processed: $45.00", "payment-service"),
    ]
    for level, msg, svc in normal_logs:
        with_spinner(f"  Sending: {msg[:50]}", client.ingest_log, level, msg, svc)
    print_success("Normal logs ingested.")

    console.print()
    time.sleep(0.5)

    # Step 2: Ingest suspicious logs
    print_info("Step 2/4: Simulating brute-force attack...")
    attack_logs = [
        ("WARNING", "Failed login attempt for admin@company.com from IP 185.220.101.42", "auth-service"),
        ("WARNING", "Failed login attempt for admin@company.com from IP 185.220.101.42", "auth-service"),
        ("ERROR", "Rate limit exceeded for IP 185.220.101.42 — 50 requests in 10s", "api-gateway"),
        ("CRITICAL", "SQL injection detected in query: SELECT * FROM users WHERE id='' OR '1'='1'", "log-service"),
        ("ERROR", "Unauthorized access attempt to /admin/export-all-data", "api-gateway"),
    ]
    for level, msg, svc in attack_logs:
        with_spinner(f"  Sending: {msg[:50]}", client.ingest_log, level, msg, svc)
    print_success("Attack simulation complete.")

    console.print()
    time.sleep(0.5)

    # Step 3: Run anomaly detection
    print_info("Step 3/4: Running AI Anomaly Detection...")
    result = with_spinner("Analyzing with PyTorch + Claude...", client.detect_anomalies)
    if result.get("status") == "success":
        print_ai_result("🔍 Anomaly Detection Report", result.get("data", {}))
    else:
        print_warning("Anomaly detection unavailable (AI key may be missing).")

    # Step 4: Show metrics
    print_info("Step 4/4: Fetching updated metrics...")
    metrics_result = with_spinner("Loading metrics...", client.get_metrics)
    if metrics_result.get("status") == "success":
        print_metrics(metrics_result.get("data", {}))

    print_success("Demo complete! The system detected and analyzed the simulated attack.")


def cmd_config():
    print_section("Configuration")
    print_kv("Gateway URL", client.base_url)
    print_kv("Authenticated", "Yes" if client.token else "No")
    if client.token:
        print_kv("Token", client.token[:50] + "...")

    console.print()
    new_url = prompt("New Gateway URL (blank to keep current)").strip()
    if new_url:
        client.base_url = new_url.rstrip("/")
        print_success(f"Gateway URL updated to: {client.base_url}")


# ─────────────────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────────────────
MAIN_MENU = [
    {"key": "1", "label": "Login",              "desc": "Authenticate with the platform"},
    {"key": "2", "label": "Register",           "desc": "Create a new user account"},
    {"key": "3", "label": "Who Am I",           "desc": "View current user profile"},
    {"key": "4", "label": "Ingest Log",         "desc": "Send a log entry to the system"},
    {"key": "5", "label": "List Logs",          "desc": "Browse and filter log entries"},
    {"key": "6", "label": "AI Analysis",        "desc": "Run Claude-3 incident summary"},
    {"key": "7", "label": "Anomaly Detection",  "desc": "PyTorch + Claude hybrid scan"},
    {"key": "8", "label": "System Health",       "desc": "Check all service statuses"},
    {"key": "9", "label": "Metrics",            "desc": "View platform statistics"},
    {"key": "d", "label": "Run Demo",           "desc": "Full attack simulation scenario"},
    {"key": "c", "label": "Config",             "desc": "Change gateway URL"},
    {"key": "q", "label": "Quit",               "desc": "Exit the CLI"},
]

COMMANDS = {
    "1": cmd_login,
    "2": cmd_register,
    "3": cmd_whoami,
    "4": cmd_ingest,
    "5": cmd_list_logs,
    "6": cmd_analyze,
    "7": cmd_anomalies,
    "8": cmd_health,
    "9": cmd_metrics,
    "d": cmd_demo,
    "c": cmd_config,
}


def main():
    print_banner()
    print_info(f"Connected to: {client.base_url}")
    console.print()

    while True:
        print_menu(MAIN_MENU)
        console.print()
        try:
            choice = prompt("Select").strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print()
            print_info("Goodbye! 👋")
            break

        if choice == "q":
            print_info("Goodbye! 👋")
            break

        handler = COMMANDS.get(choice)
        if handler:
            try:
                handler()
            except Exception as e:
                print_error(f"Command failed: {e}")
        else:
            print_warning("Invalid choice. Try again.")

        console.print()


if __name__ == "__main__":
    main()
