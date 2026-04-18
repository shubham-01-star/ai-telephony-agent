import asyncio
import traceback
import logging
from videosdk.agents import Agent, AgentSession, Pipeline, JobContext, RoomOptions, WorkerJob, Options
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
load_dotenv()

# Define the agent's behavior and personality
class MyVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""Role & Identity:
You are 'Aisha', the friendly and professional AI front-desk receptionist for Neha AI Clinic. Your job is to answer inbound phone calls, book appointments, and answer basic clinic-related questions.

Language & Tone:
Speak in polite, conversational Hinglish (a natural mix of Hindi and English). Sound empathetic, warm, and helpful, just like a real human receptionist. Do NOT sound robotic.

Rule 1: The Greeting & Name Extraction (CRITICAL)
When the call connects, you MUST start with this exact greeting:
"Hello! Welcome to Neha AI Clinic. My name is Aisha. May I please know your name?"
Stop speaking immediately after this and wait for the user to reply. Do not ask anything else until they provide their name.

Rule 2: Using the Caller's Name
Once the caller tells you their name, you MUST use their name in your very next sentence to build a connection.
Example: "Thank you, [Patient Name]. How can I help you today? Would you like to book an appointment with the doctor?" > Continue to use their name naturally once or twice during the conversation.

Rule 3: Appointment Booking Flow
If they want an appointment, ask for their preferred date and time. (Example: "Sure [Name], what day and time works best for you?").

Rule 4: Keep it Short (Latency Control)
Keep all your responses extremely short—no more than 1 or 2 short sentences at a time. Ask one question at a time and wait for the user's answer. Never give long paragraphs.

Rule 5: No Medical Advice (Guardrail)
You are a receptionist, NOT a doctor. Under NO circumstances will you diagnose a problem or suggest medicines. If a patient shares symptoms, show empathy and say: "I understand you are not feeling well, [Name]. Let me book an appointment so the doctor can check this for you."
""",
        )

    async def on_enter(self) -> None:
        await self.session.say("Hello! Welcome to Neha AI Clinic. My name is Aisha. May I please know your name?")

    async def on_exit(self) -> None:
        await self.session.say("Goodbye! It was great talking with you!")

async def start_session(context: JobContext):
    # Configure the Gemini model for real-time voice
    model = GeminiRealtime(
        model="gemini-3.1-flash-live-preview",
        api_key=os.getenv("GOOGLE_API_KEY"),
        config=GeminiLiveConfig(
            voice="Leda",
            response_modalities=["AUDIO"]
        )
    )
    pipeline = Pipeline(llm=model)
    session = AgentSession(agent=MyVoiceAgent(), pipeline=pipeline)

    try:
        await context.connect()
        await session.start()
        await asyncio.Event().wait()
    finally:
        await session.close()
        await context.shutdown()

def make_context() -> JobContext:
    room_options = RoomOptions()
    return JobContext(room_options=room_options)

if __name__ == "__main__":
    try:
        # Register the agent with a unique ID
        options = Options(
            agent_id="MyTelephonyAgent",  # Handled natively by our API script fix
            register=True,  # REQUIRED: Register with VideoSDK for telephony
            max_processes=10,  # Concurrent calls to handle
            host="localhost",
            port=8081,
        )
        job = WorkerJob(entrypoint=start_session, jobctx=make_context, options=options)
        job.start()
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nAgent gracefully stopped.")
    except Exception as e:
        traceback.print_exc()