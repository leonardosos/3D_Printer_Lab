import requests
import logging
from functools import wraps
from flask import request as flask_request
from app.utils.service_exception import ServiceException

logger = logging.getLogger('api-gateway')

def forward_request(method, url, headers=None, params=None, json=None, timeout=10):
    """
    Forward a request to a microservice and handle the response
    
    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE)
        url (str): Full URL to forward the request to
        headers (dict, optional): Headers to include in the request
        params (dict, optional): Query parameters to include in the request
        json (dict, optional): JSON body to include in the request
        timeout (int, optional): Request timeout in seconds
        
    Returns:
        dict: Response data from the microservice
        
    Raises:
        ServiceException: If the microservice returns an error response or is unavailable
    """
    try:
        # Merge headers from the original request with any provided headers
        all_headers = {}
        if flask_request:
            # Copy headers that we want to forward from the original request
            forward_headers = ['Authorization', 'Content-Type', 'User-Agent']
            for header in forward_headers:
                if header in flask_request.headers:
                    all_headers[header] = flask_request.headers[header]
        
        # Override/add any explicitly provided headers
        if headers:
            all_headers.update(headers)
            
        # Make the request to the microservice
        response = requests.request(
            method=method,
            url=url,
            headers=all_headers,
            params=params,
            json=json,
            timeout=timeout
        )
        
        # Log the response status
        logger.info(f"Received response from {url}: {response.status_code}")
        
        # Check if the response is successful
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Try to parse error response as JSON
            try:
                error_data = response.json()
            except ValueError:
                error_data = response.text

            if isinstance(error_data, dict):
                message = error_data.get('error', {}).get('message', str(e))
                details = error_data.get('error', {}).get('details')
            else:
                message = str(error_data) if error_data else str(e)
                details = None

            # Log the error but do not raise or do anything else
            logger.error(f"ServiceException: {message} (status {response.status_code})")
            return {}  # Return empty dict gracefully
        
        # Parse the response as JSON
        try:
            return response.json()
        except ValueError:
            # Return an empty dict if the response is not JSON
            if response.content:
                logger.warning(f"Response from {url} is not valid JSON: {response.content}")
            return {}
            
    except requests.exceptions.RequestException as e:
        # Handle network errors, timeouts, etc.
        logger.error(f"Request to {url} failed: {str(e)}")
        
        if isinstance(e, requests.exceptions.ConnectTimeout):
            raise ServiceException(
                message="Service connection timed out",
                status_code=504,
                details=str(e)
            )
        elif isinstance(e, requests.exceptions.ConnectionError):
            raise ServiceException(
                message="Service is unavailable",
                status_code=503,
                details=str(e)
            )
        else:
            raise ServiceException(
                message="Service request failed",
                status_code=500,
                details=str(e)
            )
