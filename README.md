# Unduh & install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Jalankan Ollama
ollama serve
curl http://localhost:11434

# Tarik model Mistral ke lokal
ollama pull mistral

# Cek proses Ollama di port 11434
sudo lsof -i :11434

# Kill proses berdasarkan PID
sudo kill -9 <PID>

# Cek proses ollama via nama
ps aux | grep ollama

# Jalankan di latar belakang 
nohup OLLAMA_HOST=0.0.0.0:11434 ollama serve > ollama.log 2>&1 &

# Install Paket yang dibutuhkan 
sudo apt install -y python3 python3-pip python3-venv
pip install --upgrade pip
pip install sentence-transformers langchain faiss-cpu fastapi uvicorn
pip install -U langchain-community
pip install -U langchain_chroma

# Buat Folder Project
mkdir local-embeding
cd local-embeding
copy repository dari github

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Atur Hak Akses Folder FAISS
sudo chown -R ubuntu:ubuntu /home/ubuntu/chatbot/vectorstore/

# Jalankan API FastAPI
uvicorn app:app --reload --host 0.0.0.0 --port 8000



