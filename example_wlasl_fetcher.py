#!/usr/bin/env python3
"""
Example script demonstrating the WLASL Dynamic Video Fetcher
Run this to test the integration before using in your main app
"""

import os
import sys
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def example_1_basic_setup():
    """Example 1: Basic setup and initialization"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Setup and Initialization")
    print("="*60)
    
    try:
        from dynamic_video_fetcher import WLASLVideoFetcher
        
        logger.info("Initializing WLASLVideoFetcher...")
        fetcher = WLASLVideoFetcher()
        
        logger.info(f"✅ Fetcher initialized successfully")
        logger.info(f"📊 Statistics:")
        logger.info(f"   - Total glosses: {len(fetcher.gloss_index)}")
        logger.info(f"   - Cache directory: {fetcher.cache_dir}")
        
        return fetcher
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        return None


def example_2_get_gloss_instances(fetcher):
    """Example 2: Get video instances for a gloss"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Get Video Instances for a Gloss")
    print("="*60)
    
    if not fetcher:
        logger.error("Fetcher not initialized")
        return
    
    try:
        gloss = "apple"
        logger.info(f"Getting instances for gloss: '{gloss}'")
        
        # Get from aslbrick source
        instances = fetcher.get_gloss_instances(gloss, source="aslbrick")
        
        logger.info(f"✅ Found {len(instances)} instances from aslbrick")
        
        # Show first 3
        for i, instance in enumerate(instances[:3], 1):
            logger.info(f"\n   Instance {i}:")
            logger.info(f"     - Video ID: {instance.get('video_id')}")
            logger.info(f"     - Signer: {instance.get('signer_id')}")
            logger.info(f"     - Split: {instance.get('split')}")
            logger.info(f"     - Source: {instance.get('source')}")
            logger.info(f"     - URL: {instance.get('url')[:60]}...")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")


def example_3_download_single_video(fetcher):
    """Example 3: Download a single video"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Download a Single Video")
    print("="*60)
    
    if not fetcher:
        logger.error("Fetcher not initialized")
        return
    
    try:
        gloss = "book"
        logger.info(f"Downloading video for '{gloss}'...")
        
        videos = fetcher.get_video_paths_for_gloss(gloss, source="aslbrick", max_videos=1)
        
        if videos:
            logger.info(f"✅ Successfully downloaded")
            logger.info(f"   Path: {videos[0]}")
            logger.info(f"   Size: {os.path.getsize(videos[0]) / (1024*1024):.2f} MB")
        else:
            logger.warning(f"⚠️ No videos found for '{gloss}'")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")


def example_4_multiple_glosses(fetcher):
    """Example 4: Get videos for multiple glosses"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Videos for Multiple Glosses")
    print("="*60)
    
    if not fetcher:
        logger.error("Fetcher not initialized")
        return
    
    try:
        tokens = ["apple", "dog", "book", "eat"]
        logger.info(f"Getting videos for {len(tokens)} glosses: {tokens}")
        
        gloss_map = fetcher.get_videos_for_gloss_tokens(
            tokens, 
            source="aslbrick", 
            max_per_gloss=1,
            skip_missing=True
        )
        
        logger.info(f"✅ Retrieved videos for {len(gloss_map)} glosses")
        for gloss, videos in gloss_map.items():
            logger.info(f"   - {gloss}: {len(videos)} video(s)")
            
        return gloss_map
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None


def example_5_concatenate_videos(fetcher, gloss_map):
    """Example 5: Concatenate videos into a single file"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Concatenate Videos")
    print("="*60)
    
    if not fetcher or not gloss_map:
        logger.error("Missing fetcher or gloss_map")
        return
    
    try:
        # Flatten videos in order
        video_files = []
        for gloss in ["apple", "dog", "book", "eat"]:
            if gloss in gloss_map:
                video_files.extend(gloss_map[gloss])
        
        output_file = "example_output.mp4"
        logger.info(f"Concatenating {len(video_files)} videos...")
        logger.info(f"Output file: {output_file}")
        
        success = fetcher.concatenate_videos(video_files, output_file)
        
        if success:
            file_size = os.path.getsize(output_file) / (1024*1024)
            logger.info(f"✅ Successfully concatenated")
            logger.info(f"   Output: {output_file}")
            logger.info(f"   Size: {file_size:.2f} MB")
        else:
            logger.error(f"❌ Failed to concatenate")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")


def example_6_different_sources(fetcher):
    """Example 6: Try different video sources"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Different Video Sources")
    print("="*60)
    
    if not fetcher:
        logger.error("Fetcher not initialized")
        return
    
    try:
        gloss = "apple"
        sources = ["aslbrick", "aslu", "handspeak", "signingsavvy"]
        
        logger.info(f"Checking '{gloss}' across different sources...")
        
        for source in sources:
            instances = fetcher.get_gloss_instances(gloss, source=source)
            logger.info(f"   {source:15} : {len(instances):3} videos")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")


