#!/usr/bin/env python3
"""Test planning generation"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.planning import get_planning_service
from src.core.decorators import with_db_session

@with_db_session
def test_planning_generation(db):
    """Test if planning generation works"""
    service = get_planning_service(db)
    
    # Generate planning for next week
    today = datetime.now()
    week_start = today
    
    print(f"Testing planning generation for week starting {week_start.date()}...")
    
    try:
        planning = service.generer_planning_ia(
            semaine_debut=week_start,
            preferences=None
        )
        
        if planning:
            print(f"✓ Planning generated successfully!")
            print(f"  Planning ID: {planning.id}")
            print(f"  Week: {planning.semaine_debut}")
            print(f"  Items: {len(planning.items)}")
            if planning.items:
                for item in planning.items[:3]:
                    print(f"    - {item.titre}")
            return True
        else:
            print("✗ Planning is empty")
            return False
    except Exception as e:
        print(f"✗ Error generating planning: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_planning_generation()
    sys.exit(0 if success else 1)
