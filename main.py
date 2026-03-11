import asyncio
import traceback
import logging
from videosdk.agents import Agent, AgentSession, RealTimePipeline, JobContext, RoomOptions, WorkerJob, Options
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
load_dotenv()


class MyVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""Rauru ek helpful AI assistant bani jo phone calls attend kare hein.
            Hamesha sirf Bhojpuri mein baat karein.
            Apna jawab chhota aur friendly rakhein.
            Agar user koi aur bhasha mein bole, tab bhi aap Bhojpuri mein hi jawab dein.""",
        )

    async def on_enter(self) -> None:
        # Wait for Gemini WebSocket to be fully ready before sending greeting
        await asyncio.sleep(1.5)
        await self.session.say("Pranam! Hum raura AI assistant bani. Rauru ke ka seva kar sakile?")

    async def on_exit(self) -> None:
        await self.session.say("Bahut dhanyawad! Rauru se baat kar ke bahut acha lagal. Phir milal jaai!")


async def start_session(context: JobContext):
    model = GeminiRealtime(
        model="gemini-2.5-flash-native-audio-preview-12-2025",
        api_key=os.getenv("GOOGLE_API_KEY"),
        config=GeminiLiveConfig(
            voice="Leda",
            response_modalities=["AUDIO"]
        )
    )
    pipeline = RealTimePipeline(model=model)
    session = AgentSession(agent=MyVoiceAgent(), pipeline=pipeline)

    # Fix: bypass the SIP audio-stream delay so on_enter fires immediately.
    # Without this, the SDK waits for AUDIO_STREAM_ENABLED before greeting the
    # caller — but Twilio drops the call due to silence before that event fires.
    session._should_delay_for_sip_user = lambda: False

    try:
        await context.connect()
        await session.start()
        await asyncio.Event().wait()
    except Exception as e:
        logging.error(f"Session error: {e}")
        traceback.print_exc()
    finally:
        await session.close()
        await context.shutdown()


def on_room_error(error):
    logging.error(f"Room error: {error}")


def make_context() -> JobContext:
    room_options = RoomOptions(
        auto_end_session=False,
        session_timeout_seconds=300,
        on_room_error=on_room_error
    )
    return JobContext(room_options=room_options)


if __name__ == "__main__":
    try:
        options = Options(
            agent_id="MyTelephonyAgent",
            register=True,
            max_processes=10,
            host="localhost",
            port=8081,
        )
        job = WorkerJob(entrypoint=start_session, jobctx=make_context, options=options)
        job.start()
    except Exception as e:
        traceback.print_exc()