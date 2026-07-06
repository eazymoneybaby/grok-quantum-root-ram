"""Grok Quantum Root RAM - Quantum Computing and AGI Control Framework

Package providing advanced quantum state management, AGI control simulation,
iOS terminal bridge integration, root skills execution, ML-based planning,
and integrated AGI execution system.

Modules:
    quantum_state_management: Quantum circuit and state management
    agi_control_simulation: AGI decision making and control
    ios_libterm_bridge: iOS terminal integration and device management
    root_skills_execution: Root-level skill execution and authorization
    ml_agi_planning: ML-based AGI planning and decision optimization
    rootskills_integration: Integrated ML-AGI-RootSkills execution system
"""

__version__ = '2.0.0'
__author__ = 'eazymoneybaby'
__license__ = 'MIT'

from .quantum_state_management import (
    QuantumStateManager,
    QuantumCircuit,
    QuantumBit,
    QuantumGate,
    MeasurementBasis,
)

from .agi_control_simulation import (
    AGIController,
    AGIState,
    Goal,
    Constraint,
    ConstraintLevel,
    GoalPriority,
    DecisionContext,
    ActionValidator,
    SafetyValidator,
    ResourceValidator,
)

from .ios_libterm_bridge import (
    IOSLibTermBridge,
    TerminalProcess,
    IOSDeviceInfo,
    IOSDeviceType,
    ProcessState,
)

from .root_skills_execution import (
    RootSkillsExecutor,
    SkillDefinition,
    ExecutionContext,
    SkillCapability,
    SkillLevel,
    ExecutionStatus,
    SkillAuthorizationManager,
    CapabilityValidator,
)

from .ml_agi_planning import (
    MLAGIPlanner,
    SimpleNeuralNetwork,
    ReinforcementLearningAgent,
    FeatureExtractor,
    PredictionResult,
    TrainingMetrics,
    LearningStrategy,
    OptimizationAlgorithm,
)

from .rootskills_integration import (
    ExecutionOrchestrator,
    IntegratedAGISystem,
    IntegratedExecutionPlan,
    ExecutionContext as IntegrationExecutionContext,
    CapabilityNegotiator,
    SafetyVerifier,
    IntegrationState,
    ExecutionPhase,
)

__all__ = [
    # Quantum State Management
    'QuantumStateManager',
    'QuantumCircuit',
    'QuantumBit',
    'QuantumGate',
    'MeasurementBasis',
    
    # AGI Control
    'AGIController',
    'AGIState',
    'Goal',
    'Constraint',
    'ConstraintLevel',
    'GoalPriority',
    'DecisionContext',
    'ActionValidator',
    'SafetyValidator',
    'ResourceValidator',
    
    # iOS LibTerm Bridge
    'IOSLibTermBridge',
    'TerminalProcess',
    'IOSDeviceInfo',
    'IOSDeviceType',
    'ProcessState',
    
    # Root Skills Execution
    'RootSkillsExecutor',
    'SkillDefinition',
    'ExecutionContext',
    'SkillCapability',
    'SkillLevel',
    'ExecutionStatus',
    'SkillAuthorizationManager',
    'CapabilityValidator',
    
    # ML-Based Planning
    'MLAGIPlanner',
    'SimpleNeuralNetwork',
    'ReinforcementLearningAgent',
    'FeatureExtractor',
    'PredictionResult',
    'TrainingMetrics',
    'LearningStrategy',
    'OptimizationAlgorithm',
    
    # Integrated System
    'ExecutionOrchestrator',
    'IntegratedAGISystem',
    'IntegratedExecutionPlan',
    'IntegrationExecutionContext',
    'CapabilityNegotiator',
    'SafetyVerifier',
    'IntegrationState',
    'ExecutionPhase',
]
