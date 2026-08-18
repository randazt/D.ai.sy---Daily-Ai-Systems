from pathlib import Path


class KnowledgeRetriever:
    """
    Simple keyword-based retriever for D.A.I.S.Y. knowledge documents.
    """

    def __init__(self):
        self.documents_path = Path(__file__).parent / "documents"

    def search(self, query: str):

        query = query.lower()

        results = []

        if not self.documents_path.exists():
            return results

        for file in self.documents_path.rglob("*"):

            if not file.is_file():
                continue

            try:

                text = file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                ).lower()

            except Exception:
                continue

            score = 0

            filename = file.name.lower()

            for word in query.split():

                if word in filename:
                    score += 3

                if word in text:
                    score += 1

            if score > 0:

                results.append(
                    {
                        "file": file.name,
                        "path": str(file),
                        "score": score,
                    }
                )

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results

knowledge_retriever = KnowledgeRetriever()