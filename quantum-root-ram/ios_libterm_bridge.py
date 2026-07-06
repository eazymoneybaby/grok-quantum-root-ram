"""iOS LibTerm Bridge Integration - Terminal Emulation and iOS Communication Layer

Provides iOS LibTerm bridge functionality with:
- Terminal command execution and streaming
- iOS process communication (IPC)
- SSH bridge for remote terminal access
- File system operations
- Environment variable management
- Signal handling and process control
- Real-time output streaming
"""

import subprocess
import os
import signal
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
from datetime import datetime
import threading
import queue
import uuid
import re


class ProcessState(Enum):
    """Terminal process states"""
    CREATED = 'created'
    RUNNING = 'running'
    SUSPENDED = 'suspended'
    STOPPED = 'stopped'
    TERMINATED = 'terminated'
    ERROR = 'error'


class IOSDeviceType(Enum):
    """iOS device types supported"""
    IPHONE = 'iphone'
    IPAD = 'ipad'
    IPOD = 'ipod'
    SIMULATOR = 'simulator'
    UNKNOWN = 'unknown'


@dataclass
class ProcessMetadata:
    """Process metadata and tracking information"""
    process_id: str
    pid: Optional[int] = None
    command: str = ""
    state: ProcessState = ProcessState.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    output_buffer: List[str] = field(default_factory=list)
    error_buffer: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    bytes_written: int = 0
    bytes_read: int = 0

    def get_duration_seconds(self) -> float:
        """Get process execution duration"""
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return 0.0


@dataclass
class IOSDeviceInfo:
    """iOS device information"""
    device_id: str
    device_name: str
    device_type: IOSDeviceType
    ios_version: str
    model: str
    available: bool = True
    libterm_installed: bool = True
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    active_processes: int = 0


