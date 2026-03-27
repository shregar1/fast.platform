"""
GitHub API client
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class GitHubIssue:
    """GitHub issue"""
    number: int
    title: str
    state: str
    body: Optional[str] = None
    labels: List[str] = None
    assignees: List[str] = None


@dataclass
class GitHubPR:
    """GitHub pull request"""
    number: int
    title: str
    state: str
    body: Optional[str] = None
    branch: str = ""
    base_branch: str = ""


class GitHubClient:
    """
    GitHub API client
    """
    
    def __init__(self, token: str):
        self.token = token
        self._headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self._session = None
    
    def _get_session(self):
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession(headers=self._headers)
        return self._session
    
    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> GitHubIssue:
        """Create an issue"""
        import aiohttp
        
        session = self._get_session()
        
        payload = {"title": title}
        if body:
            payload["body"] = body
        if labels:
            payload["labels"] = labels
        if assignees:
            payload["assignees"] = assignees
        
        async with session.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            json=payload
        ) as response:
            data = await response.json()
            return GitHubIssue(
                number=data["number"],
                title=data["title"],
                state=data["state"],
                body=data.get("body"),
                labels=[l["name"] for l in data.get("labels", [])],
                assignees=[a["login"] for a in data.get("assignees", [])]
            )
    
    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None
    ) -> GitHubPR:
        """Create a pull request"""
        import aiohttp
        
        session = self._get_session()
        
        payload = {
            "title": title,
            "head": head,
            "base": base
        }
        if body:
            payload["body"] = body
        
        async with session.post(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            json=payload
        ) as response:
            data = await response.json()
            return GitHubPR(
                number=data["number"],
                title=data["title"],
                state=data["state"],
                body=data.get("body"),
                branch=head,
                base_branch=base
            )
    
    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: Optional[str] = None
    ) -> Optional[str]:
        """Get file content from repository"""
        import aiohttp
        import base64
        
        session = self._get_session()
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        if ref:
            url += f"?ref={ref}"
        
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                content = base64.b64decode(data["content"]).decode("utf-8")
                return content
            return None
    
    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
        sha: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update a file"""
        import aiohttp
        import base64
        
        session = self._get_session()
        
        encoded_content = base64.b64encode(content.encode()).decode()
        
        payload = {
            "message": message,
            "content": encoded_content,
            "branch": branch
        }
        
        if sha:
            payload["sha"] = sha
        
        async with session.put(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            json=payload
        ) as response:
            return await response.json()
    
    async def list_releases(
        self,
        owner: str,
        repo: str
    ) -> List[Dict[str, Any]]:
        """List repository releases"""
        import aiohttp
        
        session = self._get_session()
        
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}/releases"
        ) as response:
            return await response.json()
    
    async def create_release(
        self,
        owner: str,
        repo: str,
        tag_name: str,
        name: str,
        body: Optional[str] = None,
        draft: bool = False,
        prerelease: bool = False
    ) -> Dict[str, Any]:
        """Create a release"""
        import aiohttp
        
        session = self._get_session()
        
        payload = {
            "tag_name": tag_name,
            "name": name,
            "draft": draft,
            "prerelease": prerelease
        }
        
        if body:
            payload["body"] = body
        
        async with session.post(
            f"https://api.github.com/repos/{owner}/{repo}/releases",
            json=payload
        ) as response:
            return await response.json()
    
    async def close(self):
        """Close the HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None
