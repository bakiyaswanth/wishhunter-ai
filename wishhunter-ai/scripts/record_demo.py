import asyncio
import os
import shutil
import subprocess
from playwright.async_api import async_playwright

async def record():
    temp_dir = "/tmp/playwright_recording"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    print("Launching Chromium with video recording...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=temp_dir,
            record_video_size={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print("Navigating to http://localhost:8080...")
        await page.goto("http://localhost:8080", wait_until="networkidle")
        await asyncio.sleep(2.5)

        # -------------------------------------------------------------
        # Action 1: First Prompt (What the app does best: Buy vs Wait)
        # -------------------------------------------------------------
        prompt1 = "Should I buy OnePlus 12R now or wait?"
        print(f"Typing Prompt 1: '{prompt1}'...")
        await page.click("#input")
        await page.type("#input", prompt1, delay=40)
        await asyncio.sleep(0.5)

        print("Submitting Prompt 1...")
        await page.click("button[type='submit']")

        print("Waiting for WishHunter AI Verdict card to render...")
        await page.wait_for_selector(".a2card", timeout=60000)
        print("Verdict card rendered!")

        # Allow viewer to view the verdict details
        await asyncio.sleep(5)

        # -------------------------------------------------------------
        # Action 2: Second Prompt (Richer: Image Generation & Cloud Storage)
        # -------------------------------------------------------------
        prompt2 = "Generate a visualization image for the OnePlus 12R dream setup"
        print(f"Typing Prompt 2: '{prompt2}'...")
        await page.click("#input")
        await page.type("#input", prompt2, delay=35)
        await asyncio.sleep(0.5)

        print("Submitting Prompt 2...")
        await page.click("button[type='submit']")

        print("Waiting for generated image card to render...")
        await page.wait_for_selector(".a2img", timeout=75000)
        print("Generated image detected in A2UI card!")

        # Wait for image asset to fully load and decode
        await page.wait_for_function("() => { const img = document.querySelector('.a2img'); return img && img.complete && img.naturalHeight !== 0; }", timeout=20000)
        print("Generated image loaded successfully!")

        # Smooth scroll down to view image and content perfectly
        await page.evaluate("() => { const log = document.getElementById('log'); log.scrollTop = log.scrollHeight; }")
        await asyncio.sleep(6)

        video_path = await page.video.path()
        print(f"Raw video saved at: {video_path}")

        await context.close()
        await browser.close()

    # Convert to MP4
    output_artifact = "/config/.gemini/antigravity/brain/267b53dc-90c6-49b2-84e2-4169795c4ecb/wishhunter_ai_demo.mp4"
    output_workspace = "/config/Desktop/BuildWithGemini/wishhunter-ai/wishhunter_ai_demo.mp4"

    print(f"Converting {video_path} to MP4...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.0",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        output_artifact
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    shutil.copyfile(output_artifact, output_workspace)
    print(f"MP4 successfully generated at:\n- {output_artifact}\n- {output_workspace}")

if __name__ == "__main__":
    asyncio.run(record())
