"""Single-user loopback review, serving the existing Emergency frontend build.

CSP limits this application's requests. It is NOT browser/OS network isolation.
"""
import argparse
import html
import json
import math
import mimetypes
import os
import secrets
from decimal import Decimal
from http import HTTPStatus
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit
from blood_gas_geometry import overlaps
from blood_gas_review import LIMIT, interpret, sample_type
from blood_gas_worker import safe_extract
from http_transport import (BoundedHTTPServer as HTTPServer, DeadlineRequestHandler,
                            RequestRejection, json_request_size)

DIST = Path(__file__).resolve().parents[2] / 'app' / 'dist'


def strict_json_object(body):
    """Preserve JSON meaning before clinical review, without changing its values."""
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result

    def finite_float(literal):
        exact = Decimal(literal)
        value = float(exact)
        if not math.isfinite(value) or (exact != 0 and value == 0):
            raise ValueError('JSON number is not representable')
        return value

    def reject_constant(_):
        raise ValueError('Non-finite JSON constant')

    result = json.loads(body.decode('utf-8'), object_pairs_hook=unique_object,
                        parse_float=finite_float, parse_constant=reject_constant)
    if not isinstance(result, dict):
        raise ValueError('JSON object required')
    return result


def binary_request_size(headers):
    """Framing checks for document bytes; /extract is not a JSON endpoint."""
    if headers.get_all('Transfer-Encoding'):
        raise RequestRejection(HTTPStatus.BAD_REQUEST, 'Unsupported transfer encoding')
    lengths = headers.get_all('Content-Length', [])
    if not lengths:
        raise RequestRejection(HTTPStatus.LENGTH_REQUIRED, 'Content length required')
    if len(lengths) != 1:
        raise RequestRejection(HTTPStatus.BAD_REQUEST, 'Ambiguous content length')
    literal = lengths[0].strip(' \t')
    if not literal.isascii() or not literal.isdecimal() or len(literal) > 10:
        raise RequestRejection(HTTPStatus.BAD_REQUEST, 'Invalid content length')
    size = int(literal)
    if size == 0:
        raise RequestRejection(HTTPStatus.BAD_REQUEST, 'Empty request body')
    if size > LIMIT:
        raise RequestRejection(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, 'Document too large')
    encodings = headers.get_all('Content-Encoding', [])
    if len(encodings) > 1 or (encodings and encodings[0].strip().lower() != 'identity'):
        raise RequestRejection(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, 'Unsupported content encoding')
    return size


def specimen_sources(pages):
    # Keep the first extraction's positions across successive crops.
    return [dict(page=p['source_page'], anchors=[f.get('bbox') for f in p['fields']],
                 types=[dict(m) for m in p['metadata'] if m.get('kind') == 'sample_type'])
            for p in pages]


def preserve_specimen_types(page, sources):
    candidates = [s for s in sources if s['page'] == page['source_page']]
    if not any(s['types'] for s in candidates):
        return
    owners = [s for s in candidates if any(overlaps(f.get('bbox'), box)
              for f in page['fields'] for box in s['anchors'])]
    if len(owners) > 1:
        page.update(blocked=True, warning='El recorte contiene campos de distintas muestras. Separe las áreas.')
    for source in candidates:
        for original in source['types']:
            unassigned = original.get('scope') == 'unassigned'
            if owners and not unassigned and source not in owners:
                continue
            saved = dict(original)
            if not owners or unassigned:
                saved['scope'] = 'unassigned'
            matches = [m for m in page['metadata'] if m.get('kind') == 'sample_type'
                       and (m['raw'], m['page'], m.get('source_layer')) ==
                           (saved['raw'], saved['page'], saved.get('source_layer'))
                       and (overlaps(m.get('bbox'), saved.get('bbox')) or
                            (m.get('bbox') == saved.get('bbox') and m['line'] == saved['line']))]
            if matches:
                for item in matches:
                    item.update(saved)
            else:
                page['metadata'].append(saved)


