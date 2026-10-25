"""Small standard-library Connector client. Never starts Hype or edits .hype files."""
import json
import subprocess


class ConnectorError(RuntimeError):
    def __init__(self, error):
        self.error = error
        super().__init__(json.dumps(error, ensure_ascii=False))


class Connector:
    def __init__(self, executable, pid, session=None, timeout=150):
        self.executable, self.pid, self.session = str(executable), int(pid), session
        self.timeout, self.failure = timeout, None
        if self.pid <= 0:
            raise ValueError('Select a positive PID from host discovery.')

    def _stop(self, code, message):
        self.failure = ConnectorError({'code': code, 'message': message})
        raise self.failure

    def command(self, command, value=None):
        if self.failure:
            raise self.failure
        argv = [self.executable, '--pid', str(self.pid)]
        if self.session:
            argv += ['--session', self.session]
        argv += [command]
        if value is not None:
            argv.append(json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else str(value))
        try:
            p = subprocess.run(argv, capture_output=True, text=True, timeout=self.timeout,
                               stdin=subprocess.DEVNULL)
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._stop('outcome_unknown', 'No complete Connector result. Inspect before another action: ' + str(exc))
        try:
            result = json.loads(p.stdout if p.returncode == 0 else p.stderr)
        except ValueError:
            self._stop('outcome_unknown', 'Malformed Connector response. No automatic retry.')
        if not isinstance(result, dict) or type(result.get('ok')) is not bool:
            self._stop('outcome_unknown', 'Invalid Connector response envelope.')
        if p.returncode == 0 and result['ok'] is True and 'result' in result and not p.stderr.strip():
            return result['result']
        if p.returncode == 1 and result['ok'] is False and isinstance(result.get('error'), dict) and not p.stdout.strip():
            self.failure = ConnectorError(result['error'])
            raise self.failure
        self._stop('outcome_unknown', 'Inconsistent process status and Connector envelope.')

    def discover(self):
        if self.session:
            raise ValueError('Already pinned. Do not silently switch sessions.')
        rows = self.command('run', {'op': 'host.list'}).get('sessions', [])
        if len(rows) != 1 or rows[0].get('pid') != self.pid or not rows[0].get('session'):
            self._stop('host_selection', 'Selected PID must identify exactly one session.')
        self.session = rows[0]['session']
        return rows[0]

    def run(self, op, **fields):
        if not self.session:
            raise ValueError('Call discover() or supply a discovered session before any operation.')
        return self.command('run', {'op': op, **fields})

    def native(self, op, **fields):
        if not self.session:
            raise ValueError('Pin a session before native calls.')
        return self.command('native', {'op': op, **fields})

    def invoke(self, target, selector, *args, retain=False):
        result = self.native('call', target=target, selector=selector, args=list(args), retain=retain)
        for error in result.get('out', {}).values():
            if error is not None:
                self._stop('native_error', 'Native out-parameter reported: ' + json.dumps(error))
        return result['value']

    def page(self, op, key, **fields):
        rows, offset = [], 0
        for _ in range(1000):
            result = self.run(op, **fields, offset=offset, limit=1000)
            if not isinstance(result.get(key), list) or type(result.get('hasMore')) is not bool:
                self._stop('invalid_result', 'Malformed collection page.')
            rows.extend(result[key])
            if not result['hasMore']:
                return rows
            next_offset = result.get('nextOffset')
            if type(next_offset) is not int or next_offset <= offset:
                self._stop('invalid_result', 'Collection did not advance.')
            offset = next_offset
        self._stop('collection_limit', 'Collection exceeded the client page budget.')
