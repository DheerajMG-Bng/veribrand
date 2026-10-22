import re
from datetime import datetime, timezone, timedelta

def pattern_regex(pattern):
    return (r'(?<!\w)' if pattern[0].isalnum() else '') + re.escape(pattern) + (r'(?!\w)' if pattern[-1].isalnum() else '')

def run_rules(text, channel, knowledge):
    results = []
    today = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
    for item in knowledge:
        meta = item.meta or {}
        check = meta.get('check')
        flags = 0 if meta.get('case_sensitive') else re.IGNORECASE
        matches = []
        if check in {'patterns', 'regex', 'expired_offer'}:
            if check == 'expired_offer' and (not item.valid_until or item.valid_until >= today):
                continue
            for pattern in meta.get('patterns', []):
                try:
                    matches.extend(re.finditer(pattern if check == 'regex' else pattern_regex(pattern), text, flags))
                except re.error:
                    continue
        elif check == 'hype_punctuation':
            if text.count('!') > meta.get('max_exclamations', 1):
                matches.extend(re.finditer(r'!+', text))
            if meta.get('flag_all_caps_words'):
                matches.extend(re.finditer(r'\b[A-Z]{2,}\b', text))
        elif check == 'max_hashtags':
            hashtags = list(re.finditer(r'(?<!\w)#\w+', text))
            matches = hashtags[meta.get('max', 3):]
        elif check == 'disclosure':
            markers = '|'.join(re.escape(m) + r'(?!\w)' for m in meta.get('markers', []))
            if channel in meta.get('channels', []) and not re.match(r'\s*(?:' + markers + ')', text, re.I):
                match = re.search(r'\S+', text)
                if match:
                    matches = [match]
        elif check == 'year_conflict':
            triggers = '|'.join(re.escape(t) for t in meta.get('trigger', []))
            for match in re.finditer(r'\b(?:' + triggers + r')\s+(\d{4})\b', text, flags):
                if int(match.group(1)) != meta['approved_year']:
                    matches.append(match)
        elif check == 'price_mismatch':
            if any(re.search(pattern_regex(p), text, re.I) for p in meta.get('product_patterns', [])):
                symbols = '|'.join(re.escape(s) for s in meta.get('symbols', []))
                for match in re.finditer(r'(?:' + symbols + r')\s*\.?\s*(\d+(?:\.\d+)?)', text, re.I):
                    if float(match.group(1)) != meta['approved_price'] or (item.valid_until and item.valid_until < today):
                        matches.append(match)
        for match in matches:
            quote = match.group()
            replacement = meta.get('replacement')
            if check == 'disclosure':
                replacement = meta.get('replacement_prefix', '#ad ') + quote
            elif check == 'max_hashtags':
                replacement = ''
            elif check == 'year_conflict':
                replacement = re.sub(r'\d{4}', str(meta['approved_year']), quote)
            elif check == 'price_mismatch' and (not item.valid_until or item.valid_until >= today):
                replacement = re.sub(r'\d+(?:\.\d+)?', str(meta['approved_price']), quote)
            elif check == 'hype_punctuation':
                replacement = '.' if quote.startswith('!') else quote.capitalize()
            results.append(dict(id=f'r{len(results)}', issue_type=check, severity=meta.get('severity', 'medium'),
                                quote=quote, start=match.start(), end=match.end(), source_code=item.code,
                                also_cites=meta.get('also_cites', []), reason=f'{item.code} — {item.title}: {item.text}',
                                replacement=replacement, replacement_hint='Rewrite this phrase using only approved facts.' if replacement is None else None,
                                requires_reviewer=bool(meta.get('requires_reviewer')), origin='rule', confidence=1.0, verification='verified'))
    return results
