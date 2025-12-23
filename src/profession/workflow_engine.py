"""
WorkflowEngine: Plans, executes, and reflects on multi-step reasoning tasks.
"""
from typing import List, Dict, Any
from src.profession.reflection_engine import ReflectionEngine


from src.delegation.classifier import TaskClassifier
from src.delegation.rules_engine import DelegationRulesEngine
from src.delegation.confidence import DelegationConfidence

class WorkflowEngine:
    def execute_distributed_plan(self, plan: Dict[str, Any], fragments: List[Any], context: Dict[str, Any] = None, parallel: bool = False) -> Dict[str, Any]:
        """
        Execute distributed plan fragments using the router's orchestration logic.
        Supports sequential or parallel execution, branching, merging, and recursion/depth checks.
        """
        context = context or {}
        # Recursion/depth protection (simple example)
        max_depth = context.get('max_delegation_depth', 5)
        current_depth = context.get('delegation_depth', 0)
        if current_depth > max_depth:
            return {'error': 'Max delegation depth exceeded', 'plan_id': plan.get('plan_id')}
        # Detect if fragments are parallelizable (if any have dependencies, use parallel)
        has_dependencies = any(getattr(f, 'dependencies', None) for f in fragments)
        if parallel or has_dependencies:
            # Use router's parallel dispatch
            fragment_results = self.router.dispatch_parallel_fragments(fragments, self.shared_memory, context)
            merged_result = self.merge_distributed_results([{'response': f} for f in fragment_results])
        else:
            fragment_results = self.router.orchestrate_distributed_plan(plan, fragments, context)
            merged_result = self.merge_distributed_results(fragment_results['fragment_results'])
        # Log execution state
        self.shared_memory.write(f"plan_execution:{plan.get('plan_id')}", {
            'plan': plan,
            'fragment_results': fragment_results,
            'merged_result': merged_result,
            'context': context
        }, author='workflow_engine', metadata={'plan_id': plan.get('plan_id')})
        return {
            'plan_id': plan.get('plan_id'),
            'fragment_results': fragment_results,
            'merged_result': merged_result
        }

    def merge_distributed_results(self, fragment_results: List[Dict[str, Any]]) -> Any:
        """
        Merge results from distributed plan fragments (simple concatenation, can be extended).
        """
        outputs = []
        for frag in fragment_results:
            response = frag.get('response')
            if response and hasattr(response, 'payload'):
                outputs.append(response.payload.get('result') or response.payload)
        return outputs

    def __init__(self, agent, llm_provider, router=None, rules_engine=None, shared_memory=None,
                 enable_critique=False, enable_consensus=False, enable_debate=False, enable_cross_reflection=False):
        self.agent = agent  # The agent whose reasoning capabilities are used for steps
        self.llm = llm_provider
        self.reflection = ReflectionEngine(llm_provider)
        self.router = router
        self.classifier = TaskClassifier()
        self.rules_engine = rules_engine or DelegationRulesEngine(
            agent_map={
                'planning': 'planning_agent',
                'writing': 'writing_agent',
                'research': 'research_agent',
                'critique': 'critique_agent',
                'alignment': 'persona_alignment_agent',
            },
            fallback_agent=self.agent.user_id if hasattr(self.agent, 'user_id') else None
        )
        # Consensus, Critique, Debate, Cross-Reflection modules
        from src.consensus.critique_loop import CritiqueLoop
        from src.consensus.consensus_engine import ConsensusEngine
        from src.consensus.debate_pattern import DebatePattern
        from src.profession.cross_agent_reflection import CrossAgentReflectionEngine
        from src.shared_memory import SharedBlackboard
        self.shared_memory = shared_memory or SharedBlackboard()
        self.critique_loop = CritiqueLoop(self.router, self.shared_memory)
        self.consensus_engine = ConsensusEngine(self.shared_memory)
        self.debate_pattern = DebatePattern(self.router, self.shared_memory)
        self.cross_reflection = CrossAgentReflectionEngine(llm_provider)
        # Feature toggles
        self.enable_critique = enable_critique
        self.enable_consensus = enable_consensus
        self.enable_debate = enable_debate
        self.enable_cross_reflection = enable_cross_reflection

    def plan_generation(self, user_request: str) -> List[str]:
        """
        Break a user request into a sequence of actionable steps using LLM.
        Returns a list of step descriptions.
        """
        prompt = f"""
Analyze the following user request and break it down into a step-by-step plan. Each step should be clear and actionable.

User Request:
{user_request}

Return a JSON list of steps.
"""
        messages = [
            {"role": "system", "content": "You are an expert planner for complex professional tasks."},
            {"role": "user", "content": prompt}
        ]
        steps_json = self.llm.generate(messages, temperature=0.2)
        import json
        try:
            steps = json.loads(steps_json)
            if isinstance(steps, list):
                return steps
        except Exception:
            pass
        # Fallback: treat as single-step if parsing fails
        return [user_request]

    def step_execution(self, steps: List[str], context: Dict[str, Any] = None, agent_map: Dict[int, str] = None,
                      critique_config: Dict = None, consensus_config: Dict = None, debate_config: Dict = None, cross_reflection_config: Dict = None) -> List[Dict[str, Any]]:
        """
        Execute each step in order, using Delegation Intelligence 2.0 for adaptive, multi-agent delegation.
        agent_map: Optional mapping from step index to agent_id for forced delegation.
        Returns a list of dicts: {step, output, reflection, refined_output, refinement_performed, reflection_scores, agent}
        """
        from src.agent_messaging import AgentMessage
        results = []
        context = context or {}
        agent_map = agent_map or {}
        # Propagate delegation_depth from context or message metadata if present
        incoming_depth = 0
        if 'delegation_depth' in context:
            incoming_depth = context['delegation_depth']
        elif 'metadata' in context and isinstance(context['metadata'], dict):
            incoming_depth = context['metadata'].get('delegation_depth', 0)
        for idx, step in enumerate(steps):
            # Classify the step
            task_type, clf_conf = self.classifier.classify_task(step)
            # Determine agent (forced by agent_map, or by rules engine)
            if idx in agent_map:
                delegate_agent = agent_map[idx]
            else:
                delegate_agent, rule_info = self.rules_engine.get_agent_for_task(task_type)
                if not delegate_agent:
                    delegate_agent = self.agent.user_id if hasattr(self.agent, 'user_id') else None
            # Estimate confidence
            agent_role = getattr(self.agent, 'role', None) or getattr(self.agent, 'agent_id', None) or 'unknown'
            confidence_level, confidence_score = DelegationConfidence.estimate_confidence(agent_role, task_type)
            # --- Step 1: Standard execution (delegation or local) ---
            if delegate_agent == agent_role and confidence_level != 'low':
                output = self.agent._reasoning_pipeline(step, conversation_history=context.get("history", []))
            else:
                # Delegate to the selected agent via router
                msg_metadata = {
                    "delegated_by": agent_role,
                    "delegation": {
                        "task_type": task_type,
                        "confidence": confidence_score,
                        "rule": rule_info.get('rule') if 'rule_info' in locals() else 'standard'
                    },
                    "delegation_depth": incoming_depth + 1
                }
                if 'trace_id' in context:
                    msg_metadata['trace_id'] = context['trace_id']
                from src.agent_messaging import AgentMessage
                msg = AgentMessage(
                    sender=agent_role,
                    receiver=delegate_agent,
                    intent="request",
                    payload={"user_request": step, "history": context.get("history", [])},
                    metadata=msg_metadata
                )
                context['delegation_depth'] = incoming_depth + 1
                response = self.router.route_message(msg) if self.router else None
                output = None
                if response and response.payload:
                    output = response.payload.get("output") or response.payload.get("result") or response.payload.get("plan") or response.payload.get("aligned_output") or response.payload.get("critique") or response.payload.get("results")
                if output is None:
                    output = self.agent._reasoning_pipeline(step, conversation_history=context.get("history", []))
            # --- Step 2: Critique Loop (optional) ---
            critique_trace = None
            if self.enable_critique and critique_config:
                critique_agents = critique_config.get('critique_agents', [])
                rounds = critique_config.get('rounds', 1)
                if critique_agents:
                    # Use first as producer, second as critique, third as refine (or fallback)
                    producer = critique_agents[0]
                    critique = critique_agents[1] if len(critique_agents) > 1 else producer
                    refine = critique_agents[2] if len(critique_agents) > 2 else producer
                    critique_result = self.critique_loop.run(
                        producer_agent=producer,
                        critique_agent=critique,
                        refine_agent=refine,
                        initial_input=output,
                        rounds=rounds,
                        context=context,
                        trace_id=context.get('trace_id'),
                        log=True
                    )
                    output = critique_result.get('final_output', output)
                    critique_trace = critique_result
            # --- Step 3: Reflection (always) ---
            eval_result = self.reflection.evaluate_response(output, getattr(self.agent, 'profession_schema', None)) if output else {}
            needs_refinement = eval_result.get("needs_refinement", False)
            if needs_refinement:
                refined = self.reflection.refine_response(output, getattr(self.agent, 'profession_schema', None), eval_result)
            else:
                refined = output
            refinement_performed = bool(eval_result.get("needs_refinement", False))
            # --- Step 4: Consensus (optional) ---
            consensus_trace = None
            if self.enable_consensus and consensus_config:
                agent_outputs = consensus_config.get('agent_outputs', [])
                strategy = consensus_config.get('strategy', 'majority')
                weights = consensus_config.get('weights')
                critiques = consensus_config.get('critiques')
                if agent_outputs:
                    consensus_result = self.consensus_engine.merge(
                        agent_outputs=agent_outputs,
                        strategy=strategy,
                        weights=weights,
                        critiques=critiques,
                        trace_id=context.get('trace_id'),
                        log=True
                    )
                    refined = consensus_result['consensus']
                    consensus_trace = consensus_result
            # --- Step 5: Debate (optional) ---
            debate_trace = None
            if self.enable_debate and debate_config:
                agent_ids = debate_config.get('agent_ids', [])
                topic = debate_config.get('topic', step)
                rounds = debate_config.get('rounds', 2)
                if agent_ids:
                    debate_result = self.debate_pattern.run(
                        agent_ids=agent_ids,
                        topic=topic,
                        rounds=rounds,
                        context=context,
                        trace_id=context.get('trace_id'),
                        log=True
                    )
                    debate_trace = debate_result
            # --- Step 6: Cross-Agent Reflection (optional) ---
            cross_reflection_trace = None
            if self.enable_cross_reflection and cross_reflection_config:
                outputs = cross_reflection_config.get('outputs', [])
                schemas = cross_reflection_config.get('schemas', [])
                if outputs and schemas:
                    cross_result = self.cross_reflection.reflect_on_outputs(
                        outputs=outputs,
                        schemas=schemas,
                        context=context
                    )
                    cross_reflection_trace = cross_result
            # Ensure refined_output is always a string for test compatibility
            if refined is None:
                refined = ""
            # Extract scores if present
            reflection_scores = {
                "clarity": eval_result.get("clarity"),
                "accuracy": eval_result.get("accuracy"),
                "completeness": eval_result.get("completeness"),
                "alignment": eval_result.get("alignment")
            }
            results.append({
                "step": step,
                "output": output,
                "reflection": eval_result,
                "refined_output": refined,
                "refinement_performed": refinement_performed,
                "reflection_scores": reflection_scores,
                "agent": delegate_agent,
                "critique_trace": critique_trace,
                "consensus_trace": consensus_trace,
                "debate_trace": debate_trace,
                "cross_reflection_trace": cross_reflection_trace
            })
            # Optionally, update context/history for next step
            context.setdefault("history", []).append({"role": "assistant", "content": refined})
        return results

    def assemble_final_output(self, step_results: List[Dict[str, Any]]) -> str:
        """
        Merge or assemble the step outputs into a final result.
        """
        # Simple concatenation for now; can be enhanced
        return "\n".join([r["refined_output"] for r in step_results])