class Handler(DeadlineRequestHandler):
    operation_lock = Lock()

    def log_message(self, *args):
        pass

    def reply_headers(self, status, length, mime):
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(length))
        self.send_header('Connection', 'close')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; manifest-src 'self'; worker-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()

    def reply_json(self, status, body):
        # Use the clinical API's reversible JSON markup boundary. Keep the
        # existing ASCII encoding so every accepted JSON string stays lossless.
        escaped = html.escape(json.dumps(body, allow_nan=False), quote=False)
        data = (escaped.replace('&lt;', '\\u003c').replace('&gt;', '\\u003e')
                .replace('&amp;', '\\u0026').encode('utf-8'))
        self.reply_headers(status, len(data), 'application/json')
        if self.command != 'HEAD':
            self.wfile.write(data)

    def reply_asset(self, status, data, mime):
        self.reply_headers(status, len(data), mime)
        if self.command != 'HEAD':
            self.wfile.write(data)

    def send_error(self, code, message=None, explain=None):
        # The stdlib parser can include an input request-line in HTML errors.
        # Return one static JSON message with the same privacy headers instead.
        self.close_connection = True
        if self.request_version == 'HTTP/0.9':
            self.request_version = 'HTTP/1.0'
        self.reply_json(code, {'error': 'Solicitud HTTP no admisible'})

    def trusted_browser_request(self, require_origin=False):
        origins = self.headers.get_all('Origin', [])
        allowed = getattr(self.server, 'allowed_origins', None)
        sites = self.headers.get_all('Sec-Fetch-Site', [])
        return (bool(allowed) and self.headers.get_all('Host', []) == [self.server.address]
                and (origins == [] and not require_origin or
                     len(origins) == 1 and origins[0] in allowed)
                and len(sites) <= 1
                and (not sites or sites[0].strip().lower() != 'cross-site'))

    def do_GET(self):
        if not self.trusted_browser_request():
            return self.send_error(403)
        route = urlsplit(self.path).path
        if route == '/api/blood-gas/session':
            return self.reply_json(200, dict(token=self.server.token, synthetic_only=True,
                                             extraction_available=os.name == 'nt', required_platform='win32'))
        if route.startswith('/assets/') or route in ('/favicon.svg', '/manifest.webmanifest'):
            target = (DIST / route.lstrip('/')).resolve()
            if not target.is_relative_to(DIST.resolve()) or not target.is_file():
                return self.send_error(404)
            return self.reply_asset(200, target.read_bytes(), mimetypes.guess_type(target.name)[0] or 'application/octet-stream')
        if route not in ('/', '/blood-gas', '/clinical-note'):
            return self.send_error(404)
        index = DIST / 'index.html'
        if not index.is_file():
            return self.reply_asset(503, b'Build Emergency app/ before starting the local review.', 'text/plain')
        # Tell the existing entry point not to register a service worker for this ephemeral session.
        page = index.read_text(encoding='utf8').replace('<head>', '<head><meta name="blood-gas-local" content="synthetic-only">')
        self.reply_asset(200, page.encode(), 'text/html; charset=utf-8')

    def do_POST(self):
        # Browsers open speculative connections. Serve them independently but
        # serialize all changes to the single-user extraction and review state.
        with self.operation_lock:
            self.handle_post()

    def handle_post(self):
        if (not self.trusted_browser_request(require_origin=True) or
            self.headers.get_all('X-Session', []) != [self.server.token]):
            return self.send_error(403)
        route = self.path.removeprefix('/api/blood-gas')
        if route not in ('/extract', '/regions', '/review', '/reject'):
            return self.send_error(404)
        previous_ticket, previous_source = None, None
        previous_context = []
        sources = []
        if route in ('/extract', '/regions'):
            if route == '/regions':
                previous_ticket, previous_source = self.server.ticket, self.server.source
                sources = getattr(self.server, 'sample_sources', None) or specimen_sources(self.server.pages)
                previous_context = [dict(m) for m in (getattr(self.server, 'document_context', None) or
                                    [m for page in self.server.pages for m in page['metadata']
                                     if m.get('scope') == 'unassigned'])]
            # Revoke even when the replacement body is malformed or oversized.
            # Authentication was checked first; untrusted requests cannot revoke.
            self.server.ticket = None
            self.server.pages = []
            self.server.source = None
            self.server.document_context = []
            self.server.sample_sources = []
        try:
            length = (binary_request_size(self.headers) if route == '/extract' else
                      json_request_size(self.headers, LIMIT))
            body = self.rfile.read(length)
            if len(body) != length:
                raise ValueError('Incomplete request')
            if route in ('/extract', '/regions'):
                regions = None
                if route == '/regions':
                    req = strict_json_object(body)
                    if not previous_ticket or req['ticket'] != previous_ticket:
                        raise ValueError('Stale extraction')
                    source = previous_source
                    regions = req['regions']
                    if not isinstance(regions, list):
                        raise ValueError('Explicit sample regions required')
                else:
                    source = body
                pages = safe_extract(source, regions)
                if regions is None:
                    sources = specimen_sources(pages)
                for page in pages:
                    if regions is not None:
                        preserve_specimen_types(page, sources)
                    for item in page['metadata']:
                        if item.get('kind') != 'sample_type' and item.get('scope') == 'unassigned' and item not in previous_context:
                            previous_context.append(dict(item))
                # A crop must not silently discard unassigned document headers.
                for page in pages:
                    for context in previous_context:
                        if context.get('kind') == 'sample_type' or context['page'] != page['source_page']:
                            continue
                        matches = [m for m in page['metadata'] if
                                   (m['label'], m['value']) == (context['label'], context['value'])]
                        if matches:
                            for item in matches:
                                item.update(context)
                        else:
                            page['metadata'].append(dict(context))
                self.server.source = source
                self.server.sample_sources = sources
                self.server.pages = pages
                self.server.document_context = previous_context
                self.server.ticket = secrets.token_hex(16)
                output = dict(ticket=self.server.ticket, pages=pages)
            elif route == '/reject':
                if strict_json_object(body).get('ticket') == self.server.ticket:
                    self.server.ticket = None
                    self.server.pages = []
                    self.server.source = None
                    self.server.document_context = []
                    self.server.sample_sources = []
                output = {'rejected': True}
            elif route == '/review':
                req = strict_json_object(body)
                if (not self.server.ticket or req['ticket'] != self.server.ticket or
                    req['oneSample'] is not True or req.get('medicalConfirmed') is not True or
                    req.get('areaConfirmed') is not True):
                    raise ValueError('Medical and sample confirmation required')
                idx = req['page']
                if type(idx) != int or not 0 <= idx < len(self.server.pages):
                    raise ValueError('Invalid sample')
                page = self.server.pages[idx]
                rows = req['rows']
                if page['blocked'] or [r['name'] for r in rows] != [f['name'] for f in page['fields']]:
                    raise ValueError('Ambiguous sample')
                metadata = req.get('metadata', [])
                if (not isinstance(metadata, list) or
                    [m['label'] for m in metadata] != [m['label'] for m in page['metadata']]):
                    raise ValueError('Review all extracted metadata')
                reviewed_metadata = []
                for item, original in zip(metadata, page['metadata']):
                    state, value = item.get('review'), item.get('value')
                    if (state not in ('confirmed', 'rejected') or not isinstance(value, str) or len(value) > 512
                            or (state == 'confirmed' and not value.strip() and original.get('kind') != 'sample_type')):
                        raise ValueError('Metadata confirmation required')
                    reason = item.get('reason', '')
                    if not isinstance(reason, str) or len(reason) > 512 or (state == 'rejected' and not reason.strip()):
                        raise ValueError('Explain rejected metadata')
                    scope = original.get('scope', 'sample')
                    applies = item.get('applies_to_sample') if scope == 'unassigned' else True
                    if type(applies) is not bool or (not applies and not reason.strip()):
                        raise ValueError('Resolve unassigned metadata scope')
                    decision = dict(label=original['label'], original_value=original['value'],
                                    raw=original['raw'], page=original['page'], line=original['line'],
                                    bbox=original.get('bbox'), source_sample_label=original.get('source_sample_label'),
                                    source_layer=original.get('source_layer'), visual_raw=original.get('visual_raw'),
                                    type_discrepancy=bool(original.get('type_discrepancy')),
                                    reviewed_sample_index=idx, reviewed_sample_label=page['sample_label'],
                                    value=value, review=state, reason=reason, scope=scope,
                                    applies_to_sample=applies, corrected=value != original['value'])
                    if original.get('kind') == 'sample_type':
                        declared = sample_type(original['value'])
                        required = applies and state == 'confirmed' and (
                            declared != req['sample'] or value != original['value'] or original.get('type_discrepancy'))
                        if required and (item.get('resolved_sample_type') != req['sample'] or not reason.strip()):
                            raise ValueError('Resolve the specimen type and record the reason')
                        decision.update(kind='sample_type', original_type=declared, reviewed_type=sample_type(value),
                                        resolved_sample_type=req['sample'] if required else None)
                    reviewed_metadata.append(decision)
                fio2_source = None
                for row, original in zip(rows, page['fields']):
                    if row.get('review') == 'confirmed':
                        if original['name'] == 'FiO2':
                            changed = (row['number'], row['unit']) != (original['number'], original['unit'])
                            reason = row.get('correction_reason', '')
                            if not isinstance(reason, str) or len(reason) > 512 or (changed and not reason.strip()):
                                raise ValueError('Explain the FiO2 value or unit correction')
                            attested = row.get('fio2_attestation')
                            if (changed or attested is not None) and attested != [row['number'], row['unit']]:
                                raise ValueError('Repeat visual confirmation of the corrected FiO2 pair')
                            fio2_source = dict(raw=original['raw'], original_number=original['number'],
                                               original_unit=original['unit'], corrected=changed,
                                               correction_reason=reason, transcribed=row.get('transcribed') is True,
                                               source_page=page['source_page'], sample_index=idx,
                                               sample_label=page['sample_label'], line=original['line'],
                                               bbox=original.get('bbox'))
                        if row.get('visualReviewed') is not True:
                            raise ValueError('Original crop must be reviewed')
                        uncertain = (original['legibility'] in ('low_confidence', 'location_unverified', 'unit_unreadable') or
                                     original.get('visual_check') in ('discrepancy', 'visual_only'))
                        if uncertain and row.get('transcribed') is not True:
                            raise ValueError('Manual transcription required')
                output = interpret(rows, req['sample'])
                if fio2_source is not None:
                    output['fio2_trace'].update(fio2_source)
                output['clinical_status'] = 'CLINICALLY_PENDING'
                output['reviewed_metadata'] = reviewed_metadata
                output['review_provenance'] = dict(
                    source_page=page['source_page'], sample_label=page['sample_label'],
                    region=page['region'],
                    fields=[dict(name=original['name'], raw=original['raw'], origin=original['origin'],
                                 original_number=original['number'], original_unit=original['unit'],
                                 number=row['number'], unit=row['unit'], review=row['review'],
                                 bbox=original.get('bbox'),
                                 corrected=(row['number'], row['unit']) != (original['number'], original['unit']))
                            for row, original in zip(rows, page['fields'])])
            else:
                return self.send_error(404)
            self.reply_json(200, output)
        except Exception as error:
            if route in ('/extract', '/regions'):
                self.server.ticket = None
                self.server.pages = []
                self.server.source = None
                self.server.document_context = []
                self.server.sample_sources = []
            status = error.status if isinstance(error, RequestRejection) else 422
            self.reply_json(status, {'error': 'Documento o revision no admisible; revise muestra, campos, unidades y confirmaciones'})


def make_server(port=0, ui_port=None):
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError('Port must be an integer in [0, 65535]')
    if ui_port is not None and (type(ui_port) is not int or not 1 <= ui_port <= 65535):
        raise ValueError('UI port must be an integer in [1, 65535]')
    server = HTTPServer(('127.0.0.1', port), Handler, request_timeout=10.0)
    server.address = '127.0.0.1:' + str(server.server_port)
    server.allowed_origins = {'http://127.0.0.1:' + str(server.server_port)}
    if ui_port is not None:
        server.allowed_origins.add('http://127.0.0.1:' + str(ui_port))
    server.ticket = None
    server.pages = []
    server.source = None
    server.document_context = []
    server.sample_sources = []
    server.token = secrets.token_hex(32)
    return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--ui-port', type=int, help='Additional local frontend port on 127.0.0.1')
    args = parser.parse_args()
    server = make_server(args.port, args.ui_port)
    print('http://127.0.0.1:' + str(server.server_port) + '/blood-gas', flush=True)
    try:
        server.serve_forever()
    finally:
        server.source = None
        server.document_context = []
        server.server_close()
