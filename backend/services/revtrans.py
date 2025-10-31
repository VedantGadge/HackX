# Convert text to gloss for video extraction and concatenation
import os
import logging
import openai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
assert api_key, "Please set OPENAI_API_KEY (e.g., in your shell or a .env file)."

# Use legacy OpenAI API for version 1.3.5
openai.api_key = api_key
logger.info("✅ OpenAI API key configured successfully")


# API Call
def text_to_gloss(sentence: str):
    logger.info("🤖 LLM Call: text_to_gloss - Input: %s", sentence)
    prompt = f"""
    You are a sign language gloss generator.
    Convert the following English sentence into simplified ASL gloss (UPPERCASE keywords only, drop articles like 'the', 'is'):
    
    Sentence: "{sentence}"
    Output gloss:
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0.2
    )
    
    gloss = response.choices[0].message.content.strip()
    logger.info("✅ LLM Response: text_to_gloss - Output: %s", gloss)
    return gloss


def gloss_to_english_llm(gloss_tokens):
    """Convert gloss tokens back to natural English sentence using LLM"""
    logger.info("🤖 LLM Call: gloss_to_english_llm - Input: %s", gloss_tokens)
    gloss_string = ' '.join(gloss_tokens)
    
    prompt = f"""
    You are a sign language interpreter. Convert the following ASL gloss tokens into a natural English sentence.
    
    Gloss tokens: {gloss_string}
    
    Provide a grammatically correct English sentence:
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.3
    )
    
    sentence = response.choices[0].message.content.strip()
    logger.info("✅ LLM Response: gloss_to_english_llm - Output: %s", sentence)
    return sentence


import os
import subprocess

# ============================================================================
# WLASL JSON-BASED VIDEO FETCHER - Dynamic video loading from WLASL dataset
# ============================================================================
# Instead of storing videos locally, this loads them on-demand from the
# WLASL JSON mapper, allowing access to 70k+ videos

from dynamic_video_fetcher import WLASLVideoFetcher

# Initialize the WLASL fetcher (loads JSON mapper)
try:
    wlasl_fetcher = WLASLVideoFetcher()
    logger.info("✅ WLASL Video Fetcher initialized - access to 2000+ glosses")
except Exception as e:
    logger.error(f"❌ Failed to initialize WLASL Fetcher: {e}")
    logger.warning("⚠️ Will not be able to fetch videos from WLASL")
    wlasl_fetcher = None


def gloss_to_video_list(gloss_text, source="aslbrick", max_per_word=1):
    """
    Convert gloss text to video list using WLASL JSON mapper.
    Dynamically fetches videos from WLASL dataset.
    
    Args:
        gloss_text: Space-separated gloss words (e.g., "apple book dog")
        source: Video source to use (default: "aslbrick" - recommended)
                Other options: "aslu", "handspeak", "signingsavvy", etc.
        max_per_word: Maximum number of video variations per word (default: 1)
    
    Returns:
        List of video file paths (from cache after download)
    """
    if not wlasl_fetcher:
        logger.error("❌ WLASL Fetcher not available - cannot fetch videos")
        return []
    
    words = gloss_text.lower().split()
    video_files = []
    
    logger.info(f"🔍 Fetching videos for gloss: '{gloss_text}' (source: {source})")
    
    for word in words:
        try:
            logger.info(f"  📹 Fetching videos for word: '{word}'")
            
            # Get videos for this word from WLASL
            videos = wlasl_fetcher.get_video_paths_for_gloss(
                word, 
                source=source, 
                max_videos=max_per_word
            )
            
            if videos:
                logger.info(f"  ✅ Found {len(videos)} video(s) for '{word}'")
                video_files.extend(videos)
            else:
                logger.warning(f"  ⚠️ No videos found for '{word}' from source '{source}'")
                
        except Exception as e:
            logger.error(f"  ❌ Error fetching video for '{word}': {e}")
    
    logger.info(f"📊 Total videos to concatenate: {len(video_files)}")
    return video_files


def create_concat_file(video_files, list_file="videos_to_concat.txt"):
    """
    Create FFmpeg concat demuxer file.
    
    Args:
        video_files: List of video file paths
        list_file: Output filename for concat list
    
    Returns:
        Path to concat list file
    """
    with open(list_file, "w") as f:
        for vf in video_files:
            # Escape paths properly for FFmpeg
            escaped_path = vf.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
    
    logger.info(f"✅ Created concat file: {list_file} ({len(video_files)} videos)")
    return list_file


