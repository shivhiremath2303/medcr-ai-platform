import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    scenarios: {
        // High-throughput document ingestion simulation
        ingestion_stress: {
            executor: 'constant-arrival-rate',
            rate: 5, // 5 documents per second
            timeUnit: '1s',
            duration: '5m',
            preAllocatedVUs: 10,
            maxVUs: 50,
        },
    },
    thresholds: {
        'http_req_failed': ['rate<0.01'], // Fail if more than 1% of uploads fail
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_TOKEN = __ENV.API_TOKEN || '';

// Base64 of a dummy PDF content
const dummyPdf = 'JVBERi0xLjQKJ...'; // Truncated for example

export default function () {
    // Note: k6 handles multipart/form-data via the multipart request type
    const data = {
        file: http.file(dummyPdf, 'legal_contract_test.pdf', 'application/pdf'),
    };

    const params = {
        headers: {
            'Authorization': `Bearer ${API_TOKEN}`,
        },
    };

    const res = http.post(`${BASE_URL}/documents/upload`, data, params);

    check(res, {
        'upload accepted (200)': (r) => r.status === 200,
        'has task_id': (r) => r.json().task_id !== undefined,
    });

    // We don't wait for the task to finish here (that's worker load)
    // but we sleep to simulate client behavior
    sleep(1);
}
