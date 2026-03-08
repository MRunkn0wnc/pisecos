#!/usr/bin/env python3
"""
PiSecOS CLI Interface
Updated for boot integration
"""

import os
import sys
import readline
import atexit
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Command history
histfile = Path("/opt/pisecos/.history")
try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, histfile)

# Import core modules
from core.ai_engine import handle_command
from core.recon_engine import run_recon
from core.report_engine import generate_report

class PiSecOSController:
    """Main CLI controller"""
    
    def __init__(self):
        self.running = True
        self.current_target = None
        self.commands = {
            'help': self.show_help,
            'exit': self.do_exit,
            'quit': self.do_exit,
            'target': self.set_target,
            'scan': self.do_scan,
            'report': self.do_report,
            'status': self.show_status,
            'clear': self.clear_screen,
            'ai': self.ask_ai
        }
        
        self.print_banner()
    
    def print_banner(self):
        """Show startup banner"""
        print("\n" + "="*60)
        print("PiSecOS - Pentesting Framework")
        print("="*60)
        print("Type 'help' for commands")
        print("="*60 + "\n")
    
    def show_help(self, args):
        """Display help"""
        help_text = """
COMMANDS:
---------
help                 - Show this help
exit, quit          - Exit PiSecOS
target <host>       - Set target
scan                - Start reconnaissance
report              - Generate report
status              - Show system status
clear               - Clear screen
ai <question>       - Ask AI assistant

EXAMPLES:
target example.com
scan
ai What should I check first?
"""
        print(help_text)
    
    def set_target(self, args):
        """Set target host"""
        if not args:
            print(f"Current target: {self.current_target or 'Not set'}")
            return
        
        self.current_target = args[0]
        print(f"Target set to: {self.current_target}")
    
    def do_scan(self, args):
        """Run reconnaissance scan"""
        if not self.current_target:
            print("Error: No target set. Use 'target <host>' first")
            return
        
        print(f"\n[+] Starting reconnaissance on {self.current_target}")
        print("[+] This may take several minutes...\n")
        
        try:
            run_recon(self.current_target)
            print("\n[+] Scan completed")
        except Exception as e:
            print(f"\n[!] Scan failed: {e}")
    
    def do_report(self, args):
        """Generate report"""
        if not self.current_target:
            print("Error: No target set")
            return
        
        try:
            generate_report(self.current_target)
        except Exception as e:
            print(f"[!] Report generation failed: {e}")
    
    def show_status(self, args):
        """Show system status"""
        print("\nPISECOS STATUS")
        print("-" * 40)
        print(f"Target: {self.current_target or 'Not set'}")
        print(f"Tools directory: /opt/pisecos/tools")
        print(f"Scans directory: /opt/pisecos/scans")
        print(f"Reports directory: /opt/pisecos/reports")
        
        # Check disk space
        try:
            import shutil
            usage = shutil.disk_usage("/opt/pisecos")
            percent = (usage.used / usage.total) * 100
            print(f"Disk usage: {percent:.1f}%")
        except:
            pass
        
        print("-" * 40 + "\n")
    
    def clear_screen(self, args):
        """Clear terminal"""
        os.system('clear' if os.name == 'posix' else 'cls')
        self.print_banner()
    
    def ask_ai(self, args):
        """Ask AI a question"""
        if not args:
            print("Usage: ai <your question>")
            return
        
        question = " ".join(args)
        print(f"\n[AI] Processing: {question}")
        print("[AI] Analyzing...\n")
        
        # Use existing ai_engine
        try:
            handle_command(question)
        except Exception as e:
            print(f"[AI] Error: {e}")
    
    def do_exit(self, args):
        """Exit PiSecOS"""
        print("\nShutting down PiSecOS...")
        self.running = False
    
    def run(self):
        """Main loop"""
        while self.running:
            try:
                # Show prompt
                if self.current_target:
                    prompt = f"PiSecOS [{self.current_target}]> "
                else:
                    prompt = "PiSecOS> "
                
                cmd_line = input(prompt).strip()
                
                if not cmd_line:
                    continue
                
                # Parse command
                parts = cmd_line.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Execute
                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    # Try AI engine for unknown commands
                    handle_command(cmd_line)
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Entry point"""
    controller = PiSecOSController()
    controller.run()

if __name__ == "__main__":
    main()