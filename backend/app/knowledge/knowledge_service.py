from pathlib import Path


class KnowledgeService:
    """
    Simple service for accessing D.AI.S.Y knowledge documents.
    """

    def __init__(self):
        self.base_path = Path(__file__).parent / "documents"

    def list_documents(self):
        """
        Return all knowledge documents.
        """

        if not self.base_path.exists():
            return []

        return sorted(
            file.name
            for file in self.base_path.iterdir()
            if file.is_file()
        )

    def read_document(self, filename: str):
        """
        Read a knowledge document.
        """

        path = self.base_path / filename

        if not path.exists():
            return None

        return path.read_text(encoding="utf-8")


# Singleton
knowledge_service = KnowledgeService()


if __name__ == "__main__":
    print(knowledge_service.list_documents())
    print()
    print(knowledge_service.read_document("welcome.txt"))