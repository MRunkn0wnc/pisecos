#!/usr/bin/env python3
"""
PiSecOS AI Engine - AEGIS
Enhanced with real ML capabilities
"""

import json
import os
import subprocess
from pathlib import Path

# Add real AI imports
try:
    from llama_cpp import Llama
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("[AEGIS] Note: Install llama-cpp-python for AI features")

class AEGIS:
    """
    AEGIS AI Assistant - Enhanced with real ML
    """
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.dirname(self.script_dir)
        self.config_dir = os.path.join(self.base_dir, "configs")
        
        # Load intents
        self.intents = self.load_intents()
        
        # Initialize real AI if available
        self.model = None
        if AI_AVAILABLE:
            self.init_model()
    
    def load_intents(self):
        """Load intent mappings"""
        intent_file = os.path.join(self.config_dir, "intent_map.json")
        try:
            with open(intent_file) as f:
                return json.load(f)
        except:
            return {}
    
    def init_model(self):
        """Initialize TinyLlama model"""
        model_path = os.path.join(self.base_dir, "core", "ai", "model", "tinyllama.gguf")
        if os.path.exists(model_path):
            try:
                self.model = Llama(
                    model_path=model_path,
                    n_ctx=2048,
                    n_threads=4,
                    verbose=False
                )
                print("[AEGIS] AI model loaded successfully")
            except Exception as e:
                print(f"[AEGIS] Model load failed: {e}")
    
    def understand_command(self, cmd):
        """
        Understand natural language command
        Falls back to keyword matching if AI not available
        """
        if self.model:
            # Use real AI
            prompt = f"""You are AEGIS, an aggressive pentesting AI. 
User command: {cmd}

Extract:
- Intent (scan, exploit, recon, tool)
- Target (domain/IP)
- Specific tool if mentioned

Reply in format: intent|target|tool"""
            
            response = self.model(prompt, max_tokens=50)
            parts = response['choices'][0]['text'].strip().split('|')
            
            if len(parts) >= 2:
                return {
                    'intent': parts[0],
                    'target': parts[1],
                    'tool': parts[2] if len(parts) > 2 else None,
                    'method': 'ai'
                }
        
        # Fallback to keyword matching (your original logic)
        return self.keyword_match(cmd)
    
    def keyword_match(self, cmd):
        """Your original keyword matching logic"""
        text = cmd.lower()
        parts = cmd.split()
        
        result = {
            'intent': None,
            'target': None,
            'tool': None,
            'method': 'keyword'
        }
        
        # Extract target (last word)
        if len(parts) >= 2:
            result['target'] = parts[-1]
        
        # Match intent
        for intent in self.intents:
            if intent in text:
                result['intent'] = intent
                result['tool'] = self.intents[intent][0] if self.intents[intent] else None
                break
        
        return result
    
    def explain_action(self, action, target):
        """Explain what AEGIS is doing"""
        if self.model:
            prompt = f"""You are AEGIS, an aggressive pentesting AI.
Action: {action}
Target: {target}

Explain why you're doing this and what you hope to find.
Be aggressive and technical. No emojis."""
            
            response = self.model(prompt, max_tokens=150)
            return response['choices'][0]['text'].strip()
        
        # Fallback explanations
        explanations = {
            'scan': f"Scanning {target} to discover attack surface. Finding open ports and services.",
            'subdomains': f"Enumerating subdomains of {target} to expand attack surface.",
            'ports': f"Port scanning {target} to identify running services.",
            'vulnerabilities': f"Checking {target} for known vulnerabilities."
        }
        return explanations.get(action, f"Executing {action} on {target}")

# Keep your original function for compatibility
def handle_command(cmd):
    """
    Original function enhanced with AI
    """
    aegis = AEGIS()
    
    # Understand the command
    understood = aegis.understand_command(cmd)
    
    if understood['intent']:
        # Explain what we're doing
        explanation = aegis.explain_action(understood['intent'], understood['target'])
        print(f"\n[AEGIS] {explanation}\n")
        
        # Execute based on intent
        if understood['intent'] == 'recon' or understood['intent'] == 'scan':
            from recon_engine import run_recon
            run_recon(understood['target'])
        else:
            # Use your original aegis.py execute function
            from aegis import execute
            result = execute(cmd)
            print(result)
    else:
        # Unknown command, try AI chat
        if aegis.model:
            response = aegis.model(f"User: {cmd}\nAEGIS:", max_tokens=100)
            print(f"\n[AEGIS] {response['choices'][0]['text'].strip()}\n")
        else:
            print("[AEGIS] Command not recognized")