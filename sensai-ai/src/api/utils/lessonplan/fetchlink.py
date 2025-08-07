import os
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
import requests
from typing import List, Optional, Union
from urllib.parse import quote_plus
import asyncio
import re

load_dotenv()

search = GoogleSerperAPIWrapper()

def _clean(text: str) -> str:
    """Lower-case, strip punctuation that breaks Google query parsing."""
    text = text.lower()
    text = re.sub(r'["""''–—,:;]', " ", text)   # kill quotes, dashes, colons …
    text = re.sub(r"\s+", " ", text)            # squeeze spaces
    return text.strip()

async def fetch_resources(state, class_topic: str) -> Optional[str]:
    """
    Looks up supporting content for a lesson topic.

    Search order
    ------------
    1. Khan Academy page that explicitly references **NCERT**.
    2. Khan Academy page that matches the **topic** in general.
    3. Two most-relevant YouTube videos.
       (Only queried if the Khan Academy step succeeds, to keep output size modest.)

    Returns
    -------
    * A newline-separated string of URLs if at least one resource is found.
    * ``None`` if nothing relevant could be located.
    * An error string if a network/credentials issue occurs.
    """
    grade          = state["grade"]          # e.g. 3
    subject        = state["subject"]        # e.g. "English"
    chapter_name   = state["chapter_name"]   # e.g. "Badal and Moti"
    board          = state["board"]          # e.g. "CBSE"
    chapter_number = state["chapter_number"] # e.g. 7

    # ----------------------------
    # Helper: first Khan link only
    # ----------------------------

    topic_str   = " ".join(class_topic) if isinstance(class_topic, (list, tuple)) else class_topic
    topic_clean = _clean(topic_str)

    def first_khan_link(results: dict) -> Optional[str]:
        for entry in results.get("organic", []):
            url = entry.get("link", "")
            if "khanacademy.org" in url:
                return url
        return None

    resource_links: List[str] = []
    # ----------------------------------
    # 1️⃣  NCERT-specific Khan search
    # ----------------------------------
    query_ncert = (
        f"site:khanacademy.org {subject} {chapter_name} "
        f"NCERT class {grade}"
    )
    khan_url = first_khan_link(search.results(query_ncert))

    # --------------------------------------------------------
    # 2️⃣  Topic-specific fallback if NCERT search came up dry
    # --------------------------------------------------------
    if khan_url is None:
        query_chapter_num = (
            f"site:khanacademy.org {subject} {chapter_number} "
            f"NCERT class {grade}"
        )
        query_topic = (
            f"site:khanacademy.org {subject} {topic_clean} "
            f"class {grade}"
        )
        khan_url_1 = first_khan_link(search.results(query_topic))
        khan_url_2 = first_khan_link(search.results(query_chapter_num))

        # Stop early if no Khan Academy page is available
        if khan_url_1 is not None:
            resource_links.append(khan_url_1)
        if khan_url_2 is not None:
            resource_links.append(khan_url_2)
    # -------------------
    # 3️⃣  YouTube videos
    # -------------------
    api_key = os.getenv("YOUTUBE_DATA_API_KEY")
    if not api_key:
        return "Error: YouTube API key not found."

    yt_queries = [
        f"{board} class {grade} {subject} chapter {chapter_number} "
        f"{chapter_name} - topic is {class_topic}",
        f"{subject} {chapter_name} class {grade} video"
    ]

    video_urls: List[str] = []
    for q in yt_queries:
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&q={q}&key={api_key}&type=video"
            "&order=relevance&videoCategoryId=27"
        )
        try:
            data = requests.get(url, timeout=10).json()
        except Exception as ex:
            return f"Error hitting YouTube API: {ex}"

        if "items" not in data:
            continue

        for item in data["items"]:
            if item.get("id", {}).get("kind") == "youtube#video":
                video_id = item["id"]["videoId"]
                video_urls.append(f"https://www.youtube.com/watch?v={video_id}")
                if len(video_urls) == 2:
                    break
        if video_urls:
            break  # stop after first query that yields videos

    if video_urls:
        resource_links.extend(video_urls)

    # ----------------
    # Assemble output
    # ----------------
    if not resource_links:
        return None

    return "\n".join(resource_links)
