# Licensed under the Apache License, Version 2.0.

PROFILE_ID = "xq.net:profile-0.1"
DIRECTIONALITY = {"unidirectional_observed", "bidirectional_observed"}
FUTURE_AGGREGATE_KEYS = {
    "last_observed", "connections_observed", "total_connections", "total_bytes",
    "total_packets", "aggregate_directionality", "final_directionality",
}

def _prefix(value, prefix): return isinstance(value,str) and value.startswith(prefix)

def _viewpoint_errors(event):
    cls=event.get("class")
    ctx=event.get("context") or {}
    errors=[]
    if cls in {"observation","normalized_observation","transition"}:
        if not ctx.get("observation_point"):
            errors.append("Network Profile observation/normalized_observation/transition requires context.observation_point")
    elif cls in {"derived","fusion","assessment"}:
        one=ctx.get("observation_point")
        many=ctx.get("observation_points")
        if not one and not many:
            errors.append("Network Profile derived/fusion/assessment requires context.observation_point or context.observation_points")
        if many is not None:
            if not isinstance(many,list) or not many or not all(isinstance(x,str) and x for x in many):
                errors.append("context.observation_points must be a non-empty array of non-empty strings")
            elif len(many)!=len(set(many)):
                errors.append("context.observation_points must contain unique identifiers")
    return errors

def validate(event, parse_time):
    errors=[]
    if event.get("modality") != "xq:network": errors.append("Network Profile requires modality xq:network")
    errors.extend(_viewpoint_errors(event))
    feature, action = event.get("feature"), event.get("action")
    subject, obj = event.get("subject"), event.get("object")
    cls=event.get("class")
    ctx=event.get("context") or {}
    prov=event.get("provenance") or {}

    if cls in {"normalized_observation","derived"}:
        for k in ("producer","producer_version","method"):
            if not prov.get(k): errors.append(f"Network Profile {cls} requires provenance.{k}")
    if cls=="normalized_observation" and not prov.get("source_records"):
        errors.append("Network Profile normalized_observation requires provenance.source_records")
    if cls=="derived" and not (prov.get("parents") or prov.get("source_records")):
        errors.append("Network Profile derived event requires provenance.parents or provenance.source_records")

    # first_observed is knowledge derived from observation history, not a direct source field
    if action=="xq.net:first_observed" and cls!="derived":
        errors.append("xq.net:first_observed requires class derived")
    if action=="xq.net:first_observed":
        for key in FUTURE_AGGREGATE_KEYS:
            if key in ctx:
                errors.append(f"first_observed event must not contain whole-window/future aggregate context.{key}")

    if feature=="xq.net:connection":
        if action!="xq:observed": errors.append("network connection observations must use Core xq:observed")
        if cls!="normalized_observation": errors.append("network connection observation requires class normalized_observation")
        if not (_prefix(obj,"endpoint:")): errors.append("network connection object must be an endpoint referent")
        if not any(_prefix(subject,p) for p in ("address:","interface:","device:")): errors.append("network connection subject must be address/interface/device scoped")
    elif feature=="xq.net:communication_relationship":
        if action!="xq.net:first_observed": errors.append("communication relationship event requires xq.net:first_observed")
        if ctx.get("evidence_directionality") not in DIRECTIONALITY: errors.append("communication relationship requires valid context.evidence_directionality")
        if not _prefix(obj,"endpoint:"): errors.append("communication relationship object must be endpoint-scoped unless documented fusion is used")
    elif feature=="xq.net:address_binding":
        if not _prefix(obj,"address:"): errors.append("address binding object must be address-scoped")
        if action=="xq.net:first_observed":
            if not _prefix(subject,"interface:"): errors.append("ARP-style first_observed address binding subject must be interface-scoped")
        elif action=="xq.net:assigned":
            if not any(_prefix(subject,p) for p in ("interface:","device:")): errors.append("assigned address binding subject must be interface/device scoped")
    elif feature=="xq.net:hostname_binding":
        if action!="xq.net:reported": errors.append("hostname binding requires xq.net:reported")
        if not any(_prefix(subject,p) for p in ("interface:","device:")): errors.append("hostname binding subject must be interface/device scoped")
        if not _prefix(obj,"name:host:"): errors.append("hostname binding object must be name:host scoped")
    elif feature=="xq.net:dns_query":
        if action!="xq.net:queried": errors.append("DNS query requires xq.net:queried")
        if not _prefix(obj,"domain:"): errors.append("DNS query object must be domain-scoped")
        for forbidden in ("response_code","answer_count","answers","rejected","error"):
            if forbidden in ctx and "end_time" not in event:
                errors.append(f"point DNS query must not contain response-derived context.{forbidden}")
    elif feature=="xq.net:name_resolution":
        if action!="xq.net:resolved_to": errors.append("DNS address resolution requires xq.net:resolved_to")
        if not _prefix(subject,"domain:") or not _prefix(obj,"address:"): errors.append("DNS address resolution must map domain subject to address object")
    elif feature=="xq.net:name_alias":
        if action!="xq.net:alias_of": errors.append("DNS alias requires xq.net:alias_of")
        if not _prefix(subject,"domain:") or not _prefix(obj,"domain:"): errors.append("DNS alias must map domain subject to domain object")
    elif feature=="xq.net:tls_session":
        if action!="xq:observed": errors.append("TLS session observation must use Core xq:observed")
        if not _prefix(obj,"endpoint:"): errors.append("TLS session object must be endpoint-scoped")
    elif feature=="xq.net:service":
        if action!="xq:observed": errors.append("service observation must use Core xq:observed")
        if not _prefix(subject,"endpoint:") or not _prefix(obj,"service:"): errors.append("service observation must relate endpoint subject to service object")
        if ctx.get("connection_state") in {"rejected","failed","unanswered"}: errors.append("service must not be materialized solely from a failed/rejected/unanswered connection attempt")
        if "application_stack" in ctx and not ctx.get("application_stack"): errors.append("service observation requires application-level evidence when application_stack is supplied")
    elif feature=="xq.net:software":
        if action!="xq:observed": errors.append("software observation must use Core xq:observed")
        if not _prefix(obj,"software:"): errors.append("software observation object must be software-scoped")
    elif feature=="xq:presence":
        if action!="xq.net:first_observed":
            errors.append("Network Profile 0.1 scoped presence supports xq.net:first_observed, not enter/leave or other transition labels")
        else:
            if event.get("state")!="xq:present" or event.get("polarity")!=1: errors.append("network first-observed presence requires state xq:present and polarity +1")
            if not _prefix(obj,"network:"): errors.append("network presence object must be network-scoped")
            if not any(_prefix(subject,p) for p in ("address:","interface:","device:")): errors.append("network presence subject must be address/interface/device scoped")
            if ctx.get("network_context") != obj or ctx.get("scope") not in (None,obj): errors.append("network presence context must explicitly identify the same network scope as object")

    stack=ctx.get("application_stack")
    if stack is not None:
        if not isinstance(stack,list) or not all(isinstance(x,str) and x for x in stack):
            errors.append("context.application_stack must be an array of non-empty strings")
        else:
            normalized=[x.lower() for x in stack]
            if normalized!=stack: errors.append("context.application_stack tokens must be lowercase")
            if len(stack)!=len(set(stack)): errors.append("context.application_stack must not contain duplicates")
            if "tls" in stack and stack[-1]!="tls" and len(stack)>1: errors.append("context.application_stack must place tls after non-TLS application components")
    return errors
