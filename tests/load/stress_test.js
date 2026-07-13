import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '2m', target: 50 },  // Normal load
        { duration: '2m', target: 200 }, // Breakpoint load
        { duration: '2m', target: 500 }, // Overload: Testing ResourceGuard (10.3.9)
        { duration: '2m', target: 0 },   // Recovery
    ],
    thresholds: {
        'http_req_failed': ['rate<0.1'], // Rejection is expected during overload
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_TOKEN = __ENV.API_TOKEN || '';

export default function () {
    const params = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_TOKEN}`,
        },
    };

    // Low complexity endpoint to test connection limits
    const res = http.get(`${BASE_URL}/version`, params);

    check(res, {
        'status is 200 or 503': (r) => [200, 503].includes(r.status),
    });

    if (r.status === 503) {
        console.warn('System under pressure (503 Service Unavailable). Load shedding active.');
    }

    sleep(0.5);
}
