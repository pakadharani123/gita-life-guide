from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from google import genai
from google.genai.errors import ClientError, ServerError

# ---------------- API KEY ----------------
# ⚠️ Replace with your key (for demo only)
api_key = "AIzaSyBY3KGvoGaWkbVZiJClvNdKwBDwqEYw8sA"
client = genai.Client(api_key=api_key)

# ---------------- LOAD GITA ----------------
reader = PdfReader("Bhagavad-gita-As-it-is.pdf")
gita_text = ""

for page in reader.pages:
    text = page.extract_text()
    if text:
        gita_text += text + "\n"

# ---------------- CHUNKING ----------------
def chunk_text(text, size=250, overlap=50):
    words = text.split()
    return [
        " ".join(words[i:i + size])
        for i in range(0, len(words), size - overlap)
    ]

chunks = chunk_text(gita_text)

# ---------------- EMBEDDINGS ----------------
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embed_model.encode(chunks)
embeddings = np.array(embeddings).astype("float32")

# ---------------- FAISS INDEX ----------------
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# ---------------- RETRIEVE CONTEXT ----------------
def retrieve_gita_context(question, k=5):
    q_vec = embed_model.encode([question]).astype("float32")
    _, ids = index.search(q_vec, k)
    return "\n\n".join([chunks[i] for i in ids[0]])

# ---------------- MAIN FUNCTION ----------------
def gita_life_answer(question: str, history) -> str:

    # format full conversation
    formatted_history = "\n".join(
        [f"{role.upper()}: {msg}" for role, msg in history]
    )

    # get relevant gita context
    context = retrieve_gita_context(question)

    # FINAL PROMPT (NO STATIC OUTPUT, BUT COMPLETE THINKING)
    prompt = f"""
You are a deeply insightful life guide inspired by Bhagavad-Gītā.

Internally think (DO NOT SHOW):
- What is the user feeling?
- What is their real problem?
- What principle from the Gita applies?
- What should they do NOW (clear dharma)?
- What actions can help immediately?

Then respond naturally like a human mentor.

Conversation:
{formatted_history}

User:
{question}

Gita Knowledge:
{context}

Response rules:

- Start by clearly understanding their situation
- Use Bhagavad-Gītā wisdom naturally (no lecture)
- Give a CLEAR direction (no neutrality if decision asked)
- Give 2–3 specific practical steps
- End with a strong, confident takeaway

Strict:
- No fixed template or headings
- No repeated phrases
- No vague advice
- Keep it 5–7 lines
- Make it feel complete and satisfying
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"temperature": 0.75}
        )
        return response.text.strip()

    except (ClientError, ServerError) as e:
        return f"⚠️ Model Error: {str(e)}"