#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeLab HU - GitHub push automatizáló Python verzió (Windows/Linux)
Használat: python3 push.py "feat: új plugin" [tag]
"""
import subprocess
import sys
from pathlib import Path

def run(cmd, check=True):
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result

def main():
    print("=== CodeLab HU GitHub Push Automatizáló (Python) ===")
    
    # Verzió
    try:
        from core.version import MAIN_VERSION, PLUGIN_API_VERSION
        version = str(MAIN_VERSION)
        api_version = str(PLUGIN_API_VERSION)
    except:
        version = "1.2.0"
        api_version = "1.0.0"
    print(f"Fő verzió: {version} | API: {api_version}")
    
    # Plugin számlálás
    try:
        from core.plugin_system import PluginLoader
        loader = PluginLoader()
        loader.load_all()
        plugin_count = len(loader.plugins)
        plugin_names = ", ".join([p.name for p in loader.list_plugins()])
        print(f"Pluginok: {plugin_count} | {plugin_names}")
    except Exception as e:
        print(f"Plugin számlálás hiba: {e}")
        plugin_names = "ismeretlen"
    
    commit_msg = sys.argv[1] if len(sys.argv) > 1 else f"feat: v{version} - auto push"
    tag = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Commit üzenet: {commit_msg}")
    
    # Git init ha kell
    if not Path(".git").exists():
        print("Nincs .git, inicializálás...")
        run("git init")
    
    # Status
    run("git status --short", check=False)
    
    # Add
    run("git add .")
    
    # Commit ha van változás
    result = subprocess.run("git diff --cached --quiet", shell=True)
    if result.returncode == 0:
        print("Nincs változás, nincs commit")
    else:
        full_msg = f'{commit_msg}\n\n- Fő verzió: {version}\n- API: {api_version}\n- Pluginok: {plugin_names}'
        run(f'git commit -m "{full_msg}"')
        print(f"Commit kész: {commit_msg}")
    
    # Branch
    branch_result = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True)
    branch = branch_result.stdout.strip() or "main"
    print(f"Branch: {branch}")
    
    # Remote check
    remote_result = subprocess.run("git remote", shell=True, capture_output=True, text=True)
    if "origin" not in remote_result.stdout:
        print("Nincs origin remote! Add hozzá:")
        print("git remote add origin https://github.com/felhosi/codelab-hu.git")
        sys.exit(1)
    
    # Push
    run(f"git push origin {branch}")
    print("✓ Push kész!")
    
    # Tag
    if tag:
        print(f"Tag létrehozása: {tag}")
        run(f'git tag -a {tag} -m "Release {tag} - {commit_msg}"')
        run(f"git push origin {tag}")
        print(f"✓ Tag {tag} pusholva!")
    else:
        print("Tipp: taggel is: python3 push.py \"feat: új\" v1.3.0")
    
    print("=== Kész! https://github.com/felhosi/codelab-hu ===")

if __name__ == "__main__":
    main()
