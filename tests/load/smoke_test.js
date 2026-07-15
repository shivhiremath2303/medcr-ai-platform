import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 1,
    duration: '10s',
    thresholds: {
        'http_req_failed': ['rate<0.01'],
        'http_req_duration': ['p(99)<500'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
    const res = http.get(`${BASE_URL}/health/live`);
    check(res, {
        'liveness is up': (r) => r.status === 200 && r.json().status === 'up',
    });

    const readyRes = http.get(`${BASE_URL}/health/ready`);
    check(readyRes, {
        'readiness is successful': (r) => [200, 503].includes(r.status),
    });

    sleep(1);
}
