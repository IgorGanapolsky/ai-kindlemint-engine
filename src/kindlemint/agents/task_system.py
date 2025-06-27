"""
Task Management System for KindleMint Multi-Agent Architecture

This module defines the task structure, execution framework, and result
handling for the multi-agent book publishing automation system.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_agent import AgentCapability


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"          # Task created but not yet assigned
    ASSIGNED = "assigned"        # Task assigned to agent but not started
    RUNNING = "running"          # Task currently being executed
    COMPLETED = "completed"      # Task completed successfully
    FAILED = "failed"           # Task execution failed
    CANCELLED = "cancelled"      # Task was cancelled
    TIMEOUT = "timeout"         # Task timed out
    RETRYING = "retrying"       # Task is being retried after failure


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"    # Must be executed immediately
    HIGH = "high"           # Important, execute soon
    NORMAL = "normal"       # Standard priority
    LOW = "low"            # Can be deferred
    BACKGROUND = "background"  # Execute when resources available


class TaskType(Enum):
    """Standard task types in the KindleMint system"""
    
    # Content generation tasks
    GENERATE_PUZZLES = "generate_puzzles"
    CREATE_PDF_LAYOUT = "create_pdf_layout"
    GENERATE_EPUB = "generate_epub"
    DESIGN_COVER = "design_cover"
    
    # Quality assurance tasks
    VALIDATE_CONTENT = "validate_content"
    CHECK_COMPLIANCE = "check_compliance"
    RUN_QA_TESTS = "run_qa_tests"
    
    # Market intelligence tasks
    RESEARCH_KEYWORDS = "research_keywords"
    ANALYZE_COMPETITION = "analyze_competition"
    OPTIMIZE_SEO = "optimize_seo"
    TRACK_TRENDS = "track_trends"
    
    # Marketing automation tasks
    GENERATE_MARKETING = "generate_marketing"
    CREATE_PROSPECTING = "create_prospecting"
    BUILD_FUNNELS = "build_funnels"
    AUTOMATE_SOCIAL = "automate_social"
    
    # Business intelligence tasks
    CALCULATE_METRICS = "calculate_metrics"
    GENERATE_REPORTS = "generate_reports"
    ANALYZE_PERFORMANCE = "analyze_performance"
    FORECAST_REVENUE = "forecast_revenue"
    
    # Coordination tasks
    ORCHESTRATE_WORKFLOW = "orchestrate_workflow"
    MANAGE_RESOURCES = "manage_resources"
    HANDLE_ERRORS = "handle_errors"
    COORDINATE_AGENTS = "coordinate_agents"


@dataclass
class TaskDependency:
    """Represents a dependency between tasks"""
    task_id: str
    dependency_type: str = "completion"  # completion, data, resource
    optional: bool = False


@dataclass
class TaskConstraints:
    """Constraints and requirements for task execution"""
    max_execution_time: Optional[int] = None  # seconds
    max_retries: int = 3
    required_capabilities: Optional[List[AgentCapability]] = None
    required_resources: Optional[Dict[str, Any]] = None
    exclusive_execution: bool = False  # Requires exclusive agent access
    preferred_agents: Optional[List[str]] = None
    excluded_agents: Optional[List[str]] = None


@dataclass
class TaskResult:
    """Result of task execution"""
    success: bool
    task_id: str
    agent_id: Optional[str] = None
    execution_time: Optional[float] = None
    output_data: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)  # File paths, URLs, etc.
    error_message: Optional[str] = None
    error_details: Dict[str, Any] = field(default_factory=dict)
    quality_score: Optional[float] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate result after initialization"""
        if not self.success and not self.error_message:
            raise ValueError("Failed tasks must include an error message")


