"""
FragmentDependencyGraph: Models dependencies between plan fragments for parallel execution.
"""
from typing import Dict, Set, List, Optional

class FragmentDependencyGraph:
    def __init__(self):
        # fragment_id -> set of dependent fragment_ids
        self.dependencies: Dict[str, Set[str]] = {}
        # fragment_id -> set of fragments that depend on this fragment
        self.reverse_dependencies: Dict[str, Set[str]] = {}
        # fragment_id -> fragment object (optional, for lookup)
        self.fragments: Dict[str, object] = {}
        # fragment_id -> completion state
        self.completed: Set[str] = set()

    def add_fragment(self, fragment, depends_on: Optional[List[str]] = None):
        fid = fragment.fragment_id
        self.fragments[fid] = fragment
        self.dependencies.setdefault(fid, set())
        self.reverse_dependencies.setdefault(fid, set())
        if depends_on:
            for dep in depends_on:
                self.dependencies[fid].add(dep)
                self.reverse_dependencies.setdefault(dep, set()).add(fid)

    def mark_completed(self, fragment_id: str):
        self.completed.add(fragment_id)

    def get_ready_fragments(self) -> List[object]:
        print(f"[DEPGRAPH] get_ready_fragments called: completed={self.completed}, dependencies={self.dependencies}")
        ready = []
        for fid, deps in self.dependencies.items():
            if fid not in self.completed and all(d in self.completed for d in deps):
                ready.append(self.fragments[fid])
        print(f"[DEPGRAPH] get_ready_fragments returning: {[f.fragment_id for f in ready]}")
        return ready

    def is_blocked(self, fragment_id: str) -> bool:
        return any(dep not in self.completed for dep in self.dependencies.get(fragment_id, set()))

    def all_completed(self) -> bool:
        print(f"[DEPGRAPH] all_completed called: completed={self.completed}, fragments={list(self.fragments.keys())}")
        return len(self.completed) == len(self.fragments)

    def get_dependents(self, fragment_id: str) -> Set[str]:
        return self.reverse_dependencies.get(fragment_id, set())
