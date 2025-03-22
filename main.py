import google.generativeai as genai
import json
import re
from typing import TypedDict
from langgraph.graph import StateGraph
from dbManager import create_case, update_case, delete_case, read_all_cases

genai.configure(api_key="INSERT YOUR API KEY")

model = genai.GenerativeModel('models/gemini-1.5-pro')


class CaseState(TypedDict):
    query: str
    extracted_details: dict
    result: str

def extract_case_details(state: CaseState) -> CaseState:
    query = state["query"]

    prompt = f"""
    User request: {query}

    Please extract the necessary details from the query:
    - For creating a case, extract: title, description, status, and attorney (If any of these details are missing, use 'NA').
    - For updating a case, extract: case_id, title, description, status, and attorney (If any are missing, use 'NA').
    - For reading or deleting a case, extract the case_id (If case_id is missing, use 'NA').

    Output JSON format: {{ "action": (Create=0, Read=1, Update=2, Delete=3), "details": {{...}} }}
    """

    response = model.generate_content(prompt)
    json_data = extract_json(response.text)


    if json_data == "Error":
        return {"query": query, "extracted_details": {}, "result": "Error extracting details"}

    return {"query": query, "extracted_details": json_data, "result": ""}

def extract_json(data):
    json_match = re.search(r'\{.*\}', data, re.S)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return "Error"

def handle_create(state: CaseState) -> CaseState:
    title_field = state["extracted_details"].get("details", {}).get("title", "NA")
    description_field =  state["extracted_details"].get("details", {}).get("description", "NA")
    attorney_field =  state["extracted_details"].get("details", {}).get("attorney", "NA") 
    status_field = state["extracted_details"].get("details", {}).get("status", "NA") 

    result = create_case(title=title_field, description=description_field, attorney=attorney_field, status=status_field)
    return {
        **state,
        "result": f"{result}",
    }

def handle_read(state: CaseState) -> CaseState:
    result = read_all_cases()
    return {**state, "result": f"{result}"}

def handle_update(state: CaseState) -> CaseState:
    details = state.get("extracted_details", {}).get("details", {})

    case_id_field, title_field, description_field, attorney_field, status_field = (
        None if details.get(field) == "NA" else details.get(field)
        for field in ["case_id", "title", "description", "attorney", "status"]
    )
   
    result = update_case(case_id=case_id_field, title=title_field, description=description_field, attorney=attorney_field, status=status_field)
   
    return {
        **state,
        "result": f"{result}",
    }

def handle_delete(state: CaseState) -> CaseState:
    case_id_field = state["extracted_details"].get("details", {}).get("case_id", "NA")
    case_id_field = None if case_id_field == "NA" else case_id_field
    result = delete_case(case_id=case_id_field)
    return {**state, "result": f"{result}"}

def route_action(state: CaseState):
    action_map = {
        0: "create",
        1: "read",
        2: "update",
        3: "delete"
    }
    action = state["extracted_details"].get("action", -1)
    return action_map.get(action, "unknown")


workflow = StateGraph(CaseState)

workflow.add_node("extract", extract_case_details)
workflow.add_node("create", handle_create)
workflow.add_node("read", handle_read)
workflow.add_node("update", handle_update)
workflow.add_node("delete", handle_delete)

workflow.set_entry_point("extract")
workflow.add_conditional_edges("extract", route_action, {
    "create": "create",
    "read": "read",
    "update": "update",
    "delete": "delete"
})

app = workflow.compile()


def lambda_handler(event, context):
    
    query = event.get("query")
    if not query:
        return {
            "statusCode": 400,
            "body": json.dumps("No query provided")
        }

    try:
        
        result = app.invoke({"query": query, "extracted_details": {}, "result": ""})
        
        return {
            "statusCode": 200,
            "body": json.dumps({"result": result}) 
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Internal server Error: {e}")
        }

