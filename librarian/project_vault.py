#!/usr/bin/env python3
"""
Project Vault - CSV-based Later List Manager

Manages projects saved for later using Pandas CSV.
"""

import sys
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

CSV_PATH = Path(__file__).parent / "later_list.csv"

def load_csv() -> pd.DataFrame:
    """Load or create CSV."""
    if CSV_PATH.exists():
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame(columns=["Project Name", "Stack", "Notes", "Status", "Date Added"])

def save_csv(df: pd.DataFrame) -> None:
    """Save CSV."""
    df.to_csv(CSV_PATH, index=False)

def add_project(name: str, stack: str, notes: str) -> str:
    """Add project to later list."""
    df = load_csv()
    
    if name in df["Project Name"].values:
        return f"'{name}' already in list."
    
    new_entry = pd.DataFrame([{
        "Project Name": name,
        "Stack": stack,
        "Notes": notes,
        "Status": "Saved for Later",
        "Date Added": datetime.now().strftime("%Y-%m-%d")
    }])
    
    df = pd.concat([df, new_entry], ignore_index=True)
    save_csv(df)
    return f"Added: {name}"

def list_projects() -> None:
    """List all projects."""
    df = load_csv()
    if df.empty:
        print("No projects in vault.")
        return
    
    # Calculate aging
    df["Date Added"] = pd.to_datetime(df["Date Added"])
    df["Days Active"] = (datetime.now() - df["Date Added"]).dt.days
    
    def aging_status(days):
        if days > 60: return "🔴 High"
        if days > 30: return "🟡 Medium"
        return "🟢 Fresh"
    
    df["Aging"] = df["Days Active"].apply(aging_status)
    print(df[["Project Name", "Stack", "Status", "Aging", "Days Active"]].to_string(index=False))

def show_aging() -> None:
    """Show projects sorted by age."""
    df = load_csv()
    if df.empty:
        print("No projects in vault.")
        return
    
    df["Date Added"] = pd.to_datetime(df["Date Added"])
    df["Days Active"] = (datetime.now() - df["Date Added"]).dt.days
    df = df.sort_values("Days Active", ascending=False)
    
    print("\n📋 Project Aging Report\n")
    for _, row in df.iterrows():
        status = "🔴" if row["Days Active"] > 60 else "🟡" if row["Days Active"] > 30 else "🟢"
        print(f"{status} {row['Project Name']} ({row['Days Active']} days)")
        print(f"   Stack: {row['Stack']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: project_vault.py <add|list|aging> [args...]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        if len(sys.argv) < 5:
            print("Usage: project_vault.py add 'Name' 'Stack' 'Notes'")
            sys.exit(1)
        print(add_project(sys.argv[2], sys.argv[3], sys.argv[4]))
    elif cmd == "list":
        list_projects()
    elif cmd == "aging":
        show_aging()
    else:
        print(f"Unknown command: {cmd}")