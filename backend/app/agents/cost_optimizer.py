from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from app.infrastructure.aws_client import AWSClient
from app.infrastructure.database import Database
from app.ml.cost_predictor import CostPredictor

class CostOptimizerAgent(ABC):
    """
    CostOptimizer Agent: Financial governance for cloud resources
    
    Responsibilities:
    - Detect resource waste (unused, over-provisioned)
    - Recommend cost optimizations
    - Execute approved savings actions
    - Track savings realized
    """
    
    def __init__(self):
        self.name = "cost_optimizer"
        self.status = "initializing"
        self.aws = AWSClient()
        self.db = Database()
        self.predictor = CostPredictor()
        self.running = False
        
    async def initialize(self):
        """Initialize agent connections"""
        await self.aws.connect()
        await self.db.connect()
        await self.predictor.load_model()
        self.status = "ready"
        
    async def run(self):
        """Main agent loop"""
        self.running = True
        self.status = "running"
        
        while self.running:
            try:
                # Scan all resources
                resources = await self._scan_resources()
                
                # Analyze each for optimization opportunities
                for resource in resources:
                    await self._analyze_resource(resource)
                    
                # Wait before next scan
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                print(f"CostOptimizer error: {e}")
                await asyncio.sleep(60)
                
    async def stop(self):
        """Graceful shutdown"""
        self.running = False
        self.status = "stopped"
        
    async def get_status(self) -> Dict[str, Any]:
        """Return agent health status"""
        return {
            "name": self.name,
            "status": self.status,
            "running": self.running,
            "last_scan": getattr(self, 'last_scan', None)
        }
        
    async def _scan_resources(self) -> List[Dict]:
        """Scan all cloud resources across providers"""
        resources = []
        
        # AWS resources
        ec2_instances = await self.aws.get_ec2_instances()
        rds_instances = await self.aws.get_rds_instances()
        s3_buckets = await self.aws.get_s3_buckets()
        load_balancers = await self.aws.get_load_balancers()
        
        resources.extend(ec2_instances)
        resources.extend(rds_instances)
        resources.extend(s3_buckets)
        resources.extend(load_balancers)
        
        self.last_scan = datetime.utcnow()
        return resources
        
    async def _analyze_resource(self, resource: Dict):
        """Analyze a resource for optimization opportunities"""
        resource_type = resource.get('type')
        resource_id = resource.get('id')
        
        # Get utilization metrics
        metrics = await self.aws.get_metrics(
            resource_id=resource_id,
            metric_names=['CPUUtilization', 'MemoryUtilization', 'NetworkIn'],
            hours=168  # 7 days
        )
        
        # Predict cost impact
        prediction = self.predictor.predict(
            resource_type=resource_type,
            metrics=metrics,
            current_spend=resource.get('monthly_cost', 0)
        )
        
        # Check for optimization opportunities
        opportunities = []
        
        # 1. Right-sizing
        if prediction.avg_cpu < 20 and prediction.avg_memory < 30:
            opportunities.append({
                "type": "rightsize",
                "action": f"Downsize {resource_id} from {resource['instance_type']}",
                "savings": prediction.estimated_savings,
                "confidence": prediction.confidence,
                "risk": "low"
            })
            
        # 2. Spot/preemptible migration
        if prediction.is_stateless and prediction.uptime_hours > 720:
            opportunities.append({
                "type": "spot_migration",
                "action": f"Migrate {resource_id} to spot instances",
                "savings": prediction.estimated_savings * 0.7,  # 70% cheaper
                "confidence": prediction.confidence,
                "risk": "medium"
            })
            
        # 3. Orphaned resources
        if prediction.last_accessed_days > 30:
            opportunities.append({
                "type": "orphan_cleanup",
                "action": f"Delete unused {resource_id}",
                "savings": prediction.monthly_cost,
                "confidence": 0.95,
                "risk": "low"
            })
            
        # If high-confidence opportunities exist, propose action
        for opp in opportunities:
            if opp['confidence'] > 0.8 and opp['savings'] > 50:
                await self._propose_optimization(resource, opp)
                
    async def _propose_optimization(self, resource: Dict, opportunity: Dict):
        """Propose an optimization action via orchestrator"""
        from app.agents.orchestrator import AgentDecision
        
        decision = AgentDecision(
            action_type=f"cost_{opportunity['type']}",
            target_resource=resource['id'],
            proposed_changes={
                "current_type": resource.get('instance_type'),
                "recommended_type": self._get_smaller_type(resource.get('instance_type')),
                "monthly_savings": opportunity['savings'],
                "confidence": opportunity['confidence']
            },
            estimated_impact={
                "cost_savings_monthly": opportunity['savings'],
                "performance_impact": -5 if opportunity['type'] == 'rightsize' else 0,
                "availability_risk": 0.1 if opportunity['risk'] == 'low' else 0.3
            },
            risk_score=0.2 if opportunity['risk'] == 'low' else 0.5
        )
        
        # Submit to orchestrator for consensus
        # orchestrator will call back if approved
        
    def _get_smaller_type(self, current_type: str) -> str:
        """Recommend a smaller instance type"""
        sizing_map = {
            't3.2xlarge': 't3.xlarge',
            't3.xlarge': 't3.large',
            't3.large': 't3.medium',
            't3.medium': 't3.small',
            'm5.4xlarge': 'm5.2xlarge',
            'm5.2xlarge': 'm5.xlarge',
        }
        return sizing_map.get(current_type, current_type)
        
    async def evaluate_decision(self, decision: AgentDecision) -> bool:
        """Vote on a proposed decision from another agent"""
        # CostOptimizer approves if decision saves money and has low risk
        if decision.estimated_impact.get('cost_savings_monthly', 0) > 100:
            if decision.risk_score < 0.4:
                return True
        return False
        
    async def execute(self, decision: AgentDecision):
        """Execute an approved cost optimization decision"""
        action_type = decision.action_type.replace("cost_", "")
        
        if action_type == "rightsize":
            await self._execute_rightsize(decision)
        elif action_type == "spot_migration":
            await self._execute_spot_migration(decision)
        elif action_type == "orphan_cleanup":
            await self._execute_orphan_cleanup(decision)
            
    async def _execute_rightsize(self, decision: AgentDecision):
        """Execute right-sizing action"""
        resource_id = decision.target_resource
        new_type = decision.proposed_changes['recommended_type']
        
        print(f"Right-sizing {resource_id} to {new_type}")
        # await self.aws.modify_instance_type(resource_id, new_type)
        
    async def _execute_spot_migration(self, decision: AgentDecision):
        """Migrate to spot instances"""
        resource_id = decision.target_resource
        print(f"Migrating {resource_id} to spot")
        
    async def _execute_orphan_cleanup(self, decision: AgentDecision):
        """Delete orphaned resource"""
        resource_id = decision.target_resource
        print(f"Cleaning up orphaned resource {resource_id}")
        # await self.aws.delete_resource(resource_id)