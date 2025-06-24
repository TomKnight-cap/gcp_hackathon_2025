import os
import sys
sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response
from tools import get_customer_details, get_wifi_packages, create_summary_table
from prompts import greeter_prompt, wifi_prompt, mobilephone_prompt, homephone_prompt, summary_prompt
from dotenv import load_dotenv
from google.adk import Agent
from google.genai import types
from typing import Optional, List, Dict
from google.adk.tools.tool_context import ToolContext

load_dotenv()
model_name = os.getenv("MODEL")


### Summariser/Sales Agents ###
# The summariser agent uses a tool to gather relevant information and prepare it in a document.
# This can be relayed back to the use for confirmation/edits - increasing trust.
# And it makes it straightforward to either implement an integrated sales agent, or pass onto a human agent to complete the sale.

summary_agent = Agent(
    name="summary_agent",
    model=model_name,
    description="Summarise the user's intended upgrade to help with sales.",
    instruction=summary_prompt,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[create_summary_table]
)



### Recommendation Agents ###
# These agents each have their own speciality based on a range of products.
# They will ask the user questions, and use this information, as well as access to live prices data, to make personalised suggestions.
# They have similar instructions, but splitting them out like adds much greater flexibility to test/modify each one in an enterprise setting.

wifi_helper = Agent(
    name="wifi_helper",
    model=model_name,
    description="Help a user to improve their wifi package.",
    instruction=wifi_prompt,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    generate_content_config=types.GenerateContentConfig(
    temperature=0,
    ),
    tools=[get_wifi_packages]
)

homephone_helper = Agent(
    name="homephone_helper",
    model=model_name,
    description="Help a user to improve their homephone deal.",
    instruction=homephone_prompt,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    generate_content_config=types.GenerateContentConfig(
    temperature=0,
    ),
    tools=[]
)

mobilephone_helper = Agent(
    name="mobilephone_helper",
    model=model_name,
    description="Help a user to improve their mobile contract.",
    instruction=mobilephone_prompt,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    generate_content_config=types.GenerateContentConfig(
    temperature=0,
    ),
    tools=[]
)



### Greeter Agent ###
# This agent is the first customer support agent, who keeps an eye out for opportunities to cross sell / upsell.
# When it finds one, it will pass over to the relevant expert agent to make personally relevant offers.

root_agent = Agent(
    name="steering",
    model=model_name,
    description="Help a user solve their problems with our products.",
    instruction=greeter_prompt,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    tools=[get_customer_details],
    sub_agents=[wifi_helper, mobilephone_helper, homephone_helper, summary_agent]
)