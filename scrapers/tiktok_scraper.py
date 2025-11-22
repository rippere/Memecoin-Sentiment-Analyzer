"""
TikTok Scraper - Using Correct Selectors
=========================================
Scrapes TikTok hashtag searches for meme coin analysis
Based on user's Instagram scraper architecture
"""

from scrapers.base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import logging
import re
import time

class TikTokScraper(BaseScraper):
    """
    TikTok hashtag scraper
    Uses selectors: #challenge-item-list and #column-item-video-container-{n}
    """
    
    BASE_URL = "https://www.tiktok.com"
    
    def scrape_hashtag(self, hashtag: str, max_results: int = 100) -> List[Dict]:
        """
        Scrape TikTok hashtag search
        
        Args:
            hashtag: Hashtag to search (with or without #)
            max_results: Maximum videos to collect
            
        Returns:
            List of video data dictionaries
        """
        # Clean hashtag
        hashtag = hashtag.replace('#', '').strip()
        url = f"{self.BASE_URL}/tag/{hashtag}"
        
        logging.info(f"🎵 Scraping TikTok hashtag: #{hashtag}")
        logging.info(f"   URL: {url}")
        
        self.driver.get(url)
        self.random_delay(4, 6)  # Let page fully load
        
        videos_data = []
        previous_count = 0
        stale_scrolls = 0
        max_stale_scrolls = 3
        
        while len(videos_data) < max_results and stale_scrolls < max_stale_scrolls:
            # Wait for video container to load
            container = self.wait_for_element(By.ID, "challenge-item-list", timeout=10)
            
            if not container:
                logging.warning("Could not find challenge-item-list container")
                break
            
            # Parse current page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract videos using your selectors
            new_videos = self._extract_videos_from_page(soup, hashtag)
            
            # Add only unique videos
            existing_ids = {v['video_id'] for v in videos_data}
            for video in new_videos:
                if video['video_id'] not in existing_ids:
                    videos_data.append(video)
            
            # Check if we got new videos
            if len(videos_data) == previous_count:
                stale_scrolls += 1
                logging.info(f"   No new videos found (attempt {stale_scrolls}/{max_stale_scrolls})")
            else:
                stale_scrolls = 0
                logging.info(f"   Total videos collected: {len(videos_data)}")
            
            previous_count = len(videos_data)
            
            # Scroll to load more
            if len(videos_data) < max_results:
                self._scroll_page()
                self.random_delay(3, 5)  # Wait for new content to load
        
        logging.info(f"✅ Completed: {len(videos_data)} videos for #{hashtag}")
        return videos_data[:max_results]
    
    def _scroll_page(self):
        """Scroll down to load more videos"""
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.END)  # Scroll to bottom
            time.sleep(1)
            body.send_keys(Keys.PAGE_UP)  # Scroll up slightly to trigger load
        except Exception as e:
            logging.error(f"Error scrolling: {e}")
    
    def _extract_videos_from_page(self, soup: BeautifulSoup, hashtag: str) -> List[Dict]:
        """
        Extract video metadata from page HTML
        Uses your selectors: #challenge-item-list and #column-item-video-container-{n}
        """
        videos = []
        
        # Find parent container
        parent_container = soup.find(id='challenge-item-list')
        
        if not parent_container:
            logging.warning("Parent container #challenge-item-list not found")
            return videos
        
        # Find all video containers with pattern column-item-video-container-{number}
        video_containers = parent_container.find_all(
            'div', 
            id=re.compile(r'^column-item-video-container-\d+$')
        )
        
        logging.info(f"   Found {len(video_containers)} video containers on page")
        
        for i, container in enumerate(video_containers):
            try:
                video_data = self._extract_video_data(container, hashtag, i)
                
                if video_data and video_data.get('video_id'):
                    videos.append(video_data)
                
            except Exception as e:
                logging.error(f"   Error parsing video {i}: {e}")
                continue
        
        return videos
    
    def _extract_video_data(self, container, hashtag: str, index: int) -> Optional[Dict]:
        """Extract all data from a single video container"""
        
        # Find the main link (contains video URL)
        link = container.find('a', href=True)
        
        if not link:
            logging.debug(f"   No link found in container {index}")
            return None
        
        href = link.get('href', '')
        video_id = self._extract_video_id_from_url(href)
        
        if not video_id:
            logging.debug(f"   Could not extract video ID from: {href}")
            return None
        
        # Extract username from URL (format: /@username/video/1234567890)
        username = self._extract_username_from_url(href)
        
        # Extract caption/description
        caption = self._extract_caption(container)
        
        # Extract view count
        views = self._extract_views(container)
        
        video_data = {
            'video_id': video_id,
            'username': username,
            'video_url': f"{self.BASE_URL}{href}" if href.startswith('/') else href,
            'caption': caption,
            'views': views,
            'likes': 0,  # Not available in listing view
            'shares': 0,  # Not available in listing view
            'comments': 0,  # Not available in listing view
            'hashtag_searched': hashtag,
            'scraped_at': datetime.now(),
            'container_index': index,
        }
        
        logging.debug(f"   ✓ Video {index}: @{username} | {views:,} views")
        
        return video_data
    
    def _extract_video_id_from_url(self, url: str) -> Optional[str]:
        """Extract video ID from TikTok URL"""
        # URL format: /@username/video/1234567890
        match = re.search(r'/video/(\d+)', url)
        return match.group(1) if match else None
    
    def _extract_username_from_url(self, url: str) -> Optional[str]:
        """Extract username from TikTok URL"""
        # URL format: /@username/video/1234567890
        match = re.search(r'/@([^/]+)/video', url)
        return match.group(1) if match else None
    
    def _extract_caption(self, container) -> str:
        """Extract video caption/description"""
        try:
            # TikTok captions are often in <span> or <div> with specific attributes
            # Look for common patterns
            
            # Try data-e2e attribute
            caption_elem = container.find(attrs={'data-e2e': 'search-card-desc'})
            if caption_elem:
                return caption_elem.get_text(strip=True)
            
            # Try title attribute on link
            link = container.find('a', title=True)
            if link:
                return link.get('title', '')
            
            # Try finding any text content (fallback)
            text_divs = container.find_all('div', recursive=True)
            for div in text_divs:
                text = div.get_text(strip=True)
                if len(text) > 10 and len(text) < 300:  # Reasonable caption length
                    return text
            
            return ""
            
        except Exception as e:
            logging.debug(f"Error extracting caption: {e}")
            return ""
    
    def _extract_views(self, container) -> int:
        """
        Extract view count from container

        NOTE: TikTok frequently changes HTML structure. If views return 0:
        1. Set headless=False to inspect page
        2. Check HTML for view count elements
        3. Update selectors below
        """
        try:
            # Try multiple data-e2e attributes (TikTok uses different ones)
            data_e2e_attrs = [
                'search-card-video-view-count',
                'video-views',
                'browse-video-views',
                'search-video-views'
            ]

            for attr in data_e2e_attrs:
                views_elem = container.find(attrs={'data-e2e': attr})
                if views_elem:
                    count = self._parse_count(views_elem.get_text(strip=True))
                    if count > 0:
                        return count

            # Search all text for view count patterns
            all_text = container.get_text()

            # Pattern: number followed by K/M/B and "views"
            view_patterns = [
                r'([\d.]+[KMB])\s*views?',  # "1.2M views"
                r'(\d{1,3}(?:,\d{3})*)\s*views?',  # "1,234,567 views"
                r'([\d.]+[KMB])',  # Just "1.2M" without "views"
            ]

            for pattern in view_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    count = self._parse_count(match.group(1))
                    if count > 0:
                        logging.debug(f"   Found views via pattern: {match.group(1)} = {count:,}")
                        return count

            # If still not found, log for debugging
            if len(all_text) > 0:
                logging.debug(f"   Could not extract views from text: {all_text[:200]}")

            return 0

        except Exception as e:
            logging.debug(f"Error extracting views: {e}")
            return 0
    
    def _parse_count(self, count_str: str) -> int:
        """
        Convert abbreviated counts to integers
        Examples: '1.2M' -> 1200000, '123.4K' -> 123400
        """
        if not count_str:
            return 0
        
        count_str = count_str.strip().upper().replace(',', '').replace('VIEWS', '').strip()
        
        multipliers = {
            'K': 1_000,
            'M': 1_000_000,
            'B': 1_000_000_000,
        }
        
        for suffix, multiplier in multipliers.items():
            if suffix in count_str:
                try:
                    number = float(count_str.replace(suffix, ''))
                    return int(number * multiplier)
                except ValueError:
                    return 0
        
        # No suffix, try parsing as int
        try:
            return int(float(count_str))
        except ValueError:
            return 0
    
    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        Optional: Navigate to specific video to get detailed metrics
        (likes, shares, comments)
        
        This is slower but gets complete data
        """
        url = f"{self.BASE_URL}/video/{video_id}"
        
        logging.info(f"Fetching detailed metrics for video {video_id}")
        
        try:
            self.driver.get(url)
            self.random_delay(3, 5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract detailed metrics
            # Note: These selectors may need adjustment based on TikTok's current HTML
            details = {
                'likes': self._extract_detail_metric(soup, 'like'),
                'shares': self._extract_detail_metric(soup, 'share'),
                'comments': self._extract_detail_metric(soup, 'comment'),
            }
            
            return details
            
        except Exception as e:
            logging.error(f"Error fetching video details: {e}")
            return None
    
    def _extract_detail_metric(self, soup: BeautifulSoup, metric_type: str) -> int:
        """Extract like/share/comment counts from video page"""
        # This would need specific selectors for TikTok's video page
        # Leaving as placeholder for now
        return 0
