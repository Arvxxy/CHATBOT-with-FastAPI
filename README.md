#MINIMAL SPESIFIKASI RAM 6 GB & 2 CORE CPU 

# Unduh & install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Jalankan Ollama
ollama serve

# Test Apakah Ollama Berjalan 
curl http://localhost:11434 

# Tarik model Mistral ke lokal
ollama pull mistral

# Pull Embedding Ollama
ollama pull nomic-embed-text

# pastikan ada kedua model dan embedding
ollama list 

# Cek proses Ollama di port 11434
sudo lsof -i :11434

# Kill proses lokal ( Opsional )
sudo systemctl stop ollama && sudo systemctl disable ollama

# Jalankan di latar belakang / jika ingin jalan diluar server ( opsional )
sudo nohup env OLLAMA_HOST=0.0.0.0:11434 ollama serve > /root/ollama.log 2>&1 &

# Install Paket yang dibutuhkan 
sudo apt install -y python3 python3-pip python3-venv

# Buat Folder Project
mkdir local-embeding && cd local-embeding

# Copy Project Repository
git clone https://github.com/Arvxxy/CHATBOT-with-FastAPI.git && cd CHATBOT-with-FastAPI

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Install Environment paket 
pip install -U langchain faiss-cpu fastapi uvicorn langchain-community langchain-ollama langchain_chroma python-multipart

# Atur Hak Akses Folder 
sudo chown -R user:user /home/to/path/local-embeding/CHATBOT-with-FastAPI/vectorstore/

# Jalankan API FastAPI
uvicorn app:app --reload --host 0.0.0.0 --port 8000



