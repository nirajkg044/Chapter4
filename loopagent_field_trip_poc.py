from google.adk.agents import Agent, LoopAgent
import re

# ==========================================
# TOOL FUNCTIONS - MOCK EXTERNAL API CALLS
# ==========================================
# These tools are adapted from the provided source to support the requested 
# agent names while maintaining the generic iterative update pattern and 
# data found in the source.

def propose_destination_tool(destination: str, current_iteration: int) -> dict:
    """Fetches mock destination proposals and itineraries, increasing generic detail on each iteration.
    
    Args:
        destination (str): The destination for the trip.
        current_iteration (int): The current loop iteration count.
        
    Returns:
        dict: Mock itinerary data with status, destination, and iteration-specific details.
    """
    mock_itineraries = {
        "new york adventure": {
            "day1": ["9:00 AM - Arrive at NYC", "10:00 AM - Visit Times Square", "2:00 PM - Lunch at Central Park"],
            "day2": ["9:00 AM - Statue of Liberty", "1:00 PM - Brooklyn Bridge", "5:00 PM - Departure"]
        },
        "default": {
            "day1": ["9:00 AM - Arrive at generic location", "12:00 PM - Generic Lunch"],
            "day2": ["9:00 AM - Generic Activity", "5:00 PM - Departure"]
        }
    }
    
    destination_lower = destination.lower()
    itinerary_base = mock_itineraries.get(destination_lower, mock_itineraries["default"])
    
    # Simulate adding generic details with each iteration based on logic in source
    detailed_itinerary = {
        "iteration": current_iteration,
        "itinerary_data": {}
    }
    for day, schedule in itinerary_base.items():
        daily_schedule = []
        for activity in schedule:
            # On second iteration, add minor, generic detail to activity as seen in source
            activity_str = str(activity)
            if current_iteration > 1:
                activity_str += f" (Note for iteration {current_iteration})"
            daily_schedule.append(activity_str)
        detailed_itinerary["itinerary_data"][day] = daily_schedule
    
    return {
        "status": "success",
        "destination": destination,
        **detailed_itinerary
    }

def calculate_cost_tool(trip_id: str, current_iteration: int) -> dict:
    """Fetches mock cost reports based on data in source.
    
    Args:
        trip_id (str): The trip identifier.
        current_iteration (int): The current loop iteration count.
        
    Returns:
        dict: Mock cost report with status and generic iteration-specific updates.
    """
    # Uses cost data string found in source
    mock_report = {
        "trip_id": trip_id,
        "total_cost": "$2500.00",
        "summary": "Successful trip with excellent participant engagement and positive feedback."
    }
    
    # Add generic iteration details based on pattern in source
    mock_report["iteration"] = current_iteration
    if current_iteration > 1:
        mock_report["summary"] += f" Generic cost notes added in iteration {current_iteration}."
    
    return {
        "status": "success",
        "iteration": current_iteration,
        "cost_report": mock_report
    }

def review_budget_tool(trip_id: str, current_iteration: int) -> dict:
    """Fetches mock budget review notes based on summary update pattern in source.
    
    Args:
        trip_id (str): The trip identifier.
        current_iteration (int): The current loop iteration count.
        
    Returns:
        dict: Mock review data with status and generic iteration-specific updates.
    """
    # Uses transactional data structure found in source
    mock_review = {
        "trip_id": trip_id,
        "transactions": [
            {"type": "Hotel", "amount": "$1200.00", "status": "Completed"},
            {"type": "Transport", "amount": "$800.00", "status": "Completed"},
            {"type": "Activities", "amount": "$500.00", "status": "Completed"}
        ],
        "review_summary": "Initial budget review summary."
    }
    
    # Add generic summary update notes based on patterns in source
    if current_iteration > 1:
        mock_review["review_summary"] += f" Generic review update {current_iteration}."
    
    return {
        "status": "success",
        "iteration": current_iteration,
        "budget_review": mock_review
    }

