import os
import re
import json
import csv
from typing import Optional, List, Dict, Any
from google.adk.tools.tool_context import ToolContext


### Get Customer Details Tool ###
# Reads the customer details database file, and extracts the user's information
def get_customer_details(
    tool_context: ToolContext,
    customer_name: str,
    account_number: str,
    json_file_path: str = 'customer_data.json'
) -> Dict[str, Any]:
    """
    Searches a JSON file for customer details by name and account number.

    Args:
        tool_context: The context for the tool, provided by ADK.
        customer_name: The name of the customer to search for.
        account_number: The account number of the customer to search for.
        json_file_path: The path to the customer data JSON file.

    Returns:
        A dictionary containing the status of the operation and the
        customer's data if found.
    """
    if not os.path.exists(json_file_path):
        return {
            "status": "error",
            "message": f"The data file was not found."
        }
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            all_customers = json.load(f)

        for customer in all_customers:
            # Normalize and compare both name and account number for a robust match
            if (customer.get('Customer Name', '').strip().lower() == customer_name.strip().lower() and
                    customer.get('Account Number', '').strip() == account_number.strip()):
                
                # Customer found, return their details
                return {
                    "status": "success",
                    "data": customer
                }
        
        # If the loop completes without finding a match
        return {
            "status": "not_found",
            "message": f"No customer found with Name: '{customer_name}' and Account Number: '{account_number}'."
        }

    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "The JSON data file is corrupted or not in the correct format."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An unexpected error occurred: {e}"
        }


### Get Prices Tool ###
# Reads the packages database file, and extracts relevant price points to offer to the user
def get_wifi_packages(
    tool_context: ToolContext,
    json_file_path: str = 'wifi_packages.json'
) -> Dict[str, Any]:
    """
    Retrieves a list of all available WiFi packages from a JSON file.

    Args:
        tool_context: The context for the tool, provided by ADK.
        json_file_path: The path to the WiFi packages JSON data file.

    Returns:
        A dictionary containing the status of the operation and a list
        of all WiFi package options if successful.
    """
    if not os.path.exists(json_file_path):
        return {
            "status": "error",
            "message": f"The WiFi packages data file was not found at the specified path: {json_file_path}"
        }
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            wifi_packages_data = json.load(f)
        
        return {
            "status": "success",
            "data": wifi_packages_data
        }

    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "The JSON data file is corrupted or not in the correct format."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An unexpected error occurred while reading the packages file: {e}"
        }


### Create Summary Tool ###
#Reads the conversation history and creates a table of relevant information to be passed on
def create_summary_table(tool_context: ToolContext) -> Dict[str, Any]:

    """
    Analyzes the conversation history to extract key user information and the new plan.
    It then creates a summary table and saves it to the state.

    Args:
        tool_context (ToolContext): The context object provided by the ADK,
                                     which contains the conversation state.

    Returns:
        dict[str, Any]: A dictionary containing a status message.
    """
    # Load conversation history from state (e.g., from 'history' key).
    history = tool_context.state.get("history", [])

    # Initialize variables
    user_name = "Not found"
    user_id = "Not found"
    current_issue = "Not found"
    new_plan = "Not found"

    # --- Extraction Logic (using regex or other methods) ---
    
    # Combine all user messages into a single string for easier searching
    user_messages = "\n".join([
        msg.get("content", "") for msg in history if msg.get("author") == "user"
    ])

    # Define regex patterns
    name_pattern = re.compile(r"my name is ([\w\s]+?)(?:\.|\n|$)", re.IGNORECASE)
    id_pattern = re.compile(r"user ID is ([\w\d\-]+)", re.IGNORECASE)
    issue_pattern = re.compile(r"(?:issue with|problem with|trouble with)\s(.*?)(?:\.|\n|$)", re.IGNORECASE)
    plan_pattern = re.compile(r"(?:interested in the|upgrade to the|go with the|switch to the)\s([\w\s]+?)\splan", re.IGNORECASE)

    # Extract information
    name_match = name_pattern.search(user_messages)
    if name_match:
        user_name = name_match.group(1).strip()

    id_match = id_pattern.search(user_messages)
    if id_match:
        user_id = id_match.group(1).strip()

    issue_match = issue_pattern.search(user_messages)
    if issue_match:
        current_issue = issue_match.group(1).strip()

    plan_match = plan_pattern.search(user_messages)
    if plan_match:
        new_plan = plan_match.group(1).strip()

    # --- End of Extraction Logic ---

    # Create the summary table
    summary_table = {
        "User name": user_name,
        "User ID": user_id,
        "Current issue": current_issue,
        "New plan": new_plan,
    }

    # Save the summary table back to the state
    tool_context.state["summary_table"] = summary_table

    # Return a status message
    found_items = sum(1 for value in summary_table.values() if value != "Not found")
    return {
        "status": "success",
        "message": f"Summary table created. Found {found_items} of 4 items.",
    }
