"""
Reddit Scraper
==============
Scrapes Reddit using old.reddit.com (simpler HTML, more stable)
No API required, no authentication needed for public posts
"""

from scrapers.base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import logging
import re

class RedditScraper(BaseScraper):
    """
    Reddit scraper using old.reddit.com
    Much simpler and more reliable than new Reddit
    """
    
    BASE_URL = "https://old.reddit.com"
    
    def scrape_subreddit_search(
        self, 
        subreddit: str, 
        query: str, 
        max_results: int = 50,
        sort: str = 'new'
    ) -> List[Dict]:
        """
        Search a subreddit for posts mentioning a query
        
        Args:
            subreddit: Subreddit name (without r/)
            query: Search term
            max_results: Maximum posts to return
            sort: Sort order (new, hot, top, relevance)
            
        Returns:
            List of post dictionaries
        """
        # Build search URL
        url = f"{self.BASE_URL}/r/{subreddit}/search"
        params = f"?q={query}&restrict_sr=1&sort={sort}&t=all"
        full_url = url + params
        
        logging.info(f"🤖 Scraping r/{subreddit} for '{query}'")
        logging.info(f"   URL: {full_url}")
        
        try:
            self.driver.get(full_url)
            self.random_delay(2, 4)
            
            # Wait for results to load
            self.wait_for_element(By.CLASS_NAME, "search-result", timeout=10)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract posts
            posts = self._extract_posts(soup, subreddit, query)
            
            logging.info(f"✅ Found {len(posts)} posts in r/{subreddit}")
            
            return posts[:max_results]
            
        except Exception as e:
            logging.error(f"❌ Error scraping r/{subreddit}: {e}")
            return []
    
    def scrape_multiple_subreddits(
        self,
        subreddits: List[str],
        query: str,
        max_per_subreddit: int = 20
    ) -> List[Dict]:
        """
        Search multiple subreddits for the same query
        
        Args:
            subreddits: List of subreddit names
            query: Search term
            max_per_subreddit: Max posts per subreddit
            
        Returns:
            Combined list of posts
        """
        all_posts = []
        
        for subreddit in subreddits:
            posts = self.scrape_subreddit_search(
                subreddit, 
                query, 
                max_results=max_per_subreddit
            )
            all_posts.extend(posts)
            
            # Polite delay between subreddits
            self.random_delay(2, 4)
        
        logging.info(f"✅ Total posts collected: {len(all_posts)}")
        return all_posts
    
    def _extract_posts(
        self, 
        soup: BeautifulSoup, 
        subreddit: str, 
        query: str
    ) -> List[Dict]:
        """
        Extract post data from old Reddit search results HTML
        Old Reddit has simple, stable class names
        """
        posts = []
        
        # Find all post containers
        # Old Reddit uses class="search-result" or "thing"
        post_containers = soup.find_all('div', class_='search-result')
        
        if not post_containers:
            # Fallback to "thing" class (older structure)
            post_containers = soup.find_all('div', class_='thing')
        
        logging.info(f"   Parsing {len(post_containers)} post containers...")
        
        for i, container in enumerate(post_containers):
            try:
                post_data = self._extract_post_data(container, subreddit, query, i)
                
                if post_data:
                    posts.append(post_data)
                
            except Exception as e:
                logging.error(f"   Error parsing post {i}: {e}")
                continue
        
        return posts
    
    def _extract_post_data(
        self, 
        container, 
        subreddit: str, 
        query: str, 
        index: int
    ) -> Dict:
        """Extract all data from a single post container"""
        
        post_data = {
            'post_id': container.get('data-fullname', f'unknown_{index}'),
            'post_url': self._extract_post_url(container),
            'title': self._extract_title(container),
            'author': self._extract_author(container),
            'score': self._extract_score(container),
            'num_comments': self._extract_comment_count(container),
            'created_utc': self._extract_timestamp(container),
            'subreddit': subreddit,
            'flair': self._extract_flair(container),
            'is_self': self._is_self_post(container),
            'query': query,
            'scraped_at': datetime.now(),
        }
        
        logging.debug(
            f"   ✓ Post {index}: {post_data['score']} pts | "
            f"{post_data['num_comments']} comments | "
            f"{post_data['title'][:50]}..."
        )
        
        return post_data
    
    def _extract_title(self, container) -> str:
        """Extract post title"""
        try:
            title_elem = container.find('a', class_='search-title')
            if not title_elem:
                title_elem = container.find('a', class_='title')
            return title_elem.get_text(strip=True) if title_elem else ""
        except:
            return ""
    
    def _extract_author(self, container) -> str:
        """Extract author username"""
        try:
            author_elem = container.find('a', class_='author')
            return author_elem.get_text(strip=True) if author_elem else "[deleted]"
        except:
            return "[deleted]"
    
    def _extract_score(self, container) -> int:
        """Extract upvote score"""
        try:
            # Try different score class names
            score_elem = (
                container.find('div', class_='score unvoted') or
                container.find('div', class_='score') or
                container.find('span', class_='search-score')
            )
            
            if score_elem:
                score_text = score_elem.get_text(strip=True)
                
                # Remove " points" suffix if present
                score_text = score_text.replace(' points', '').replace(' point', '')
                
                # Try to parse as int
                match = re.search(r'(\d+)', score_text)
                if match:
                    return int(match.group(1))
            
            return 0
            
        except Exception as e:
            logging.debug(f"Error extracting score: {e}")
            return 0
    
    def _extract_comment_count(self, container) -> int:
        """Extract number of comments"""
        try:
            # Find comments link
            comments_elem = container.find('a', class_='search-comments')
            if not comments_elem:
                comments_elem = container.find('a', class_='comments')
            
            if comments_elem:
                text = comments_elem.get_text(strip=True)
                
                # Extract number from text like "123 comments" or "1 comment"
                match = re.search(r'(\d+)', text)
                if match:
                    return int(match.group(1))
            
            return 0
            
        except Exception as e:
            logging.debug(f"Error extracting comments: {e}")
            return 0
    
    def _extract_post_url(self, container) -> str:
        """Extract post URL"""
        try:
            link = container.find('a', class_='search-title')
            if not link:
                link = container.find('a', class_='title')
            
            if link:
                href = link.get('href', '')
                
                # If relative URL, make absolute
                if href.startswith('/r/'):
                    return f"{self.BASE_URL}{href}"
                
                return href
            
            return ""
            
        except:
            return ""
    
    def _extract_timestamp(self, container) -> Optional[datetime]:
        """Extract post creation time"""
        try:
            time_elem = container.find('time', datetime=True)
            if time_elem:
                timestamp_str = time_elem.get('datetime')
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            return None
            
        except Exception as e:
            logging.debug(f"Error extracting timestamp: {e}")
            return None
    
    def _extract_flair(self, container) -> str:
        """Extract post flair (tag)"""
        try:
            flair_elem = container.find('span', class_='linkflairlabel')
            return flair_elem.get_text(strip=True) if flair_elem else ""
        except:
            return ""
    
    def _is_self_post(self, container) -> bool:
        """Check if this is a text post (self-post) vs link"""
        try:
            # Self posts have class "self"
            return 'self' in container.get('class', [])
        except:
            return False
    
    def get_post_content(self, post_url: str) -> Dict:
        """
        Optional: Navigate to specific post to get full text content
        Useful for text posts where we want the body
        
        Args:
            post_url: Full URL to Reddit post
            
        Returns:
            Dictionary with post content
        """
        try:
            # Convert to old.reddit.com if needed
            if 'reddit.com' in post_url and 'old.reddit.com' not in post_url:
                post_url = post_url.replace('reddit.com', 'old.reddit.com')
            
            logging.info(f"Fetching post content: {post_url}")
            
            self.driver.get(post_url)
            self.random_delay(2, 3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract post body
            body_elem = soup.find('div', class_='usertext-body')
            body_text = body_elem.get_text(strip=True) if body_elem else ""
            
            # Extract top comments (optional)
            comment_elems = soup.find_all('div', class_='usertext-body', limit=5)
            top_comments = [c.get_text(strip=True) for c in comment_elems[1:]]  # Skip first (post body)
            
            return {
                'body': body_text,
                'top_comments': top_comments,
            }
            
        except Exception as e:
            logging.error(f"Error fetching post content: {e}")
            return {'body': '', 'top_comments': []}
