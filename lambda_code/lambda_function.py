import json
import os
import sys
import time
from datetime import datetime

# Add all project subdirectories to the Python path
# This allows the Lambda function to find the agent and utility modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Now, import our project modules
try:
    from cto_agent import CTOAgent
    from cmo_agent import CMOAgent
    from cfo_agent import CFOAgent
    from publisher_agent import PublisherAgent
    from logger import MissionLogger
    import config
except ImportError as e:
    # This helps debug packaging issues
    print(f"Error importing modules: {e}")
    print(f"Current sys.path: {sys.path}")
    # It's useful to list files to see if they were packaged correctly
    for root, dirs, files in os.walk('.'):
        for name in files:
            print(os.path.join(root, name))
    raise e


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    This function is triggered by Amazon EventBridge on a schedule.
    """

    logger = MissionLogger("AWS_Lambda_Mission_Control")

    # --- Define the daily book topic ---
    # The 'event' object can be used to pass in a topic from the trigger
    book_topic = event.get('topic', f"The Mystery of the {datetime.now().strftime('%A')} Comet")

    logger.info("=" * 60)
    logger.info("🚀 AWS LAMBDA MISSION ACTIVATED")
    logger.info(f"📚 Book Topic: {book_topic}")

    # Initialize Agents
    cto_agent = CTOAgent()
    cmo_agent = CMOAgent()
    cfo_agent = CFOAgent()
    publisher_agent = PublisherAgent()

    mission_start_time = time.time()
    mission_success = False

    try:
        # === PHASE 1: CONTENT CREATION (CTO) ===
        logger.info("\n🎯 PHASE 1: CONTENT CREATION (CTO)")
        cto_result = cto_agent.run_cto_tasks(book_topic)
        if not cto_result.get('success'):
            raise Exception(f"CTO Phase failed: {cto_result.get('error', 'Unknown Error')}")

        # === PHASE 2: MARKETING (CMO) ===
        logger.info("\n📈 PHASE 2: MARKETING CONTENT (CMO)")
        cmo_result = cmo_agent.run_cmo_tasks(book_topic)

        # === PHASE 3: PUBLISHING PREP (Publisher) ===
        logger.info("\n🚀 PHASE 3: KDP PUBLISHING PREPARATION (PublisherAgent)")
        book_file_path = cto_result.get('kpf_path')
        if book_file_path:
            # Note: The PublisherAgent will intelligently fallback to creating
            # manual instructions, as browser automation is complex in base Lambda.
            publishing_result = publisher_agent.publish_to_kdp(book_file_path)
        else:
            publishing_result = {'success': False, 'error': 'No book file path from CTO.'}

        # === PHASE 4: FINANCIALS & LOGGING (CFO) ===
        logger.info("\n📊 PHASE 4: LOGGING & ANALYTICS (CFO)")
        activity_data = {
            'book_topic': book_topic,
            'cto_success': cto_result.get('success', False),
            'cmo_success': cmo_result.get('success', False),
            'publishing_success': publishing_result.get('success', False),
            'mission_duration': time.time() - mission_start_time
        }
        cfo_agent.run_cfo_tasks(f"Completed AWS Lambda mission for '{book_topic}'", activity_data)

        mission_success = True

    except Exception as e:
        logger.error(f"💥 MISSION CONTROL CRITICAL ERROR: {e}")
        # Optionally, send an error notification here

    duration = time.time() - mission_start_time
    status = "✅ SUCCESS" if mission_success else "❌ FAILED"
    logger.info("\n" + "=" * 60)
    logger.info(f"MISSION COMPLETE - STATUS: {status} (Duration: {duration:.2f}s)")
    logger.info("=" * 60)

    # Return a response required by AWS Lambda
    return {
        'statusCode': 200 if mission_success else 500,
        'body': json.dumps({
            'status': status,
            'topic': book_topic,
            'duration_seconds': round(duration, 2)
        })
    }

