"""Agent factory functions for Pydantic AI testing."""

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic import BaseModel
from dataclasses import dataclass


# ============================================================================
# Data Models
# ============================================================================

class CalculationResult(BaseModel):
    """Result from mathematical calculations."""
    result: float
    operation: str
    explanation: str


class CustomerSupportResponse(BaseModel):
    """Response from customer support agent."""
    response: str
    customer_tier: str
    action_taken: str


class MCPCalculationResult(BaseModel):
    """Result from MCP-based calculations."""
    result: int
    operation: str
    explanation: str


@dataclass
class CustomerContext:
    """Structured context data for customer support agent."""
    customer_id: str
    name: str
    tier: str
    account_balance: float
    open_tickets: int
    last_purchase_days_ago: int


# ============================================================================
# Agent Factory Functions
# ============================================================================

def create_customer_support_agent(name: str, model: str) -> Agent:
    """Create a customer support agent with single tool and structured context."""
    agent = Agent(
        model,
        name=name,
        instructions=(
            "You are a customer support assistant. Use the customer's tier and account information "
            "to provide personalized support. Use the tool to check if the customer is eligible for perks."
        ),
        output_type=CustomerSupportResponse,
        model_settings={
            "temperature": 0.3,
            "max_tokens": 300,
        },
    )
    
    @agent.tool
    def check_perk_eligibility(ctx, perk_name: str) -> dict:
        """Check if customer is eligible for a specific perk based on their tier."""
        customer: CustomerContext = ctx.deps
        
        perk_requirements = {
            "priority_support": ["gold", "platinum"],
            "free_shipping": ["silver", "gold", "platinum"],
            "discount_20": ["platinum"],
            "discount_10": ["gold", "platinum"],
            "early_access": ["gold", "platinum"],
        }
        
        eligible = customer.tier in perk_requirements.get(perk_name, [])
        
        return {
            "perk_name": perk_name,
            "eligible": eligible,
            "customer_tier": customer.tier,
            "reason": f"Customer tier '{customer.tier}' {'is' if eligible else 'is not'} eligible for '{perk_name}'"
        }
    
    return agent


def create_math_agent(name: str, model: str) -> Agent:
    """Create a math agent with multiple calculation tools."""
    agent = Agent(
        model,
        name=name,
        instructions=(
            "You are a mathematical assistant. Use the available tools to perform calculations "
            "and return structured results. Always explain your work step by step."
        ),
        output_type=CalculationResult,
        model_settings={
            "temperature": 0.1,
            "max_tokens": 400,
        },
    )
    
    @agent.tool_plain
    def add(a: float, b: float) -> float:
        """Add two numbers together."""
        return a + b
    
    @agent.tool_plain
    def subtract(a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b
    
    @agent.tool_plain
    def multiply(a: float, b: float) -> float:
        """Multiply two numbers together."""
        return a * b
    
    @agent.tool_plain
    def divide(a: float, b: float) -> float:
        """Divide a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    @agent.tool_plain
    def calculate_percentage(part: float, total: float) -> float:
        """Calculate what percentage 'part' is of 'total'."""
        if total == 0:
            return 0.0
        return (part / total) * 100
    
    @agent.tool_plain
    def power(base: float, exponent: float) -> float:
        """Calculate base raised to the power of exponent."""
        return base ** exponent
    
    return agent


def create_mcp_agent(name: str, model: str) -> Agent:
    """Create an agent that connects to an MCP server via stdio."""
    # Connect to the MCP server
    mcp_server = MCPServerStdio("python", args=["mcp_server.py"])
    
    # Create agent with MCP server as a toolset
    agent = Agent(
        model,
        name=name,
        instructions=(
            "You are a helpful assistant that can perform calculations and text analysis "
            "using MCP tools. Use the available tools to answer user questions."
        ),
        output_type=MCPCalculationResult,
        toolsets=[mcp_server],
        model_settings={
            "temperature": 0.2,
            "max_tokens": 400,
        },
    )
    
    return agent
