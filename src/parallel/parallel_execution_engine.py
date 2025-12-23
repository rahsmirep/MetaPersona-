"""
ParallelExecutionEngine: Executes independent plan fragments in parallel, manages dependencies, and merges results.
"""
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.parallel.fragment_dependency_graph import FragmentDependencyGraph
import threading

class ParallelExecutionEngine:
    def log_fragment_states(self, fragment_ids):
        """
        Logs the state, dependencies, unresolved dependencies, and timestamps for each fragment.
        """
        from datetime import datetime
        print("\n[FRAGMENT STATE INSPECTOR]")
        for fid in fragment_ids:
            fragment = self.shared_memory.read(f"fragment:{fid}")
            state = fragment.get('state') if fragment else 'unknown'
            updated_at = fragment.get('updated_at') if fragment else None
            deps = []
            unresolved = []
            if hasattr(self, 'dependency_graph') and self.dependency_graph:
                deps = list(self.dependency_graph.dependencies.get(fid, []))
                unresolved = [d for d in deps if d not in self.dependency_graph.completed]
            print(f"  Fragment {fid}: state={state}, deps={deps}, unresolved={unresolved}, updated_at={updated_at}, ts={datetime.now().isoformat(timespec='seconds')}")
        print("[END FRAGMENT STATE INSPECTOR]\n")

    def wait_for_fragments(self, fragment_ids, timeout=30, poll_interval=0.5):
        """
        Wait for all given fragment_ids to reach 'completed' state in SharedBlackboard.
        Diagnostic logs show fragment state, dependencies, unresolved deps, and timestamps.
        """
        print(">>> wait_for_fragments called")
        print(f">>> fragment_ids: {fragment_ids}")
        import time
        from datetime import datetime
        start = time.time()
        last_long_log = start
        # For state transition logs
        last_states = {}
        try:
            while time.time() - start < timeout:
                print(">>> Entered wait loop")
                self.log_fragment_states(fragment_ids)
                all_done = True
                now = time.time()
                for fid in fragment_ids:
                    fragment = self.shared_memory.read(f"fragment:{fid}")
                    state = fragment.get('state') if fragment else 'unknown'
                    # Get dependencies if possible
                    deps = []
                    unresolved = []
                    if hasattr(self, 'dependency_graph') and self.dependency_graph:
                        deps = list(self.dependency_graph.dependencies.get(fid, []))
                        unresolved = [d for d in deps if d not in self.dependency_graph.completed]
                    # Log state changes
                    prev_state = last_states.get(fid)
                    if prev_state != state:
                        print(f"[TRANSITION] Fragment {fid} {prev_state or 'None'} -> {state} ts={datetime.now().isoformat(timespec='seconds')}")
                        last_states[fid] = state
                        if state == 'in_progress':
                            print(f"[RUNNING] Fragment {fid} is now running at {datetime.now().isoformat(timespec='seconds')}")
                        if state == 'completed':
                            print(f"[DONE] Fragment {fid} is done at {datetime.now().isoformat(timespec='seconds')}")
                    # Log dependency resolution
                    if deps:
                        for dep in deps:
                            if dep not in self.dependency_graph.completed and fragment and fragment.get('state') == 'completed':
                                print(f"[DEPENDENCY] Fragment {fid} completed, but dependency {dep} unresolved at {datetime.now().isoformat(timespec='seconds')}")
                    # Main wait log
                    print(f"[WAIT] Fragment {fid} state={state} deps={deps} unresolved={unresolved} ts={datetime.now().isoformat(timespec='seconds')}")
                    if not fragment or state != 'completed':
                        all_done = False
                # Log every 5 seconds if still waiting
                if now - last_long_log >= 5:
                    print(f"[WAIT-LOOP] Still waiting after {int(now - start)}s at {datetime.now().isoformat(timespec='seconds')}")
                    last_long_log = now
                if all_done:
                    return True
                time.sleep(poll_interval)
            print(f"[TIMEOUT] wait_for_fragments timed out after {timeout}s at {datetime.now().isoformat(timespec='seconds')}")
            return False
        except Exception as e:
            print(f"[ERROR] Exception in wait_for_fragments: {e}")
            raise

    def merge_results(self, fragments: List[Any], group_id: str, merge_strategy: str = 'last_write_wins') -> Any:
        """
        Merge results from parallel fragments using the specified strategy.
        Logs all merge decisions in SharedBlackboard.
        Supported strategies: 'last_write_wins', 'priority', 'agent_weighted'.
        """
        merged = None
        merge_info = {
            'group_id': group_id,
            'strategy': merge_strategy,
            'fragments': [f.fragment_id for f in fragments],
            'decisions': []
        }
        if merge_strategy == 'last_write_wins':
            # Use the result of the fragment with the latest update timestamp
            latest = max(fragments, key=lambda f: getattr(f, 'updated_at', 0))
            merged = latest.result
            merge_info['decisions'].append({'selected': latest.fragment_id, 'reason': 'last_write'})
        elif merge_strategy == 'priority':
            # Use a priority field in fragment.metadata if present
            prioritized = sorted(fragments, key=lambda f: f.metadata.get('priority', 0), reverse=True)
            merged = prioritized[0].result
            merge_info['decisions'].append({'selected': prioritized[0].fragment_id, 'reason': 'priority'})
        elif merge_strategy == 'agent_weighted':
            # Use agent_weight in fragment.metadata if present
            weighted = sorted(fragments, key=lambda f: f.metadata.get('agent_weight', 0), reverse=True)
            merged = weighted[0].result
            merge_info['decisions'].append({'selected': weighted[0].fragment_id, 'reason': 'agent_weight'})
        else:
            # Default: concatenate all results
            merged = [f.result for f in fragments]
            merge_info['decisions'].append({'selected': [f.fragment_id for f in fragments], 'reason': 'concat'})
        # Log merge decision
        self.shared_memory.log_merge_decision(group_id, merge_info)
        return merged

    def __init__(self, router, shared_memory, max_workers: int = 4):
        self.router = router
        self.shared_memory = shared_memory
        self.max_workers = max_workers
        self.lock = threading.Lock()
        self.dependency_graph = None
        print("[ENGINE INIT] ParallelExecutionEngine initialized")

    def execute(self, fragments: List[Any], dependency_graph: FragmentDependencyGraph, context: Optional[Dict[str, Any]] = None) -> List[Any]:
        print("[EXECUTE] Entered execute method")
        self.dependency_graph = dependency_graph  # Ensure diagnostics have access
        context = context or {}
        results = []
        futures = []
        print(f"[EXECUTE] Starting execution loop")
        print(f"[EXECUTE] About to create ThreadPoolExecutor")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            print(f"[EXECUTE] ThreadPoolExecutor created")
            while not dependency_graph.all_completed():
                print(f"[EXECUTE] Top of while loop, completed: {dependency_graph.completed}")
                print("[EXECUTE] About to call get_ready_fragments")
                ready = dependency_graph.get_ready_fragments()
                print(f"[EXECUTE] get_ready_fragments returned: {[f.fragment_id for f in ready]}")
                if not ready:
                    print(f"[EXECUTE] No ready fragments, breaking loop (possible deadlock or waiting)")
                    break  # Deadlock or waiting for external completion
                for fragment in ready:
                    print(f"[EXECUTE] Submitting fragment {fragment.fragment_id} for execution")
                    futures.append(executor.submit(self._execute_fragment, fragment, context, dependency_graph))
                for future in as_completed(futures):
                    result = future.result()
                    print(f"[EXECUTE] Fragment {result.fragment_id} finished with state {result.state}")
                    results.append(result)
                    print(f"[EXECUTE] Dependency graph completed: {dependency_graph.completed}")
        print(f"[EXECUTE] Execution loop finished. Returning results.")
        return results

    def _execute_fragment(self, fragment, context, dependency_graph):
        try:
            print(f"[_EXECUTE_FRAGMENT] ENTER: {fragment.fragment_id}")
            # Mark as in progress
            fragment.update_state("in_progress")
            print(f"[_EXECUTE_FRAGMENT] State set to in_progress for {fragment.fragment_id}")
            self.log_fragment_states([fragment.fragment_id])
            print(f"[_EXECUTE_FRAGMENT] SKIPPING AgentMessage import and instantiation for {fragment.fragment_id}")
            # from src.agent_messaging import AgentMessage
            # frag_dict = fragment.to_dict()
            # msg = AgentMessage(
            #     sender="parallel_execution_engine",
            #     receiver=fragment.assigned_agent,
            #     intent="execute_fragment",
            #     payload={"fragment": frag_dict, "context": context},
            #     metadata={"plan_id": fragment.parent_plan_id, "fragment_id": fragment.fragment_id}
            # )
            # response = self.router.route_message(msg)
            print(f"[_EXECUTE_FRAGMENT] Would call route_message here for {fragment.fragment_id}")
            response = type('Resp', (), {'intent': 'response', 'payload': {'result': f"SIM:{fragment.fragment_id}"}, 'metadata': {}})()
            print(f"[_EXECUTE_FRAGMENT] Simulated response for {fragment.fragment_id}: {response}")
            print(f"[_EXECUTE_FRAGMENT] About to acquire lock for {fragment.fragment_id}")
            with self.lock:
                print(f"[_EXECUTE_FRAGMENT] Acquired lock for {fragment.fragment_id}")
                if response and response.payload:
                    print(f"[_EXECUTE_FRAGMENT] Updating state to completed for {fragment.fragment_id}")
                    fragment.update_state("completed", result=response.payload.get("result"))
                else:
                    print(f"[_EXECUTE_FRAGMENT] Updating state to failed for {fragment.fragment_id}")
                    fragment.update_state("failed", result=None)
                print(f"[_EXECUTE_FRAGMENT] Updating shared memory for {fragment.fragment_id}")
                self.shared_memory.update(f"fragment:{fragment.fragment_id}", fragment.to_dict(), author="parallel_execution_engine", metadata={"plan_id": fragment.parent_plan_id, "assigned_agent": fragment.assigned_agent})
                print(f"[_EXECUTE_FRAGMENT] Marking completed in dep graph for {fragment.fragment_id}")
                dependency_graph.mark_completed(fragment.fragment_id)
                print(f"[_EXECUTE_FRAGMENT] State after completion for {fragment.fragment_id}")
                self.log_fragment_states([fragment.fragment_id])
            print(f"[_EXECUTE_FRAGMENT] EXIT: {fragment.fragment_id} state={fragment.state}")
            return fragment
        except Exception as e:
            print(f"[_EXECUTE_FRAGMENT] Exception in fragment {fragment.fragment_id}: {e}")
            raise
    def __init__(self, router, shared_memory, max_workers: int = 4):
        self.router = router
        self.shared_memory = shared_memory
        self.max_workers = max_workers
        self.lock = threading.Lock()

    def execute(self, fragments: List[Any], dependency_graph: FragmentDependencyGraph, context: Optional[Dict[str, Any]] = None) -> List[Any]:
        context = context or {}
        results = []
        futures = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while not dependency_graph.all_completed():
                ready = dependency_graph.get_ready_fragments()
                if not ready:
                    break  # Deadlock or waiting for external completion
                for fragment in ready:
                    futures.append(executor.submit(self._execute_fragment, fragment, context, dependency_graph))
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
        return results

    def _execute_fragment(self, fragment, context, dependency_graph):
        # Mark as in progress
        fragment.update_state("in_progress")
        from src.agent_messaging import AgentMessage
        msg = AgentMessage(
            sender="parallel_execution_engine",
            receiver=fragment.assigned_agent,
            intent="execute_fragment",
            payload={"fragment": fragment.to_dict(), "context": context},
            metadata={"plan_id": fragment.parent_plan_id, "fragment_id": fragment.fragment_id}
        )
        response = self.router.route_message(msg)
        with self.lock:
            if response and response.payload:
                fragment.update_state("completed", result=response.payload.get("result"))
            else:
                fragment.update_state("failed", result=None)
            self.shared_memory.update(f"fragment:{fragment.fragment_id}", fragment.to_dict(), author="parallel_execution_engine", metadata={"plan_id": fragment.parent_plan_id, "assigned_agent": fragment.assigned_agent})
            dependency_graph.mark_completed(fragment.fragment_id)
        return fragment
