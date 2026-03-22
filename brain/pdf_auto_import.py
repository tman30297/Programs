#!/usr/bin/env python3
"""
Brain PDF Auto-Importer - Hourly cron job to import PDFs with content.
Does ~15 pages (5 PDFs x 3 pages) from rotating topics. Reduced from 50 for token efficiency.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Topics to cycle through for variety
TOPICS = [
    # Original topics
    ("python", "/media/tony/Drive2/python3/"),
    ("class", "/media/tony/Drive2/python3/"),
    ("async", "/media/tony/Drive2/python3/"),
    ("function", "/media/tony/Drive2/python3/"),
    ("esp32", "/media/tony/Drive2/IOT/"),
    ("arduino", "/media/tony/Drive2/IOT/"),
    ("sensor", "/media/tony/Drive2/IOT/"),
    ("rust", "/media/tony/Drive2/Rust/"),
    ("ownership", "/media/tony/Drive2/Rust/"),
    ("memory", "/media/tony/Drive2/Rust/"),
    
    # Programming fundamentals
    ("algorithm", "/media/tony/Drive2/python3/"),
    ("data-structure", "/media/tony/Drive2/python3/"),
    ("object-oriented", "/media/tony/Drive2/python3/"),
    ("functional-programming", "/media/tony/Drive2/python3/"),
    ("variable", "/media/tony/Drive2/python3/"),
    ("loop", "/media/tony/Drive2/python3/"),
    ("recursion", "/media/tony/Drive2/python3/"),
    ("compiler", "/media/tony/Drive2/python3/"),
    ("interpreter", "/media/tony/Drive2/python3/"),
    ("debugging", "/media/tony/Drive2/python3/"),
    ("testing", "/media/tony/Drive2/python3/"),
    ("unit-test", "/media/tony/Drive2/python3/"),
    ("refactoring", "/media/tony/Drive2/python3/"),
    ("design-pattern", "/media/tony/Drive2/python3/"),
    ("api", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("framework", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("library", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("dependency", "/media/tony/Drive2/python3/"),
    ("package-manager", "/media/tony/Drive2/python3/"),
    ("version-control", "/media/tony/Drive2/python3/"),
    
    # Web development
    ("html", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("css", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("javascript", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("typescript", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("react", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("vue", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("angular", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("nodejs", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("express", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("rest-api", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("graphql", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("websocket", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("http", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("json", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("xml", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("responsive-design", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("css-grid", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("flexbox", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("bootstrap", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("webpack", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("npm", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("frontend", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("backend", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("fullstack", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("mvc", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("server", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("router", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("middleware", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("session", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("cookie", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("authentication", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("jwt", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("oauth", "/media/tony/Drive2/Full_Stack_Dev/"),
    
    # Databases
    ("database", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("sql", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("mysql", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("postgresql", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("mongodb", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("redis", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("sqlite", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("query", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("join", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("transaction", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("nosql", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("orm", "/media/tony/Drive2/Full_Stack_Dev/"),
    
    # Mobile development
    ("ios", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("android", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("swift", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("kotlin", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("objective-c", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("mobile-app", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("xcode", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("android-studio", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("flutter", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("react-native", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("push-notification", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("geolocation", "/media/tony/Drive2/Full_Stack_Dev/"),
    
    # DevOps & Cloud
    ("docker", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("kubernetes", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("ci-cd", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("jenkins", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("github-actions", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("aws", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("azure", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("google-cloud", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("cloud", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("serverless", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("lambda", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("microservice", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("container", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("deployment", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("terraform", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("monitoring", "/media/tony/Drive2/Full_Stack_Dev/"),
    
    # Security
    ("security", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("encryption", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("cryptography", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("vulnerability", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("firewall", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("ssl", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("tls", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("xss", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("sql-injection", "/media/tony/Drive2/Full_Stack_Dev/"),
    
    # Java ecosystem
    ("java", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("spring", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("hibernate", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("maven", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("gradle", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("jvm", "/media/tony/Drive2/Full_Stack_Dev/"),
    
    # Python ecosystem
    ("django", "/media/tony/Drive2/python3/"),
    ("flask", "/media/tony/Drive2/python3/"),
    ("fastapi", "/media/tony/Drive2/python3/"),
    ("pandas", "/media/tony/Drive2/python3/"),
    ("numpy", "/media/tony/Drive2/python3/"),
    ("tensorflow", "/media/tony/Drive2/python3/"),
    ("pytorch", "/media/tony/Drive2/python3/"),
    ("opencv", "/media/tony/Drive2/python3/"),
    ("scrapy", "/media/tony/Drive2/python3/"),
    ("pytest", "/media/tony/Drive2/python3/"),
    
    # JavaScript/TypeScript
    ("yarn", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("redux", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("nextjs", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("tailwind", "/media/tony/Drive2/Full_Stack_Dev/"),
    
    # C family
    ("c-plus-plus", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("c-sharp", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("golang", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("ruby", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("rails", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("php", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("laravel", "/media/tony/Drive2/Full_Stack_Dev/"),
    
    # Data Science & ML
    ("machine-learning", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("deep-learning", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("neural-network", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("data-science", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("nlp", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("computer-vision", "/media/tony/Drive2/Full_Stack_Dev/"),
    
    # Networking
    ("networking", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("tcp", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("dns", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("https", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("ssh", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("vpn", "/media/tony/Drive2/Full_Stack_Dev/"),
    
    # Software Engineering
    ("agile", "/media/tony/Drive2/python3/"),
    ("scrum", "/media/tony/Drive2/python3/"),
    ("sprint", "/media/tony/Drive2/python3/"),
    ("code-review", "/media/tony/Drive2/python3/"),
    ("pull-request", "/media/tony/Drive2/python3/"),
    ("scaling", "/media/tony/Drive2/python3/"),
    ("performance", "/media/tony/Drive2/python3/"),
    ("caching", "/media/tony/Drive2/python3/"),
    ("load-balancing", "/media/tony/Drive2/python3/"),
    
    # More programming terms
    ("regex", "/media/tony/Drive2/python3/"),
    ("yaml", "/media/tony/Drive2/python3/"),
    ("thread", "/media/tony/Drive2/python3/"),
    ("concurrency", "/media/tony/Drive2/python3/"),
    ("callback", "/media/tony/Drive2/python3/"),
    ("promise", "/media/tony/Drive2/python3/"),
    ("decorator", "/media/tony/Drive2/python3/"),
    ("closure", "/media/tony/Drive2/python3/"),
    ("polymorphism", "/media/tony/Drive2/python3/"),
    ("inheritance", "/media/tony/Drive2/python3/"),
    ("interface", "/media/tony/Drive2/python3/"),
    
    # New folders - detected by Memory Updater
    ("fpga", "/media/tony/Drive2/FPGA/"),
    ("vhdl", "/media/tony/Drive2/FPGA/"),
    ("verilog", "/media/tony/Drive2/FPGA/"),
    ("digital-logic", "/media/tony/Drive2/FPGA/"),
    ("ios", "/media/tony/Drive2/IOS/"),
    ("swiftui", "/media/tony/Drive2/IOS/"),
    ("xamarin", "/media/tony/Drive2/IOS/"),
    ("smart-home", "/media/tony/Drive2/IOT/"),
    ("home-automation", "/media/tony/Drive2/IOT/"),
    ("actuators", "/media/tony/Drive2/IOT/"),
    ("proxmox", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("unifi", "/media/tony/Drive2/Full_Stack_Dev/"),
    ("esp32", "/media/tony/Drive2/IOT/"),
    ("arduino", "/media/tony/Drive2/IOT/"),
    ("sensor", "/media/tony/Drive2/IOT/"),
    ("iot", "/media/tony/Drive2/IOT/"),
]

import brain
import json
import re

# Track which topics have been imported
STATE_FILE = Path("/media/tony/Drive2/Brain/.pdf_import_state.json")

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {"topic_index": 0, "imported": []}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def main():
    print("📚 Brain PDF Auto-Importer")
    print("-" * 30)
    
    state = load_state()
    topic_index = state.get("topic_index", 0)
    
    # Get current topic
    topic, directory = TOPICS[topic_index % len(TOPICS)]
    print(f"🔍 Topic: '{topic}' from {directory}")
    
    # Import with content (5 PDFs x 3 pages = 15 pages)
    # Use --no-content flag to skip if we want metadata only
    brain.import_pdf_search_to_notes(
        search_term=topic,
        directory=directory,
        tags=f"pdf,auto-import,{topic}",
        max_pdfs=5,
        extract_content=True
    )
    
    # Move to next topic
    state["topic_index"] = topic_index + 1
    save_state(state)
    
    print(f"\n✅ Hourly import complete!")
    print(f"   Next topic: {TOPICS[(topic_index + 1) % len(TOPICS)][0]}")

if __name__ == "__main__":
    main()