def concat_videos(video_files, output_file="output.mp4"):
    """
    Concatenate video files using FFmpeg.
    
    Args:
        video_files: List of video file paths to concatenate
        output_file: Output video filename
    
    Returns:
        True if successful, False otherwise
    """
    if not video_files:
        logger.warning("⚠️ No videos found for concatenation")
        return False
    
    list_file = create_concat_file(video_files)
    
    try:
        logger.info(f"🎬 Starting FFmpeg concatenation of {len(video_files)} videos...")
        result = subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", list_file, "-c", "copy", output_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ Concatenated video saved as {output_file}")
            return True
        else:
            logger.error(f"❌ FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to concatenate videos: {e}")
        return False
    finally:
        # Clean up concat list file
        if os.path.exists(list_file):
            os.remove(list_file)
            logger.debug(f"🧹 Cleaned up concat file: {list_file}")



def concat_videos_speed(video_files, output_file, speed=1.0):
    """
    Concatenate videos with speed adjustment using FFmpeg.
    
    Args:
        video_files: List of video file paths to concatenate
        output_file: Output video filename
        speed: Playback speed multiplier (e.g., 1.5 for 1.5x speed)
    
    Returns:
        True if successful, False otherwise
    """
    if not video_files:
        logger.warning("⚠️ No videos to concatenate")
        return False
    
    list_file = create_concat_file(video_files)
    speed_filter = f"setpts={1/speed}*PTS"
    
    try:
        logger.info(f"🎬 Concatenating {len(video_files)} videos at {speed}x speed...")
        result = subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-filter:v", speed_filter,
            "-an",  # remove audio
            output_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ Concatenated video saved as {output_file} (speed ×{speed})")
            return True
        else:
            logger.error(f"❌ FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to concatenate videos: {e}")
        return False
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)



# Function to convert sentence to gloss tokens
def sentence_to_gloss_tokens(sentence, available_tokens=None):
    """Convert sentence to gloss and return tokens list"""
    logger.info("🤖 LLM Call: sentence_to_gloss_tokens - Input: %s", sentence)
    gloss = text_to_gloss(sentence)
    tokens = gloss.lower().split()
    
    # Filter by available tokens if provided
    if available_tokens:
        original_count = len(tokens)
        tokens = [token for token in tokens if token in available_tokens]
        logger.info("🔍 Filtered tokens from %d to %d based on available videos", original_count, len(tokens))
    
    logger.info("✅ LLM Response: sentence_to_gloss_tokens - Output: %s", tokens)
    return tokens


# Standalone execution (only when run directly)
if __name__ == "__main__":
    print("\n" + "="*70)
    print("  INTELLIFY: Text to Sign Language Video Conversion")
    print("  Powered by WLASL Dataset (2000+ glosses, 70k+ videos)")
    print("="*70 + "\n")
    
    try:
        print('Enter text to convert to sign language video:')
        sentence = input(">>> ").strip()
        
        if not sentence:
            print("❌ No text provided")
            exit(1)
        
        logger.info(f"\n📝 Processing: '{sentence}'")
        
        # Convert text to gloss
        print("\n🤖 Converting text to ASL gloss...")
        gloss = text_to_gloss(sentence)
        print(f"✅ Generated gloss: {gloss}\n")
        
        # Fetch videos using WLASL mapper
        print("📹 Fetching videos from WLASL dataset...")
        video_files = gloss_to_video_list(gloss, source="aslbrick", max_per_word=1)
        
        if not video_files:
            print("\n❌ No videos found for the given text")
            print("   Available glosses in WLASL: apple, book, dog, family, work, school, etc.")
            print("   Try a sentence with common ASL words.")
            exit(1)
        
        # Ask for speed preference
        print(f"\n✅ Found {len(video_files)} video(s)")
        print("\nPlayback speed options:")
        print("  1 = Normal speed")
        print("  1.5 = 1.5x faster")
        print("  2 = 2x faster")
        print("  0.5 = Half speed")
        
        speed_input = input("Select speed (default 1): ").strip()
        speed = float(speed_input) if speed_input else 1.0
        
        # Concatenate videos
        output_file = "output.mp4"
        print(f"\n🎬 Creating video (speed: {speed}x)...")
        
        if speed == 1.0:
            success = concat_videos(video_files, output_file)
        else:
            success = concat_videos_speed(video_files, output_file, speed=speed)
        
        if success:
            print(f"\n{'='*70}")
            print(f"✅ SUCCESS! Video created: {output_file}")
            print(f"   Gloss: {gloss}")
            print(f"   Videos: {len(video_files)}")
            print(f"   Speed: {speed}x")
            print(f"{'='*70}\n")
        else:
            print("\n❌ Failed to create video")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        exit(1)
