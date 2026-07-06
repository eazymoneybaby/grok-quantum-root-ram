"""Grok Quantum Root RAM - Quantum Computing and AGI Control Framework

Package providing advanced quantum state management, AGI control simulation,
iOS terminal bridge integration, and root skills execution.

Modules:
    quantum_state_management: Quantum circuit and state management
    agi_control_simulation: AGI decision making and control
    ios_libterm_bridge: iOS terminal integration and device management
    root_skills_execution: Root-level skill execution and authorization
"""

__version__ = '1.0.0'
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
]
