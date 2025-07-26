from google.adk.agents import SequentialAgent, ParallelAgent
from .sub_agents.image_agent import image_object_agent
from .sub_agents.location_agent import location_agent
from .sub_agents.property_details_agent import property_details_agent
from .sub_agents.verification_agent import verification_agent
from .sub_agents.reporting_agent import reporting_agent
from .parallel_reasearch_agents.object_price_estimator import object_price_estimator_agent
from .parallel_reasearch_agents.market_context_estimator import market_context_estimator_agent
from .parallel_reasearch_agents.risk_identifier import risk_identifier_agent

from dotenv import load_dotenv

load_dotenv()

# Define model constant
GEMINI_MODEL = "gemini-2.0-flash"

# Create the parallel research agent
research_parallel_agent = ParallelAgent(
    name="ResearchParallelAgent",
    sub_agents=[
        object_price_estimator_agent,
        market_context_estimator_agent,
        risk_identifier_agent
    ],
    description="Executes property research tasks in parallel using web search"
)

# Main sequential workflow
home_loan_assessment_pipeline = SequentialAgent(
    name="HomeLoanAssessmentPipeline",
    sub_agents=[
        image_object_agent,
        location_agent,
        property_details_agent,
        research_parallel_agent,
        verification_agent,
        reporting_agent
    ],
    description="Complete home loan assessment workflow from image analysis to final report"
)

# Required root agent for ADK

