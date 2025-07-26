import os
import vertexai
from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from dotenv import load_dotenv

# Import your root agent
from agent import root_agent  # Your orchestrator agent

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.getenv("LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET", "gs://your-staging-bucket")

def initialize_vertex_ai():
    """Initialize Vertex AI with project settings"""
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )
    print(f"Initialized Vertex AI for project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Staging bucket: {STAGING_BUCKET}")

def create_adk_app():
    """Wrap the root agent in AdkApp for deployment"""
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )
    print("Created ADK App wrapper")
    return app

def test_locally(app):
    """Test the agent locally before deployment"""
    print("\n=== Testing Agent Locally ===")
    
    # Create session
    session = app.create_session(user_id="test_user")
    print(f"Created local session: {session.id}")
    
    # Test query
    test_message = "I want to assess a property for a home loan"
    print(f"Sending test message: {test_message}")
    
    try:
        events = []
        for event in app.stream_query(
            user_id="test_user",
            session_id=session.id,
            message=test_message,
        ):
            events.append(event)
            print(f"Event: {event}")
        
        print("Local testing successful!")
        return True
    except Exception as e:
        print(f"Local testing failed: {e}")
        return False

def deploy_to_agent_engine(app):
    """Deploy the agent to Vertex AI Agent Engine"""
    print("\n=== Deploying to Agent Engine ===")
    print("This may take several minutes...")
    
    try:
        remote_app = agent_engines.create(
            agent_engine=app,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]",
                "google-adk>=1.0.0",
                "pillow>=10.0.0",
                "pydantic>=2.5.0",
                "python-dotenv>=1.0.0",
                "aiofiles>=23.2.0"
            ]
        )
        
        print("Deployment successful!")
        print(f"Resource name: {remote_app.resource_name}")
        
        return remote_app
    except Exception as e:
        print(f"Deployment failed: {e}")
        return None

def test_remote_agent(remote_app):
    """Test the deployed agent"""
    print("\n=== Testing Remote Agent ===")
    
    try:
        # Create remote session
        remote_session = remote_app.create_session(user_id="remote_test_user")
        print(f"Created remote session: {remote_session['id']}")
        
        # Test query
        test_message = "I have property images to analyze for a home loan assessment"
        print(f"Sending test message: {test_message}")
        
        events = []
        for event in remote_app.stream_query(
            user_id="remote_test_user",
            session_id=remote_session["id"],
            message=test_message,
        ):
            events.append(event)
            print(f"Remote event: {event}")
        
        print("Remote testing successful!")
        return True
    except Exception as e:
        print(f"Remote testing failed: {e}")
        return False

def main():
    """Main deployment workflow"""
    print("=== Home Loan Assessment Agent Deployment ===")
    
    # Initialize Vertex AI
    initialize_vertex_ai()
    
    # Create ADK App
    app = create_adk_app()
    
    # Test locally first
    local_success = test_locally(app)
    if not local_success:
        print("Local testing failed. Please fix issues before deploying.")
        return
    
    # Deploy to Agent Engine
    remote_app = deploy_to_agent_engine(app)
    if not remote_app:
        print("Deployment failed. Please check your configuration.")
        return
    
    # Test remote deployment
    remote_success = test_remote_agent(remote_app)
    if remote_success:
        print("\n=== Deployment Complete ===")
        print(f"Your agent is deployed and accessible at:")
        print(f"Resource Name: {remote_app.resource_name}")
        print(f"Agent Engine UI: https://console.cloud.google.com/vertex-ai/agents/agent-engines")
        
        # Save deployment info
        with open("deployment_info.txt", "w") as f:
            f.write(f"Resource Name: {remote_app.resource_name}\n")
            f.write(f"Project ID: {PROJECT_ID}\n")
            f.write(f"Location: {LOCATION}\n")
            f.write(f"Deployment Time: {datetime.now()}\n")
        
        print("Deployment info saved to deployment_info.txt")
    else:
        print("Remote testing failed. Agent deployed but may have issues.")

if __name__ == "__main__":
    import datetime
    main()