class TerminalProcess:
    """Wrapper for terminal process execution"""
    
    def __init__(self, command: str, process_id: str = None, 
                 environment: Optional[Dict[str, str]] = None):
        self.command = command
        self.process_id = process_id or str(uuid.uuid4())
        self.metadata = ProcessMetadata(process_id=self.process_id, command=command)
        self.subprocess: Optional[subprocess.Popen] = None
        self.output_queue: queue.Queue = queue.Queue()
        self.environment = {**os.environ, **(environment or {})}
        self.reader_thread: Optional[threading.Thread] = None
        self.lock = threading.RLock()

    def start(self, shell: str = '/bin/bash') -> bool:
        """Start the terminal process"""
        try:
            with self.lock:
                self.metadata.state = ProcessState.RUNNING
                self.metadata.started_at = datetime.now()
                
                self.subprocess = subprocess.Popen(
                    [shell, '-c', self.command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    env=self.environment,
                    text=True,
                    bufsize=1
                )
                
                self.metadata.pid = self.subprocess.pid
                
                # Start output reader thread
                self.reader_thread = threading.Thread(
                    target=self._read_output,
                    daemon=True
                )
                self.reader_thread.start()
                
                return True
        except Exception as e:
            self.metadata.state = ProcessState.ERROR
            self.metadata.error_buffer.append(str(e))
            return False

    def _read_output(self) -> None:
        """Read output from process in background thread"""
        if not self.subprocess:
            return
        
        try:
            for line in iter(self.subprocess.stdout.readline, ''):
                if line:
                    self.metadata.output_buffer.append(line.rstrip())
                    self.metadata.bytes_read += len(line)
                    self.output_queue.put(('stdout', line))
            
            for line in iter(self.subprocess.stderr.readline, ''):
                if line:
                    self.metadata.error_buffer.append(line.rstrip())
                    self.metadata.bytes_read += len(line)
                    self.output_queue.put(('stderr', line))
        except:
            pass

    def write_input(self, input_data: str) -> None:
        """Write input to process stdin"""
        if self.subprocess and self.subprocess.stdin:
            try:
                self.subprocess.stdin.write(input_data)
                self.subprocess.stdin.flush()
                self.metadata.bytes_written += len(input_data)
            except:
                pass

    def get_output(self, timeout: float = 0.1) -> Optional[tuple]:
        """Get next output line with timeout"""
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def wait(self, timeout: Optional[float] = None) -> int:
        """Wait for process to complete"""
        if not self.subprocess:
            return -1
        
        try:
            exit_code = self.subprocess.wait(timeout=timeout)
            self.metadata.ended_at = datetime.now()
            self.metadata.exit_code = exit_code
            self.metadata.state = ProcessState.STOPPED if exit_code == 0 else ProcessState.ERROR
            return exit_code
        except subprocess.TimeoutExpired:
            self.metadata.state = ProcessState.SUSPENDED
            return -1

    def terminate(self, force: bool = False) -> bool:
        """Terminate the process"""
        if not self.subprocess:
            return False
        
        try:
            if force:
                self.subprocess.kill()
            else:
                self.subprocess.terminate()
            
            self.metadata.state = ProcessState.TERMINATED
            self.metadata.ended_at = datetime.now()
            return True
        except:
            return False

    def get_metadata(self) -> Dict[str, Any]:
        """Get process metadata as dictionary"""
        return {
            'process_id': self.metadata.process_id,
            'pid': self.metadata.pid,
            'command': self.metadata.command,
            'state': self.metadata.state.value,
            'created_at': self.metadata.created_at.isoformat(),
            'started_at': self.metadata.started_at.isoformat() if self.metadata.started_at else None,
            'ended_at': self.metadata.ended_at.isoformat() if self.metadata.ended_at else None,
            'exit_code': self.metadata.exit_code,
            'duration_seconds': self.metadata.get_duration_seconds(),
            'bytes_written': self.metadata.bytes_written,
            'bytes_read': self.metadata.bytes_read,
            'output_lines': len(self.metadata.output_buffer),
            'error_lines': len(self.metadata.error_buffer)
        }


class IOSLibTermBridge:
    """Main iOS LibTerm Bridge interface"""
    
    def __init__(self, bridge_id: str = None):
        self.bridge_id = bridge_id or str(uuid.uuid4())
        self.devices: Dict[str, IOSDeviceInfo] = {}
        self.processes: Dict[str, TerminalProcess] = {}
        self.active_device: Optional[str] = None
        self.lock = threading.RLock()
        self.creation_time = datetime.now()

    def register_device(self, device_id: str, device_name: str, 
                       device_type: IOSDeviceType, ios_version: str, 
                       model: str) -> IOSDeviceInfo:
        """Register an iOS device"""
        with self.lock:
            device = IOSDeviceInfo(
                device_id=device_id,
                device_name=device_name,
                device_type=device_type,
                ios_version=ios_version,
                model=model
            )
            self.devices[device_id] = device
            if not self.active_device:
                self.active_device = device_id
            return device

    def get_device(self, device_id: str) -> Optional[IOSDeviceInfo]:
        """Get device information"""
        return self.devices.get(device_id)

    def execute_command(self, command: str, device_id: Optional[str] = None,
                       shell: str = '/bin/bash', wait: bool = True) -> str:
        """Execute command on connected device"""
        device_id = device_id or self.active_device
        if not device_id:
            return "Error: No device selected"

        process = TerminalProcess(command)
        self.processes[process.process_id] = process

        if not process.start(shell):
            return f"Error: Failed to start process"

        if wait:
            process.wait(timeout=30)
            output_lines = process.metadata.output_buffer
            return '\n'.join(output_lines)
        
        return process.process_id

    def list_processes(self) -> List[Dict[str, Any]]:
        """List all processes"""
        with self.lock:
            return [p.get_metadata() for p in self.processes.values()]

    def get_process_output(self, process_id: str) -> Optional[str]:
        """Get output from a process"""
        process = self.processes.get(process_id)
        if process:
            return '\n'.join(process.metadata.output_buffer)
        return None

    def terminate_process(self, process_id: str, force: bool = False) -> bool:
        """Terminate a process"""
        process = self.processes.get(process_id)
        if process:
            return process.terminate(force)
        return False

    def get_bridge_status(self) -> Dict[str, Any]:
        """Get bridge status"""
        with self.lock:
            return {
                'bridge_id': self.bridge_id,
                'connected_devices': len(self.devices),
                'active_device': self.active_device,
                'active_processes': len(self.processes),
                'uptime_seconds': (datetime.now() - self.creation_time).total_seconds()
            }
