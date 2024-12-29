import requests
from datetime import datetime
import time
from collections import Counter
from typing import Dict, List

class ContentDistributionAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Subreddit category mapping (example)
        self.subreddit_categories = {
            'finance': ['personalfinance', 'financialindependence', 'investing'],
            'technology': ['technology', 'gadgets', 'programming'],
            # Add more categories as needed
        }

    def analyze_subreddit(self, subreddit: str) -> Dict:
        """Analyze a subreddit for content distribution potential"""
        try:
            # Get subreddit info
            about_url = f'https://www.reddit.com/r/{subreddit}/about.json'
            about_response = requests.get(about_url, headers=self.headers)
            about_response.raise_for_status()
            about_data = about_response.json()['data']

            # Get recent posts
            posts_url = f'https://www.reddit.com/r/{subreddit}/new.json?limit=50'
            posts_response = requests.get(posts_url, headers=self.headers)
            posts_response.raise_for_status()
            posts_data = posts_response.json()['data']['children']

            # Analyze activity
            post_times = [post['data']['created_utc'] for post in posts_data]
            current_time = time.time()
            activity_last_24h = sum(1 for t in post_times if current_time - t < 86400)

            return {
                'subscribers': about_data['subscribers'],
                'active_users': about_data.get('active_user_count', 0),
                'posts_last_24h': activity_last_24h,
            }
        except requests.RequestException as e:
            print(f"Error analyzing subreddit {subreddit}: {e}")
            return {}

    def recommend_subreddits(self, prompt: str) -> List[Dict]:
        """Recommend subreddits based on a user prompt"""
        # Determine category from prompt (naive matching)
        category = None
        for key in self.subreddit_categories:
            if key in prompt.lower():
                category = key
                break

        if not category:
            return [{'error': 'No matching category found for the prompt.'}]

        recommendations = []
        for subreddit in self.subreddit_categories[category]:
            analysis = self.analyze_subreddit(subreddit)
            if analysis:
                recommendations.append({
                    'subreddit': subreddit,
                    'subscribers': analysis['subscribers'],
                    'active_users': analysis['active_users'],
                    'posts_last_24h': analysis['posts_last_24h'],
                })

        # Sort recommendations by activity (e.g., active users or posts_last_24h)
        recommendations.sort(key=lambda x: x['active_users'], reverse=True)
        return recommendations

    def track_activity(self, subreddits: List[str]) -> Dict[str, Dict]:
        """Track activity for multiple subreddits"""
        tracked_data = {}
        for subreddit in subreddits:
            tracked_data[subreddit] = self.analyze_subreddit(subreddit)
        return tracked_data

# Example usage
if __name__ == "__main__":
    analyzer = ContentDistributionAnalyzer()
    user_prompt = "I want to share my Substack about finance."

    print("Recommendations:")
    recommendations = analyzer.recommend_subreddits(user_prompt)
    for rec in recommendations:
        print(rec)
