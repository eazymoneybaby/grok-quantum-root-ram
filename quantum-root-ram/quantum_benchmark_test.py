"""Benchmarking and Testing Framework - Comprehensive Quantum System Validation

Provides benchmarking capabilities for:
- Quantum circuit performance testing
- Error correction effectiveness measurement
- State fidelity tracking
- Protocol implementation validation
- Comparative analysis of error models
- Performance metrics collection
"""

import time
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Any, Tuple
from datetime import datetime
import uuid
import json


@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    benchmark_id: str
    name: str
    duration_seconds: float
    operations_performed: int
    throughput_ops_per_sec: float
    accuracy: float
    fidelity: float
    error_rate: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'benchmark_id': self.benchmark_id,
            'name': self.name,
            'duration_seconds': self.duration_seconds,
            'operations_performed': self.operations_performed,
            'throughput_ops_per_sec': self.throughput_ops_per_sec,
            'accuracy': self.accuracy,
            'fidelity': self.fidelity,
            'error_rate': self.error_rate,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results"""
    suite_id: str
    name: str
    results: List[BenchmarkResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def add_result(self, result: BenchmarkResult) -> None:
        """Add benchmark result to suite"""
        self.results.append(result)
    
    def get_average_accuracy(self) -> float:
        """Get average accuracy across all benchmarks"""
        if not self.results:
            return 0.0
        return np.mean([r.accuracy for r in self.results])
    
    def get_average_fidelity(self) -> float:
        """Get average fidelity"""
        if not self.results:
            return 0.0
        return np.mean([r.fidelity for r in self.results])
    
    def get_average_throughput(self) -> float:
        """Get average throughput"""
        if not self.results:
            return 0.0
        return np.mean([r.throughput_ops_per_sec for r in self.results])
    
    def get_total_duration(self) -> float:
        """Get total duration"""
        return sum(r.duration_seconds for r in self.results)
    
    def summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            'suite_id': self.suite_id,
            'name': self.name,
            'num_benchmarks': len(self.results),
            'total_duration_seconds': self.get_total_duration(),
            'avg_accuracy': self.get_average_accuracy(),
            'avg_fidelity': self.get_average_fidelity(),
            'avg_throughput_ops_per_sec': self.get_average_throughput(),
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class QuantumBenchmark:
    """Quantum system benchmarking framework"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.suites: Dict[str, BenchmarkSuite] = {}
    
    def benchmark_function(self, func: Callable, func_args: Dict[str, Any],
                          name: str, num_iterations: int = 10) -> BenchmarkResult:
        """Benchmark a quantum function"""
        benchmark_id = str(uuid.uuid4())
        
        # Warmup
        for _ in range(2):
            func(**func_args)
        
        # Actual benchmark
        start_time = time.time()
        accuracies = []
        fidelities = []
        error_rates = []
        
        for _ in range(num_iterations):
            result = func(**func_args)
            
            # Extract metrics if available
            if isinstance(result, dict):
                if 'accuracy' in result:
                    accuracies.append(result['accuracy'])
                if 'fidelity' in result:
                    fidelities.append(result['fidelity'])
                if 'error_rate' in result:
                    error_rates.append(result['error_rate'])
        
        duration = time.time() - start_time
        
        # Calculate metrics
        throughput = num_iterations / duration if duration > 0 else 0
        avg_accuracy = np.mean(accuracies) if accuracies else 0.0
        avg_fidelity = np.mean(fidelities) if fidelities else 0.0
        avg_error_rate = np.mean(error_rates) if error_rates else 0.0
        
        result = BenchmarkResult(
            benchmark_id=benchmark_id,
            name=name,
            duration_seconds=duration,
            operations_performed=num_iterations,
            throughput_ops_per_sec=throughput,
            accuracy=avg_accuracy,
            fidelity=avg_fidelity,
            error_rate=avg_error_rate
        )
        
        self.results.append(result)
        return result
    
    def create_suite(self, name: str) -> BenchmarkSuite:
        """Create new benchmark suite"""
        suite_id = str(uuid.uuid4())
        suite = BenchmarkSuite(suite_id=suite_id, name=name)
        self.suites[suite_id] = suite
        return suite
    
    def run_suite(self, suite: BenchmarkSuite, benchmarks: List[Tuple[Callable, Dict, str]]) -> None:
        """Run collection of benchmarks"""
        for func, args, name in benchmarks:
            result = self.benchmark_function(func, args, name)
            suite.add_result(result)
        
        suite.completed_at = datetime.now()
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get summary of all results"""
        if not self.results:
            return {}
        
        return {
            'total_benchmarks': len(self.results),
            'avg_accuracy': np.mean([r.accuracy for r in self.results]),
            'avg_fidelity': np.mean([r.fidelity for r in self.results]),
            'avg_throughput': np.mean([r.throughput_ops_per_sec for r in self.results]),
            'avg_error_rate': np.mean([r.error_rate for r in self.results])
        }


class QuantumTestSuite:
    """Comprehensive quantum system testing"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def test_state_preparation(self, circuit_fn: Callable, expected_fidelity: float = 0.99) -> Dict[str, Any]:
        """Test quantum state preparation accuracy"""
        test_id = str(uuid.uuid4())
        
        try:
            state = circuit_fn()
            fidelity = np.abs(np.linalg.norm(state)) ** 2
            
            passed = fidelity >= expected_fidelity
            if passed:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            result = {
                'test_id': test_id,
                'test_name': 'State Preparation',
                'fidelity': fidelity,
                'expected_fidelity': expected_fidelity,
                'passed': passed,
                'timestamp': datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
        
        except Exception as e:
            self.failed_tests += 1
            result = {
                'test_id': test_id,
                'test_name': 'State Preparation',
                'passed': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
    
    def test_error_correction(self, circuit_fn: Callable, expected_success_rate: float = 0.98) -> Dict[str, Any]:
        """Test error correction effectiveness"""
        test_id = str(uuid.uuid4())
        
        try:
            successes = 0
            num_trials = 100
            
            for _ in range(num_trials):
                success = circuit_fn()
                if success:
                    successes += 1
            
            success_rate = successes / num_trials
            passed = success_rate >= expected_success_rate
            
            if passed:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            result = {
                'test_id': test_id,
                'test_name': 'Error Correction',
                'success_rate': success_rate,
                'expected_success_rate': expected_success_rate,
                'passed': passed,
                'trials': num_trials,
                'timestamp': datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
        
        except Exception as e:
            self.failed_tests += 1
            result = {
                'test_id': test_id,
                'test_name': 'Error Correction',
                'passed': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
    
    def test_gate_fidelity(self, gate_fn: Callable, expected_fidelity: float = 0.99) -> Dict[str, Any]:
        """Test single quantum gate fidelity"""
        test_id = str(uuid.uuid4())
        
        try:
            fidelities = []
            num_samples = 100
            
            for _ in range(num_samples):
                fidelity = gate_fn()
                fidelities.append(fidelity)
            
            avg_fidelity = np.mean(fidelities)
            passed = avg_fidelity >= expected_fidelity
            
            if passed:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            result = {
                'test_id': test_id,
                'test_name': 'Gate Fidelity',
                'avg_fidelity': avg_fidelity,
                'std_fidelity': np.std(fidelities),
                'expected_fidelity': expected_fidelity,
                'passed': passed,
                'samples': num_samples,
                'timestamp': datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
        
        except Exception as e:
            self.failed_tests += 1
            result = {
                'test_id': test_id,
                'test_name': 'Gate Fidelity',
                'passed': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
    
    def test_protocol(self, protocol_fn: Callable, num_trials: int = 100) -> Dict[str, Any]:
        """Test quantum protocol (teleportation, QKD, etc.)"""
        test_id = str(uuid.uuid4())
        
        try:
            results = []
            for _ in range(num_trials):
                result = protocol_fn()
                results.append(result)
            
            # Extract success metrics
            successes = sum(1 for r in results if r.get('success', False))
            success_rate = successes / num_trials
            
            avg_fidelity = np.mean([r.get('fidelity', 1.0) for r in results])
            
            result = {
                'test_id': test_id,
                'test_name': 'Quantum Protocol',
                'success_rate': success_rate,
                'avg_fidelity': avg_fidelity,
                'num_trials': num_trials,
                'timestamp': datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
        
        except Exception as e:
            result = {
                'test_id': test_id,
                'test_name': 'Quantum Protocol',
                'passed': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'pass_rate_percent': pass_rate,
            'test_results': self.test_results
        }
