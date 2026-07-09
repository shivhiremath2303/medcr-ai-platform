from app.services.document.document_service import DocumentService

document_service = DocumentService()

result = document_service.ingest_document("tests/sample.docx")

print(f"Chunks created: {result['chunk_count']}")

results = document_service.search(
    "What is this agreement about?"
)

print("\nSearch Results:\n")

for i, doc in enumerate(results, start=1):
    print(f"Result {i}")
    print(doc.page_content)
    print("-" * 40)