@dataclass
class Task:
    """
    Represents a task in the KindleMint multi-agent system
    """
    
    # Task identification
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = TaskType.GENERATE_PUZZLES
    name: str = ""
    description: str = ""
    
    # Task data
    input_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Execution control
    priority: TaskPriority = TaskPriority.NORMAL
    constraints: TaskConstraints = field(default_factory=TaskConstraints)
    dependencies: List[TaskDependency] = field(default_factory=list)
    
    # State tracking
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    assigned_at: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Results
    result: Optional[TaskResult] = None
    error: Optional[str] = None
    retry_count: int = 0
    
    # Workflow integration
    parent_task_id: Optional[str] = None
    child_task_ids: List[str] = field(default_factory=list)
    workflow_id: Optional[str] = None
    
    @property
    def required_capabilities(self) -> List[AgentCapability]:
        """Get required capabilities from constraints"""
        return self.constraints.required_capabilities or []
    
    @property
    def execution_time(self) -> Optional[float]:
        """Calculate task execution time in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def is_expired(self) -> bool:
        """Check if task has exceeded maximum execution time"""
        if not self.constraints.max_execution_time or not self.start_time:
            return False
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed > self.constraints.max_execution_time
    
    @property
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return (
            self.status == TaskStatus.FAILED and 
            self.retry_count < self.constraints.max_retries
        )
    
    def add_dependency(self, task_id: str, dependency_type: str = "completion", optional: bool = False) -> None:
        """Add a dependency to this task"""
        dependency = TaskDependency(
            task_id=task_id,
            dependency_type=dependency_type,
            optional=optional
        )
        self.dependencies.append(dependency)
    
    def add_child_task(self, child_task_id: str) -> None:
        """Add a child task ID"""
        if child_task_id not in self.child_task_ids:
            self.child_task_ids.append(child_task_id)
    
    def mark_assigned(self, agent_id: str) -> None:
        """Mark task as assigned to an agent"""
        self.status = TaskStatus.ASSIGNED
        self.assigned_agent = agent_id
        self.assigned_at = datetime.now()
    
    def mark_started(self) -> None:
        """Mark task as started"""
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.now()
    
    def mark_completed(self, result: TaskResult) -> None:
        """Mark task as completed with result"""
        self.status = TaskStatus.COMPLETED
        self.end_time = datetime.now()
        self.result = result
    
    def mark_failed(self, error_message: str, result: Optional[TaskResult] = None) -> None:
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.end_time = datetime.now()
        self.error = error_message
        if result:
            self.result = result
    
    def mark_cancelled(self, reason: str = "") -> None:
        """Mark task as cancelled"""
        self.status = TaskStatus.CANCELLED
        self.end_time = datetime.now()
        self.error = f"Cancelled: {reason}"
    
    def prepare_retry(self) -> None:
        """Prepare task for retry"""
        if not self.can_retry:
            raise ValueError("Task cannot be retried")
        
        self.retry_count += 1
        self.status = TaskStatus.RETRYING
        self.assigned_agent = None
        self.assigned_at = None
        self.start_time = None
        self.end_time = None
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "name": self.name,
            "description": self.description,
            "input_data": self.input_data,
            "context": self.context,
            "priority": self.priority.value,
            "status": self.status.value,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at.isoformat(),
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "error": self.error,
            "retry_count": self.retry_count,
            "parent_task_id": self.parent_task_id,
            "child_task_ids": self.child_task_ids,
            "workflow_id": self.workflow_id,
            "dependencies": [
                {
                    "task_id": dep.task_id,
                    "dependency_type": dep.dependency_type,
                    "optional": dep.optional
                }
                for dep in self.dependencies
            ],
            "constraints": {
                "max_execution_time": self.constraints.max_execution_time,
                "max_retries": self.constraints.max_retries,
                "required_capabilities": [cap.value for cap in (self.constraints.required_capabilities or [])],
                "required_resources": self.constraints.required_resources,
                "exclusive_execution": self.constraints.exclusive_execution,
                "preferred_agents": self.constraints.preferred_agents,
                "excluded_agents": self.constraints.excluded_agents,
            },
            "result": {
                "success": self.result.success,
                "task_id": self.result.task_id,
                "agent_id": self.result.agent_id,
                "execution_time": self.result.execution_time,
                "output_data": self.result.output_data,
                "artifacts": self.result.artifacts,
                "error_message": self.result.error_message,
                "error_details": self.result.error_details,
                "quality_score": self.result.quality_score,
                "performance_metrics": self.result.performance_metrics,
            } if self.result else None,
        }
    
    def __repr__(self) -> str:
        return (
            f"Task(id={self.task_id[:8]}, type={self.task_type.value}, "
            f"status={self.status.value}, agent={self.assigned_agent})"
        )


# Utility functions for creating common task types

def create_puzzle_generation_task(
    puzzle_type: str,
    count: int,
    difficulty: str = "mixed",
    theme: Optional[str] = None,
    output_dir: Optional[str] = None,
    priority: TaskPriority = TaskPriority.NORMAL
) -> Task:
    """Create a puzzle generation task"""
    return Task(
        task_type=TaskType.GENERATE_PUZZLES,
        name=f"Generate {count} {puzzle_type} puzzles",
        description=f"Generate {count} {puzzle_type} puzzles with {difficulty} difficulty",
        input_data={
            "puzzle_type": puzzle_type,
            "count": count,
            "difficulty": difficulty,
            "theme": theme,
            "output_dir": output_dir,
        },
        priority=priority,
        constraints=TaskConstraints(
            required_capabilities=[AgentCapability.PUZZLE_CREATION],
            max_execution_time=1800,  # 30 minutes
        ),
    )


def create_pdf_layout_task(
    title: str,
    input_dir: str,
    output_dir: str,
    author: str = "KindleMint Publishing",
    priority: TaskPriority = TaskPriority.NORMAL
) -> Task:
    """Create a PDF layout task"""
    return Task(
        task_type=TaskType.CREATE_PDF_LAYOUT,
        name=f"Create PDF layout for {title}",
        description=f"Generate professional PDF layout for book: {title}",
        input_data={
            "title": title,
            "input_dir": input_dir,
            "output_dir": output_dir,
            "author": author,
        },
        priority=priority,
        constraints=TaskConstraints(
            required_capabilities=[AgentCapability.PDF_LAYOUT],
            max_execution_time=900,  # 15 minutes
        ),
    )


def create_qa_validation_task(
    file_path: str,
    validation_type: str = "comprehensive",
    priority: TaskPriority = TaskPriority.HIGH
) -> Task:
    """Create a quality assurance validation task"""
    return Task(
        task_type=TaskType.RUN_QA_TESTS,
        name=f"QA validation for {file_path}",
        description=f"Run {validation_type} quality assurance checks",
        input_data={
            "file_path": file_path,
            "validation_type": validation_type,
        },
        priority=priority,
        constraints=TaskConstraints(
            required_capabilities=[AgentCapability.QUALITY_ASSURANCE],
            max_execution_time=600,  # 10 minutes
        ),
    )


def create_keyword_research_task(
    category: str,
    target_market: str = "US",
    language: str = "en",
    priority: TaskPriority = TaskPriority.NORMAL
) -> Task:
    """Create a keyword research task"""
    return Task(
        task_type=TaskType.RESEARCH_KEYWORDS,
        name=f"Keyword research for {category}",
        description=f"Research optimal keywords for {category} in {target_market}",
        input_data={
            "category": category,
            "target_market": target_market,
            "language": language,
        },
        priority=priority,
        constraints=TaskConstraints(
            required_capabilities=[AgentCapability.MARKET_RESEARCH],
            max_execution_time=1200,  # 20 minutes
        ),
    )