import os
import chromadb
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings

from .constants import RAG_PROMPT_CONSTANT

class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Embedding function to create embeddings for document retrieval using the Gemini API.

    This function configures and utilizes the Gemini API to generate embeddings for input text,
    which is then used for document retrieval in the Chroma database.
    """

    def __call__(self, input: Documents) -> Embeddings:
        gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not gemini_api_key:
            raise ValueError(
                "Gemini API Key not provided. Please provide GEMINI_API_KEY as an environment variable"
            )

        genai.configure(api_key=gemini_api_key)
        model = "models/embedding-001"
        title = "Custom query"

        return genai.embed_content(
            model=model, content=input, task_type="retrieval_document", title=title
        )["embedding"]


def generate_answer(db, query, current_location):
    """
    Generates an answer to a query by retrieving relevant text passages and using the Gemini model
    to generate a response.

    Parameters:
        db (chromadb.PersistentClient): Chroma database collection used for document retrieval.
        query (str): The question or query to be answered.

    Returns:
        str: Generated answer text based on the retrieved content and generative model.
    """

    def __generate_answer(prompt):
        """
        Private function to generate an answer using the Gemini API given a prompt.

        Parameters:
            prompt (str): The input prompt for generating content.

        Returns:
            str: Text response generated by the Gemini model.
        """
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError(
                "Gemini API Key not provided. Please provide GEMINI_API_KEY as an environment variable"
            )

        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        answer = model.generate_content(prompt)
        return answer.text

    relevant_text = get_relevant_passage(query, db, n_results=5)
    prompt = make_rag_prompt(query, relevant_passage="".join(relevant_text), current_location=current_location)

    answer = __generate_answer(prompt)

    return answer


def load_chroma_collection(path, name):
    """
    Loads a Chroma database collection with a specific name and embedding function.

    Parameters:
        path (str): Path to the directory where the Chroma database is stored.
        name (str): Name of the Chroma database collection to be loaded.

    Returns:
        chromadb.Collection: Loaded Chroma database collection with the specified name.
    """
    chroma_client = chromadb.PersistentClient(path=path)
    return chroma_client.get_collection(
        name=name, embedding_function=GeminiEmbeddingFunction()
    )


def get_relevant_passage(query, db, n_results):
    """
    Queries the Chroma database to retrieve relevant text passages for a given query.

    Parameters:
        query (str): The query or question to find relevant passages for.
        db (chromadb.Collection): The Chroma database collection to query from.
        n_results (int): Number of top relevant results to retrieve.

    Returns:
        list: A list of relevant text documents for the query.
    """
    return db.query(query_texts=[query], n_results=n_results)["documents"][0]


def make_rag_prompt(query, relevant_passage, current_location):
    """
    Creates a prompt for a retrieval-augmented generation (RAG) model by combining the query with
    relevant passages.

    Parameters:
        query (str): The question or query to be answered.
        relevant_passage (str): Text passages retrieved to support the query.

    Returns:
        str: Formatted RAG prompt combining the query with the relevant passages.
    """
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    return RAG_PROMPT_CONSTANT.format(query=query, relevant_passage=escaped, current_location=current_location)


def ask_question(query, current_location=None):
    """
    Main function to handle a user's question by loading the Chroma collection,
    retrieving relevant passages, and generating an answer.

    Parameters:
        query (str): The question or query from the user.

    Returns:
        str: Generated answer based on the query.
    """
    db = load_chroma_collection(
        path=r"./chroma", name="chatbot_rag_collection"
    )
    return generate_answer(db, query=query, current_location=current_location)


if __name__ == "__main__":
    print(ask_question("Tell me about the brts system"))