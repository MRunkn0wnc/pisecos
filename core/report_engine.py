import csv
import os

SCAN_DIR = "/opt/pisecos/scans"
REPORT_DIR = "/opt/pisecos/reports"

def generate_report(target):

    scan_path = f"{SCAN_DIR}/{target}"
    report_file = f"{REPORT_DIR}/{target}_report.csv"

    data = []

    # read subdomains
    sub_file = f"{scan_path}/subfinder.txt"
    if os.path.exists(sub_file):
        with open(sub_file) as f:
            for line in f:
                host = line.strip()
                data.append({
                    "Host": host,
                    "IP": "",
                    "Port": "",
                    "Service": "",
                    "Vulnerability": "",
                    "Severity": "",
                    "Description": "Discovered subdomain"
                })

    # read nmap results
    nmap_file = f"{scan_path}/nmap.txt"
    if os.path.exists(nmap_file):
        with open(nmap_file) as f:
            for line in f:
                if "/tcp" in line:
                    parts = line.split()
                    port = parts[0]
                    service = parts[-1]

                    data.append({
                        "Host": target,
                        "IP": "",
                        "Port": port,
                        "Service": service,
                        "Vulnerability": "",
                        "Severity": "",
                        "Description": "Open port detected"
                    })

    # read nuclei results
    nuclei_file = f"{scan_path}/nuclei.txt"
    if os.path.exists(nuclei_file):
        with open(nuclei_file) as f:
            for line in f:
                data.append({
                    "Host": target,
                    "IP": "",
                    "Port": "",
                    "Service": "",
                    "Vulnerability": line.strip(),
                    "Severity": "Unknown",
                    "Description": "Potential vulnerability detected"
                })

    # write CSV
    os.makedirs(REPORT_DIR, exist_ok=True)

    with open(report_file, "w", newline="") as csvfile:

        fieldnames = [
            "Host",
            "IP",
            "Port",
            "Service",
            "Vulnerability",
            "Severity",
            "Description"
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in data:
            writer.writerow(row)

    print(f"\n[+] Report generated: {report_file}")
