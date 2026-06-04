import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.loader import load_json

Subject = Dict[str, Any]
Resource = Dict[str, Any]
Policy = Dict[str, Any]
Request = Dict[str, Any]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input directory")
    parser.add_argument("--output", required=True, help="Output JSON file")
    return parser.parse_args()


def build_dicts(items):
    dictionary = {}

    for item in items:
        item_id = item.get("id")

        if item_id is not None:
            dictionary[item_id] = item

    return dictionary


def check_subject_conditions(policy_subject, subject):

    matched_conditions = []

    if "role" in policy_subject:
        required_role = policy_subject["role"]

        if subject.get("role") != required_role:
            return False, []

        matched_conditions.append(f"subject.role={required_role}")

    if "clearance_min" in policy_subject:
        minimum_clearance = policy_subject["clearance_min"]
        subject_clearance = subject.get("clearance")

        if subject_clearance is None or subject_clearance < minimum_clearance:
            return False, []

        matched_conditions.append(f"subject.clearance>={minimum_clearance}")

    return True, matched_conditions


def check_resource_conditions(policy_resource, resource, subject_id):

    matched_conditions = []

    if "type" in policy_resource:
        required_type = policy_resource["type"]

        if resource.get("type") != required_type:
            return False, []

        matched_conditions.append(f"resource.type={required_type}")

    if "classification" in policy_resource:
        required_classification = policy_resource["classification"]

        if resource.get("classification") != required_classification:
            return False, []

        matched_conditions.append(f"resource.classification={required_classification}")

    if policy_resource.get("owner_is_subject") is True:
        if resource.get("owner") != subject_id:
            return False, []

        matched_conditions.append("owner_is_subject=true")

    return True, matched_conditions


def check_action(policy_actions, requested_action):

    if requested_action in policy_actions:
        return True, [f"action={requested_action}"]

    return False, []


def check_context_conditions(policy_context, request_context):

    matched_conditions = []

    if policy_context.get("mfa_required") is True:
        if request_context.get("mfa") == False:
            return False, []

        matched_conditions.append("context.mfa=true")

    if "hour_min" in policy_context or "hour_max" in policy_context:
        request_hour = request_context.get("hour")

        if (
            request_hour < policy_context["hour_min"]
            or request_hour > policy_context["hour_max"]
        ):
            return False, []

        matched_conditions.append(
            f"context.hour_between={policy_context['hour_min']}-{policy_context['hour_max']}"
        )

    return True, matched_conditions


def policy_matches(policy, request, subject, resource):

    matched_conditions = []

    subject_ok, subject_matches = check_subject_conditions(
        policy.get("subject"), subject
    )

    if subject_ok == False:
        return False, []
    matched_conditions.extend(subject_matches)

    resource_ok, resource_matches = check_resource_conditions(
        policy.get("resource", {}), resource, request.get("subject_id", "")
    )
    if resource_ok == False:
        return False, []
    matched_conditions.extend(resource_matches)

    action_ok, action_matches = check_action(
        policy.get("actions", []), request.get("action", "")
    )
    if action_ok == False:
        return False, []
    matched_conditions.extend(action_matches)

    context_ok, context_matches = check_context_conditions(
        policy.get("context", {}),
        request.get("context", {}),
    )
    if context_ok == False:
        return False, []
    matched_conditions.extend(context_matches)

    return True, matched_conditions


def evaluate_request(request, subjects_by_id, resources_by_id, policies):

    request_id = request.get("request_id")
    subject_id = request.get("subject_id")
    resource_id = request.get("resource_id")

    subject = subjects_by_id.get(subject_id)
    resource = resources_by_id.get(resource_id)

    if subject is None or resource is None:
        return {
            "request_id": request_id,
            "decision": "Deny",
            "matched_policy": None,
            "matched_conditions": [],
        }

    for policy in policies:
        matches, matched_conditions = policy_matches(policy, request, subject, resource)

        if matches:
            return {
                "request_id": request_id,
                "decision": "Permit",
                "matched_policy": policy.get("id"),
                "matched_conditions": matched_conditions,
            }

    return {
        "request_id": request_id,
        "decision": "Deny",
        "matched_policy": None,
        "matched_conditions": [],
    }


def evaluate_requests(subjects_data, resources_data, policies_data, requests_data):

    subjects = subjects_data.get("subjects", [])
    resources = resources_data.get("resources", [])
    policies = policies_data.get("policies", [])
    requests = requests_data.get("requests", [])

    subjects_by_id = build_dicts(subjects)
    resources_by_id = build_dicts(resources)
    
    results = []

    for request in requests:
        results.append(evaluate_request(request, subjects_by_id, resources_by_id, policies))
    
    
    permitted_requests = denied_requests = 0    
    
    for result in results:
        if(result["decision"] == "Permit"):
            permitted_requests += 1
        elif(result["decision"] == "Deny"):
            denied_requests += 1
            
    return {
        "summary": {
            "total_requests": len(results),
            "permitted_requests": permitted_requests,
            "denied_requests": denied_requests,
        },
        "results": results,
    }


def main():
    args = parse_args()
    input_dir = Path(args.input)

    subjects = load_json(input_dir / "subjects.json")
    resources = load_json(input_dir / "resources.json")
    policies = load_json(input_dir / "policies.json")
    requests = load_json(input_dir / "requests.json")

    result = evaluate_requests(subjects, resources, policies, requests)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
