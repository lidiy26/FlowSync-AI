# FlowSync AI (Streamlit MVP)

Bu proje, PRD kapsamına göre `MVP` seviyesinde çalışan bir Streamlit arayüzü sağlar:
- Yolcu için rota arama ve “konfor skoru”
- Yoğunluk yüksekse nudging (alternatif önerisi)
- Operatör için durak bazında yoğunluk (kırmızı/yeşil) ve önerilen ek sefer
- İsteğe bağlı Gemini tabanlı “AI açıklaması”

Varsayılan olarak mock (örnek) veri kullanılır. GTFS-Realtime/GPS ingest bağlandığında gerçek verilere geçilebilir.

## Kurulum

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Gemini API anahtarı

API anahtarınızı kodun içine yazmayın. Streamlit secrets veya ortam değişkeni kullanın.

`.streamlit/secrets.toml` örneği:
```toml
GOOGLE_API_KEY="REPLACE_ME"
```

Alternatif: PowerShell ortam değişkeni olarak `GOOGLE_API_KEY` tanımlayabilirsiniz.

## Çalıştırma

```powershell
streamlit run app.py
```

