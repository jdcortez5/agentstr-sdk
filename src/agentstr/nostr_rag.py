import json
from typing import List, Dict, Any
from nostr_client import NostrClient
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

class NostrRAG:
    def __init__(self, api_url: str = "wss://nostr-relay.wellorder.net"):
        self.nostr_client = NostrClient(api_url)
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.chat = ChatOpenAI(temperature=0.7)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.qa_chain = None

    def _process_event(self, event: Dict[str, Any]) -> str:
        """Process a Nostr event into text format"""
        content = event.get('content', '')
        tags = event.get('tags', [])
        metadata = {tag[0]: tag[1] for tag in tags if len(tag) >= 2}
        return f"Content: {content}\nMetadata: {json.dumps(metadata)}"

    def build_knowledge_base(self, query: str, limit: int = 10) -> None:
        """Build a knowledge base from Nostr events matching the query"""
        events = self.nostr_client.query_events(query, limit=limit)
        
        # Process events into text documents
        documents = [self._process_event(event) for event in events]
        
        # Create vector store
        self.vector_store = FAISS.from_texts(
            documents,
            self.embeddings
        )
        
        # Initialize QA chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            self.chat,
            self.vector_store.as_retriever(),
            memory=self.memory
        )

    def ask_question(self, question: str) -> str:
        """Ask a question using the knowledge base"""
        if not self.qa_chain:
            raise ValueError("Knowledge base not built. Call build_knowledge_base() first.")
            
        result = self.qa_chain.invoke({"question": question})
        return result['answer']

    def add_to_knowledge_base(self, event: Dict[str, Any]) -> None:
        """Add a new event to the existing knowledge base"""
        if not self.vector_store:
            raise ValueError("Knowledge base not initialized. Call build_knowledge_base() first.")
            
        document = self._process_event(event)
        self.vector_store.add_texts([document])

    def clear_knowledge_base(self) -> None:
        """Clear the current knowledge base"""
        self.vector_store = None
        self.qa_chain = None
        self.memory.clear()

# Example usage:
if __name__ == "__main__":
    # Initialize RAG system
    rag = NostrRAG()
    
    # Build knowledge base from Nostr events
    rag.build_knowledge_base("#bitcoin", limit=50)
    
    # Ask questions
    while True:
        question = input("\nAsk a question (or type 'exit' to quit): ")
        if question.lower() == 'exit':
            break
            
        try:
            answer = rag.ask_question(question)
            print(f"\nAnswer: {answer}")
        except Exception as e:
            print(f"Error: {str(e)}")
