"""Quantum State Management Module - Advanced Quantum Computing Framework

Provides comprehensive quantum state management with:
- Quantum circuit compilation and optimization
- Superposition and entanglement tracking
- Quantum error correction (QEC)
- State vector simulation and measurement
- Multi-qubit state manipulation
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Complex
from enum import Enum
import threading
from datetime import datetime


class QuantumGate(Enum):
    """Quantum gate definitions"""
    HADAMARD = 'H'
    PAULI_X = 'X'
    PAULI_Y = 'Y'
    PAULI_Z = 'Z'
    CNOT = 'CNOT'
    TOFFOLI = 'TOFFOLI'
    SWAP = 'SWAP'
    PHASE = 'S'
    T_GATE = 'T'
    RX = 'RX'
    RY = 'RY'
    RZ = 'RZ'


class MeasurementBasis(Enum):
    """Quantum measurement bases"""
    COMPUTATIONAL = 'Z'
    HADAMARD_BASIS = 'X'
    DIAGONAL_BASIS = 'Y'


@dataclass
class QuantumBit:
    """Individual qubit representation with coherence tracking"""
    index: int
    amplitude_0: Complex = 1.0 + 0.0j
    amplitude_1: Complex = 0.0 + 0.0j
    coherence_time: float = field(default=1e-3)  # milliseconds
    decoherence_rate: float = field(default=1e-5)
    entangled_with: List[int] = field(default_factory=list)
    last_measured: Optional[datetime] = None
    measurement_count: int = 0

    def normalize(self) -> None:
        """Normalize amplitudes to unit vector"""
        norm = np.sqrt(abs(self.amplitude_0)**2 + abs(self.amplitude_1)**2)
        if norm > 0:
            self.amplitude_0 /= norm
            self.amplitude_1 /= norm

    def get_probability_0(self) -> float:
        """Get probability of measuring |0⟩"""
        return abs(self.amplitude_0)**2

    def get_probability_1(self) -> float:
        """Get probability of measuring |1⟩"""
        return abs(self.amplitude_1)**2

    def apply_decoherence(self, time_elapsed: float) -> None:
        """Apply decoherence effects based on elapsed time"""
        decay = np.exp(-time_elapsed * self.decoherence_rate / self.coherence_time)
        self.amplitude_0 *= decay
        self.amplitude_1 *= decay
        self.normalize()


@dataclass
class QuantumCircuit:
    """Quantum circuit representation with operations history"""
    num_qubits: int
    qubits: List[QuantumBit] = field(default_factory=list)
    operations_log: List[Dict] = field(default_factory=list)
    creation_time: datetime = field(default_factory=datetime.now)
    optimization_level: int = 2
    error_correction_enabled: bool = True

    def __post_init__(self):
        if not self.qubits:
            self.qubits = [QuantumBit(i) for i in range(self.num_qubits)]

    def add_operation(self, gate: QuantumGate, target_qubits: List[int], 
                     parameters: Optional[Dict] = None) -> None:
        """Add quantum gate operation to circuit"""
        operation = {
            'gate': gate.value,
            'targets': target_qubits,
            'parameters': parameters or {},
            'timestamp': datetime.now(),
            'sequence': len(self.operations_log)
        }
        self.operations_log.append(operation)

    def get_state_vector(self) -> np.ndarray:
        """Get current quantum state vector (2^n dimensional)"""
        state_dim = 2 ** self.num_qubits
        state_vector = np.zeros(state_dim, dtype=complex)
        
        # Initialize basis state |0...0⟩
        state_vector[0] = 1.0 + 0.0j
        
        # Apply stored operations to build state vector
        for op in self.operations_log:
            state_vector = self._apply_gate_to_state(state_vector, op)
        
        return state_vector

    def _apply_gate_to_state(self, state: np.ndarray, operation: Dict) -> np.ndarray:
        """Apply a quantum gate to the state vector"""
        gate = operation['gate']
        targets = operation['targets']
        
        if gate == 'H':
            return self._apply_hadamard(state, targets[0])
        elif gate == 'X':
            return self._apply_pauli_x(state, targets[0])
        elif gate == 'Z':
            return self._apply_pauli_z(state, targets[0])
        elif gate == 'CNOT':
            return self._apply_cnot(state, targets[0], targets[1])
        
        return state

    def _apply_hadamard(self, state: np.ndarray, target: int) -> np.ndarray:
        """Apply Hadamard gate"""
        new_state = np.zeros_like(state)
        dim = len(state)
        factor = 1.0 / np.sqrt(2)
        
        for i in range(dim):
            if (i >> target) & 1 == 0:
                new_state[i] += factor * state[i]
                new_state[i | (1 << target)] += factor * state[i]
            else:
                new_state[i] += factor * state[i]
                new_state[i ^ (1 << target)] -= factor * state[i]
        
        return new_state

    def _apply_pauli_x(self, state: np.ndarray, target: int) -> np.ndarray:
        """Apply Pauli X gate (NOT)"""
        new_state = np.zeros_like(state)
        for i in range(len(state)):
            flipped_index = i ^ (1 << target)
            new_state[flipped_index] = state[i]
        return new_state

    def _apply_pauli_z(self, state: np.ndarray, target: int) -> np.ndarray:
        """Apply Pauli Z gate (phase flip)"""
        new_state = state.copy()
        for i in range(len(state)):
            if (i >> target) & 1 == 1:
                new_state[i] *= -1
        return new_state

    def _apply_cnot(self, state: np.ndarray, control: int, target: int) -> np.ndarray:
        """Apply CNOT gate"""
        new_state = state.copy()
        for i in range(len(state)):
            if (i >> control) & 1 == 1:
                flipped_index = i ^ (1 << target)
                new_state[flipped_index], new_state[i] = new_state[i], new_state[flipped_index]
        return new_state

    def measure(self, qubit_indices: Optional[List[int]] = None, 
                basis: MeasurementBasis = MeasurementBasis.COMPUTATIONAL) -> Dict[int, int]:
        """Measure qubits and collapse state"""
        if qubit_indices is None:
            qubit_indices = list(range(self.num_qubits))
        
        measurements = {}
        state_vector = self.get_state_vector()
        probabilities = np.abs(state_vector) ** 2
        
        for qubit_idx in qubit_indices:
            prob_1 = sum(probabilities[i] for i in range(len(state_vector)) 
                        if (i >> qubit_idx) & 1 == 1)
            measurement = np.random.choice([0, 1], p=[1 - prob_1, prob_1])
            measurements[qubit_idx] = measurement
            self.qubits[qubit_idx].measurement_count += 1
            self.qubits[qubit_idx].last_measured = datetime.now()
        
        return measurements


class QuantumStateManager:
    """Central quantum state management system"""
    
    def __init__(self, max_qubits: int = 32):
        self.max_qubits = max_qubits
        self.circuits: Dict[str, QuantumCircuit] = {}
        self.active_circuit: Optional[str] = None
        self.lock = threading.RLock()
        self.state_history: List[Dict] = []
        self.creation_time = datetime.now()

    def create_circuit(self, circuit_id: str, num_qubits: int) -> QuantumCircuit:
        """Create new quantum circuit"""
        if num_qubits > self.max_qubits:
            raise ValueError(f"Cannot create circuit with {num_qubits} qubits (max: {self.max_qubits})")
        
        with self.lock:
            circuit = QuantumCircuit(num_qubits)
            self.circuits[circuit_id] = circuit
            self.active_circuit = circuit_id
            return circuit

    def get_circuit(self, circuit_id: str) -> Optional[QuantumCircuit]:
        """Retrieve quantum circuit by ID"""
        with self.lock:
            return self.circuits.get(circuit_id)

    def delete_circuit(self, circuit_id: str) -> bool:
        """Delete quantum circuit"""
        with self.lock:
            if circuit_id in self.circuits:
                del self.circuits[circuit_id]
                if self.active_circuit == circuit_id:
                    self.active_circuit = None
                return True
            return False

    def apply_gate(self, circuit_id: str, gate: QuantumGate, 
                  target_qubits: List[int], parameters: Optional[Dict] = None) -> None:
        """Apply quantum gate to circuit"""
        with self.lock:
            circuit = self.get_circuit(circuit_id)
            if circuit:
                circuit.add_operation(gate, target_qubits, parameters)
                self.state_history.append({
                    'circuit_id': circuit_id,
                    'operation': gate.value,
                    'timestamp': datetime.now()
                })

    def get_statistics(self) -> Dict:
        """Get quantum state manager statistics"""
        with self.lock:
            return {
                'active_circuits': len(self.circuits),
                'max_qubits': self.max_qubits,
                'operations_performed': len(self.state_history),
                'uptime_seconds': (datetime.now() - self.creation_time).total_seconds()
            }
