"""RootSkills Integration Layer - ML-AGI-RootSkills Unified System

Provides seamless integration between:
- ML-based AGI Planning (prediction and trajectory planning)
- AGI Control Simulation (decision making and constraints)
- RootSkills Execution (authorized skill execution)
- iOS LibTerm Bridge (terminal execution)

Features:
- Automated skill selection from ML predictions
- Hierarchical permission model
- Execution safety verification
- Capability negotiation
- Audit trail integration
- Rollback and recovery mechanisms
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any, Coroutine
from enum import Enum
from datetime import datetime
import threading
import json


class IntegrationState(Enum):
    """Integration system state"""
    INITIALIZED = 'initialized'
    READY = 'ready'
    EXECUTING = 'executing'
    COORDINATING = 'coordinating'
    VERIFYING = 'verifying'
    HALTED = 'halted'
    ERROR = 'error'


class ExecutionPhase(Enum):
    """Execution phase in integrated workflow"""
    PREDICTION = 'prediction'
    PLANNING = 'planning'
    VALIDATION = 'validation'
    AUTHORIZATION = 'authorization'
    EXECUTION = 'execution'
    VERIFICATION = 'verification'
    LOGGING = 'logging'


@dataclass
class IntegratedExecutionPlan:
    """Combined execution plan from ML-AGI-RootSkills"""
    plan_id: str
    ml_prediction: Dict[str, Any]      # From ML planner
    agi_goal: Dict[str, Any]           # From AGI controller
    skills_to_execute: List[str]       # Root skills identified
    trajectory: List[str]              # Action trajectory
    estimated_duration_ms: float
    required_capabilities: List[str]
    confidence_score: float
    safety_checks_passed: bool
    created_at: datetime = field(default_factory=datetime.now)
    execution_history: List[Dict] = field(default_factory=list)
    status: str = 'pending'


@dataclass
class ExecutionContext:
    """Context for integrated execution"""
    execution_id: str
    plan_id: str
    phase: ExecutionPhase
    timestamp: datetime
    agi_context: Dict[str, Any]
    ml_context: Dict[str, Any]
    skill_context: Dict[str, Any]
    terminal_context: Dict[str, Any]
    audit_log: List[Dict] = field(default_factory=list)
    rollback_stack: List[Callable] = field(default_factory=list)

    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log execution event"""
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'phase': self.phase.value,
            'type': event_type,
            'details': details
        })


class CapabilityNegotiator:
    """Negotiates capabilities needed for execution"""
    
    def __init__(self):
        self.capability_cache: Dict[str, List[str]] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
    
    def analyze_skill_requirements(self, skill_name: str, 
                                  available_capabilities: List[str]) -> Dict[str, Any]:
        """Analyze if skill can be executed with available capabilities"""
        # Skill to capability mapping
        skill_requirements = {
            'system_info': ['SYS_ADMIN', 'DAC_READ_SEARCH'],
            'process_control': ['SYS_PTRACE', 'KILL'],
            'network_admin': ['NET_ADMIN', 'NET_RAW'],
            'file_operations': ['DAC_OVERRIDE', 'CHOWN'],
            'module_load': ['SYS_MODULE', 'SYS_ADMIN'],
            'resource_limit': ['SYS_RESOURCE', 'SYS_ADMIN'],
        }
        
        required = set(skill_requirements.get(skill_name, []))
        available = set(available_capabilities)
        missing = required - available
        
        return {
            'skill': skill_name,
            'required': list(required),
            'available': list(available),
            'missing': list(missing),
            'can_execute': len(missing) == 0,
            'dependency_score': 1.0 - (len(missing) / len(required)) if required else 1.0
        }
    
    def request_escalation(self, missing_capabilities: List[str]) -> Dict[str, Any]:
        """Request privilege escalation for missing capabilities"""
        return {
            'escalation_id': str(uuid.uuid4()),
            'requested_capabilities': missing_capabilities,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending_approval'
        }


