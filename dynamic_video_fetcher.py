# Dynamic Video Fetcher using WLASL JSON Mapper
# Fetches ASL videos from URLs instead of local storage
import os
import json
import logging
import subprocess
import tempfile
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to WLASL mapper
MAPPER_PATH = os.path.join(os.path.dirname(__file__), "mapper", "WLASL_v0.3.json")
TEMP_VIDEO_DIR = tempfile.gettempdir()  # Use system temp directory for fetched videos

class WLASLVideoFetcher:
    """
    Fetches ASL videos dynamically from WLASL JSON mapper.
    Supports filtering by source (e.g., "aslbrick") and caching.
    """
    
    def __init__(self, mapper_path: str = MAPPER_PATH, cache_dir: Optional[str] = None):
        """
        Initialize the fetcher with WLASL mapper.
        
        Args:
            mapper_path: Path to WLASL_v0.3.json file
            cache_dir: Directory for caching downloaded videos (default: temp dir)
        """
        self.mapper_path = mapper_path
        self.cache_dir = cache_dir or os.path.join(TEMP_VIDEO_DIR, "asl_video_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.mapper_data = self._load_mapper()
        self.gloss_index = self._build_gloss_index()
        
        logger.info(f"✅ WLASL Fetcher initialized with {len(self.gloss_index)} glosses")
        logger.info(f"📁 Cache directory: {self.cache_dir}")
    
    def _load_mapper(self) -> List[Dict]:
        """Load WLASL JSON mapper file."""
        try:
            with open(self.mapper_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ Loaded WLASL mapper from {self.mapper_path}")
            return data
        except FileNotFoundError:
            logger.error(f"❌ Mapper file not found: {self.mapper_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in mapper: {e}")
            raise
    
    def _build_gloss_index(self) -> Dict[str, List[Dict]]:
        """Build an index mapping gloss -> list of instances."""
        index = {}
        for entry in self.mapper_data:
            gloss = entry.get("gloss", "").lower()
            if gloss:
                index[gloss] = entry.get("instances", [])
        return index
    
    def get_gloss_instances(self, gloss: str, source: str = "aslbrick") -> List[Dict]:
        """
        Get video instances for a gloss, optionally filtered by source.
        
        Args:
            gloss: The sign word (e.g., "apple")
            source: Video source filter (e.g., "aslbrick", "aslu", etc.)
        
        Returns:
            List of instance dictionaries containing video metadata
        """
        gloss_lower = gloss.lower()
        
        if gloss_lower not in self.gloss_index:
            logger.warning(f"⚠️ Gloss '{gloss}' not found in mapper")
            return []
        
        instances = self.gloss_index[gloss_lower]
        
        # Filter by source if specified
        if source:
            filtered = [i for i in instances if i.get("source") == source]
            logger.info(f"📹 Found {len(filtered)}/{len(instances)} '{gloss}' instances from source '{source}'")
            return filtered
        
        logger.info(f"📹 Found {len(instances)} instances for gloss '{gloss}'")
        return instances
    
    def download_video(self, url: str, video_id: str, gloss: str) -> Optional[str]:
        """
        Download a video from URL and cache it.
        
        Args:
            url: Video URL
            video_id: Unique video identifier
            gloss: The gloss this video belongs to
        
        Returns:
            Path to cached video file, or None if download failed
        """
        # Create cache filename based on video_id
        cache_file = os.path.join(self.cache_dir, f"{video_id}.mp4")
        
        # Return cached file if it exists
        if os.path.exists(cache_file):
            logger.info(f"✅ Using cached video: {cache_file}")
            return cache_file
        
        try:
            logger.info(f"📥 Downloading {gloss} (ID: {video_id}) from {url}")
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Write to cache
            with open(cache_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size_mb = os.path.getsize(cache_file) / (1024 * 1024)
            logger.info(f"✅ Downloaded {gloss} to cache ({file_size_mb:.2f} MB)")
            return cache_file
            
        except requests.RequestException as e:
            logger.error(f"❌ Failed to download {gloss} (ID: {video_id}): {e}")
            # Clean up partial file
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return None
    
    def get_videos_for_gloss(self, gloss: str, source: str = "aslbrick", 
                            max_videos: int = 1, download: bool = True) -> List[str]:
        """
        Get and optionally download videos for a gloss.
        
        Args:
            gloss: The sign word
            source: Video source filter
            max_videos: Maximum number of videos to fetch
            download: Whether to download videos (True) or just return URLs (False)
        
        Returns:
            List of video file paths (if download=True) or URLs (if download=False)
        """
        instances = self.get_gloss_instances(gloss, source)
        
        if not instances:
            logger.warning(f"⚠️ No videos found for gloss '{gloss}' from source '{source}'")
            return []
        
        # Limit to max_videos
        instances = instances[:max_videos]
        
        results = []
        for instance in instances:
            url = instance.get("url")
            video_id = instance.get("video_id")
            
            if not url or not video_id:
                logger.warning(f"⚠️ Missing URL or video_id in instance: {instance}")
                continue
            
            if download:
                video_path = self.download_video(url, video_id, gloss)
                if video_path:
                    results.append(video_path)
            else:
                results.append(url)
        
        return results
    
    def get_video_urls_for_gloss(self, gloss: str, source: str = "aslbrick",
                                max_videos: int = 1) -> List[str]:
        """
        Get video URLs for a gloss without downloading.
        
        Args:
            gloss: The sign word
            source: Video source filter
            max_videos: Maximum number of video URLs to fetch
        
        Returns:
            List of video URLs
        """
        return self.get_videos_for_gloss(gloss, source, max_videos, download=False)
    
    def get_video_paths_for_gloss(self, gloss: str, source: str = "aslbrick",
                                 max_videos: int = 1) -> List[str]:
        """
        Get video file paths for a gloss, downloading if necessary.
        
        Args:
            gloss: The sign word
            source: Video source filter
            max_videos: Maximum number of videos to download
        
        Returns:
            List of video file paths
        """
        return self.get_videos_for_gloss(gloss, source, max_videos, download=True)
    
    def get_videos_for_gloss_tokens(self, gloss_tokens: List[str], source: str = "aslbrick",
                                    max_per_gloss: int = 1, skip_missing: bool = True) -> Dict[str, List[str]]:
        """
        Get videos for multiple gloss tokens (useful for sentence to video).
        
        Args:
            gloss_tokens: List of sign words
            source: Video source filter
            max_per_gloss: Max videos per gloss
            skip_missing: If True, skip glosses not in mapper; if False, raise error
        
        Returns:
            Dictionary mapping gloss -> list of video file paths
        """
        result = {}
        
        for token in gloss_tokens:
            videos = self.get_video_paths_for_gloss(token, source, max_per_gloss)
            
            if not videos and not skip_missing:
                raise ValueError(f"No videos found for gloss '{token}'")
            
            if videos:
                result[token] = videos
            else:
                logger.warning(f"⚠️ Skipping token '{token}' - no videos found")
        
        return result
    
    def create_concat_file(self, video_files: List[str], 
                          list_file: str = "videos_to_concat.txt") -> str:
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
                # Escape single quotes in path
                escaped_path = vf.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
        
        logger.info(f"✅ Created concat file: {list_file} ({len(video_files)} videos)")
        return list_file
    
    def concatenate_videos(self, video_files: List[str], output_file: str = "output.mp4") -> bool:
        """
        Concatenate video files using FFmpeg.
        
        Args:
            video_files: List of video file paths to concatenate
            output_file: Output video filename
        
        Returns:
            True if successful, False otherwise
        """
        if not video_files:
            logger.warning("⚠️ No videos to concatenate")
            return False
        
        list_file = self.create_concat_file(video_files)
        
        try:
            logger.info(f"🎬 Concatenating {len(video_files)} videos...")
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
    
    def gloss_tokens_to_video(self, gloss_tokens: List[str], output_file: str = "output.mp4",
                             source: str = "aslbrick", max_per_gloss: int = 1,
                             skip_missing: bool = True) -> Optional[str]:
        """
        Convert gloss tokens to a concatenated video.
        
        Args:
            gloss_tokens: List of sign words
            output_file: Output video filename
            source: Video source filter
            max_per_gloss: Max videos per gloss
            skip_missing: Whether to skip glosses not found
        
        Returns:
            Path to output video if successful, None otherwise
        """
        logger.info(f"🔤 Converting {len(gloss_tokens)} gloss tokens to video...")
        
        # Get videos for each token
        gloss_video_map = self.get_videos_for_gloss_tokens(
            gloss_tokens, source, max_per_gloss, skip_missing
        )
        
        if not gloss_video_map:
            logger.warning("⚠️ No videos found for any gloss tokens")
            return None
        
        # Flatten to single video list (in order of gloss_tokens)
        video_files = []
        for token in gloss_tokens:
            if token in gloss_video_map:
                video_files.extend(gloss_video_map[token])
        
        # Concatenate
        if self.concatenate_videos(video_files, output_file):
            logger.info(f"✅ Generated video: {output_file}")
            return output_file
        else:
            logger.error("❌ Failed to generate video")
            return None
    
    def clear_cache(self) -> int:
        """
        Clear all cached videos.
        
        Returns:
            Number of files deleted
        """
        count = 0
        for file in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    count += 1
            except Exception as e:
                logger.error(f"❌ Failed to delete {file_path}: {e}")
        
        logger.info(f"✅ Cleared cache: {count} files deleted")
        return count


# Standalone usage example
if __name__ == "__main__":
    try:
        # Initialize fetcher
        fetcher = WLASLVideoFetcher()
        
        # Example 1: Get videos for a single gloss
        print("\n=== Example 1: Single Gloss ===")
        gloss = "apple"
        videos = fetcher.get_video_paths_for_gloss(gloss, source="aslbrick", max_videos=2)
        print(f"Videos for '{gloss}': {videos}")
        
        # Example 2: Get videos for multiple glosses
        print("\n=== Example 2: Multiple Glosses ===")
        tokens = ["apple", "book", "dog"]
        gloss_map = fetcher.get_videos_for_gloss_tokens(tokens, source="aslbrick", max_per_gloss=1)
        for token, videos in gloss_map.items():
            print(f"  {token}: {len(videos)} video(s)")
        
        # Example 3: Generate video from gloss tokens
        print("\n=== Example 3: Generate Video from Tokens ===")
        tokens = ["book", "apple"]
        output = fetcher.gloss_tokens_to_video(tokens, output_file="sample_output.mp4", source="aslbrick")
        if output:
            print(f"✅ Generated: {output}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
