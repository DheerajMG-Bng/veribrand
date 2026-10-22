import re
from .rules import run_rules

SEVERITY = {'low': 0, 'medium': 1, 'high': 2}

def find_quote(text, quote):
    # Flexible whitespace/case for grounding, but persist the exact original slice.
    words = re.split(r'\s+', quote.strip())
    if not words or not words[0]:
        return []
    return list(re.finditer(r'\s+'.join(re.escape(w) for w in words), text, re.I))

def validate(text, channel, knowledge, rule_findings, ai_result=None):
    codes = {k.code: k for k in knowledge}
    findings = [dict(f) for f in rule_findings]
    ai_result = ai_result if isinstance(ai_result, dict) else {}
    for proposed in ai_result.get('replacements', []):
        if not isinstance(proposed, dict):
            continue
        for finding in findings:
            if str(finding.get('id')) == str(proposed.get('rule_finding_id')) and finding['replacement'] is None:
                if isinstance(proposed.get('replacement'), str):
                    finding['replacement'] = proposed['replacement']
    occupied = set()
    raw = ai_result.get('findings', [])
    for finding in raw if isinstance(raw, list) else []:
        if not isinstance(finding, dict) or not isinstance(finding.get('quote'), str):
            continue
        matches = find_quote(text, finding['quote'])
        match = next((m for m in matches if (m.start(), m.end()) not in occupied), None)
        if match is None:
            continue
        occupied.add((match.start(), match.end()))
        source = finding.get('source_code')
        source = source if isinstance(source, str) and source in codes else None
        # Terminology pattern policies are exhaustive data-driven checks. AI may
        # not invent additional banned spellings or remove approved variants.
        referenced = [k for k in knowledge if k.kind == 'term' and k.meta.get('check') == 'patterns'
                      and (k.code == source or k.code in str(finding.get('reason', '')))]
        if referenced and not any(f['source_code'] in {k.code for k in referenced}
                                  and f['start'] < match.end() and match.start() < f['end'] for f in rule_findings):
            continue
        severity = finding.get('severity', 'low')
        severity = severity if severity in SEVERITY else 'low'
        issue = str(finding.get('issue_type', 'unsupported_claim'))[:80]
        if source is None:
            severity = 'medium' if ('fact' in issue or 'claim' in issue) and severity != 'low' else 'low'
        meta = codes[source].meta if source else {}
        try:
            confidence = max(0, min(1, float(finding.get('confidence', 0.5))))
        except (TypeError, ValueError):
            confidence = 0.5
        findings.append(dict(issue_type=issue, severity=severity, quote=text[match.start():match.end()], start=match.start(), end=match.end(),
                             source_code=source, also_cites=meta.get('also_cites', []), reason=str(finding.get('reason', 'Needs a human review.')),
                             replacement=finding.get('replacement') if source and isinstance(finding.get('replacement'), str) else None,
                             replacement_hint=None if source else 'Unverified, needs a human. Add evidence or remove the claim.',
                             requires_reviewer=bool(meta.get('requires_reviewer')), origin='ai', confidence=confidence,
                             verification='verified' if source else 'unverified'))
    # Phrase replacements are checked for content violations. Channel-wide disclosure
    # remains a whole-draft check on mandatory re-review after applying changes.
    for finding in findings:
        replacement = finding.get('replacement')
        if replacement is not None and run_rules(replacement, 'social', knowledge):
            finding['replacement'] = None
            finding['replacement_hint'] = 'Suggested wording failed the rule check. Please edit this phrase.'
    # Sort by priority, then merge transitively. Widening an overlap invalidates a
    # phrase replacement so that no unrelated text is accidentally deleted.
    merged = []
    for finding in sorted(findings, key=lambda f: (SEVERITY[f['severity']], f['origin'] == 'rule'), reverse=True):
        overlapping = [f for f in merged if finding['start'] < f['end'] and f['start'] < finding['end']]
        if not overlapping:
            merged.append(finding)
            continue
        winner = overlapping[0]
        group = [winner, finding] + overlapping[1:]
        start, end = min(f['start'] for f in group), max(f['end'] for f in group)
        cites = set()
        for member in group:
            cites.update(member.get('also_cites', []))
            if member.get('source_code'):
                cites.add(member['source_code'])
        cites.discard(winner.get('source_code'))
        winner['also_cites'] = sorted(c for c in cites if c in codes)
        winner['requires_reviewer'] = any(f.get('requires_reviewer') for f in group)
        if (start, end) != (winner['start'], winner['end']):
            winner.update(start=start, end=end, quote=text[start:end], replacement=None,
                          replacement_hint='Overlapping findings: edit the complete highlighted phrase.')
        # A grounded finding can absorb an unverified span, but must never inherit
        # an automatic replacement for that unsupported claim.
        if any(f.get('verification') == 'unverified' for f in group):
            winner['replacement'] = None
        for other in overlapping[1:]:
            merged.remove(other)
    return sorted(merged, key=lambda f: f['start'])
