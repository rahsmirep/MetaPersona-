import threading
import time
from typing import Any, Dict, List, Optional

class BlackboardEntry:
    def __init__(self, key: str, value: Any, author: str, metadata: Optional[Dict[str, Any]] = None):
        self.key = key
        self.value = value
        self.author = author
        self.metadata = metadata or {}
        self.metadata.setdefault('timestamp', time.time())
        self.metadata.setdefault('history', [])

    def update(self, value: Any, author: str, metadata: Optional[Dict[str, Any]] = None):
        # Log previous value in history
        self.metadata['history'].append({
            'value': self.value,
            'author': self.author,
            'timestamp': self.metadata.get('timestamp', time.time())
        })
        self.value = value
        self.author = author
        self.metadata['timestamp'] = time.time()
        if metadata:
            self.metadata.update(metadata)

class SharedBlackboard:
    def list_parallel_groups(self) -> List[Any]:
        """
        List all parallel execution groups.
        """
        with self._lock:
            return [entry.value for key, entry in self._entries.items() if key.startswith('parallel_group:')]

    def get_parallel_group(self, group_id: str) -> Optional[Any]:
        """
        Get the fragment IDs for a parallel execution group.
        """
        with self._lock:
            entry = self._entries.get(f'parallel_group:{group_id}')
            return entry.value if entry else None

    def log_merge_decision(self, group_id: str, merge_info: dict):
        """
        Log a merge decision for a parallel execution group.
        """
        with self._lock:
            key = f'merge_history:{group_id}'
            if key in self._entries:
                self._entries[key].update(merge_info, 'shared_blackboard', metadata={'group_id': group_id})
            else:
                self.write(key, [merge_info], 'shared_blackboard', metadata={'group_id': group_id})

    def get_merge_history(self, group_id: str) -> Optional[Any]:
        """
        Get the merge history for a parallel execution group.
        """
        with self._lock:
            entry = self._entries.get(f'merge_history:{group_id}')
            return entry.value if entry else None
    def list_plan_fragments(self, plan_id: str) -> List[Any]:
        """
        List all fragments for a given plan_id.
        """
        with self._lock:
            return [entry.value for key, entry in self._entries.items() if key.startswith('fragment:') and entry.metadata.get('plan_id') == plan_id]

    def get_plan_state(self, plan_id: str) -> Dict[str, Any]:
        """
        Get the current state of a plan and its fragments.
        """
        with self._lock:
            plan = self._entries.get(f'plan:{plan_id}')
            fragments = self.list_plan_fragments(plan_id)
            return {
                'plan': plan.value if plan else None,
                'fragments': fragments
            }

    def list_negotiation_logs(self, plan_id: str) -> List[Any]:
        """
        List all negotiation logs for a given plan_id.
        """
        with self._lock:
            return [entry.value for key, entry in self._entries.items() if key.startswith('negotiation:') and entry.metadata.get('plan_id') == plan_id]
    """
    Thread-safe shared memory for agent collaboration.
    Supports read, write, update, merge, and trace logging.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._entries: Dict[str, BlackboardEntry] = {}
        self._trace_log: List[Dict[str, Any]] = []

    def write(self, key: str, value: Any, author: str, metadata: Optional[Dict[str, Any]] = None):
        with self._lock:
            entry = BlackboardEntry(key, value, author, metadata)
            self._entries[key] = entry
            self._log('write', key, author, value, entry.metadata)

    def read(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._entries.get(key)
            self._log('read', key, None, entry.value if entry else None, entry.metadata if entry else None)
            return entry.value if entry else None

    def update(self, key: str, value: Any, author: str, metadata: Optional[Dict[str, Any]] = None):
        with self._lock:
            if key in self._entries:
                self._entries[key].update(value, author, metadata)
                self._log('update', key, author, value, self._entries[key].metadata)
            else:
                self.write(key, value, author, metadata)

    def merge(self, key: str, value: Any, author: str, merge_fn, metadata: Optional[Dict[str, Any]] = None):
        with self._lock:
            if key in self._entries:
                merged_value = merge_fn(self._entries[key].value, value)
                self._entries[key].update(merged_value, author, metadata)
                self._log('merge', key, author, merged_value, self._entries[key].metadata)
            else:
                self.write(key, value, author, metadata)

    def trace_log(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._trace_log)

    def _log(self, action: str, key: str, author: Optional[str], value: Any, metadata: Optional[Dict[str, Any]]):
        self._trace_log.append({
            'action': action,
            'key': key,
            'author': author,
            'value': value,
            'metadata': metadata,
            'timestamp': time.time()
        })
