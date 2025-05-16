from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
import shutil

VECTORSTORE_DIR = "vectorstore"

# Inisialisasi global
llm = OllamaLLM(model="mistral")
embedding = OllamaEmbeddings(model="nomic-embed-text:latest")

# Prompt Bahasa Indonesia
prompt_template = """
Kamu adalah asisten virtual perusahaan MMT. Jawab pertanyaan karyawan secara ramah, jelas, dan profesional seperti ChatGPT.

Gaya bahasa:
- Gunakan bahasa Indonesia yang alami, sopan, dan profesional.
- Jangan terlalu formal atau terlalu santai.

Aturan menjawab:
- Jawab **langsung sesuai pertanyaan**, tanpa menambahkan konteks lain.
- **Jangan memberikan informasi tambahan** di luar isi pertanyaan, walaupun masih berkaitan.
- **Jangan menyimpulkan, mengarang, atau menebak** di luar isi dokumen.
- Jika ada tautan atau URL, tampilkan persis seperti di dokumen, tanpa diubah.
- Jika informasi tidak ditemukan secara eksplisit dalam dokumen, jawab:
  > "Maaf saya tidak menemukan informasi terkait data yang diprogramkan."

Jika pengguna memberikan koreksi:
- Jangan membantah atau bersikeras.
- Tanggapi dengan sopan.
- Akui jika pengguna benar, dan sampaikan bahwa mungkin dokumen belum memuat info tersebut.
  Contoh:
  > "Terima kasih atas koreksinya. Informasi tersebut belum tercantum dalam data yang saya akses, tapi sangat membantu."

Konteks:
{context}

Pertanyaan: {question}
Jawaban:
"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template
)

def load_document(file_path):
    ext = file_path.lower()
    if ext.endswith('.pdf'):
        return PyMuPDFLoader(file_path).load()
    elif ext.endswith('.docx'):
        return Docx2txtLoader(file_path).load()
    else:
        raise ValueError("Unsupported file type")

def clear_vectorstore():
    if os.path.exists(VECTORSTORE_DIR):
        for filename in os.listdir(VECTORSTORE_DIR):
            file_path = os.path.join(VECTORSTORE_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Gagal menghapus {file_path}. Alasan: {e}")

def get_qa_chain(file_path):
    # Bersihkan dulu vectorstore sebelumnya
    clear_vectorstore()

    # Load dokumen
    docs = load_document(file_path)

    # Buat vectorstore baru
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embedding,
        persist_directory=VECTORSTORE_DIR
    )

    # Simpan permanen vectorstore
    vectorstore.persist()

    retriever = vectorstore.as_retriever()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain

def load_qa_chain_from_vectorstore(file_path=None):
    if not os.path.exists(VECTORSTORE_DIR):
        raise ValueError("Vectorstore tidak ditemukan. Harap upload dokumen terlebih dahulu.")

    vectorstore = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embedding
    )

    retriever = vectorstore.as_retriever()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain
