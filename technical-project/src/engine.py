def match_policy(policy: dict, subject: dict, resource: dict, request: dict) -> list | None:
    """Check if a single policy matches the request. 
    Returns a list of matched conditions, or None if no match is found."""

    matched = []

    # conditions of the subject:
    policy_subject = policy.get("subject", {})

    if "role" in policy_subject:
        if subject["role"] != policy_subject["role"]:
            return None
        matched.append(f"subject.role={policy_subject['role']}")
    if "clearance_min" in policy_subject:
        if subject["clearance"] < policy_subject["clearance_min"]:
            return None
        matched.append(f"subject.clearance>={policy_subject['clearance_min']}")

    # conditions of the resource:
    policy_resource = policy.get("resource", {})

    if "type" in policy_resource:
        if resource["type"] != policy_resource["type"]:
            return None
        matched.append(f"resource.type={policy_resource['type']}")
    if "classification" in policy_resource:
        if resource["classification"] != policy_resource["classification"]:
            return None
        matched.append(f"resource.classification={policy_resource['classification']}")
    if "owner_is_subject" in policy_resource and policy_resource["owner_is_subject"]:
        if resource["owner"] != request["subject_id"]:
            return None
        matched.append("owner_is_subject=true")
    
    # action:
    if request["action"] not in policy.get("actions", []):
        return None
    matched.append(f"action={request['action']}")

    # context conditions:
    policy_context = policy.get("context", {})
    request_context = request.get("context", {})

    if "mfa_required" in policy_context and policy_context["mfa_required"]:
        if not request_context.get("mfa", False):
            return None
        matched.append("context.mfa=true")
    if "hour_min" in policy_context or "hour_max" in policy_context:
        hour = request_context.get("hour")
        if hour is None:
            return None
        if "hour_min" in policy_context and hour < policy_context["hour_min"]:
            return None
        if "hour_max" in policy_context and hour > policy_context["hour_max"]:
            return None
        parts = []
        if "hour_min" in policy_context:
            parts.append(f">={policy_context['hour_min']}")
        if "hour_max" in policy_context:
            parts.append(f"<={policy_context['hour_max']}")
        matched.append("context.hour " + ", ".join(parts))

    return matched
    

def evaluate_request(request: dict, subject_map: dict, resource_map: dict, policies: dict) -> dict:
    """Evaluate a single request. Returns a result dict."""

    subject_id = request["subject_id"]
    resource_id = request["resource_id"]

    done = False
    decision = None
    matched_policy = None
    matched_conditions = []

    if subject_id not in subject_map or resource_id not in resource_map:
        decision = "Deny"
        done = True

    if not done:
        subject = subject_map[subject_id]
        resource = resource_map[resource_id]
        for policy in policies:
            matched_conditions = match_policy(policy, subject, resource, request)
            if matched_conditions is not None:
                decision = "Permit"
                matched_policy = policy["id"]
                done = True
                break
    
    if not done:
        decision = "Deny"
        matched_conditions = []

    return {
        "request_id": request["request_id"],
        "decision": decision,
        "matched_policy": matched_policy,
        "matched_conditions": matched_conditions,
    }
    

def evaluate_requests(requests: dict, subject_map: dict, resource_map: dict, policies: dict) -> dict:
    """Evaluate all requests and return the output dict."""
    
    results = []
    for request in requests:
        result = evaluate_request(request, subject_map, resource_map, policies)
        results.append(result)

    tot_permitted = sum(1 for r in results if r["decision"] == "Permit")
    tot_denied = len(results) - tot_permitted

    return {
        "summary": {
            "total_requests": len(results),
            "permitted_requests": tot_permitted,
            "denied_requests": tot_denied
        },
        "results": results
    }