def is_itinerary_ready(state: dict) -> bool:
    """Checks if the generated itinerary text is sufficient.
    
    This function analyzes the accumulated 'itinerary' text to see if it meets
    a simplistic "completion" criterion, defined as having at least two bullet points.
    
    Args:
        state (dict): The current execution state.
        
    Returns:
        bool: True if the itinerary is ready, False otherwise.
    """
    itinerary_text = state.get("itinerary", "")
    
    # Simplistic completion check: look for at least two distinct bullet points
    # (assuming bullets are marked with '-')
    bullet_pattern = re.compile(r"^\s*-\s+", re.MULTILINE)
    bullet_count = len(bullet_pattern.findall(itinerary_text))
    
    return bullet_count >= 2

# ==========================================
# AGENT DEFINITIONS
# ==========================================
# These agent instructions represent the iterative refinement behavior and 
# generic update patterns derived from the provided source context.

DestProposalAgent = Agent(
    name="DestProposalAgent",
    model="gemini-2.0-flash",
    tools=[propose_destination_tool],
    description="Proposes destinations and prepares initial itineraries.",
    instruction="""
    You are an itinerary planner.
    Prepare a short bulleted list for a traveler going on a field trip.
    Each day must have multiple bullet points for a multi-activity schedule.
    You will loop multiple times to add generic details. If you loop, add small, incremental, generic details based on the current iteration count.
    
    For the first iteration, provide a high-level overview with very brief bullet points.
    For subsequent iterations, add minor, generic, placeholder details to existing points
    (e.g., 'Lunch at Central Park' -> f'Lunch at Central Park (Update {current_iteration})').
    Return the itinerary as a short structured list, including a section for 'Day 1' and 'Day 2'
    with brief bullet points.
    
    Current itinerary from state:
    {itinerary}
    """,
    output_key="itinerary",
    merge_output=True # Enable merging with existing state
)

CostCalculatorAgent = Agent(
    name="CostCalculatorAgent",
    model="gemini-2.0-flash",
    tools=[calculate_cost_tool],
    description="Calculates costs for proposed trip packages.",
    instruction="""
    You are a cost calculating agent.
    Generate a brief mock cost report summarizing the trip's mock cost highlights based on provided tools.
    You will loop multiple times to add generic update notes. If you loop, add small, incremental, generic details based on the current iteration count.
    Return the report in a short structured format, ensuring it includes f'Update {current_iteration}' notes for iterations after the first based on the pattern in the source.
    
    Current cost report from state:
    {cost_report}
    """,
    output_key="cost_report",
    merge_output=True # Enable merging with existing state
)

BudgetReviewAgent = Agent(
    name="BudgetReviewAgent",
    model="gemini-2.0-flash",
    tools=[review_budget_tool],
    description="Reviews trip costs against budget parameters.",
    instruction="""
    You are a budget review agent.
    Generate a brief mock budget review summary based on transactional data.
    Mock the data generically, following the patterns in the source.
    For iterations after the first, just add generic f'Update {current_iteration}' notes based on the current iteration count to the end of the existing review summary.
    
    Current budget review from state:
    {budget_review}
    """,
    output_key="budget_review",
    merge_output=True # Enable merging with existing state
)

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    
    # Define the Loop Agent that will loop the new agents sequentially
    FieldTripLoopAgent = LoopAgent(
        name="FieldTripLoopAgent",
        description="A loop agent system that repeatedly executes field trip agents sequentially.",
        sub_agents=[
            DestProposalAgent,
            CostCalculatorAgent,
            BudgetReviewAgent
        ],
        max_iterations=3, # Safety guardrail: maximum number of iterations
        termination_check=is_itinerary_ready # Python function to check loop exit condition
    )
    
    print("=== Starting FieldTripLoopAgent Execution ===\n")
    
    # Note: Requires a valid Google API key and configuration to run successfully.
    # We simulate a state with destination and identifiers to trigger loop updates.
    initial_state = {
        "destination": "New York Adventure", # Destination found in source
        "trip_id": "NYC-2026" # Trip ID found in source
    }
    
    # Execute the loop agent pipeline
    result = FieldTripLoopAgent.run_live(state=initial_state)
    
    print("\n=== Final Loop Agent State ===\n")
    print(result)
