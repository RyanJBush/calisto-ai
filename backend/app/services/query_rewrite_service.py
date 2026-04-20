from app.services.text_utils import tokenize


class QueryRewriteService:
    AMBIGUOUS_TERMS = {"it", "that", "this", "they", "them", "those", "these", "he", "she"}

    def rewrite(self, query: str) -> str:
        compact = " ".join(query.split())
        if not compact:
            return query

        query_terms = tokenize(compact)
        has_ambiguous_term = any(term in self.AMBIGUOUS_TERMS for term in query_terms)
        if has_ambiguous_term and "knowledge base context" not in compact.lower():
            return f"{compact} (using available knowledge base context)"
        return compact
