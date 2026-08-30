"""
Manual test script for Digital Twin snapshot persistence.

This script verifies the complete lifecycle:
1. Observation recording
2. Snapshot creation
3. Supabase persistence
4. Twin recovery

BEFORE RUNNING:
- Ensure Supabase credentials are in .env
- Ensure a test cow exists in the database
- Run: python test_twin_persistence.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from webapp.repositories.supabase_client import SupabaseClient
from webapp.repositories.snapshot_repository import SnapshotRepository
from webapp.repositories.observation_repository import ObservationRepository
from webapp.repositories.cow_repository import CowRepository
from webapp.services.cow_service import CowService
from webapp.services.observation_service import ObservationService
from webapp.digital_twin.observation import Observation


def print_step(step_num: int, description: str) -> None:
    """Print a test step."""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {description}")
    print('='*70)


def print_success(message: str) -> None:
    """Print success message."""
    print(f"✓ {message}")


def print_error(message: str) -> None:
    """Print error message."""
    print(f"✗ {message}")


def print_info(message: str) -> None:
    """Print info message."""
    print(f"ℹ {message}")


def test_supabase_connection() -> bool:
    """STEP 1: Verify Supabase connection."""
    print_step(1, "Verify Supabase Connection")
    
    try:
        client = SupabaseClient.from_env()
        if not client.is_configured:
            print_error("Supabase is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY in .env")
            return False
        
        print_success("Supabase client initialized")
        print_info(f"Connected to: {client.url[:50]}...")
        return True
    except Exception as e:
        print_error(f"Supabase connection failed: {e}")
        return False


def test_cow_retrieval() -> dict | None:
    """STEP 2: Retrieve an existing test cow."""
    print_step(2, "Retrieve Test Cow")
    
    try:
        cow_repo = CowRepository()
        cows = cow_repo.client.list("cows")
        
        if not cows:
            print_error("No cows found in database")
            print_info("Please register a cow first using the application")
            return None
        
        test_cow = cows[0]
        cow_id = test_cow.get("id") or test_cow.get("cow_id")
        cow_name = test_cow.get("cow_name") or test_cow.get("name")
        
        print_success(f"Found test cow: {cow_name} (ID: {cow_id})")
        print_info(f"Cow record: {test_cow}")
        
        return test_cow
    except Exception as e:
        print_error(f"Cow retrieval failed: {e}")
        return None


def test_observation_creation(cow_id: str, cow_record: dict) -> dict | None:
    """STEP 3: Create a test observation."""
    print_step(3, "Create Test Observation")
    
    try:
        obs_service = ObservationService()
        
        # Create observation with test data
        result = obs_service.record_observation(
            cow_id=cow_id,
            age=36.0,
            weight=450.0,
            feed=20.0,
            temperature=28.0,
            humidity=65.0,
            health_status=0,
            notes="Test observation for persistence verification",
        )
        
        print_success("Observation created successfully")
        print_info(f"Observation cow_id: {result['observation'].get('cow_id')}")
        
        # Verify snapshot was created in memory
        if result.get("snapshot"):
            print_success("Snapshot created in memory")
            print_info(f"Snapshot ID: {result['snapshot'].snapshot_id}")
            print_info(f"Snapshot status: {result['snapshot'].twin_status}")
        else:
            print_error("Snapshot not created")
            return None
        
        return result
    except Exception as e:
        print_error(f"Observation creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_observation_in_database(cow_id: str) -> dict | None:
    """STEP 4: Verify observation was persisted to database."""
    print_step(4, "Verify Observation in Database")
    
    try:
        obs_repo = ObservationRepository()
        observations = obs_repo.list_for_cow(cow_id)
        
        if not observations:
            print_error("No observations found in database for this cow")
            return None
        
        latest_obs = observations[-1]  # Get most recent
        print_success(f"Found {len(observations)} observation(s) for this cow")
        print_success(f"Latest observation persisted")
        print_info(f"Observation ID: {latest_obs.get('id')}")
        print_info(f"Feed: {latest_obs.get('feed')} kg/day")
        print_info(f"Temperature: {latest_obs.get('temperature')} °C")
        print_info(f"Humidity: {latest_obs.get('humidity')} %")
        print_info(f"Created at: {latest_obs.get('created_at')}")
        
        return latest_obs
    except Exception as e:
        print_error(f"Database verification failed: {e}")
        return None


def test_snapshot_in_database(cow_id: str) -> dict | None:
    """STEP 5: Verify snapshot was persisted to twin_snapshots table."""
    print_step(5, "Verify Snapshot in Database")
    
    try:
        snapshot_repo = SnapshotRepository()
        latest_snapshot = snapshot_repo.get_latest_for_cow(cow_id)
        
        if not latest_snapshot:
            print_error("No snapshots found in twin_snapshots table for this cow")
            print_info("This is the KEY PERSISTENCE TEST - snapshot should be here!")
            return None
        
        print_success("Snapshot persisted to Supabase!")
        print_info(f"Snapshot ID (db): {latest_snapshot.get('id')}")
        print_info(f"Cow ID: {latest_snapshot.get('cow_id')}")
        print_info(f"Observation ID: {latest_snapshot.get('observation_id')}")
        print_info(f"Twin Status: {latest_snapshot.get('twin_status')}")
        print_info(f"Created at: {latest_snapshot.get('created_at')}")
        
        # Check JSONB fields
        if latest_snapshot.get("prediction"):
            print_success(f"Prediction persisted: {latest_snapshot['prediction']}")
        else:
            print_error("Prediction missing from snapshot")
        
        if latest_snapshot.get("health"):
            print_success(f"Health assessment persisted: {latest_snapshot['health']}")
        else:
            print_error("Health missing from snapshot")
        
        if latest_snapshot.get("explanation"):
            print_success("Explanation persisted")
        else:
            print_info("No explanation (may be normal)")
        
        if latest_snapshot.get("recommendations"):
            print_success(f"Recommendations persisted: {len(latest_snapshot['recommendations'])} items")
        else:
            print_info("No recommendations (may be normal)")
        
        return latest_snapshot
    except Exception as e:
        print_error(f"Snapshot verification failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_twin_recovery(cow_id: str) -> bool:
    """STEP 6: Verify digital twin can be recovered from snapshots."""
    print_step(6, "Verify Twin Recovery from Snapshots")
    
    try:
        # Clear in-memory cache to simulate new session
        cow_service = CowService()
        cow_service._cow_twins.clear()
        
        print_info("Cleared in-memory twin cache (simulating new session)")
        
        # Load twin from snapshots
        recovered_twin = cow_service.load_twin_from_snapshots(cow_id)
        
        if recovered_twin is None:
            print_error("Failed to load twin from snapshots")
            return False
        
        print_success("Twin recovered from Supabase snapshots!")
        print_info(f"Twin cow_id: {recovered_twin.cow_id}")
        print_info(f"Twin status: {recovered_twin.state.status}")
        
        # Verify recovered state
        if recovered_twin.latest_prediction:
            print_success(f"Prediction recovered: {recovered_twin.latest_prediction}")
        else:
            print_warning("Prediction not recovered")
        
        if recovered_twin.latest_health:
            print_success(f"Health recovered: {recovered_twin.latest_health}")
        else:
            print_warning("Health not recovered")
        
        return True
    except Exception as e:
        print_error(f"Twin recovery failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_warning(message: str) -> None:
    """Print warning message."""
    print(f"⚠ {message}")


def test_snapshot_history(cow_id: str) -> bool:
    """STEP 7: Verify snapshot history retrieval."""
    print_step(7, "Verify Snapshot History Retrieval")
    
    try:
        snapshot_repo = SnapshotRepository()
        history = snapshot_repo.list_for_cow(cow_id)
        
        if not history:
            print_warning("No snapshot history found")
            return False
        
        print_success(f"Found {len(history)} snapshot(s)")
        
        for i, snapshot in enumerate(history, 1):
            print_info(f"  {i}. {snapshot.get('created_at')} - Status: {snapshot.get('twin_status')}")
        
        return True
    except Exception as e:
        print_error(f"History retrieval failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("DIGITAL TWIN PERSISTENCE TEST SUITE")
    print("="*70)
    
    # Test sequence
    if not test_supabase_connection():
        return
    
    cow_record = test_cow_retrieval()
    if not cow_record:
        return
    
    cow_id = cow_record.get("id") or cow_record.get("cow_id")
    
    obs_result = test_observation_creation(cow_id, cow_record)
    if not obs_result:
        return
    
    obs_in_db = test_observation_in_database(cow_id)
    if not obs_in_db:
        return
    
    snapshot_in_db = test_snapshot_in_database(cow_id)
    if not snapshot_in_db:
        print_error("\n🔴 CRITICAL: Snapshot was not persisted to Supabase!")
        print_info("Check observation_service._persist_snapshot_to_supabase() was called")
        return
    
    if not test_twin_recovery(cow_id):
        return
    
    if not test_snapshot_history(cow_id):
        return
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print_success("All tests passed!")
    print_success("Snapshot persistence is working correctly")
    print_success("Twin recovery from snapshots is functional")
    print_success("Digital Twin lifecycle is complete:")
    print_info("  1. Observation → Database ✓")
    print_info("  2. Snapshot → Supabase ✓")
    print_info("  3. Twin Recovery ✓")
    print_info("  4. Cross-session persistence ✓")


if __name__ == "__main__":
    main()
