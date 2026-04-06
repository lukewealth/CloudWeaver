# Agent Orchestrator with MPC (Multi-Party Computation)
# Coordinates multiple agents with secure communication

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib

from app.agents.cost_optimizer import CostOptimizerAgent
from app.agents.security_auditor import SecurityAuditorAgent
from app.agents.auto_scaler import AutoScalerAgent
from app.agents.incident_responder import IncidentResponderAgent

@dataclass
class AgentMessage:
    """Message between agents with MPC signature"""
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: datetime
    signature: Optional[str] = None
    
    def sign(self, private_key: str):
        """Sign message for MPC verification"""
        payload = f"{self.sender}:{self.receiver}:{json.dumps(self.content, sort_keys=True)}:{self.timestamp.isoformat()}"
        self.signature = hashlib.sha256(f"{payload}:{private_key}".encode()).hexdigest()

@dataclass
class AgentDecision:
    """Decision requiring MPC consensus"""
    action_type: str
    target_resource: str
    proposed_changes: Dict[str, Any]
    estimated_impact: Dict[str, float]
    risk_score: float
    votes: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.votes is None:
            self.votes = {}
    
    @property
    def consensus_reached(self) -> bool:
        """Check if majority of agents agree"""
        if not self.votes:
            return False
        return sum(self.votes.values()) / len(self.votes) > 0.5

class AgentOrchestrator:
    """
    Multi-Agent Orchestrator with MPC Consensus
    
    Manages 4 specialized agents:
    - CostOptimizer: Financial governance
    - SecurityAuditor: Security & compliance
    - AutoScaler: Performance optimization
    - IncidentResponder: Incident management
    """
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.decisions_pending: List[AgentDecision] = []
        self.running = False
        
    async def start_all_agents(self):
        """Initialize and start all agents"""
        self.agents = {
            "cost_optimizer": CostOptimizerAgent(),
            "security_auditor": SecurityAuditorAgent(),
            "auto_scaler": AutoScalerAgent(),
            "incident_responder": IncidentResponderAgent()
        }
        
        for name, agent in self.agents.items():
            await agent.initialize()
            asyncio.create_task(agent.run())
            
        self.running = True
        asyncio.create_task(self._message_router())
        asyncio.create_task(self._consensus_handler())
        
    async def stop_all_agents(self):
        """Gracefully stop all agents"""
        self.running = False
        for agent in self.agents.values():
            await agent.stop()
            
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get health status of all agents"""
        status = {}
        for name, agent in self.agents.items():
            status[name] = await agent.get_status()
        return status
    
    async def propose_action(self, decision: AgentDecision) -> bool:
        """
        Propose an action requiring MPC consensus
        Returns True if consensus reached and action approved
        """
        self.decisions_pending.append(decision)
        
        # Broadcast to all agents for voting
        for agent_name, agent in self.agents.items():
            vote = await agent.evaluate_decision(decision)
            decision.votes[agent_name] = vote
            
        return decision.consensus_reached
    
    async def _message_router(self):
        """Route messages between agents"""
        while self.running:
            try:
                msg: AgentMessage = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )
                
                # Route to recipient
                if msg.receiver in self.agents:
                    await self.agents[msg.receiver].receive_message(msg)
                    
            except asyncio.TimeoutError:
                continue
                
    async def _consensus_handler(self):
        """Handle pending decisions and execute approved actions"""
        while self.running:
            for decision in self.decisions_pending[:]:
                if decision.consensus_reached:
                    await self._execute_decision(decision)
                    self.decisions_pending.remove(decision)
                    
            await asyncio.sleep(5)
            
    async def _execute_decision(self, decision: AgentDecision):
        """Execute an approved decision"""
        # Log the action
        print(f"Executing {decision.action_type} on {decision.target_resource}")
        
        # Route to appropriate executor
        if decision.action_type.startswith("cost_"):
            await self.agents["cost_optimizer"].execute(decision)
        elif decision.action_type.startswith("security_"):
            await self.agents["security_auditor"].execute(decision)
        elif decision.action_type.startswith("scale_"):
            await self.agents["auto_scaler"].execute(decision)
        elif decision.action_type.startswith("incident_"):
            await self.agents["incident_responder"].execute(decision)