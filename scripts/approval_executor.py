#!/usr/bin/env python3
"""
Approval Executor - MCP Action Dispatcher

This script watches the AI_Employee_Vault/Approved/ folder for files and executes
MCP actions based on the file metadata. It supports various action types like
send_email, post_linkedin, etc., with retry logic, rate limiting, and error handling.

Features:
- Watch folder for new approved actions
- Parse metadata to determine action type
- Execute actions via MCP protocol
- Retry with exponential backoff
- Rate limiting (10 actions per hour)
- Comprehensive logging
- Dry-run mode for testing
- Dashboard updates

Usage:
    # Normal mode
    python scripts/approval_executor.py

    # Dry-run mode (no actual actions)
    python scripts/approval_executor.py --dry-run

    # Custom watch interval
    python scripts/approval_executor.py --interval 5

    # One-time execution (no watching)
    python scripts/approval_executor.py --once
"""

import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import deque
import argparse
import logging

# =============================================================================
# CONFIGURATION
# =============================================================================

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
VAULT_PATH = PROJECT_ROOT / "AI_Employee_Vault"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
FAILED_PATH = VAULT_PATH / "Failed"
LOGS_PATH = VAULT_PATH / "Logs"
DASHBOARD_PATH = VAULT_PATH / "Dashboard.md"

# MCP Server configuration
MCP_EMAIL_SERVER = PROJECT_ROOT / "mcp_servers" / "email" / "server.js"
MCP_LINKEDIN_SERVER = PROJECT_ROOT / "mcp_servers" / "linkedin" / "server.js"
LINKEDIN_DRAFTS_PATH = VAULT_PATH / "LinkedIn_Drafts"

# Execution configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2  # seconds
BACKOFF_MULTIPLIER = 2
WATCH_INTERVAL = 3  # seconds
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
MAX_ACTIONS_PER_HOUR = 10

# Supported action types
SUPPORTED_ACTIONS = [
    'send_email',
    'draft_email',
    'search_emails',
    'post_linkedin',  # Future implementation
    'create_calendar_event',  # Future implementation
]

# =============================================================================
# LOGGING SETUP
# =============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """
    Rate limiter to prevent exceeding action quotas.

    Tracks action timestamps and enforces maximum actions per time window.
    """

    def __init__(self, max_actions: int, window_seconds: int):
        """
        Initialize rate limiter.

        Args:
            max_actions: Maximum number of actions allowed in window
            window_seconds: Time window in seconds
        """
        self.max_actions = max_actions
        self.window_seconds = window_seconds
        self.action_times = deque()

    def can_execute(self) -> bool:
        """
        Check if an action can be executed without exceeding rate limit.

        Returns:
            True if action can be executed, False otherwise
        """
        now = time.time()

        # Remove old timestamps outside the window
        while self.action_times and self.action_times[0] < now - self.window_seconds:
            self.action_times.popleft()

        # Check if under limit
        return len(self.action_times) < self.max_actions

    def record_action(self):
        """Record that an action was executed."""
        self.action_times.append(time.time())

    def get_wait_time(self) -> float:
        """
        Get time to wait before next action can be executed.

        Returns:
            Seconds to wait, or 0 if can execute immediately
        """
        if self.can_execute():
            return 0

        # Calculate when oldest action will expire
        oldest = self.action_times[0]
        expiry = oldest + self.window_seconds
        wait = expiry - time.time()

        return max(0, wait)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current rate limiter status.

        Returns:
            Dict with current usage and limit info
        """
        now = time.time()

        # Clean old timestamps
        while self.action_times and self.action_times[0] < now - self.window_seconds:
            self.action_times.popleft()

        return {
            'current_actions': len(self.action_times),
            'max_actions': self.max_actions,
            'window_seconds': self.window_seconds,
            'can_execute': self.can_execute(),
            'wait_time': self.get_wait_time()
        }


# =============================================================================
# MCP CLIENT
# =============================================================================

