from __future__ import annotations

import json
import time

from duckduckgo_search import DDGS

from ..registry import action
from forge.utils.exceptions import ConfigurationError
from forge.utils.url_validator import JSONSchema

DUCKDUCKGO_MAX_ATTEMPTS = 3


@action(
    name="web_search",
    description="Searches the web",
    parameters=[
        {
            "name": "query",
            "description": "The search query",
            "type": "string",
            "required": True,
        }
    ],
    output_type="list[str]",
)
async def web_search(agent, task_id: str, query: str) -> str:
    """Return the results of a Google search

    Args:
        query (str): The search query.
        num_results (int): The number of results to return.

    Returns:
        str: The results of the search.
    """
    search_results = []
    attempts = 0
    num_results = 8

    while attempts < DUCKDUCKGO_MAX_ATTEMPTS:
        if not query:
            return json.dumps(search_results)

        search_results = DDGS().text(query, max_results=num_results)

        if search_results:
            break

        time.sleep(1)
        attempts += 1

    results = json.dumps(search_results, ensure_ascii=False, indent=4)
    return safe_google_results(results)


@action(
    name="google",
    description="Google Search",
    parameters={
        "query": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The search query",
            required=True,
        ),
        "num_results": JSONSchema(
            type=JSONSchema.Type.INTEGER,
            description="The number of results to return",
            minimum=1,
            maximum=10,
            required=False,
        ),
    },
)
async def google(self, query: str, num_results: int = 8) -> str | list[str]:
    """Return the results of a Google search using the official Google API

    Args:
        query (str): The search query.
        num_results (int): The number of results to return.

    Returns:
        str: The results of the search.
    """

    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    try:
        # Should be the case if this command is enabled:
        assert self.config.google_api_key
        assert self.config.google_custom_search_engine_id

        # Initialize the Custom Search API service
        service = build(
            "customsearch",
            "v1",
            developerKey=self.config.google_api_key.get_secret_value(),
        )

        # Send the search query and retrieve the results
        result = (
            service.cse()
            .list(
                q=query,
                cx=self.config.google_custom_search_engine_id.get_secret_value(),
                num=num_results,
            )
            .execute()
        )

        # Extract the search result items from the response
        search_results = result.get("items", [])

        # Create a list of only the URLs from the search results
        search_results_links = [item["link"] for item in search_results]

    except HttpError as e:
        # Handle errors in the API call
        error_details = json.loads(e.content.decode())

        # Check if the error is related to an invalid or missing API key
        if error_details.get("error", {}).get(
                "code"
        ) == 403 and "invalid API key" in error_details.get("error", {}).get(
            "message", ""
        ):
            raise ConfigurationError(
                "The provided Google API key is invalid or missing."
            )
        raise
    # google_result can be a list or a string depending on the search results

    # Return the list of search result URLs
    return self.safe_google_results(search_results_links)


def safe_google_results(results: str | list) -> str:
    """
        Return the results of a Google search in a safe format.

    Args:
        results (str | list): The search results.

    Returns:
        str: The results of the search.
    """
    if isinstance(results, list):
        safe_message = json.dumps(
            [result.encode("utf-8", "ignore").decode("utf-8") for result in results]
        )
    else:
        safe_message = results.encode("utf-8", "ignore").decode("utf-8")
    return safe_message
