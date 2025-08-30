from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, UTC
from collections import defaultdict
import difflib
import re
import hashlib
from ..database.models import AppreciationToken, User

class AppreciationTokenFraudDetector:
    def __init__(
            self, 
            db_session: Session, 
            time_window_minutes=10, 
            comment_similarity_threshold=0.8, 
            username_similarity_threshold=0.8, 
            interaction_limit=50, 
            ip_cluster_limit=10):
        self.db_session = db_session
        self.time_window = timedelta(minutes=time_window_minutes)
        self.comment_similarity_threshold = comment_similarity_threshold
        self.username_similarity_threshold = username_similarity_threshold
        self.interaction_limit = interaction_limit
        self.ip_cluster_limit = ip_cluster_limit
        
        # Spam patterns for comment detection
        self.spam_patterns = [
            r"free gift", r"click here", r"visit now", r"buy now", 
            r"subscribe", r"win", r"prize", r"claim reward", 
            r"whatsapp", r"telegram", r"dm me", r"contact me",
            r"check my profile", r"follow me", r"bitcoin", r"crypto"
        ]

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts"""
        if not text1 or not text2:
            return 0.0
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def is_spam_comment(self, comment: str) -> bool:
        """Check if comment contains spam patterns"""
        if not comment:
            return False
        comment_lower = comment.lower()
        return any(re.search(pattern, comment_lower) for pattern in self.spam_patterns)

    def fetch_token_data_with_user_info(self, video_id: Optional[int] = None, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Fetch appreciation tokens with related user and comment data
        """
        # Calculate time threshold
        time_threshold = datetime.now(UTC) - timedelta(hours=hours_back)
        
        # Base query
        query = self.db_session.query(
            AppreciationToken.token_id,
            AppreciationToken.user_id,
            AppreciationToken.video_id,
            AppreciationToken.ip_hash,
            AppreciationToken.used_at,
            AppreciationToken.source,
            # Join with User table to get username and recent comments
            User.username,
            # You might need to join with a Comments table if comments are separate
            # For now, assuming we can get recent comment data somehow
        ).join(User, AppreciationToken.user_id == User.id, isouter=True)
        
        # Filter by video if specified
        if video_id:
            query = query.filter(AppreciationToken.video_id == video_id)
        
        # Filter by time
        query = query.filter(AppreciationToken.used_at >= time_threshold)
        
        results = query.all()
        
        # Convert to list of dictionaries for easier processing
        token_data = []
        for row in results:
            token_data.append({
                'token_id': row.token_id,
                'user_id': row.user_id,
                'video_id': row.video_id,
                'ip_hash': row.ip_hash,
                'used_at': row.used_at,
                'source': row.source,
                'username': row.username or 'anonymous',
            })
        
        return token_data

    def detect_ip_clustering_fraud(self, token_data: List[Dict[str, Any]]) -> List[int]:
        """Detect fraud based on IP address clustering"""
        ip_groups = defaultdict(list)
        
        for token in token_data:
            ip_groups[token['ip_hash']].append(token)
        
        fraudulent_token_ids = []
        for ip_hash, tokens in ip_groups.items():
            if len(tokens) > self.ip_cluster_limit:
                # Too many tokens from same IP in time window
                fraudulent_token_ids.extend([t['token_id'] for t in tokens])
        
        return fraudulent_token_ids

    def detect_time_proximity_fraud(self, token_data: List[Dict[str, Any]]) -> List[int]:
        """Detect fraud based on time proximity and similar behavior"""
        fraudulent_token_ids = set()
        
        for i in range(len(token_data)):
            for j in range(i + 1, len(token_data)):
                token1, token2 = token_data[i], token_data[j]
                
                # Skip if different IPs
                if token1['ip_hash'] != token2['ip_hash']:
                    continue
                
                # Check time proximity
                time_diff = abs(token1['used_at'] - token2['used_at'])
                if time_diff > self.time_window:
                    continue
                
                fraud_score = 0
                
                # Username similarity
                username_sim = self.calculate_similarity(token1['username'], token2['username'])
                if username_sim >= self.username_similarity_threshold:
                    fraud_score += 2
                
                # Comment similarity (check all recent comments)
                for comment1 in token1['comments']:
                    for comment2 in token2['comments']:
                        comment_sim = self.calculate_similarity(comment1, comment2)
                        if comment_sim >= self.comment_similarity_threshold:
                            fraud_score += 3
                            break
                    if fraud_score >= 3:
                        break
                
                # Spam detection
                spam_detected = any(self.is_spam_comment(c) for c in token1['comments'] + token2['comments'])
                if spam_detected:
                    fraud_score += 3
                
                # Unreasonable interactions
                if (token1['interaction_count'] > self.interaction_limit or 
                    token2['interaction_count'] > self.interaction_limit):
                    fraud_score += 2
                
                # Same video appreciation within short time from same IP
                if token1['video_id'] == token2['video_id'] and time_diff < timedelta(minutes=2):
                    fraud_score += 4
                
                if fraud_score >= 4:
                    fraudulent_token_ids.add(token1['token_id'])
                    fraudulent_token_ids.add(token2['token_id'])
        
        return list(fraudulent_token_ids)

    def detect_pattern_based_fraud(self, token_data: List[Dict[str, Any]]) -> List[int]:
        """Detect fraud based on suspicious patterns"""
        fraudulent_token_ids = []
        
        # Group by user to detect suspicious user behavior
        user_groups = defaultdict(list)
        for token in token_data:
            if token['user_id']:  # Skip anonymous tokens
                user_groups[token['user_id']].append(token)
        
        for user_id, tokens in user_groups.items():
            # User appreciating too many videos in short time
            if len(tokens) > 20:  # More than 20 appreciations in time window
                fraudulent_token_ids.extend([t['token_id'] for t in tokens])
            
            # User with multiple different IP hashes (potential account sharing/botting)
            unique_ips = set(t['ip_hash'] for t in tokens)
            if len(unique_ips) > 3:  # Same user from more than 3 different IPs
                fraudulent_token_ids.extend([t['token_id'] for t in tokens])
        
        return fraudulent_token_ids

    def detect_fraud(self, video_id: Optional[int] = None, hours_back: int = 24) -> Dict[str, Any]:
        """
        Main fraud detection function for AppreciationTokens
        
        Args:
            video_id: Optional video ID to focus analysis on specific video
            hours_back: How many hours back to analyze (default 24)
        
        Returns:
            Dictionary with fraud detection results
        """
        # Fetch token data
        token_data = self.fetch_token_data_with_user_info(video_id, hours_back)
        
        if not token_data:
            return {
                'total_tokens': 0,
                'fraudulent_token_ids': [],
                'fraud_types': {},
                'summary': {'fraud_percentage': 0}
            }
        
        results = {
            'total_tokens': len(token_data),
            'fraudulent_token_ids': set(),
            'fraud_types': {},
            'summary': {}
        }
        
        # IP clustering detection
        ip_fraud = self.detect_ip_clustering_fraud(token_data)
        results['fraudulent_token_ids'].update(ip_fraud)
        results['fraud_types']['ip_clustering'] = ip_fraud
        
        # Time proximity fraud
        time_fraud = self.detect_time_proximity_fraud(token_data)
        results['fraudulent_token_ids'].update(time_fraud)
        results['fraud_types']['time_proximity'] = time_fraud
        
        # Pattern-based fraud
        pattern_fraud = self.detect_pattern_based_fraud(token_data)
        results['fraudulent_token_ids'].update(pattern_fraud)
        results['fraud_types']['pattern_based'] = pattern_fraud
        
        # Convert to list and create summary
        results['fraudulent_token_ids'] = list(results['fraudulent_token_ids'])
        results['summary'] = {
            'total_fraudulent': len(results['fraudulent_token_ids']),
            'fraud_percentage': (len(results['fraudulent_token_ids']) / len(token_data)) * 100,
            'ip_clustering_cases': len(ip_fraud),
            'time_proximity_cases': len(time_fraud),
            'pattern_based_cases': len(pattern_fraud),
            'analysis_timeframe_hours': hours_back
        }
        
        return results

    def mark_tokens_as_fraudulent(self, token_ids: List[int]) -> int:
        """
        Mark tokens as fraudulent (you might want to add a fraud flag to your model)
        This is a placeholder - implement based on your needs
        """
        # Example: Add a fraud flag to your model and update
        # affected_rows = self.db_session.query(AppreciationToken).filter(
        #     AppreciationToken.token_id.in_(token_ids)
        # ).update({'is_fraudulent': True}, synchronize_session=False)
        # self.db_session.commit()
        # return affected_rows
        return len(token_ids)

# Usage example:
def run_fraud_detection(db_session: Session, video_id: Optional[int] = None):
    """Example usage of the fraud detector"""
    detector = AppreciationTokenFraudDetector(db_session)
    results = detector.detect_fraud(video_id=video_id, hours_back=24)
    
    print(f"Fraud Detection Results for {'all videos' if not video_id else f'video {video_id}'}:")
    print(f"Total tokens analyzed: {results['total_tokens']}")
    print(f"Fraudulent tokens found: {results['summary']['total_fraudulent']}")
    print(f"Fraud percentage: {results['summary']['fraud_percentage']:.2f}%")
    
    if results['fraudulent_token_ids']:
        print(f"Fraudulent token IDs: {results['fraudulent_token_ids']}")
        
        # Optionally mark as fraudulent
        # detector.mark_tokens_as_fraudulent(results['fraudulent_token_ids'])
    
    return results
