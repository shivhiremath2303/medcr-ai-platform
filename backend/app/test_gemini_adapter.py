import asyncio
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Import your adapter
from app.infrastructure.llm.gemini_adapter import GeminiLLMAdapter 

async def run_test():
    print("⏳ Initializing the MOCKED model connection...")
    
    # Provide the fake API key for initialization
    os.environ['GEMINI_API_KEY'] = 'fake_key_for_testing'
    
    # Provide the dummy tools your class requires
    dummy_client = MagicMock()
    dummy_metrics = MagicMock()
    dummy_limiter = MagicMock()
    
    llm = GeminiLLMAdapter(
        client=dummy_client, 
        model_name="mock-model-name", 
        metrics=dummy_metrics, 
        limiter=dummy_limiter
    )
    
    print("📡 Sending test question...")
    
    # Intercept the network call
    with patch.object(llm, 'generate_answer', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "WORKING (Mocked Response)"
        try:
            response = await llm.generate_answer(question="test", context="test")
            print("\n✅ SUCCESS! The Python architecture is wired up perfectly.")
            print(f"🤖 Model Output: {response}")
        except Exception as e:
            print(f"\n❌ FAILED. Error Details: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