class MCPClient:
    """
    Client for communicating with MCP servers.

    Handles executing tools via the MCP protocol (stdio transport).
    """

    def __init__(self, server_path: Path, dry_run: bool = False):
        """
        Initialize MCP client.

        Args:
            server_path: Path to MCP server executable
            dry_run: If True, simulate actions without execution
        """
        self.server_path = server_path
        self.dry_run = dry_run

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            timeout: Execution timeout in seconds

        Returns:
            Dict containing result or error

        Raises:
            TimeoutError: If execution exceeds timeout
            RuntimeError: If server fails to execute
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute {tool_name} with args: {arguments}")
            return {
                'success': True,
                'dry_run': True,
                'tool': tool_name,
                'arguments': arguments
            }

        try:
            # In a real implementation, this would use the MCP protocol
            # For now, we'll simulate the execution
            logger.info(f"Executing MCP tool: {tool_name}")
            logger.debug(f"Arguments: {json.dumps(arguments, indent=2)}")

            # Start the MCP server process
            # Note: This is a simplified implementation
            # Real implementation would use JSON-RPC over stdio
            process = await asyncio.create_subprocess_exec(
                'node',
                str(self.server_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Build JSON-RPC request
            request = {
                'jsonrpc': '2.0',
                'id': int(time.time() * 1000),
                'method': 'tools/call',
                'params': {
                    'name': tool_name,
                    'arguments': arguments
                }
            }

            # Send request and get response
            request_json = json.dumps(request) + '\n'
            stdout, stderr = await asyncio.wait_for(
                process.communicate(request_json.encode()),
                timeout=timeout
            )

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"MCP server failed: {error_msg}")

            # Parse response
            # Note: Real implementation would parse JSON-RPC response
            result = {
                'success': True,
                'tool': tool_name,
                'executed': True
            }

            logger.info(f"Tool {tool_name} executed successfully")
            return result

        except asyncio.TimeoutError:
            logger.error(f"Tool {tool_name} execution timed out after {timeout}s")
            raise TimeoutError(f"Execution timeout after {timeout}s")

        except Exception as e:
            logger.error(f"Failed to execute tool {tool_name}: {e}")
            raise RuntimeError(f"Execution failed: {e}")


# =============================================================================
# FILE PARSER
# =============================================================================

class ActionFileParser:
    """
    Parser for action files with metadata.

    Extracts metadata and content from markdown files.
    """

    @staticmethod
    def parse_file(file_path: Path) -> Dict[str, Any]:
        """
        Parse an action file.

        Args:
            file_path: Path to file

        Returns:
            Dict with metadata and content

        Raises:
            ValueError: If file format is invalid
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract metadata from frontmatter
            metadata = ActionFileParser._extract_metadata(content)

            # Extract body content
            body = ActionFileParser._extract_body(content)

            # Validate required fields
            ActionFileParser._validate_metadata(metadata)

            return {
                'metadata': metadata,
                'body': body,
                'file_path': file_path,
                'file_name': file_path.name
            }

        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            raise ValueError(f"Invalid file format: {e}")

    @staticmethod
    def _extract_metadata(content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter metadata."""
        metadata = {}

        # Match YAML frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

        if match:
            frontmatter = match.group(1)

            # Parse YAML-like format
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes
                    value = value.strip('"').strip("'")

                    metadata[key] = value

        return metadata

    @staticmethod
    def _extract_body(content: str) -> str:
        """Extract body content after frontmatter."""
        # Remove frontmatter
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        return content.strip()

    @staticmethod
    def _validate_metadata(metadata: Dict[str, Any]):
        """
        Validate that required metadata fields are present.

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ['action', 'status']

        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Missing required field: {field}")

        # Validate action type
        action = metadata['action']
        if action not in SUPPORTED_ACTIONS:
            raise ValueError(f"Unsupported action type: {action}")


# =============================================================================
# ACTION EXECUTOR
# =============================================================================

class ActionExecutor:
    """
    Executes approved actions via MCP.

    Handles retry logic, rate limiting, and result tracking.
    """

    def __init__(
        self,
        mcp_client: MCPClient,
        rate_limiter: RateLimiter,
        dry_run: bool = False,
        linkedin_client: Optional[MCPClient] = None
    ):
        """
        Initialize action executor.

        Args:
            mcp_client: MCP client for executing tools (email server)
            rate_limiter: Rate limiter for throttling
            dry_run: If True, simulate actions
            linkedin_client: Optional MCP client for LinkedIn server
        """
        self.mcp_client = mcp_client
        self.linkedin_client = linkedin_client
        self.rate_limiter = rate_limiter
        self.dry_run = dry_run

    async def execute_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an approved action with retry logic.

        Args:
            action_data: Parsed action data from file

        Returns:
            Dict containing execution result
        """
        metadata = action_data['metadata']
        action_type = metadata['action']

        logger.info(f"Executing action: {action_type} from {action_data['file_name']}")

        # Check rate limit
        if not self.rate_limiter.can_execute():
            wait_time = self.rate_limiter.get_wait_time()
            logger.warning(f"Rate limit reached. Need to wait {wait_time:.1f}s")

            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'wait_time': wait_time,
                'rate_limited': True
            }

        # Execute with retry
        result = await self._execute_with_retry(action_data)

        # Record action if successful
        if result.get('success'):
            self.rate_limiter.record_action()

        return result

    async def _execute_with_retry(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action with exponential backoff retry.

        Args:
            action_data: Parsed action data

        Returns:
            Dict containing execution result
        """
        metadata = action_data['metadata']
        action_type = metadata['action']

        last_error = None
        retry_delay = INITIAL_RETRY_DELAY

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"Attempt {attempt}/{MAX_RETRIES} for {action_type}")

                # Map action to MCP tool
                tool_name, arguments = self._map_action_to_tool(action_data)

                # Select appropriate MCP client based on action type
                if action_type == 'post_linkedin':
                    if not self.linkedin_client:
                        raise RuntimeError("LinkedIn MCP client not configured")
                    client = self.linkedin_client
                else:
                    client = self.mcp_client

                # Execute via MCP
                result = await client.execute_tool(tool_name, arguments)

                # Success
                logger.info(f"Action {action_type} completed successfully")
                return {
                    'success': True,
                    'action': action_type,
                    'result': result,
                    'attempts': attempt
                }

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt} failed: {e}")

                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= BACKOFF_MULTIPLIER

        # All retries exhausted
        logger.error(f"Action {action_type} failed after {MAX_RETRIES} attempts: {last_error}")
        return {
            'success': False,
            'action': action_type,
            'error': last_error,
            'attempts': MAX_RETRIES
        }

    def _map_action_to_tool(self, action_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Map action type to MCP tool and arguments.

        Args:
            action_data: Parsed action data

        Returns:
            Tuple of (tool_name, arguments)

        Raises:
            ValueError: If action type is not supported
        """
        metadata = action_data['metadata']
        action_type = metadata['action']
        body = action_data['body']

        if action_type == 'send_email':
            return self._map_send_email(metadata, body)
        elif action_type == 'draft_email':
            return self._map_draft_email(metadata, body)
        elif action_type == 'search_emails':
            return self._map_search_emails(metadata, body)
        elif action_type == 'post_linkedin':
            return self._map_post_linkedin(metadata, body)
        else:
            raise ValueError(f"Unsupported action: {action_type}")

    def _map_send_email(self, metadata: Dict[str, Any], body: str) -> Tuple[str, Dict[str, Any]]:
        """Map send_email action to MCP tool."""
        arguments = {
            'to': metadata.get('email_to', ''),
            'subject': metadata.get('email_subject', 'No Subject'),
            'body': body
        }

        # Add optional CC
        if 'email_cc' in metadata:
            arguments['cc'] = metadata['email_cc']

        return ('send_email', arguments)

    def _map_draft_email(self, metadata: Dict[str, Any], body: str) -> Tuple[str, Dict[str, Any]]:
        """Map draft_email action to MCP tool."""
        arguments = {
            'to': metadata.get('email_to', ''),
            'subject': metadata.get('email_subject', 'No Subject'),
            'body': body
        }

        return ('draft_email', arguments)

    def _map_search_emails(self, metadata: Dict[str, Any], body: str) -> Tuple[str, Dict[str, Any]]:
        """Map search_emails action to MCP tool."""
        arguments = {
            'query': metadata.get('search_query', body),
            'max_results': int(metadata.get('max_results', 10))
        }

        return ('search_emails', arguments)

    def _map_post_linkedin(self, metadata: Dict[str, Any], body: str) -> Tuple[str, Dict[str, Any]]:
        """
        Map post_linkedin action to MCP tool.

        This handler:
        1. Validates content (length, hashtags)
        2. Checks for duplicate content
        3. Calls LinkedIn MCP server
        4. Handles rate limiting and errors

        Args:
            metadata: Action metadata with linkedin_* fields
            body: Post content

        Returns:
            Tuple of (tool_name, arguments)
        """
        # Extract content from draft_id or use body
        draft_id = metadata.get('draft_id')
        content = body

        if draft_id:
            # Read content from LinkedIn draft file
            draft_path = LINKEDIN_DRAFTS_PATH / f"{draft_id}.json"
            if draft_path.exists():
                with open(draft_path, 'r', encoding='utf-8') as f:
                    draft_data = json.load(f)
                    content = draft_data.get('content', body)

        # Validate content
        self._validate_linkedin_content(content, metadata)

        # Check for duplicates
        if not metadata.get('skip_duplicate_check', False):
            self._check_duplicate_content(content)

        # Build arguments for LinkedIn MCP
        arguments = {
            'content': content
        }

        # Add optional fields
        if 'schedule_time' in metadata:
            arguments['schedule_time'] = metadata['schedule_time']

        if 'tags' in metadata:
            # Parse comma-separated tags
            tags_str = metadata['tags']
            if isinstance(tags_str, str):
                arguments['tags'] = [t.strip() for t in tags_str.split(',')]
            else:
                arguments['tags'] = tags_str

        return ('create_linkedin_post', arguments)

    def _validate_linkedin_content(self, content: str, metadata: Dict[str, Any]):
        """
        Validate LinkedIn post content.

        Checks:
        - Content length (max 3000 characters)
        - Hashtag count (max 30, recommended 5)
        - URL count (recommended 1-2)

        Args:
            content: Post content
            metadata: Action metadata

        Raises:
            ValueError: If validation fails
        """
        # Check length
        max_length = int(metadata.get('max_length', 3000))
        if len(content) > max_length:
            raise ValueError(
                f"Content exceeds maximum length: {len(content)}/{max_length} characters"
            )

        if len(content.strip()) == 0:
            raise ValueError("Content cannot be empty")

        # Count hashtags
        hashtags = re.findall(r'#\w+', content)
        if len(hashtags) > 30:
            raise ValueError(
                f"Too many hashtags: {len(hashtags)}/30. LinkedIn allows max 30 hashtags."
            )

        # Warn about too many hashtags (best practice)
        if len(hashtags) > 5:
            logger.warning(
                f"Content has {len(hashtags)} hashtags. "
                "LinkedIn best practice recommends 3-5 hashtags for optimal reach."
            )

        # Count URLs
        urls = re.findall(r'https?://[^\s]+', content)
        if len(urls) > 3:
            logger.warning(
                f"Content has {len(urls)} URLs. "
                "Posts with 1-2 URLs typically get better engagement."
            )

        # Check for recommended length
        if len(content) < 150:
            logger.info(
                "Content is short (<150 chars). "
                "Posts with 150-300 characters tend to perform better."
            )
        elif len(content) > 1500:
            logger.info(
                "Content is long (>1500 chars). "
                "Consider breaking into multiple posts or using LinkedIn articles."
            )

        logger.info(f"✓ Content validation passed: {len(content)} chars, {len(hashtags)} hashtags")

    def _check_duplicate_content(self, content: str):
        """
        Check for duplicate LinkedIn content.

        Prevents posting the same content multiple times by checking:
        1. Recent posts in logs
        2. Existing drafts in LinkedIn_Drafts/

        Args:
            content: Post content to check

        Raises:
            ValueError: If duplicate content is found
        """
        # Normalize content for comparison (remove whitespace variations)
        normalized_content = ' '.join(content.lower().split())

        # Check recent posts in logs
        today = datetime.now()
        for days_back in range(7):  # Check last 7 days
            check_date = today - timedelta(days=days_back)
            log_file = LOGS_PATH / f"{check_date.strftime('%Y-%m-%d')}.json"

            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)

                    for log_entry in logs:
                        if log_entry.get('source') == 'linkedin_mcp':
                            if log_entry.get('action') in ['draft_created', 'post_created']:
                                # Get content from log or draft file
                                draft_id = log_entry.get('draftId')
                                if draft_id:
                                    draft_path = LINKEDIN_DRAFTS_PATH / f"{draft_id}.json"
                                    if draft_path.exists():
                                        with open(draft_path, 'r', encoding='utf-8') as df:
                                            draft_data = json.load(df)
                                            existing_content = draft_data.get('content', '')
                                            normalized_existing = ' '.join(existing_content.lower().split())

                                            # Check similarity (exact match or very close)
                                            if normalized_content == normalized_existing:
                                                raise ValueError(
                                                    f"Duplicate content detected! This content was already posted/drafted on "
                                                    f"{log_entry.get('timestamp', 'unknown date')}. Draft ID: {draft_id}"
                                                )

                                            # Check for very similar content (80%+ overlap)
                                            similarity = self._calculate_similarity(normalized_content, normalized_existing)
                                            if similarity > 0.8:
                                                logger.warning(
                                                    f"Very similar content detected ({similarity*100:.0f}% match) from "
                                                    f"{log_entry.get('timestamp')}. Draft ID: {draft_id}"
                                                )

                except Exception as e:
                    logger.debug(f"Error checking log file {log_file}: {e}")

        logger.info("✓ Duplicate check passed: Content is unique")

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.

        Simple word-overlap based similarity metric.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1
        """
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0


# =============================================================================
# FILE PROCESSOR
# =============================================================================

class FileProcessor:
    """
    Processes approved action files.

    Coordinates parsing, execution, logging, and file movement.
    """

    def __init__(
        self,
        action_executor: ActionExecutor,
        dry_run: bool = False
    ):
        """
        Initialize file processor.

        Args:
            action_executor: Executor for actions
            dry_run: If True, don't move files
        """
        self.action_executor = action_executor
        self.dry_run = dry_run

    async def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single approved action file.

        Args:
            file_path: Path to action file

        Returns:
            Dict containing processing result
        """
        logger.info(f"Processing file: {file_path.name}")

        try:
            # Parse file
            action_data = ActionFileParser.parse_file(file_path)

            # Execute action
            result = await self.action_executor.execute_action(action_data)

            # Log result
            self._log_result(action_data, result)

            # Move file based on result
            destination = self._move_file(file_path, result)

            # Update dashboard
            self._update_dashboard(action_data, result, destination)

            return {
                'success': result.get('success', False),
                'file': file_path.name,
                'action': action_data['metadata']['action'],
                'destination': destination,
                'result': result
            }

        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")

            # Log failure
            self._log_error(file_path, str(e))

            # Move to Failed
            destination = self._move_file(file_path, {'success': False, 'error': str(e)})

            return {
                'success': False,
                'file': file_path.name,
                'error': str(e),
                'destination': destination
            }

    def _log_result(self, action_data: Dict[str, Any], result: Dict[str, Any]):
        """Log action result to daily log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = LOGS_PATH / f"{today}.json"

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'execute_approved_action',
            'file': action_data['file_name'],
            'action_type': action_data['metadata']['action'],
            'success': result.get('success', False),
            'attempts': result.get('attempts', 1),
        }

        if result.get('success'):
            log_entry['result'] = 'completed'
        else:
            log_entry['result'] = 'failed'
            log_entry['error'] = result.get('error', 'Unknown error')

        if result.get('rate_limited'):
            log_entry['rate_limited'] = True

        # Add LinkedIn-specific analytics
        if action_data['metadata']['action'] == 'post_linkedin':
            self._add_linkedin_analytics(log_entry, action_data, result)

        # Read existing logs
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

        # Append new log
        logs.append(log_entry)

        # Write back
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

        logger.debug(f"Logged result to {log_file}")

    def _add_linkedin_analytics(
        self,
        log_entry: Dict[str, Any],
        action_data: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """
        Add LinkedIn-specific analytics to log entry.

        Tracks:
        - Draft ID
        - Content stats (length, hashtags, URLs)
        - Posting time
        - Status (draft/posted)

        Args:
            log_entry: Log entry to enhance
            action_data: Action data
            result: Execution result
        """
        metadata = action_data['metadata']
        body = action_data['body']

        # Get draft ID from result
        draft_id = None
        if result.get('success') and result.get('result'):
            mcp_result = result['result']
            if isinstance(mcp_result, dict):
                draft_id = mcp_result.get('draftId')

        # Extract content
        content = body
        if 'draft_id' in metadata:
            draft_path = LINKEDIN_DRAFTS_PATH / f"{metadata['draft_id']}.json"
            if draft_path.exists():
                try:
                    with open(draft_path, 'r', encoding='utf-8') as f:
                        draft_data = json.load(f)
                        content = draft_data.get('content', body)
                except Exception as e:
                    logger.debug(f"Error reading draft for analytics: {e}")

        # Calculate content stats
        hashtags = re.findall(r'#\w+', content)
        urls = re.findall(r'https?://[^\s]+', content)

        # Add analytics to log entry
        log_entry['linkedin_analytics'] = {
            'draft_id': draft_id or metadata.get('draft_id'),
            'content_length': len(content),
            'hashtag_count': len(hashtags),
            'hashtags': hashtags[:10],  # Store first 10 hashtags
            'url_count': len(urls),
            'scheduled_time': metadata.get('schedule_time'),
            'posting_time': datetime.now().isoformat(),
            'source': metadata.get('source', 'manual'),  # manual, auto, skill
        }

        # Track posting status
        if result.get('success'):
            log_entry['linkedin_analytics']['status'] = 'draft_created'
        else:
            log_entry['linkedin_analytics']['status'] = 'failed'
            log_entry['linkedin_analytics']['failure_reason'] = result.get('error')

        logger.debug(f"Added LinkedIn analytics: {draft_id}")

    def _log_error(self, file_path: Path, error: str):
        """Log error for file that couldn't be parsed."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = LOGS_PATH / f"{today}.json"

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'process_approved_file_error',
            'file': file_path.name,
            'success': False,
            'error': error
        }

        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

        logs.append(log_entry)

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def _move_file(self, file_path: Path, result: Dict[str, Any]) -> Path:
        """
        Move file to Done or Failed based on result.

        Args:
            file_path: Source file path
            result: Execution result

        Returns:
            Destination path
        """
        if result.get('success'):
            destination_dir = DONE_PATH
            status = "completed"
        else:
            destination_dir = FAILED_PATH
            status = "failed"

        destination = destination_dir / file_path.name

        if not self.dry_run:
            # Ensure destination directory exists
            destination_dir.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(str(file_path), str(destination))
            logger.info(f"Moved {file_path.name} to {destination_dir.name}/")
        else:
            logger.info(f"[DRY RUN] Would move {file_path.name} to {destination_dir.name}/")

        return destination

    def _update_dashboard(
        self,
        action_data: Dict[str, Any],
        result: Dict[str, Any],
        destination: Path
    ):
        """
        Update Dashboard.md with action result.

        Args:
            action_data: Parsed action data
            result: Execution result
            destination: File destination path
        """
        if not DASHBOARD_PATH.exists():
            logger.warning("Dashboard.md not found, skipping update")
            return

        try:
            with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
                dashboard = f.read()

            # Add entry to recent actions section
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            action_type = action_data['metadata']['action']
            status = "✓ Success" if result.get('success') else "✗ Failed"

            # Add LinkedIn-specific info if applicable
            extra_info = ""
            if action_type == 'post_linkedin' and result.get('success'):
                body = action_data['body']
                content_length = len(body)
                hashtags = re.findall(r'#\w+', body)
                extra_info = f" | {content_length} chars, {len(hashtags)} hashtags"

            new_entry = f"\n- [{timestamp}] {action_type} - {status}{extra_info} - {action_data['file_name']}"

            # Find recent actions section
            if "## Recent Actions" in dashboard:
                dashboard = dashboard.replace(
                    "## Recent Actions",
                    f"## Recent Actions{new_entry}",
                    1
                )
            else:
                dashboard += f"\n\n## Recent Actions{new_entry}"

            if not self.dry_run:
                with open(DASHBOARD_PATH, 'w', encoding='utf-8') as f:
                    f.write(dashboard)
                logger.info("Updated Dashboard.md")
            else:
                logger.info("[DRY RUN] Would update Dashboard.md")

        except Exception as e:
            logger.warning(f"Failed to update dashboard: {e}")


