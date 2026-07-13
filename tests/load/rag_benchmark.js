import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Counter } from 'k6/metrics';

// Custom metrics for AI Benchmarking
const ragLatency = new Trend('rag_total_latency');
const ragSuccess = new Counter('rag_success_total');
const ragError = new Counter('rag_error_total');

export const options = {
    scenarios: {
        // AI Workload Simulation: Gradual ramp up to 50 concurrent users
        rag_load: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '2m', target: 20 }, // Warm up
                { duration: '5m', target: 50 }, // Main load
                { duration: '2m', target: 0 },  // Cool down
            ],
            gracefulStop: '30s',
        },
    },
    thresholds: {
        'http_req_duration': ['p(95)<5000'], // 95% of RAG requests should be < 5s
        'rag_success_total': ['count>0'],
        'rag_error_total': ['count<50'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_TOKEN = __ENV.API_TOKEN || '';

export default function () {
    const params = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_TOKEN}`,
            'X-Enable-Profiler': 'false',
        },
    };

    const payload = JSON.stringify({
        question: 'What are the termination conditions for liability breach?',
        k: 3,
    });

    const startTime = Date.now();
    const res = http.post(`${BASE_URL}/rag/ask`, payload, params);
    const duration = Date.now() - startTime;

    const success = check(res, {
        'status is 200': (r) => r.status === 200,
        'has answer': (r) => r.json().answer !== undefined,
        'grounding score present': (r) => r.json().grounding_score !== undefined,
    });

    if (success) {
        ragSuccess.add(1);
        ragLatency.add(duration);
    } else {
        ragError.add(1);
        console.error(`RAG Request failed: ${res.status} - ${res.body}`);
    }

    sleep(Math.random() * 3 + 2); // Think time between questions
}
