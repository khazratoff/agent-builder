"""
Research and web search tools for the ResearchAgent.

These tools provide web search, content summarization, and information
extraction capabilities.
"""

from langchain.tools import tool
from langchain_openai import ChatOpenAI
import os


# Initialize LLM for summarization tasks
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for information.

    This tool performs a web search and returns relevant results.
    Uses DuckDuckGo search (no API key required).

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        str: Formatted search results with titles, URLs, and snippets

    Example:
        web_search("LangGraph tutorial", max_results=3)
    """
    try:
        # Try to use DuckDuckGo search
        try:
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return f"No results found for query: '{query}'"

            formatted_results = [f"Search results for '{query}':\n"]

            for idx, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                url = result.get('href', 'No URL')
                snippet = result.get('body', 'No description')

                formatted_results.append(f"{idx}. {title}")
                formatted_results.append(f"   URL: {url}")
                formatted_results.append(f"   {snippet}\n")

            return "\n".join(formatted_results)

        except ImportError:
            return (
                "Error: DuckDuckGo search is not installed. "
                "Install it with: pip install duckduckgo-search\n\n"
                "Alternatively, for production use, consider using Tavily API:\n"
                "pip install tavily-python"
            )

    except Exception as e:
        return f"Error performing web search: {str(e)}"


@tool
def summarize_content(content: str, max_length: int = 200) -> str:
    """
    Summarize long text content into a concise summary.

    This tool uses an LLM to create a brief summary of longer content,
    making it easier to understand key points quickly.

    Args:
        content: The text content to summarize
        max_length: Approximate maximum length of summary in words (default: 200)

    Returns:
        str: A concise summary of the content

    Example:
        summarize_content("Long article text here...", max_length=150)
    """
    try:
        if len(content.strip()) == 0:
            return "Error: Content is empty."

        if len(content.split()) <= max_length:
            return f"Content is already concise ({len(content.split())} words). No summarization needed:\n\n{content}"

        prompt = f"""Summarize the following content in approximately {max_length} words or less.
Focus on the key points and main ideas:

{content}

Summary:"""

        response = llm.invoke(prompt)
        summary = response.content.strip()

        return f"Summary ({len(summary.split())} words):\n\n{summary}"

    except Exception as e:
        return f"Error summarizing content: {str(e)}"


@tool
def extract_information(content: str, query: str) -> str:
    """
    Extract specific information from content based on a query.

    This tool uses an LLM to find and extract relevant information
    from a larger body of text based on what you're looking for.

    Args:
        content: The text content to extract from
        query: What information to look for

    Returns:
        str: The extracted information or a message if not found

    Example:
        extract_information("Article about AI...", "What is LangGraph?")
    """
    try:
        if len(content.strip()) == 0:
            return "Error: Content is empty."

        if len(query.strip()) == 0:
            return "Error: Query is empty."

        prompt = f"""From the following content, extract information relevant to this query: "{query}"

If the information is present, provide a clear and concise answer.
If the information is not present, say "Information not found in the provided content."

Content:
{content}

Extracted Information:"""

        response = llm.invoke(prompt)
        extracted = response.content.strip()

        return extracted

    except Exception as e:
        return f"Error extracting information: {str(e)}"


@tool
def analyze_topic(topic: str) -> str:
    """
    Get a comprehensive analysis of a topic.

    This tool provides detailed information about a given topic,
    including key concepts, applications, and relevant context.

    Args:
        topic: The topic to analyze

    Returns:
        str: Detailed analysis of the topic

    Example:
        analyze_topic("Multi-agent systems in AI")
    """
    try:
        if len(topic.strip()) == 0:
            return "Error: Topic is empty."

        prompt = f"""Provide a comprehensive but concise analysis of the following topic:

Topic: {topic}

Include:
1. Definition and key concepts
2. Main applications or use cases
3. Important considerations
4. Related topics or technologies

Analysis:"""

        response = llm.invoke(prompt)
        analysis = response.content.strip()

        return f"Analysis of '{topic}':\n\n{analysis}"

    except Exception as e:
        return f"Error analyzing topic: {str(e)}"
