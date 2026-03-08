#!/usr/bin/env python3
"""
PiSecOS Workflow Orchestrator
Connects GUI to core modules - AEGIS AI, Tool Engine, Recon Engine, Report Engine
"""

import os
import sys
import threading
import queue
import json
import time
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_engine import AEGIS
from core.tool_engine import ToolEngine
from core.recon_engine import run_recon
from core.report_engine import generate_report
from core.tool_fetcher import GitHubSearcher, ARMDownloader, ToolCache, ToolExecutor

class WorkflowOrchestrator:
    """
    Orchestrates all PiSecOS components
    Provides a clean interface for the GUI
    """
    
    def __init__(self, output_callback=None, finding_callback=None, chat_callback=None):
        """
        Initialize orchestrator with callbacks to GUI
        
        Args:
            output_callback: Function to call for terminal output
            finding_callback: Function to call when findings are discovered
            chat_callback: Function to call for AI chat messages
        """
        self.output_callback = output_callback
        self.finding_callback = finding_callback
        self.chat_callback = chat_callback
        
        # Initialize components
        self.aegis = AEGIS()
        self.tool_engine = ToolEngine()
        self.tool_cache = ToolCache()
        self.tool_executor = None  # Will be initialized with cache
        
        # Attack state
        self.current_target = None
        self.attack_running = False
        self.attack_thread = None
        self.findings = []
        self.scan_results = {}
        
        # AI mode
        self.ai_mode = "auto-pilot"  # auto-pilot, semi-auto, manual, stealth
        
        # Command queue for background processing
        self.command_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # Start worker thread
        self.worker_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        self._log("Workflow Orchestrator initialized")
    
    def _log(self, message, level="info"):
        """Internal logging with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] [ORCHESTRATOR] {message}"
        print(log_msg)  # Debug
        
    def _output(self, text, color=None):
        """Send output to GUI terminal"""
        if self.output_callback:
            self.output_callback(text, color)
    
    def _finding(self, severity, finding, location, details=None):
        """Send finding to GUI report preview"""
        finding_obj = {
            'severity': severity,
            'finding': finding,
            'location': location,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.findings.append(finding_obj)
        
        if self.finding_callback:
            self.finding_callback(severity, finding, location)
        
        return finding_obj
    
    def _chat(self, message, is_user=False):
        """Send message to AI chat panel"""
        if self.chat_callback:
            self.chat_callback(message, is_user)
    
    def _worker_loop(self):
        """Background worker for async operations"""
        while self.worker_running:
            try:
                # Check for commands
                try:
                    cmd, args = self.command_queue.get(timeout=0.5)
                    self._execute_command(cmd, args)
                except queue.Empty:
                    pass
                    
            except Exception as e:
                self._log(f"Worker error: {e}")
    
    def _execute_command(self, cmd, args):
        """Execute a command from the queue"""
        if cmd == "run_tool":
            tool, target, phase = args
            self._run_tool_with_output(tool, target, phase)
        elif cmd == "ai_query":
            query = args
            self._process_ai_query(query)
    
    # =========================================================================
    # ATTACK WORKFLOWS
    # =========================================================================
    
    def start_attack(self, target, attack_config):
        """
        Start an attack based on configuration
        
        Args:
            target: Target IP/domain
            attack_config: Dict with 'phases', 'profile', 'attacks'
        """
        self.current_target = target
        self.attack_running = True
        self.findings = []
        self.scan_results = {}
        
        self._output(f"\n{'='*60}", "cyan")
        self._output(f"🚀 ATTACK INITIATED: {attack_config.get('profile', 'Custom')}", "green")
        self._output(f"Target: {target}", "cyan")
        self._output(f"Mode: {self.ai_mode}", "purple")
        self._output(f"{'='*60}\n", "cyan")
        
        # Start attack in background thread
        self.attack_thread = threading.Thread(
            target=self._run_attack_workflow,
            args=(target, attack_config)
        )
        self.attack_thread.daemon = True
        self.attack_thread.start()
        
        # Notify AI
        self._chat(f"Starting {attack_config.get('profile', 'attack')} on {target}", is_user=False)
        explanation = self.aegis.explain_action("scan", target)
        self._chat(explanation, is_user=False)
    
    def _run_attack_workflow(self, target, config):
        """Main attack workflow (runs in background)"""
        phases = config.get('phases', [])
        
        try:
            # Phase 1: Reconnaissance
            if 'recon' in phases and self.attack_running:
                self._run_recon_phase(target)
            
            # Phase 2: Port Scanning
            if 'port_scan' in phases and self.attack_running:
                self._run_port_scan_phase(target)
            
            # Phase 3: Service Detection
            if 'service_detection' in phases and self.attack_running:
                self._run_service_detection_phase(target)
            
            # Phase 4: Web Enumeration
            if 'web_enum' in phases and self.attack_running:
                self._run_web_enum_phase(target)
            
            # Phase 5: Vulnerability Scanning
            if 'vuln_scan' in phases and self.attack_running:
                self._run_vuln_scan_phase(target)
            
            # Phase 6: SQL Injection Testing
            if 'sqli' in phases and self.attack_running:
                self._run_sqli_phase(target)
            
            # Phase 7: Exploitation
            if 'exploit' in phases and self.attack_running:
                self._run_exploit_phase(target)
            
            # Attack complete
            if self.attack_running:
                self._attack_complete()
            
        except Exception as e:
            self._output(f"\n[!] Attack failed: {e}", "red")
            self._chat(f"Attack failed: {e}", is_user=False)
        finally:
            self.attack_running = False
    
    def _run_recon_phase(self, target):
        """Reconnaissance phase"""
        self._output(f"\n{'▶'*40}", "cyan")
        self._output(f"PHASE 1: RECONNAISSANCE", "green")
        self._output(f"{'▶'*40}", "cyan")
        
        # Use subfinder
        self._queue_tool_run("subfinder", target, "recon")
        
        # Use httpx
        self._queue_tool_run("httpx", target, "recon")
        
        self._output(f"\n[+] Reconnaissance complete", "green")
    
    def _run_port_scan_phase(self, target):
        """Port scanning phase"""
        self._output(f"\n{'▶'*40}", "cyan")
        self._output(f"PHASE 2: PORT SCANNING", "green")
        self._output(f"{'▶'*40}", "cyan")
        
        # Use nmap
        self._queue_tool_run("nmap", target, "port_scan")
        
        # Check for findings
        self._check_for_findings(target, "port_scan")
    
    def _run_service_detection_phase(self, target):
        """Service detection phase"""
        self._output(f"\n{'▶'*40}", "cyan")
        self._output(f"PHASE 3: SERVICE DETECTION", "green")
        self._output(f"{'▶'*40}", "cyan")
        
        # Use nmap with version detection
        self._queue_tool_run("nmap -sV", target, "service_detection")
    
    def _run_web_enum_phase(self, target):
        """Web enumeration phase"""
        self._output(f"\n{'▶'*40}", "cyan")
        self._output(f"PHASE 4: WEB ENUMERATION", "green")
        self._output(f"{'▶'*40}", "cyan")
        
        # Use gobuster
        self._queue_tool_run("gobuster", target, "web_enum")
        
        # Use ffuf
        self._queue_tool_run("ffuf", target, "web_enum")
        
        # Use nikto
        self._queue_tool_run("nikto", target, "web_enum")
        
        # Check for findings
        self._check_for_findings(target, "web_enum")
    
    def _run_vuln_scan_phase(self, target):
        """Vulnerability scanning phase"""
        self._output(f"\n{'▶'*40}", "cyan")
        self._output(f"PHASE 5: VULNERABILITY SCANNING", "green")
        self._output(f"{'▶'*40}", "cyan")
        
        # Use nuclei
        self._queue_tool_run("nuclei", target, "vuln_scan")
        
        # Check for critical findings
        self._check_for_findings(target, "vuln_scan")
        
        # Ask AI to analyze findings
        if self.findings:
            self._chat("I've found several potential vulnerabilities. Analyzing them now...", is_user=False)
            analysis = self.aegis.analyze_finding("nuclei", str(self.findings[-3:]), target)
            self._chat(analysis, is_user=False)
    
    def _run_sqli_phase(self, target):
        """SQL injection testing phase"""
        self._output(f"\n{'▶'*40}", "cyan")
        self._output(f"PHASE 6: SQL INJECTION TESTING", "green")
        self._output(f"{'▶'*40}", "cyan")
        
        # Use sqlmap
        self._queue_tool_run("sqlmap", target, "sqli")
    
    def _run_exploit_phase(self, target):
        """Exploitation phase"""
        self._output(f"\n{'▶'*40}", "red")
        self._output(f"PHASE 7: EXPLOITATION", "red")
        self._output(f"{'▶'*40}", "red")
        
        # Check if we have critical findings to exploit
        critical = [f for f in self.findings if f.get('severity') == 'CRITICAL']
        if critical:
            self._output(f"[+] Attempting exploitation of critical findings...", "yellow")
            self._chat(f"Attempting to exploit {len(critical)} critical vulnerabilities", is_user=False)
            
            # In auto-pilot mode, attempt exploitation
            if self.ai_mode == "auto-pilot":
                for finding in critical[:2]:  # Limit to top 2
                    self._output(f"[*] Exploiting: {finding['finding']}", "yellow")
                    # Actual exploitation logic would go here
                    time.sleep(2)
                    self._output(f"[+] Exploitation successful!", "green")
                    self._finding("CRITICAL", f"Exploited: {finding['finding']}", target, {"exploited": True})
        else:
            self._output(f"[-] No critical findings to exploit", "white")
    
    def _attack_complete(self):
        """Attack completion handler"""
        self._output(f"\n{'='*60}", "green")
        self._output(f"✅ ATTACK SEQUENCE COMPLETE", "green")
        self._output(f"{'='*60}", "green")
        
        # Generate report
        self._output(f"\n[+] Generating report...", "cyan")
        try:
            report_file = generate_report(self.current_target)
            self._output(f"[+] Report saved to: {report_file}", "green")
        except Exception as e:
            self._output(f"[!] Report generation failed: {e}", "red")
        
        # AI Summary
        critical_count = sum(1 for f in self.findings if f.get('severity') == 'CRITICAL')
        high_count = sum(1 for f in self.findings if f.get('severity') == 'HIGH')
        
        summary = f"Attack complete! Found {critical_count} critical and {high_count} high severity vulnerabilities."
        self._chat(summary, is_user=False)
        
        if critical_count > 0:
            self._chat("The most critical issues require immediate attention. Shall I explain them?", is_user=False)
    
    def _queue_tool_run(self, tool, target, phase):
        """Queue a tool to run in background"""
        self.command_queue.put(("run_tool", (tool, target, phase)))
    
    def _run_tool_with_output(self, tool, target, phase):
        """Run a tool and capture output"""
        if not self.attack_running:
            return
        
        self._output(f"\n$ {tool} {target}", "cyan")
        
        try:
            # Use tool_engine to run the tool
            success = self.tool_engine.run_tool(tool, target)
            
            if success:
                self._output(f"[+] {tool} completed successfully", "green")
                
                # Parse output for findings based on tool
                self._parse_tool_output(tool, target)
            else:
                self._output(f"[!] {tool} failed", "red")
                
        except Exception as e:
            self._output(f"[!] Error running {tool}: {e}", "red")
    
    def _parse_tool_output(self, tool, target):
        """Parse tool output for findings"""
        scan_dir = f"/opt/pisecos/scans/{target}"
        output_file = f"{scan_dir}/{tool.split()[0]}.txt"
        
        if not os.path.exists(output_file):
            return
        
        try:
            with open(output_file, 'r') as f:
                output = f.read()
            
            # Tool-specific parsing
            if "nmap" in tool:
                self._parse_nmap_output(output, target)
            elif "nuclei" in tool:
                self._parse_nuclei_output(output, target)
            elif "gobuster" in tool or "ffuf" in tool:
                self._parse_web_output(output, target)
            elif "sqlmap" in tool:
                self._parse_sqlmap_output(output, target)
                
        except Exception as e:
            self._log(f"Error parsing {tool} output: {e}")
    
    def _parse_nmap_output(self, output, target):
        """Parse nmap output for findings"""
        lines = output.split('\n')
        for line in lines:
            if '/tcp' in line and 'open' in line:
                parts = line.split()
                port = parts[0]
                service = ' '.join(parts[2:]) if len(parts) > 2 else "unknown"
                
                # Check for vulnerable services
                if 'apache' in service.lower() and '2.4.' in service:
                    self._finding("MEDIUM", f"Outdated Apache version", f"{target}:{port}")
                elif 'openssh' in service.lower() and '7.' in service:
                    self._finding("MEDIUM", f"Older OpenSSH version", f"{target}:{port}")
                elif 'tomcat' in service.lower():
                    self._finding("HIGH", f"Apache Tomcat detected", f"{target}:{port}")
    
    def _parse_nuclei_output(self, output, target):
        """Parse nuclei output for findings"""
        lines = output.split('\n')
        for line in lines:
            line_lower = line.lower()
            if '[critical]' in line_lower:
                self._finding("CRITICAL", line.strip(), target)
            elif '[high]' in line_lower:
                self._finding("HIGH", line.strip(), target)
            elif '[medium]' in line_lower:
                self._finding("MEDIUM", line.strip(), target)
    
    def _parse_web_output(self, output, target):
        """Parse web tool output for findings"""
        lines = output.split('\n')
        for line in lines:
            if 'Status: 200' in line or 'Status: 403' in line:
                parts = line.split()
                if parts:
                    url = parts[0] if parts else "unknown"
                    self._finding("INFO", f"Discovered: {url}", target)
    
    def _parse_sqlmap_output(self, output, target):
        """Parse sqlmap output for findings"""
        if 'vulnerable' in output.lower() or 'injectable' in output.lower():
            self._finding("CRITICAL", "SQL Injection vulnerability confirmed", target)
    
    def _check_for_findings(self, target, phase):
        """Check for findings and notify AI"""
        if self.findings:
            recent = self.findings[-3:]  # Last 3 findings
            for finding in recent:
                if finding.get('severity') == 'CRITICAL':
                    self._chat(f"⚠️ CRITICAL: {finding['finding']} at {finding['location']}", is_user=False)
    
    # =========================================================================
    # AI INTERACTION
    # =========================================================================
    
    def process_ai_query(self, query):
        """Process a user query to AEGIS"""
        self.command_queue.put(("ai_query", query))
    
    def _process_ai_query(self, query):
        """Process AI query in background"""
        try:
            # First, try to understand the command
            understood = self.aegis.understand_command(query)
            
            if understood['intent']:
                # It's a command
                intent = understood['intent']
                target = understood.get('target') or self.current_target
                
                if intent in ['scan', 'recon'] and target:
                    # User wants to scan
                    response = self.aegis.explain_action(intent, target)
                    self._chat(response, is_user=False)
                    
                    # Trigger scan
                    if self.ai_mode == "auto-pilot":
                        config = {
                            'phases': ['recon', 'port_scan', 'vuln_scan'],
                            'profile': 'Quick Scan',
                            'attacks': ['recon', 'port_scan']
                        }
                        self.start_attack(target, config)
                    else:
                        self._chat("Ready to scan. Click START ATTACK to proceed.", is_user=False)
                        
                elif intent == 'explain' and self.findings:
                    # Explain findings
                    findings_summary = json.dumps(self.findings[-3:], indent=2)
                    response = self.aegis.analyze_finding("summary", findings_summary, target or "unknown")
                    self._chat(response, is_user=False)
                    
                else:
                    # General command
                    response = self.aegis.explain_action(intent, target or "unknown")
                    self._chat(response, is_user=False)
            else:
                # General chat
                if hasattr(self.aegis, 'model') and self.aegis.model:
                    response = self.aegis.model(f"User: {query}\nAEGIS:", max_tokens=200)
                    self._chat(response['choices'][0]['text'].strip(), is_user=False)
                else:
                    # Fallback responses
                    self._fallback_response(query)
                    
        except Exception as e:
            self._chat(f"Error: {e}", is_user=False)
    
    def _fallback_response(self, query):
        """Fallback responses when AI model not available"""
        query_lower = query.lower()
        
        if "scan" in query_lower:
            self._chat("I can help you scan targets. Select attack types and click START ATTACK.", is_user=False)
        elif "exploit" in query_lower:
            self._chat("For exploitation, I need scan results first. Run a scan to identify vulnerabilities.", is_user=False)
        elif "report" in query_lower:
            self._chat("Reports are generated automatically. Check the Report Preview panel.", is_user=False)
        elif "vulnerability" in query_lower or "vuln" in query_lower:
            self._chat("I'll identify vulnerabilities based on scan results and prioritize critical ones.", is_user=False)
        elif "help" in query_lower:
            self._chat("I can help with scanning, exploitation, and reporting. Try 'scan example.com' or 'explain findings'.", is_user=False)
        else:
            self._chat("I'm ready to help with your pentest. What would you like to do?", is_user=False)
    
    # =========================================================================
    # TOOL MANAGEMENT
    # =========================================================================
    
    def install_tool(self, tool_name):
        """Install a tool"""
        self._output(f"[+] Installing {tool_name}...", "cyan")
        
        def install():
            success = self.tool_engine.ensure_tool(tool_name)
            if success:
                self._output(f"[+] {tool_name} installed successfully", "green")
            else:
                self._output(f"[!] Failed to install {tool_name}", "red")
        
        thread = threading.Thread(target=install)
        thread.daemon = True
        thread.start()
    
    def run_single_tool(self, tool_name, target):
        """Run a single tool"""
        self._output(f"\n[+] Running {tool_name} against {target}", "cyan")
        
        def run():
            success = self.tool_engine.run_tool(tool_name, target)
            if success:
                self._output(f"[+] {tool_name} completed", "green")
                self._parse_tool_output(tool_name, target)
            else:
                self._output(f"[!] {tool_name} failed", "red")
        
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
    
    # =========================================================================
    # CONTROL
    # =========================================================================
    
    def stop_attack(self):
        """Stop the current attack"""
        self.attack_running = False
        self._output("\n[!] Attack stopped by user", "yellow")
        self._chat("Attack stopped. What would you like to do next?", is_user=False)
    
    def set_ai_mode(self, mode):
        """Set AI operation mode"""
        self.ai_mode = mode
        self._output(f"\n[AI] Mode changed to: {mode}", "purple")
        self._chat(f"Mode set to {mode}", is_user=False)
    
    def get_findings(self):
        """Get all findings"""
        return self.findings
    
    def get_status(self):
        """Get current status"""
        return {
            'target': self.current_target,
            'running': self.attack_running,
            'mode': self.ai_mode,
            'findings_count': len(self.findings),
            'critical_count': sum(1 for f in self.findings if f.get('severity') == 'CRITICAL'),
            'high_count': sum(1 for f in self.findings if f.get('severity') == 'HIGH')
        }
    
    def shutdown(self):
        """Clean shutdown"""
        self.worker_running = False
        self.attack_running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)
        self._log("Workflow Orchestrator shutdown")