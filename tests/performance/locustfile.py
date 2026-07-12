import random
from locust import HttpUser, task, between


class LegalAIUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """
        Login and get token if authentication is enabled.
        Currently using a dummy token or assuming public access for load testing
        in a controlled environment.
        """
        self.token = "dummy-token"  # In production, this would be a real JWT

    @task(3)
    def query_rag(self):
        """
        Simulate a RAG query.
        """
        payload = {
            "question": "What are the conflict resolution rules in the provided evidence?",
            "k": 3,
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        with self.client.post(
            "/api/v1/rag/query", json=payload, headers=headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def get_health(self):
        """
        Simulate health check probes.
        """
        self.client.get("/health/ready")

    @task(2)
    def list_documents(self):
        """
        Simulate listing documents.
        """
        self.client.get("/api/v1/documents")

    @task(1)
    def get_metrics(self):
        """
        Simulate Prometheus scraping.
        """
        self.client.get("/metrics")
