"""
AlertHistory: Stores and manages all triggered emergency alerts.
"""
from typing import List, Dict, Any
import threading
import csv
from datetime import datetime
from app.classes.emergency_model import EmergencyAlert
import os

class AlertHistory:
    def __init__(self, debug: bool = False):
        
        # Thread-safe storage for emergency alerts
        self._lock = threading.RLock()

        # Store all emergency alerts
        self.alerts: List[EmergencyAlert] = []

        # Debug mode
        self.debug = debug
    

    def add_alert(self, alert: EmergencyAlert) -> bool:
        """
        Add a new alert to the history.
        Only adds if there is no unresolved alert with the same type, source, and source_id.
        Returns True if added, False if duplicate.
        """
        with self._lock:
            for existing in self.alerts:
                if (
                    existing.alert_type == alert.alert_type and
                    existing.source == alert.source and
                    existing.source_id == alert.source_id and
                    not existing.resolved
                ):
                    if self.debug:
                        print(f"[ALERT_HISTORY DEBUG] Duplicate active alert not added: {alert.alert_id}")
                    return False  # Duplicate, not added

            self.alerts.append(alert)
            if self.debug:
                print(f"[ALERT_HISTORY DEBUG] Added alert: {alert.alert_id}")
            return True

    def resolve_alert(self, alert_id: str):
        with self._lock:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.mark_resolved()

                    if self.debug:
                        print(f"[ALERT_HISTORY DEBUG] Resolved alert: {alert_id}")

                    return True
            
            if self.debug:
                print(f"[ALERT_HISTORY DEBUG] Alert not found for resolution: {alert_id}")

            return False

    def clear(self):
        with self._lock:
            self.alerts.clear()

    def csv_dump(self, file_path: str):
        """Dump the alert history to a CSV file."""

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write to CSV file
        with open(file_path, mode="a", newline="") as csvfile:
            fieldnames = ["alert_id", "timestamp", "source", "source_id", "alert_type", "resolved", "details"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if os.path.getsize(file_path) == 0:
                writer.writeheader()
            for alert in self.alerts:
                writer.writerow({
                    "alert_id": alert.alert_id,
                    "timestamp": alert.timestamp,
                    "source": alert.source,
                    "source_id": alert.source_id,
                    "alert_type": alert.alert_type,
                    "resolved": alert.resolved,
                    "details": str(alert.details) if alert.details else ""
                })
    

    # Retrieval methods

    def get_latest_alert(self, timestamp: str) -> EmergencyAlert:
        """Get the latest alert up to the given timestamp."""
        with self._lock:
            filtered = [a for a in self.alerts if a.timestamp <= timestamp]
            if filtered:
                return filtered[-1]
            return None

    def get_unresolved_alerts(self) -> List[EmergencyAlert]:
        with self._lock:
            return [a for a in self.alerts if a.is_active()]
        



if __name__ == "__main__":
    # Example usage for testing
    #
    #    cd /home/leonardo/iot/IoT_Project/anomaly_detection
    #    python3 -m app.persistence.alert_history
    #
    history = AlertHistory(debug=True)
    from datetime import timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # Add first alert
    print("Add first room alert (should succeed):")
    print(history.add_alert(EmergencyAlert(
        alert_id="A1", source="room", source_id="room1", alert_type="overheat", timestamp=now, details={"temperature": 45}
    )))
    # Try to add duplicate unresolved alert (should fail)
    print("Add duplicate unresolved room alert (should fail):")
    print(history.add_alert(EmergencyAlert(
        alert_id="A1_DUP", source="room", source_id="room1", alert_type="overheat", timestamp=now, details={"temperature": 46}
    )))
    # Add printer alert
    print("Add first printer alert (should succeed):")
    print(history.add_alert(EmergencyAlert(
        alert_id="A2", source="printer", source_id="printer1", alert_type="overheat", timestamp=now, details={"temperature": 250}
    )))
    # Resolve room alert
    print("Resolve room alert:")
    history.resolve_alert("A1")
    # Try to add room alert again after resolving (should succeed)
    print("Add room alert after resolving (should succeed):")
    print(history.add_alert(EmergencyAlert(
        alert_id="A1_NEW", source="room", source_id="room1", alert_type="overheat", timestamp=now, details={"temperature": 47}
    )))

    def print_alerts(alerts):
        for alert in alerts:
            print(f"AlertID: {alert.alert_id} | Source: {alert.source} | SourceID: {alert.source_id} | "
                  f"Type: {alert.alert_type} | Time: {alert.timestamp} | Resolved: {alert.resolved} | Details: {alert.details}")

    print("\nAll alerts:")
    print_alerts(history.alerts)

    print("\nUnresolved alerts:")
    print_alerts(history.get_unresolved_alerts())
