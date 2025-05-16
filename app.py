from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import shutil

from lim_chat import get_qa_chain, load_qa_chain_from_vectorstore

app = FastAPI()

qa_chain = None

# Buat folder jika belum ada
os.makedirs("uploads", exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# ✅ Load vectorstore saat startup server
@app.on_event("startup")
def startup_event():
    global qa_chain
    try:
        qa_chain = load_qa_chain_from_vectorstore()
        print("✅ Vectorstore berhasil dimuat.")
    except Exception as e:
        print(f"⚠️ Belum ada vectorstore: {e}")
        qa_chain = None


# Fungsi tambahan untuk membersihkan vectorstore
def clear_vectorstore():
    dir_path = "vectorstore"
    if os.path.exists(dir_path):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"[ERROR] Gagal menghapus {file_path}: {e}")


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    filename = Path(file.filename).name
    ext = Path(filename).suffix.lower()
    allowed_ext = {".pdf", ".docx"}
    allowed_mime = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/x-pdf",
        "application/octet-stream",
    }

    print(f"[DEBUG] Upload file: {filename}")
    print(f"[DEBUG] MIME type: {file.content_type}")

    if ext not in allowed_ext:
        raise HTTPException(status_code=400, detail="Format file tidak didukung")

    if file.content_type not in allowed_mime:
        raise HTTPException(status_code=400, detail="Format file tidak didukung")

    file_path = f"uploads/{filename}"

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Bersihkan dan proses ulang vectorstore
        clear_vectorstore()

        global qa_chain
        qa_chain = get_qa_chain(file_path)
        print(f"[DEBUG] Dokumen dimuat dan QA Chain dibuat.")
        return {"message": "Dokumen berhasil dimuat", "filename": filename}
    except ValueError:
        return JSONResponse(content={"message": "Format file tidak didukung"}, status_code=400)
    except Exception as e:
        print(f"[ERROR] Gagal memproses dokumen: {e}")
        return JSONResponse(content={"message": f"Gagal memproses dokumen: {str(e)}"}, status_code=500)


@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
    except Exception:
        try:
            form = await request.form()
            message = form.get("message")
        except Exception:
            return JSONResponse(content={"response": "Format request tidak dikenali."}, status_code=400)

    if not message:
        return JSONResponse(content={"response": "Pesan kosong atau tidak ditemukan dalam permintaan."}, status_code=400)

    global qa_chain
    if qa_chain is None:
        return JSONResponse(content={"response": "Belum ada dokumen yang dimuat."}, status_code=400)

    try:
        result = qa_chain.invoke({"query": message})
        return {"response": result}
    except Exception as e:
        print(f"[ERROR] Saat menjawab pertanyaan: {e}")
        return JSONResponse(content={"response": f"Gagal menjawab: {str(e)}"}, status_code=500)


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("chat.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/uploaded-file")
def uploaded_file():
    files = os.listdir("uploads")
    if files:
        return {"filename": files[0]}  # asumsikan satu file
    return {"filename": None}
