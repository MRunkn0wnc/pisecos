import csv
import os

SCAN_DIR = "/opt/pisecos/scans"
REPORT_DIR = "/opt/pisecos/reports"


def generate_report(target):

    scan_path = f"{SCAN_DIR}/{target}"
    os.makedirs(REPORT_DIR, exist_ok=True)

    report_file = f"{REPORT_DIR}/{target}_report.csv"

    findings = []

    for file in os.listdir(scan_path):

        file_path = os.path.join(scan_path, file)

        with open(file_path) as f:

            for line in f.readlines():

                if "open" in line or "vulnerable" in line:

                    findings.append({

                        "Host": target,
                        "Source": file,
                        "Finding": line.strip()
                    })

    with open(report_file, "w", newline="") as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=["Host", "Source", "Finding"]
        )

        writer.writeheader()

        for row in findings:
            writer.writerow(row)

    print(f"\n[+] Report generated: {report_file}")

    return report_file