# Gunakan Python 3.10 sebagai sistem dasar
FROM python:3.10

# Atur folder kerja di dalam mesin Hugging Face
WORKDIR /app

# Beri izin agar folder ini bisa ditulis oleh sistem
RUN chmod 777 /app

# Copy file requirements dan install library-nya
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh file backend kamu ke mesin Hugging Face
COPY . .

# Beri tahu Hugging Face port berapa yang dipakai (standarnya 7860)
EXPOSE 7860

# Perintah untuk menjalankan backend kamu
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
