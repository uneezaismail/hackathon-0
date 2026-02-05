#!/usr/bin/env python3
"""
Content Adaptation Library for Social Media Platforms

Provides platform-specific content adaptation for Facebook, Instagram, Twitter, and LinkedIn.
Handles character limits, hashtag optimization, and platform-specific formatting.
"""

import re
from typing import List, Dict, Any, Tuple


class ContentAdapter:
    """Adapt content for different social media platforms."""

    # Platform character limits
    TWITTER_LIMIT = 280
    INSTAGRAM_CAPTION_LIMIT = 2200
    LINKEDIN_LIMIT = 3000
    FACEBOOK_LIMIT = None  # No limit

    # Platform hashtag limits
    INSTAGRAM_HASHTAG_LIMIT = 30
    TWITTER_HASHTAG_LIMIT = 3  # Recommended for engagement
    FACEBOOK_HASHTAG_LIMIT = 2  # Recommended for engagement
    LINKEDIN_HASHTAG_LIMIT = 10  # Hard limit, but 3-5 recommended

    @staticmethod
    def adapt_for_facebook(content: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """
        Adapt content for Facebook (no character limit).

        Args:
            content: Original content
            hashtags: List of hashtags (optional)

        Returns:
            Adapted content with message and metadata
        """
        # Facebook has no character limit, but keep it concise for engagement
        message = content

        # Add hashtags at end if provided (max 2 recommended)
        if hashtags:
            selected_hashtags = hashtags[:ContentAdapter.FACEBOOK_HASHTAG_LIMIT]
            hashtag_str = ' '.join(f'#{tag}' for tag in selected_hashtags)
            message = f"{content}\n\n{hashtag_str}"

        return {
            "message": message,
            "platform": "facebook",
            "char_count": len(message),
            "hashtags_used": len(hashtags) if hashtags else 0,
            "truncated": False
        }

    @staticmethod
    def adapt_for_instagram(content: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """
        Adapt content for Instagram (2200 char limit, hashtag strategy).

        Args:
            content: Original content
            hashtags: List of hashtags (optional)

        Returns:
            Adapted content with caption and metadata
        """
        # Instagram allows 2200 characters
        caption = content

        # Add hashtags (max 30, but 5-10 recommended for engagement)
        if hashtags:
            # Limit to 30 hashtags (Instagram max)
            selected_hashtags = hashtags[:ContentAdapter.INSTAGRAM_HASHTAG_LIMIT]
            # Use first 10 for better engagement
            recommended_hashtags = selected_hashtags[:10]
            hashtag_str = ' '.join(f'#{tag}' for tag in recommended_hashtags)

            # Add hashtags at end
            full_caption = f"{content}\n\n{hashtag_str}"

            # Truncate if exceeds limit
            if len(full_caption) > ContentAdapter.INSTAGRAM_CAPTION_LIMIT:
                available_space = ContentAdapter.INSTAGRAM_CAPTION_LIMIT - len(hashtag_str) - 4  # 4 for "\n\n"
                caption = content[:available_space] + "..."
                caption = f"{caption}\n\n{hashtag_str}"
                truncated = True
            else:
                caption = full_caption
                truncated = False
        else:
            # No hashtags, just check length
            if len(content) > ContentAdapter.INSTAGRAM_CAPTION_LIMIT:
                caption = content[:ContentAdapter.INSTAGRAM_CAPTION_LIMIT - 3] + "..."
                truncated = True
            else:
                truncated = False

        return {
            "caption": caption,
            "platform": "instagram",
            "char_count": len(caption),
            "hashtags_used": len(hashtags) if hashtags else 0,
            "truncated": truncated
        }

    @staticmethod
    def adapt_for_twitter(content: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """
        Adapt content for Twitter (280 char limit, thread creation if needed).

        Args:
            content: Original content
            hashtags: List of hashtags (optional)

        Returns:
            Adapted content with text/thread and metadata
        """
        # Add hashtags (max 3 recommended for engagement)
        hashtag_str = ""
        if hashtags:
            selected_hashtags = hashtags[:ContentAdapter.TWITTER_HASHTAG_LIMIT]
            hashtag_str = ' '.join(f'#{tag}' for tag in selected_hashtags)

        # Check if content fits in single tweet
        full_text = f"{content} {hashtag_str}".strip() if hashtag_str else content

        if len(full_text) <= ContentAdapter.TWITTER_LIMIT:
            # Single tweet
            return {
                "text": full_text,
                "platform": "twitter",
                "char_count": len(full_text),
                "hashtags_used": len(hashtags) if hashtags else 0,
                "is_thread": False,
                "tweet_count": 1,
                "truncated": False
            }
        else:
            # Create thread
            thread = ContentAdapter._create_twitter_thread(content, hashtag_str)
            return {
                "thread": thread,
                "platform": "twitter",
                "char_count": sum(len(tweet) for tweet in thread),
                "hashtags_used": len(hashtags) if hashtags else 0,
                "is_thread": True,
                "tweet_count": len(thread),
                "truncated": False
            }

    @staticmethod
    def adapt_for_linkedin(content: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """
        Adapt content for LinkedIn (3000 char limit, professional tone).

        Args:
            content: Original content
            hashtags: List of hashtags (optional)

        Returns:
            Adapted content with text and metadata
        """
        # LinkedIn allows 3000 characters
        text = content

        # Add hashtags at end if provided (3-5 recommended for professional content)
        if hashtags:
            # Limit to 10 hashtags (LinkedIn max), but recommend 3-5
            selected_hashtags = hashtags[:ContentAdapter.LINKEDIN_HASHTAG_LIMIT]
            # Use first 5 for better engagement
            recommended_hashtags = selected_hashtags[:5]
            hashtag_str = ' '.join(f'#{tag}' for tag in recommended_hashtags)

            # Add hashtags at end
            full_text = f"{content}\n\n{hashtag_str}"

            # Truncate if exceeds limit
            if len(full_text) > ContentAdapter.LINKEDIN_LIMIT:
                available_space = ContentAdapter.LINKEDIN_LIMIT - len(hashtag_str) - 4  # 4 for "\n\n"
                text = content[:available_space] + "..."
                text = f"{text}\n\n{hashtag_str}"
                truncated = True
            else:
                text = full_text
                truncated = False
        else:
            # No hashtags, just check length
            if len(content) > ContentAdapter.LINKEDIN_LIMIT:
                text = content[:ContentAdapter.LINKEDIN_LIMIT - 3] + "..."
                truncated = True
            else:
                truncated = False

        return {
            "text": text,
            "platform": "linkedin",
            "char_count": len(text),
            "hashtags_used": len(hashtags) if hashtags else 0,
            "truncated": truncated
        }

    @staticmethod
    def adapt_for_facebook(content: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """
        Adapt content for Facebook (no character limit).

        Args:
            content: Original content
            hashtags: List of hashtags (optional)

        Returns:
            Adapted content with message and metadata
        """
        # Facebook has no character limit, but keep it concise for engagement
        message = content

        # Add hashtags at end if provided (max 2 recommended)
        if hashtags:
            selected_hashtags = hashtags[:ContentAdapter.FACEBOOK_HASHTAG_LIMIT]
            hashtag_str = ' '.join(f'#{tag}' for tag in selected_hashtags)
            message = f"{content}\n\n{hashtag_str}"

        return {
            "message": message,
            "platform": "facebook",
            "char_count": len(message),
            "hashtags_used": len(hashtags) if hashtags else 0,
            "truncated": False
        }

    @staticmethod
    def adapt_for_instagram(content: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """
        Adapt content for Instagram (2200 char limit, hashtag strategy).

        Args:
            content: Original content
            hashtags: List of hashtags (optional)

        Returns:
            Adapted content with caption and metadata
        """
        # Instagram allows 2200 characters
        caption = content

        # Add hashtags (max 30, but 5-10 recommended for engagement)
        if hashtags:
            # Limit to 30 hashtags (Instagram max)
            selected_hashtags = hashtags[:ContentAdapter.INSTAGRAM_HASHTAG_LIMIT]
            # Use first 10 for better engagement
            recommended_hashtags = selected_hashtags[:10]
            hashtag_str = ' '.join(f'#{tag}' for tag in recommended_hashtags)

            # Add hashtags at end
            full_caption = f"{content}\n\n{hashtag_str}"

            # Truncate if exceeds limit
            if len(full_caption) > ContentAdapter.INSTAGRAM_CAPTION_LIMIT:
                available_space = ContentAdapter.INSTAGRAM_CAPTION_LIMIT - len(hashtag_str) - 4  # 4 for "\n\n"
                caption = content[:available_space] + "..."
                caption = f"{caption}\n\n{hashtag_str}"
                truncated = True
            else:
                caption = full_caption
                truncated = False
        else:
            # No hashtags, just check length
            if len(content) > ContentAdapter.INSTAGRAM_CAPTION_LIMIT:
                caption = content[:ContentAdapter.INSTAGRAM_CAPTION_LIMIT - 3] + "..."
                truncated = True
            else:
                truncated = False

        return {
            "caption": caption,
            "platform": "instagram",
            "char_count": len(caption),
            "hashtags_used": len(hashtags) if hashtags else 0,
            "truncated": truncated
        }

    @staticmethod
    def adapt_for_twitter(content: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """
        Adapt content for Twitter (280 char limit, thread creation if needed).

        Args:
            content: Original content
            hashtags: List of hashtags (optional)

        Returns:
            Adapted content with text/thread and metadata
        """
        # Add hashtags (max 3 recommended for engagement)
        hashtag_str = ""
        if hashtags:
            selected_hashtags = hashtags[:ContentAdapter.TWITTER_HASHTAG_LIMIT]
            hashtag_str = ' '.join(f'#{tag}' for tag in selected_hashtags)

        # Check if content fits in single tweet
        full_text = f"{content} {hashtag_str}".strip() if hashtag_str else content

        if len(full_text) <= ContentAdapter.TWITTER_LIMIT:
            # Single tweet
            return {
                "text": full_text,
                "platform": "twitter",
                "char_count": len(full_text),
                "hashtags_used": len(hashtags) if hashtags else 0,
                "is_thread": False,
                "tweet_count": 1,
                "truncated": False
            }
        else:
            # Create thread
            thread = ContentAdapter._create_twitter_thread(content, hashtag_str)
            return {
                "thread": thread,
                "platform": "twitter",
                "char_count": sum(len(tweet) for tweet in thread),
                "hashtags_used": len(hashtags) if hashtags else 0,
                "is_thread": True,
                "tweet_count": len(thread),
                "truncated": False
            }

    @staticmethod
    def _create_twitter_thread(content: str, hashtag_str: str = "") -> List[str]:
        """
        Split content into Twitter thread.

        Args:
            content: Content to split
            hashtag_str: Hashtags to add to last tweet

        Returns:
            List of tweet texts
        """
        # Reserve space for thread numbering (e.g., "1/3 ")
        max_tweet_length = ContentAdapter.TWITTER_LIMIT - 10

        # Split content into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)

        tweets = []
        current_tweet = ""

        for sentence in sentences:
            # If single sentence exceeds limit, split it
            if len(sentence) > max_tweet_length:
                # Add current tweet if not empty
                if current_tweet:
                    tweets.append(current_tweet.strip())
                    current_tweet = ""

                # Split long sentence into chunks
                words = sentence.split()
                for word in words:
                    if len(current_tweet) + len(word) + 1 <= max_tweet_length:
                        current_tweet += f" {word}" if current_tweet else word
                    else:
                        tweets.append(current_tweet.strip())
                        current_tweet = word
            else:
                # Try to add sentence to current tweet
                test_tweet = f"{current_tweet} {sentence}".strip() if current_tweet else sentence
                if len(test_tweet) <= max_tweet_length:
                    current_tweet = test_tweet
                else:
                    # Start new tweet
                    tweets.append(current_tweet.strip())
                    current_tweet = sentence

        # Add remaining content
        if current_tweet:
            tweets.append(current_tweet.strip())

        # Add hashtags to last tweet if space allows
        if hashtag_str and tweets:
            last_tweet = tweets[-1]
            if len(last_tweet) + len(hashtag_str) + 1 <= max_tweet_length:
                tweets[-1] = f"{last_tweet} {hashtag_str}"

        # Add thread numbering
        total = len(tweets)
        numbered_tweets = [f"{i+1}/{total} {tweet}" for i, tweet in enumerate(tweets)]

        return numbered_tweets

    @staticmethod
    def extract_hashtags(content: str) -> Tuple[str, List[str]]:
        """
        Extract hashtags from content.

        Args:
            content: Content with hashtags

        Returns:
            Tuple of (content without hashtags, list of hashtags)
        """
        # Find all hashtags
        hashtags = re.findall(r'#(\w+)', content)

        # Remove hashtags from content
        content_without_hashtags = re.sub(r'#\w+\s*', '', content).strip()

        return content_without_hashtags, hashtags

    @staticmethod
    def adapt_for_all_platforms(content: str, hashtags: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Adapt content for all platforms simultaneously.

        Args:
            content: Original content
            hashtags: List of hashtags (optional)

        Returns:
            Dictionary with adapted content for each platform
        """
        return {
            "facebook": ContentAdapter.adapt_for_facebook(content, hashtags),
            "instagram": ContentAdapter.adapt_for_instagram(content, hashtags),
            "twitter": ContentAdapter.adapt_for_twitter(content, hashtags),
            "linkedin": ContentAdapter.adapt_for_linkedin(content, hashtags)
        }


if __name__ == "__main__":
    # Test content adaptation
    adapter = ContentAdapter()

    # Test content
    content = "Excited to announce our new product launch! We've been working on this for months and can't wait to share it with you. Check out our website for more details."
    hashtags = ["innovation", "tech", "startup", "product", "launch"]

    # Adapt for all platforms
    adapted = adapter.adapt_for_all_platforms(content, hashtags)

    print("Facebook:")
    print(f"  Message: {adapted['facebook']['message'][:100]}...")
    print(f"  Char count: {adapted['facebook']['char_count']}")
    print()

    print("Instagram:")
    print(f"  Caption: {adapted['instagram']['caption'][:100]}...")
    print(f"  Char count: {adapted['instagram']['char_count']}")
    print()

    print("Twitter:")
    if adapted['twitter']['is_thread']:
        print(f"  Thread ({adapted['twitter']['tweet_count']} tweets):")
        for i, tweet in enumerate(adapted['twitter']['thread']):
            print(f"    {i+1}. {tweet}")
    else:
        print(f"  Text: {adapted['twitter']['text']}")
    print(f"  Char count: {adapted['twitter']['char_count']}")
    print()

    print("LinkedIn:")
    print(f"  Text: {adapted['linkedin']['text'][:100]}...")
    print(f"  Char count: {adapted['linkedin']['char_count']}")
    print(f"  Hashtags used: {adapted['linkedin']['hashtags_used']}")