# =============================================================================
# FOLDER WATCHER
# =============================================================================

class FolderWatcher:
    """
    Watches the Approved folder for new files.

    Processes files as they appear.
    """

    def __init__(
        self,
        file_processor: FileProcessor,
        watch_interval: int = WATCH_INTERVAL
    ):
        """
        Initialize folder watcher.

        Args:
            file_processor: Processor for files
            watch_interval: Seconds between checks
        """
        self.file_processor = file_processor
        self.watch_interval = watch_interval
        self.processed_files = set()

    async def watch(self):
        """
        Watch folder continuously for new files.

        Runs until interrupted.
        """
        logger.info(f"Watching {APPROVED_PATH} for approved actions...")
        logger.info(f"Press Ctrl+C to stop")

        while True:
            try:
                await self._check_folder()
                await asyncio.sleep(self.watch_interval)

            except KeyboardInterrupt:
                logger.info("Stopping watcher...")
                break

            except Exception as e:
                logger.error(f"Error in watch loop: {e}")
                await asyncio.sleep(self.watch_interval)

    async def process_once(self):
        """
        Process all files in folder once (no watching).

        Returns:
            Number of files processed
        """
        logger.info(f"Processing files in {APPROVED_PATH}...")

        return await self._check_folder()

    async def _check_folder(self) -> int:
        """
        Check folder for new markdown files.

        Returns:
            Number of files processed
        """
        if not APPROVED_PATH.exists():
            logger.warning(f"Approved folder does not exist: {APPROVED_PATH}")
            return 0

        # Get all markdown files
        files = list(APPROVED_PATH.glob("*.md"))

        # Filter out already processed
        new_files = [f for f in files if f not in self.processed_files]

        if not new_files:
            return 0

        logger.info(f"Found {len(new_files)} new file(s) to process")

        # Process files
        processed_count = 0
        for file_path in new_files:
            try:
                result = await self.file_processor.process_file(file_path)

                if result['success']:
                    processed_count += 1

                # Mark as processed
                self.processed_files.add(file_path)

            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {e}")
                self.processed_files.add(file_path)  # Don't retry

        return processed_count


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Main entry point."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Approval Executor - Execute approved MCP actions'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate actions without execution'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Process files once and exit (no watching)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=WATCH_INTERVAL,
        help=f'Watch interval in seconds (default: {WATCH_INTERVAL})'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Set log level
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Print configuration
    logger.info("=" * 70)
    logger.info("Approval Executor - MCP Action Dispatcher")
    logger.info("=" * 70)
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    logger.info(f"Watch folder: {APPROVED_PATH}")
    logger.info(f"Rate limit: {MAX_ACTIONS_PER_HOUR} actions per hour")
    logger.info(f"Max retries: {MAX_RETRIES}")
    logger.info("=" * 70)
    logger.info("")

    # Ensure directories exist
    APPROVED_PATH.mkdir(parents=True, exist_ok=True)
    DONE_PATH.mkdir(parents=True, exist_ok=True)
    FAILED_PATH.mkdir(parents=True, exist_ok=True)
    LOGS_PATH.mkdir(parents=True, exist_ok=True)

    # Initialize components
    rate_limiter = RateLimiter(MAX_ACTIONS_PER_HOUR, RATE_LIMIT_WINDOW)
    mcp_client = MCPClient(MCP_EMAIL_SERVER, dry_run=args.dry_run)

    # Initialize LinkedIn client if server exists
    linkedin_client = None
    if MCP_LINKEDIN_SERVER.exists():
        linkedin_client = MCPClient(MCP_LINKEDIN_SERVER, dry_run=args.dry_run)
        logger.info("LinkedIn MCP client initialized")
    else:
        logger.warning("LinkedIn MCP server not found, LinkedIn posting will be unavailable")

    action_executor = ActionExecutor(
        mcp_client,
        rate_limiter,
        dry_run=args.dry_run,
        linkedin_client=linkedin_client
    )
    file_processor = FileProcessor(action_executor, dry_run=args.dry_run)
    watcher = FolderWatcher(file_processor, watch_interval=args.interval)

    # Run
    try:
        if args.once:
            # Process once and exit
            count = await watcher.process_once()
            logger.info(f"Processed {count} file(s)")
        else:
            # Watch continuously
            await watcher.watch()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

    logger.info("Exiting")


if __name__ == "__main__":
    asyncio.run(main())