def example_7_gloss_tokens_to_video(fetcher):
    """Example 7: Convert gloss tokens directly to video"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Gloss Tokens to Video (End-to-End)")
    print("="*60)
    
    if not fetcher:
        logger.error("Fetcher not initialized")
        return
    
    try:
        tokens = ["book", "apple"]
        output_file = "gloss_tokens_output.mp4"
        
        logger.info(f"Converting gloss tokens to video: {tokens}")
        logger.info(f"Output: {output_file}")
        
        result = fetcher.gloss_tokens_to_video(
            tokens, 
            output_file=output_file,
            source="aslbrick",
            max_per_gloss=1
        )
        
        if result:
            file_size = os.path.getsize(result) / (1024*1024)
            logger.info(f"✅ Successfully generated video")
            logger.info(f"   File: {result}")
            logger.info(f"   Size: {file_size:.2f} MB")
        else:
            logger.error(f"❌ Failed to generate video")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")


def example_8_cache_management(fetcher):
    """Example 8: Cache management"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Cache Management")
    print("="*60)
    
    if not fetcher:
        logger.error("Fetcher not initialized")
        return
    
    try:
        cache_dir = fetcher.cache_dir
        cache_files = os.listdir(cache_dir)
        cache_size = sum(
            os.path.getsize(os.path.join(cache_dir, f)) 
            for f in cache_files
        ) / (1024*1024)
        
        logger.info(f"📊 Cache Status:")
        logger.info(f"   Directory: {cache_dir}")
        logger.info(f"   Files: {len(cache_files)}")
        logger.info(f"   Size: {cache_size:.2f} MB")
        
        if cache_files:
            logger.info(f"\n   Sample files:")
            for f in cache_files[:5]:
                file_path = os.path.join(cache_dir, f)
                size = os.path.getsize(file_path) / (1024*1024)
                logger.info(f"   - {f} ({size:.2f} MB)")
        
        # Option to clear cache
        user_input = input("\nClear cache? (y/n): ").strip().lower()
        if user_input == 'y':
            deleted = fetcher.clear_cache()
            logger.info(f"✅ Cleared cache: {deleted} files deleted")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")


def example_9_integration_with_revtrans(fetcher):
    """Example 9: Integration with existing revtrans.py"""
    print("\n" + "="*60)
    print("EXAMPLE 9: Integration with revtrans.py")
    print("="*60)
    
    try:
        logger.info("Testing integration with revtrans...")
        
        # Example: how revtrans.py would use fetcher
        gloss_text = "apple book dog"
        logger.info(f"Input gloss: '{gloss_text}'")
        
        words = gloss_text.lower().split()
        video_files = []
        
        for word in words:
            videos = fetcher.get_video_paths_for_gloss(word, source="aslbrick", max_videos=1)
            if videos:
                video_files.extend(videos)
                logger.info(f"✅ Found video for '{word}'")
            else:
                logger.warning(f"⚠️ No video for '{word}'")
        
        logger.info(f"✅ Integration test successful")
        logger.info(f"   Total videos to concatenate: {len(video_files)}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  WLASL Dynamic Video Fetcher - Example Suite  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Run examples
    fetcher = example_1_basic_setup()
    
    if fetcher:
        example_2_get_gloss_instances(fetcher)
        example_3_download_single_video(fetcher)
        
        gloss_map = example_4_multiple_glosses(fetcher)
        if gloss_map:
            example_5_concatenate_videos(fetcher, gloss_map)
        
        example_6_different_sources(fetcher)
        example_7_gloss_tokens_to_video(fetcher)
        example_8_cache_management(fetcher)
        example_9_integration_with_revtrans(fetcher)
        
        print("\n" + "="*60)
        print("✅ All examples completed!")
        print("="*60)
    else:
        print("\n❌ Failed to initialize fetcher")
        print("Check that mapper/WLASL_v0.3.json exists")


if __name__ == "__main__":
    main()
