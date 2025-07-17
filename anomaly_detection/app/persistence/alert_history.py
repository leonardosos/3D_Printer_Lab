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
    

    def add_alert(self, alert: EmergencyAlert):
        with self._lock:
            self.alerts.append(alert)

            if self.debug:
                print(f"[ALERT_HISTORY DEBUG] Added alert: {alert.alert_id}")

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
    history = AlertHistory()
    from datetime import timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    history.add_alert(EmergencyAlert(
        alert_id="A1", source="room", source_id="room1", alert_type="overheat", timestamp=now, details={"temperature": 45}
    ))
    history.add_alert(EmergencyAlert(
        alert_id="A2", source="printer", source_id="printer1", alert_type="overheat", timestamp=now, details={"temperature": 250}
    ))

    def print_alerts(alerts):
        for alert in alerts:
            print(f"AlertID: {alert.alert_id} | Source: {alert.source} | SourceID: {alert.source_id} | "
                  f"Type: {alert.alert_type} | Time: {alert.timestamp} | Resolved: {alert.resolved} | Details: {alert.details}")

    print("Latest alert:")
    latest = history.get_latest_alert(now)
    print_alerts([latest] if latest else [])

    print("\nUnresolved alerts:")
    print_alerts(history.get_unresolved_alerts())

    history.resolve_alert("A1")
    print("\nUnresolved alerts after resolving A1:")
    print_alerts(history.get_unresolved_alerts())
