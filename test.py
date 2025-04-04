# Save this as test_slurm.py
import os
import sys
import pyslurm
from dotenv import load_dotenv

load_dotenv('.env')

def test_slurm_connection():
    print("Testing Slurm connection...")
    try:
        nodes = pyslurm.node().get()
        print(f"✅ Successfully connected to Slurm! Found {len(nodes)} nodes.")
        
        if nodes:
            first_node = list(nodes.items())[0]
            print(f"\nSample node information ({first_node[0]}):")
            for k, v in first_node[1].items():
                if not isinstance(v, (list, dict)) or len(str(v)) < 100:
                    print(f"  {k}: {v}")
        
        jobs = pyslurm.job().get()
        print(f"\n✅ Successfully retrieved job information! Found {len(jobs)} jobs.")
        
        return True
    except ValueError as e:
        print(f"❌ Failed to connect to Slurm: {e}")
    except Exception as e:
        print(f"❌ Unknown error accessing Slurm: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def test_slack_connection():
    print("\nTesting Slack connection...")
    try:
        from slack_sdk import WebClient
        client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        response = client.auth_test()
        print(f"✅ Successfully connected to Slack as: {response['user']}")
        return True
    except Exception as e:
        print(f"❌ Error connecting to Slack: {e}")
        return False

if __name__ == "__main__":
    print("=== SusBot Diagnostic Tool ===\n")
    
    # Check environment variables
    print("Checking environment variables...")
    slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_app_token = os.environ.get("SLACK_APP_TOKEN")
    
    print(f"SLACK_BOT_TOKEN exists: {'✅' if slack_bot_token else '❌'}")
    print(f"SLACK_APP_TOKEN exists: {'✅' if slack_app_token else '❌'}")
    
    slurm_ok = test_slurm_connection()
    slack_ok = test_slack_connection()
    
    print("\n=== Diagnostic Summary ===")
    print(f"Slack connection: {'✅ OK' if slack_ok else '❌ FAILED'}")
    print(f"Slurm connection: {'✅ OK' if slurm_ok else '❌ FAILED'}")
    
    if not slurm_ok:
        print("\nTroubleshooting Slurm connection:")
        print("1. Make sure pyslurm is installed: pip install pyslurm")
        print("2. Verify you're running this on a host that can connect to the Slurm controller")
        print("3. Check if your user has proper permissions to query Slurm")
    
    if not slack_ok:
        print("\nTroubleshooting Slack connection:")
        print("1. Check your SLACK_BOT_TOKEN and SLACK_APP_TOKEN in the .env file")
        print("2. Verify your bot has proper OAuth scopes configured in the Slack API dashboard")
        print("3. Ensure your firewall allows outbound connections to Slack APIs")