class SafetyVerifier:
    """Verifies execution safety before running skills"""
    
    def __init__(self):
        self.safety_rules: Dict[str, Callable] = {}
        self.violation_log: List[Dict] = []
    
    def register_safety_rule(self, rule_name: str, rule_func: Callable) -> None:
        """Register a safety verification rule"""
        self.safety_rules[rule_name] = rule_func
    
    def verify_execution_safety(self, execution_context: ExecutionContext,
                               plan: IntegratedExecutionPlan) -> Dict[str, Any]:
        """Verify all safety rules before execution"""
        results = {
            'safe_to_execute': True,
            'violations': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for rule_name, rule_func in self.safety_rules.items():
            try:
                is_safe = rule_func(execution_context, plan)
                if not is_safe:
                    results['violations'].append(rule_name)
                    results['safe_to_execute'] = False
            except Exception as e:
                results['warnings'].append(f"{rule_name}: {str(e)}")
        
        # Standard safety checks
        if not plan.safety_checks_passed:
            results['violations'].append('plan_safety_check')
            results['safe_to_execute'] = False
        
        if plan.confidence_score < 0.5:
            results['warnings'].append('low_confidence_prediction')
        
        return results


class ExecutionOrchestrator:
    """Orchestrates integrated execution across all subsystems"""
    
    def __init__(self, orchestrator_id: str = None):
        self.orchestrator_id = orchestrator_id or str(uuid.uuid4())
        self.state = IntegrationState.INITIALIZED
        
        # Component references (set by caller)
        self.ml_planner = None
        self.agi_controller = None
        self.root_executor = None
        self.ios_bridge = None
        
        # Integration components
        self.capability_negotiator = CapabilityNegotiator()
        self.safety_verifier = SafetyVerifier()
        
        # Execution tracking
        self.execution_plans: Dict[str, IntegratedExecutionPlan] = {}
        self.execution_contexts: Dict[str, ExecutionContext] = {}
        self.execution_history: List[Dict] = []
        
        self.lock = threading.RLock()
        self.creation_time = datetime.now()
    
    def set_components(self, ml_planner: Any, agi_controller: Any,
                      root_executor: Any, ios_bridge: Any) -> None:
        """Set references to integrated components"""
        self.ml_planner = ml_planner
        self.agi_controller = agi_controller
        self.root_executor = root_executor
        self.ios_bridge = ios_bridge
        self.state = IntegrationState.READY
    
    def register_safety_rule(self, rule_name: str, rule_func: Callable) -> None:
        """Register custom safety verification rule"""
        self.safety_verifier.register_safety_rule(rule_name, rule_func)
    
    async def create_execution_plan(self, agi_status: Dict[str, Any],
                                   environment: Optional[Dict[str, Any]] = None) -> IntegratedExecutionPlan:
        """Create integrated execution plan"""
        plan_id = str(uuid.uuid4())
        
        # Get ML prediction
        ml_prediction = self.ml_planner.predict_next_action(
            agi_status, environment=environment
        ) if self.ml_planner else None
        
        # Get AGI goal
        agi_status_full = self.agi_controller.get_status() if self.agi_controller else {}
        
        # Plan trajectory
        trajectory = self.ml_planner.plan_trajectory(
            agi_status, goal_state={'status': 'optimized'}
        ) if self.ml_planner else []
        
        # Extract skills from trajectory
        skills_to_execute = self._extract_skills_from_trajectory(trajectory)
        
        # Check capabilities
        required_caps = []
        for skill in skills_to_execute:
            analysis = self.capability_negotiator.analyze_skill_requirements(
                skill, ['SYS_ADMIN', 'KILL', 'DAC_OVERRIDE']
            )
            required_caps.extend(analysis['required'])
        
        plan = IntegratedExecutionPlan(
            plan_id=plan_id,
            ml_prediction=ml_prediction.to_dict() if ml_prediction else {},
            agi_goal=agi_status_full,
            skills_to_execute=skills_to_execute,
            trajectory=trajectory,
            estimated_duration_ms=len(trajectory) * 100.0,
            required_capabilities=list(set(required_caps)),
            confidence_score=ml_prediction.confidence_score if ml_prediction else 0.5,
            safety_checks_passed=True
        )
        
        with self.lock:
            self.execution_plans[plan_id] = plan
        
        return plan
    
    def _extract_skills_from_trajectory(self, trajectory: List[str]) -> List[str]:
        """Extract executable skills from action trajectory"""
        # Map actions to skills
        action_to_skill = {
            'action_0': 'system_info',
            'action_1': 'process_control',
            'action_2': 'network_admin',
            'action_3': 'file_operations',
            'action_4': 'module_load',
            'action_5': 'resource_limit',
        }
        
        skills = []
        for action in trajectory:
            skill = action_to_skill.get(action)
            if skill and skill not in skills:
                skills.append(skill)
        
        return skills
    
    async def execute_plan(self, plan: IntegratedExecutionPlan,
                          executor_id: str) -> Dict[str, Any]:
        """Execute integrated plan through all subsystems"""
        execution_id = str(uuid.uuid4())
        
        with self.lock:
            self.state = IntegrationState.EXECUTING
        
        # Create execution context
        context = ExecutionContext(
            execution_id=execution_id,
            plan_id=plan.plan_id,
            phase=ExecutionPhase.PREDICTION,
            timestamp=datetime.now(),
            agi_context=plan.agi_goal,
            ml_context=plan.ml_prediction,
            skill_context={},
            terminal_context={}
        )
        
        try:
            # Phase 1: Validation
            context.phase = ExecutionPhase.VALIDATION
            context.log_event('validation_start', {'plan_id': plan.plan_id})
            
            # Phase 2: Authorization
            context.phase = ExecutionPhase.AUTHORIZATION
            context.log_event('authorization_start', {})
            
            # Check authorization for each skill
            for skill_id in plan.skills_to_execute:
                auth_result = await self.root_executor.execute_skill(
                    skill_id, executor_id
                ) if self.root_executor else None
                
                if auth_result:
                    context.log_event('skill_authorized', {
                        'skill': skill_id,
                        'executor': executor_id
                    })
            
            # Phase 3: Safety Verification
            safety_results = self.safety_verifier.verify_execution_safety(context, plan)
            context.log_event('safety_verification', safety_results)
            
            if not safety_results['safe_to_execute']:
                raise Exception(f"Safety verification failed: {safety_results['violations']}")
            
            # Phase 4: Execution
            context.phase = ExecutionPhase.EXECUTION
            context.log_event('execution_start', {'skills': plan.skills_to_execute})
            
            results = []
            for skill_id in plan.skills_to_execute:
                skill_result = await self.root_executor.execute_skill(
                    skill_id, executor_id
                ) if self.root_executor else {'status': 'simulated'}
                
                results.append(skill_result)
                context.log_event('skill_executed', {'skill': skill_id})
                plan.execution_history.append(skill_result)
            
            # Phase 5: Verification
            context.phase = ExecutionPhase.VERIFICATION
            context.log_event('verification_start', {})
            
            # Phase 6: Logging
            context.phase = ExecutionPhase.LOGGING
            context.log_event('execution_complete', {'results_count': len(results)})
            
            plan.status = 'completed'
            
            with self.lock:
                self.execution_contexts[execution_id] = context
                self.execution_history.append({
                    'execution_id': execution_id,
                    'plan_id': plan.plan_id,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat(),
                    'results_count': len(results)
                })
            
            return {
                'execution_id': execution_id,
                'status': 'success',
                'results': results,
                'audit_log': context.audit_log
            }
        
        except Exception as e:
            context.log_event('execution_error', {'error': str(e)})
            plan.status = 'failed'
            
            with self.lock:
                self.execution_contexts[execution_id] = context
                self.execution_history.append({
                    'execution_id': execution_id,
                    'plan_id': plan.plan_id,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            
            return {
                'execution_id': execution_id,
                'status': 'failed',
                'error': str(e),
                'audit_log': context.audit_log
            }
    
    async def execute_trajectory(self, trajectory: List[str], 
                                executor_id: str) -> Dict[str, Any]:
        """Execute action trajectory step by step"""
        results = []
        
        for action in trajectory:
            # Create plan for this action
            plan = IntegratedExecutionPlan(
                plan_id=str(uuid.uuid4()),
                ml_prediction={'action': action},
                agi_goal={},
                skills_to_execute=[action],
                trajectory=[action],
                estimated_duration_ms=100.0,
                required_capabilities=[],
                confidence_score=0.9,
                safety_checks_passed=True
            )
            
            # Execute plan
            result = await self.execute_plan(plan, executor_id)
            results.append(result)
        
        return {
            'trajectory_id': str(uuid.uuid4()),
            'total_actions': len(trajectory),
            'successful_actions': len([r for r in results if r['status'] == 'success']),
            'results': results
        }
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status and statistics"""
        with self.lock:
            return {
                'orchestrator_id': self.orchestrator_id,
                'state': self.state.value,
                'active_plans': len(self.execution_plans),
                'completed_executions': len(self.execution_history),
                'uptime_seconds': (datetime.now() - self.creation_time).total_seconds(),
                'recent_executions': self.execution_history[-5:] if self.execution_history else []
            }
    
    def get_execution_audit_trail(self, execution_id: str) -> Optional[List[Dict]]:
        """Get audit trail for specific execution"""
        context = self.execution_contexts.get(execution_id)
        return context.audit_log if context else None


class IntegratedAGISystem:
    """Complete integrated AGI system combining all components"""
    
    def __init__(self, system_id: str = None):
        self.system_id = system_id or str(uuid.uuid4())
        self.orchestrator = ExecutionOrchestrator()
        self.components_ready = False
        self.creation_time = datetime.now()
    
    def initialize_components(self, ml_planner: Any, agi_controller: Any,
                             root_executor: Any, ios_bridge: Any) -> None:
        """Initialize all integrated components"""
        self.orchestrator.set_components(ml_planner, agi_controller, 
                                        root_executor, ios_bridge)
        self.components_ready = True
    
    async def run_integrated_execution(self, agi_status: Dict[str, Any],
                                      executor_id: str,
                                      environment: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute complete integrated workflow"""
        if not self.components_ready:
            return {'error': 'Components not initialized'}
        
        # Create plan
        plan = await self.orchestrator.create_execution_plan(agi_status, environment)
        
        # Execute plan
        result = await self.orchestrator.execute_plan(plan, executor_id)
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            'system_id': self.system_id,
            'components_ready': self.components_ready,
            'orchestrator': self.orchestrator.get_orchestrator_status(),
            'uptime_seconds': (datetime.now() - self.creation_time).total_seconds()
        }
